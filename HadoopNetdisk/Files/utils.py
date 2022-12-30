from django.db import models
from pyhdfs import HdfsClient
import math
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from hbase.ttypes import ColumnDescriptor
from hbase import Hbase
from hbase.ttypes import Mutation


def hdfs_read(hdfs_file):
    client = HdfsClient(hosts='localhost:9870')  # hdfs地址
    res = client.open(hdfs_file)  # hdfs文件路径,根目录/
    return res
    # csv等文本文件按行读取可用以下方式
    # for r in res:
    #     line = str(r, encoding='utf8')  # open后是二进制,str()转换为字符串并转码
    #     print(line)


def hdfs_write(file_dir, hdfs_dir):
    client = HdfsClient(hosts='localhost:9870')  # hdfs地址
    try:
        client.copy_to_local(file_dir, hdfs_dir)  # hdfs地址一定要不存在
    except:
        print("file_dir or hdfs_dir error")


def hdfs_create(file, hdfs_dir):
    client = HdfsClient(hosts='localhost:9870')  # hdfs地址
    client.create(hdfs_dir, file)


def connect_to_hbase():
    '''
    连接远程HBase
    :return: 连接HBase的客户端实例
    '''
    # thrift默认端口是9090
    socket = TSocket.TSocket('10.0.86.245', 9090)  # 10.0.86.245是master结点ip
    socket.setTimeout(5000)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Hbase.Client(protocol)
    socket.open()
    return client


def list_all_tables(client):
    '''
    列出所有表
    '''
    print(client.getTableNames())


def create_table(client, tableName, *colFamilys):
    '''
    创建新表
    :param client: 连接HBase的客户端实例
    :param tableName: 表名
    :param *colFamilys: 任意个数的列簇名
    '''
    colFamilyList = []
    # 根据可变参数定义列族
    for colFamily in colFamilys:
        col = ColumnDescriptor(name=str(colFamily))
        colFamilyList.append(col)
    # 创建表
    client.create_table(tableName, colFamilyList)
    print('建表成功！')


def del_table(client, tableName):
    '''
    删除表
    '''
    if client.isTableEnabled(tableName):
        client.disableTable(tableName)  # 删除表前需要先设置该表不可用
    client.del_table(tableName, )
    print('删除表{}成功！'.format(tableName))


def del_all_rows(client, tableName, rowKey):
    '''
    删除指定表某一行数据
    :param client: 连接HBase的客户端实例
    :param tableName: 表名
    :param rowKey: 行键
    '''
    if query_a_row(client, tableName, rowKey):
        client.del_all_rows(tableName, rowKey, )
        print('删除{0}表{1}行成功！'.format(tableName, rowKey))
    else:
        print('错误提示：未找到{0}表{1}行数据！'.format(tableName, rowKey))


def insert_a_row(client, tableName, rowName, colFamily, columnName, value):
    '''
    在指定表指定行指定列簇插入/更新列值
    '''
    mutations = [Mutation(column='{0}:{1}'.format(colFamily, columnName), value=str(value))]
    client.mutateRow(tableName, rowName, mutations)
    print('在{0}表{1}列簇{2}列插入{3}数据成功.'.format(tableName, colFamily, columnName, value))


def query_a_row(client, table_name, row_name, col_name=None, columns=None):
    '''
    功能：获取HBase指定表的某一行数据。
    :param client 连接HBase的客户端实例
    :param table_name 表名
    :param row_name 行键名
    :param col_name 列簇名
    :param columns 一个包含指定列名的列表
    :return RowDict 一个包含列名和列值的字典(若直接返回指定列值，则返回的是字符串)
    '''
    # 1.如果列簇和列名两个都为空，则直接取出当前行所有值，并转换成字典形式作为返回值
    row_dict = {}
    if col_name is None and columns is None:
        results = client.query_a_row(table_name, row_name, )
        for result in results:
            for key, TCell_value in result.columns.items():
                # 由于key值是'列簇:列名'形式,所以需要通过split函数以':'把列名分割出来
                each_col = key.split(':')[1]
                row_dict[each_col] = TCell_value.value  # 取出TCell元组中的value值
        return row_dict
    # 2.如果仅是列名为空，则直接取出当前列簇所有值，并转换成字典形式作为返回值
    elif columns is None:
        results = client.getRowWithColumns(table_name, row_name, [col_name])
        for result in results:
            for key, TCell_value in result.columns.items():
                # 由于key值是'列簇:列名'形式,所以需要通过split函数以':'把列名分割出来
                each_col = key.split(':')[1]
                row_dict[each_col] = TCell_value.value  # 取出TCell元组中的value值
        return row_dict
    # 3.如果列簇和列名都不为空，则直接取出当前列的值
    elif col_name is not None and columns is not None:
        results = client.query_a_row(table_name, row_name, )
        for result in results:
            value = result.columns.get('{0}:{1}'.format(col_name, columns)).value
        return value
    else:
        raise Exception('关键参数缺失，请重新检查参数！')


def scanner_get_select(client, table_name, columns, start_row, stop_row=None, rows_cnt=2000):
    '''
    依次扫描HBase指定表的每行数据(根据起始行，扫描到表的最后一行或指定行的前一行)
    :param client: 连接HBase的客户端实例
    :param table_name: 表名
    :param columns: 一个包含(一个或多个列簇下对应列名的)列表
    :param start_row: 起始扫描行
    :param stop_row:  停止扫描行(默认为空)
    :param rows_cnt:  需要扫描的行数
    :return MutilRowsDict: 返回一个包含多行数据的字典，以每行行键定位是哪一行
    '''
    # 如果stopRow为空，则使用scannerOpen方法扫描到表最后一行
    if stop_row is None:
        scannerId = client.scannerOpen(table_name, start_row, columns)
    # 如果stopRow不为空，则使用scannerOpenWithStop方法扫描到表的stopRow行
    else:
        scannerId = client.scannerOpenWithStop(table_name, start_row, stop_row, columns)
    results = client.scannerGetList(scannerId, rows_cnt)
    # 如果查询结果不为空，则传入行键值或列值参数正确
    if results:
        mutil_rows_dict = {}
        for result in results:
            row_dict = {}
            for key, TCell_value in result.columns.items():
                # 获取该行行键
                rowKey = result.row
                # 由于key值是'列簇:列名'形式,所以需要通过split函数以':'把列名分割出来
                each_col = key.split(':')[1]
                row_dict[each_col] = TCell_value.value  # 取出TCell元组中的value值
                # 把当前含有多个列值信息的行的字典和改行行键存储在MutilRowsDict中
                mutil_rows_dict[rowKey] = row_dict
        return mutil_rows_dict
    # 如果查询结果为空，则传入行键值或列值参数错误，返回空列表
    else:
        return []


def bigInt2str(bigNum):
    '''
    大整数转换为字符串
    :param bigNum: 大整数
    :return string: 转换后的字符串
    '''
    string = ''
    for i in range(len(str(bigNum)), 0, -1):
        a = int(math.pow(10, (i - 1)))
        b = bigNum // a % 10
        string += str(b)
    return string


if __name__ == '__main__':
    # 连接HBase数据库，返回客户端实例
    client = connect_to_hbase()
    # 创建表
    # createTable(client, 'firstTable', 'c1', 'c2', 'c3')
    # 插入或更新列值
    # insertRow(client, 'firstTable', '0001', 'c1', 'name', 'sparks')
    # 获取HBase指定表的某一行数据
    # dataDict = getRow(client, 'firstTable', '0001')
    # print(dataDict)
    # 删除指定表某行数据
    # deleteAllRow(client, '2018AAAI_Papers', '20181106')
    # 依次扫描HBase指定表的每行数据(根据起始行，扫描到表的最后一行或指定行的前一行)
    MutilRowsDict = scanner_get_select(client, '2018AAAI_Papers', ['paper_info:title', 'paper_info:keywords'],
                                       '20180900', '20180904')
    print(MutilRowsDict)
    # 列出所有表名
    list_all_tables(client)
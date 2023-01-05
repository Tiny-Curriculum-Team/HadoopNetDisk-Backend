import os
import zipfile
from hdfs import InsecureClient
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from hbase.ttypes import ColumnDescriptor
from hbase import Hbase
from hbase.ttypes import Mutation


def zip_ya(compress_dir, file_name, file_path):
    zip_file_path = os.path.join(file_path, file_name)
    z = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(compress_dir):
        fpath = dirpath.replace(compress_dir, '')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
            print('压缩成功')
    z.close()


def connect_to_hdfs():
    client = InsecureClient("http://127.0.0.1:14000/", root='/user/hadoop/', timeout=10000)
    return client


def hdfs_read(cli, hdfs_file: str):
    res = cli.read(hdfs_file)
    return res


def hdfs_del_files(cli, hdfs_path):
    cli.delete(hdfs_path)


def hdfs_create(cli, file, hdfs_dir):
    cli.create(hdfs_dir, file)


def hdfs_mkdir(cli, hdfs_path):
    cli.makedirs(hdfs_path)


# 上传文件到hdfs
def upload_to_hdfs(cli, local_path, hdfs_path):
    cli.upload(hdfs_path, local_path, cleanup=True)


# 从hdfs获取文件到本地
def download_from_hdfs(cli, hdfs_path, local_path):
    cli.download(hdfs_path, local_path, overwrite=False)


#覆盖数据写到hdfs文件
def hdfs_write(client, hdfs_path, data, overwrite=False):
    client.write(hdfs_path, data, overwrite=overwrite, append=False)


def hdfs_mv(client, hdfs_src_path, hdfs_dst_path):
    client.rename(hdfs_src_path, hdfs_dst_path)


def hdfs_list(client, hdfs_path, verbose=False):
    return client.list(hdfs_path, status=True) if verbose else client.list(hdfs_path, status=False)


###
### HBase
###
def connect_to_hbase():
    '''
    连接远程HBase
    :return: 连接HBase的客户端实例
    '''
    # thrift默认端口是9090
    socket = TSocket.TSocket('127.0.0.1', 9090)  # 10.0.86.245是master结点ip
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
    return client.getTableNames()



def create_table(client, table_name, *col_familys):
    '''
    创建新表
    :param client: 连接HBase的客户端实例
    :param table_name: 表名
    :param *colFamilys: 任意个数的列簇名
    '''
    col_family_list = []
    # 根据可变参数定义列族
    for col_family in col_familys:
        col = ColumnDescriptor(name=str(col_family))
        col_family_list.append(col)
    # 创建表
    client.createTable(table_name, col_family_list)
    print('建表成功！')


def del_table(client, table_name):
    '''
    删除表
    '''
    if client.isTableEnabled(table_name):
        client.disableTable(table_name)  # 删除表前需要先设置该表不可用
    client.deleteTable(table_name)
    print('删除表{}成功！'.format(table_name))


def del_all_rows(client, table_name, row_key):
    '''
    删除指定表某一行数据
    :param client: 连接HBase的客户端实例
    :param table_name: 表名
    :param row_key: 行键
    '''
    if query_a_row(client, table_name, row_key):
        client.deleteAllRow(table_name, row_key)
        print('删除{0}表{1}行成功！'.format(table_name, row_key))
    else:
        print('错误提示：未找到{0}表{1}行数据！'.format(table_name, row_key))


def insert_a_row(client, table_name, row_name, col_family, column_name, value):
    '''
    在指定表指定行指定列簇插入/更新列值
    '''
    mutations = [Mutation(column='{0}:{1}'.format(col_family, column_name), value=str(value))]
    client.mutateRow(table_name, row_name, mutations)
    print('在{0}表{1}列簇{2}列插入{3}数据成功.'.format(table_name, col_family, column_name, value))


def find_file(client, table_name, profix, columus):
    scan_id = client.scannerOpenWithPrefix(table_name, profix, columus)
    result = client.scannerGet(scan_id)
    return result


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
        results = client.getRowWithColumns(table_name, row_name, col_name)
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
        results = client.getRowWithColumns(table_name, row_name, )
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
        scanner_id = client.scannerOpen(table_name, start_row, columns)
    # 如果stopRow不为空，则使用scannerOpenWithStop方法扫描到表的stopRow行
    else:
        scanner_id = client.scannerOpenWithStop(table_name, start_row, stop_row, columns)
    results = client.scannerGetList(scanner_id, rows_cnt)
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
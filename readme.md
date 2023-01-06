# Docker配置Hadoop集群步骤

```shell
docker pull pommespeter0601/hbase-docker
docker run -itd -p 9090:9090 -p 14000:14000 --name hdp --restart=always pommespeter0601/hbase-docker
docker exec -it hdp bash
# docker stop $(docker ps -a -q) # 停止所有容器
# docker rm $(docker ps -a -q) # 删除所有容器
cd /usr/local/hadoop/etc/hadoop

vim httpfs-env.sh
# export HTTPFS_HTTP_PORT=14000 # 取消该行的注释

vim hdfs-site.xml
# 添加以下部分
    <property>
        <name>dfs.webhdfs.enabled</name>
        <value>true</value>
    </property>
    <property>
        <name>dfs.permissions.enabled</name>
        <value>false</value>
    </property>
vim core-site.xml
# 添加以下部分
    <property>
        <name>hadoop.proxyuser.hadoop.hosts</name>
        <value>*</value>
    </property>
    <property>
        <name>hadoop.proxyuser.hadoop.groups</name>
        <value>*</value>
    </property>
```

# Hadoop启动步骤
```shell
docker exec -it hdp bash # 通过Bash进入Docker容器的终端
su hadoop # 切换用户为Hadoop
sudo /etc/init.d/ssh restart # 重启SSH
start-dfs.sh && start-hbase.sh && hbase-daemon.sh start thrift && hdfs --daemon start httpfs # 启动项目所需的所有服务
jps # 查看正在运行的进程
```

# 为什么用MySQL存储用户信息而不是使用HBase？

> 参考：https://xie.infoq.cn/article/071daf5f50cfbfb5198b9c30d

1. 从引擎结构上看，HBase侧重于写、存储紧凑无浪费、IO放大、数据导入能力强，而我们存储用户数据对写的要求不高
2. 我们面对的用户规模并没有达到那种规模
3. 从存储数据结构看，HBase是使用基于LSM树的数据结构进行存储的，该数据结构本身特性就是有利于写，不利于读，先从 memtable 查找，再到磁盘所有的 sstable 文件查找。

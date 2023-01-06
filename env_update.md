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
    
vim hadoop-env.sh
# 在其中加入这一行
HADOOP_SHELL_EXECNAME=root

su hadoop
sudo /etc/init.d/ssh restart
start-dfs.sh && start-hbase.sh && hbase-daemon.sh start thrift && hdfs --daemon start httpfs
jps
hadoop fs -chmod -R 777 /
```

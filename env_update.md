# env update

```shell
cd /usr/local/hadoop/etc/hadoop

vim httpfs-env.sh
# export HTTPFS_HTTP_PORT=14000 # 取消该行的注释

vim hdfs-site.xml
# 在coufiguration中加上这一列
    <property>
        <name>dfs.webhdfs.enabled</name>
        <value>true</value>
    </property>
vim core-site.xml
# 在coufiguration中加上这两列
    <property>
        <name>hadoop.proxyuser.hadoop.hosts</name>
        <value>*</value>
    </property>
    <property>
        <name>hadoop.proxyuser.hadoop.groups</name>
        <value>*</value>
    </property>
    
su hadoop
sudo /etc/init.d/ssh restart
start-dfs.sh
start-hbase.sh
httpfs.sh start
jps
```
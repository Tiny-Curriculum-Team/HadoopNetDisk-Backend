## Docker

本项目需要由docker安装Hadoop集群，进入到`Hadoop_Cluster`文件夹内，执行`docker-compose up -d`。

# 答辩应对问题：

## 为什么用MySQL存储用户信息而不是使用HBase？

> 参考：https://xie.infoq.cn/article/071daf5f50cfbfb5198b9c30d

1. 从引擎结构上看，HBase侧重于写、存储紧凑无浪费、IO放大、数据导入能力强，而我们存储用户数据对写的要求不高
2. 我们面对的用户规模并没有达到那种规模
3. 从存储数据结构看，HBase是使用基于LSM树的数据结构进行存储的，该数据结构本身特性就是有利于写，不利于读，先从 memtable 查找，再到磁盘所有的 sstable 文件查找。
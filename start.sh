docker pull pommespeter0601/hbase-docker
docker run -itd -p 9090:9090 -p 14000:14000 --name hdp --restart=always pommespeter0601/hbase-docker
docker exec -it <containerID or containerName> bash
# docker stop $(docker ps -a -q)
# docker rm $(docker ps -a -q)
su hadoop
sudo /etc/init.d/ssh restart
start-dfs.sh
start-hbase.sh
hbase-daemon.sh start thrift
httpfs.sh start
jps

python HadoopNetdisk/manage.py makemigrations
python HadoopNetdisk/manage.py migrate
python HadoopNetdisk/manage.py runserver localhost:2731

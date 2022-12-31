docker pull pommespeter0601/hbase-docker
docker run -itd -p 9870:9870 -p 9090:9090 --name hdp pommespeter0601/hbase-docker

python HadoopNetdisk/manage.py makemigrations
python HadoopNetdisk/manage.py migrate
python HadoopNetdisk/manage.py runserver localhost:2731
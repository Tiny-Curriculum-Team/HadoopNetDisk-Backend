cd Hadoop_Cluster
docker-compose up -d
cd ..

python HadoopNetdisk/manage.py makemigrations
python HadoopNetdisk/manage.py migrate
python HadoopNetdisk/manage.py runserver localhost:2731
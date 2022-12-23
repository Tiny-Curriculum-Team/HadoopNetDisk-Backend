FROM sunwenxiang/hadoop-hbase-spark:10.0

WORKDIR ~

COPY startall.sh /root/startall.sh
COPY stopall.sh /root/stopall.sh
ADD run.sh /run.sh
RUN /usr/local/hadoop/bin/hadoop namenode -format
RUN chmod a+x /run.sh
RUN chmod a+x /root/startall.sh
RUN chmod a+x /root/stopall.sh

EXPOSE 9870 8088

CMD ["/run.sh"]
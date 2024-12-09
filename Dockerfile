FROM apache/airflow:2.7.0

ENV PATH=$PATH:$JAVA_HOME/bin

USER root
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget procps && \
    apt-get clean

RUN wget https://downloads.apache.org/spark/spark-3.4.4/spark-3.4.4-bin-hadoop3.tgz && \
    tar -xvf spark-3.4.4-bin-hadoop3.tgz && \
    mv spark-3.4.4-bin-hadoop3 /opt/spark && \
    rm spark-3.4.4-bin-hadoop3.tgz

    
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV PATH=$PATH:$JAVA_HOME/bin:$SPARK_HOME/bin

USER airflow

COPY requirements.txt .
RUN pip install -r requirements.txt

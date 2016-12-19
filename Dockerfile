FROM debian:testing

MAINTAINER Xero-Hige <Gaston.martinez.90@gmail.com>
WORKDIR /

RUN echo "deb http://mirrors.dcarsat.com.ar/debian/ testing main contrib non-free \
          \ndeb-src http://mirrors.dcarsat.com.ar/debian/ testing main contrib non-free" > /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends aptitude && \
    aptitude install -y \
        wget \
        python3-pip \
		python3-setuptools && \
    echo 'deb http://www.rabbitmq.com/debian/ testing main' | tee /etc/apt/sources.list.d/rabbitmq.list && \
    wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | apt-key add - && \
    aptitude update && aptitude install rabbitmq-server -y && \
    rm -rf /var/lib/apt/lists/* && \
    aptitude clean

RUN pip3 install twitter --no-cache-dir

COPY /src /Magus

CMD ["python3","/Magus/tweetsFetcher.py"]
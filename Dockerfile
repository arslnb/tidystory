FROM ubuntu
MAINTAINER Arsalan Bashir <arsalan.b4@gmail.com>

ENV INSTALL_PATH /tidystory
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN apt-get update && apt-get -y install python \
    python-pip \
    build-essential \
    software-properties-common \
    unzip \
    curl \
    xvfb \
    wget

# Firefox browser to run the tests
RUN apt-get update && apt-get install -y firefox
 
# Gecko Driver
ENV GECKODRIVER_VERSION 0.21.0
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GECKODRIVER_VERSION \
  && chmod 755 /opt/geckodriver-$GECKODRIVER_VERSION \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/geckodriver \
  && ln -fs /opt/geckodriver-$GECKODRIVER_VERSION /usr/bin/wires

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD gunicorn app:app -b 0.0.0.0:5000
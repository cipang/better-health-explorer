FROM ubuntu
RUN mkdir /app /appstatic
WORKDIR /app
RUN apt-get update && apt-get install -y curl \
    software-properties-common \
    libxext6 \
    libxrender1 \
    libfontconfig \
    libpq-dev

RUN add-apt-repository -y ppa:fkrull/deadsnakes
RUN apt-get update && apt-get install -y python3.5 python3.5-dev
RUN curl -s https://bootstrap.pypa.io/get-pip.py | python3.5

ADD requirements.txt /app
RUN pip install -r requirements.txt

RUN curl -s http://download.patrickpang.net/bhx/hisdb.sqlite3.tar.gz | tar zxf -

ADD . /app
RUN python3.5 manage.py collectstatic --noinput -v 0
RUN python3.5 manage.py migrate

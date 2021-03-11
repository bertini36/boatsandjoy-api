FROM python:3.7

ARG REQUIREMENTS

WORKDIR /code/

RUN apt update \
 && apt install -y libjpeg-dev libgraphviz-dev libpq-dev build-essential \
 && apt install -y libxmlsec1-dev pkg-config graphviz graphicsmagick python-dev gettext

COPY requirements/prod.txt /code/requirements/
COPY requirements/dev.txt /code/requirements/

RUN pip3 install --upgrade pip  && pip3 install -r /code/requirements/prod.txt && pip3 install -r /code/requirements/dev.txt

RUN groupadd nobody

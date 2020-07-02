FROM python:3.7

ARG REQUIREMENTS

WORKDIR /code/

RUN apt update \
 && apt install -y libjpeg-dev libgraphviz-dev libpq-dev build-essential \
 && apt install -y libxmlsec1-dev pkg-config graphviz graphicsmagick python-dev gettext

COPY requirements.txt /code/requirements/
COPY ${REQUIREMENTS} /code/requirements/

RUN pip3 install --upgrade pip && pip3 install -r /code/requirements/${REQUIREMENTS}

COPY . /code/

RUN groupadd nobody

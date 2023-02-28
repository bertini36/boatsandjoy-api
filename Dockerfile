FROM python:3.10

WORKDIR /code/

RUN apt update \
 && apt install -y libjpeg-dev libgraphviz-dev libpq-dev build-essential wait-for-it \
 && apt install -y libxmlsec1-dev pkg-config graphviz graphicsmagick python-dev gettext

COPY requirements/prod.txt /code/requirements/
COPY requirements/dev.txt /code/requirements/

RUN pip install --upgrade pip  && pip install -r /code/requirements/prod.txt && pip install -r /code/requirements/dev.txt
RUN pip install --upgrade pip-tools

RUN groupadd nobody

FROM python:3

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>
ENV PYTHONUNBUFFERED 1
# give tendermint some time to start
ENV STARTUP_DELAY 30

RUN mkdir -p /client

WORKDIR /client/

add requirements.txt /client/

RUN pip install -r requirements.txt

add . /client/

ENTRYPOINT ["python"]
CMD ["src/client.py", "5", "5"]

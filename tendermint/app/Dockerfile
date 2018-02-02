FROM python:3

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

WORKDIR /app/

add requirements.txt /app/

RUN pip install -r requirements.txt

add . /app/

ENTRYPOINT ["python"]
CMD ["src/app.py"]

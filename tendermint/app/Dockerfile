FROM python:3

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

WORKDIR /app/

add requirements.txt /app/

RUN pip install -r requirements.txt

add . /app/

# RUN yarn --frozen-lockfile && \
	# yarn cache clean

ENTRYPOINT ["python3"]
cmd ["app.py"]
# CMD ["manage.py", "runserver", "0.0.0.0:8000"]
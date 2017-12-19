FROM node:8

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>
# ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app

WORKDIR /app/

# add requirements.txt /app/

add package.json /app/

RUN yarn --frozen-lockfile && \
	yarn cache clean

# RUN pip install -r requirements.txt

add . /app/



#nodemon --exec "python -v" ./app.py

ENTRYPOINT ["node"]
CMD ["index.js"]
#ENTRYPOINT ["nodemon"]
#cmd ["--exec", "python", "app.py"]
# CMD ["manage.py", "runserver", "0.0.0.0:8000"]
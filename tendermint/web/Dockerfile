FROM node:8

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>

RUN mkdir -p /app

WORKDIR /app/

add package.json /app/

RUN yarn

add . /app/

ENTRYPOINT ["node"]
CMD ["index.js"]
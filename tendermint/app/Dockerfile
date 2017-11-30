FROM node:8

MAINTAINER Joseph Verburg <j.p.verburg@student.tudelft.nl>

RUN mkdir -p /app

WORKDIR /app

copy package.json yarn.lock index.js ./

RUN yarn --frozen-lockfile && \
	yarn cache clean

ENTRYPOINT ["npm"]
CMD ["start"]
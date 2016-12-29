FROM node:argon
RUN mkdir -p /app
WORKDIR /app
COPY package.json /tmp/
RUN cd /tmp && npm -g install && cp -R node_modules /app/
RUN npm install eslint eslint-plugin-smells istanbul mocha babel-cli
CMD /app/docker_entry.sh
# ENV NODE_PATH=/usr/local/lib/node_modules
ENV NODE_PATH=/app/node_modules
ENV NODE_ENV=test
EXPOSE 8080

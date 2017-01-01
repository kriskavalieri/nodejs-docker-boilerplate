FROM node:argon
RUN mkdir -p /app
WORKDIR /app
COPY package.json /tmp/
RUN cd /tmp && \
    npm install && \
    npm install eslint eslint-plugin-smells istanbul@1.0.0-alpha.2 mocha babel-cli && \
    cp -R node_modules /app/
# ENV NODE_PATH=/usr/local/lib/node_modules
ENV NODE_PATH=/app/node_modules
ENV NODE_ENV=test
EXPOSE 8080
CMD /app/docker_entry.sh

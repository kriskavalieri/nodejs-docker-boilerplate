FROM node:argon
RUN mkdir -p /app
WORKDIR /app
COPY package.json /tmp/
RUN cd /tmp && npm -g install
RUN npm install -g eslint eslint-plugin-smells istanbul tape
CMD /app/docker_entry.sh
ENV NODE_PATH=/usr/local/lib/node_modules
EXPOSE 8080

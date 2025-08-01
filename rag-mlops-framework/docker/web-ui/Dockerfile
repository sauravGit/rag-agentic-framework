FROM node:16-alpine

WORKDIR /app

COPY web-ui /app/
RUN npm install

EXPOSE 3000

CMD ["npm", "start"]

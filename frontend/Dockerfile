FROM node:18

WORKDIR /app
COPY . .

RUN rm -rf package-lock.json node_modules
RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
FROM node:18 AS builder

WORKDIR /app
COPY . .

# 移除 lockfile 與 node_modules 以免平台不相容
RUN rm -rf package-lock.json node_modules

# 安裝乾淨的依賴
RUN npm install

# 正式 build
RUN npm run build

# 部署到 nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
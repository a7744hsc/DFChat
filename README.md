# Vue Chat GUI & FastAPI Backend

中文版 | [English](README-EN.md)

这是一个可以自行部署的类似 chatGPT 功能的 BS 架构工具，包含一个 vue 编写的前端和 fastapi 编写的后端。工具可以使用 Azure OpenAI API 或者 OpenAI API 进行对话。

## 项目介绍

**前端项目：vue-chat-gui（已弃用，请使用基于quasar的前端）**

这是一个基于 Vue.js 的类 ChatGPT 聊天程序，用户可以通过这个应用程序向 chatGPT 提问。

**前端项目2：quasar-dfchat**

新版本的前端，界面更加友好，功能更加完善。

**后端项目：backend (FastAPI)**

这是一个基于 FastAPI 的后端项目，它为前端提供 API 接口。

## 安装与运行

### 使用 docker 启动前后端(推荐)

1. 修改 backend/config.py 中的配置

2. 在根目录 Build docker image
   ```
   docker build -t dfchat:0.1 -f deployment/Dockerfile-AllinOne .
   ```
3. 运行 docker image（这里的 80 是你的本地端口）
   ```
   sudo docker run -d -p 80:8000 dfchat:0.1
   sudo docker run -d -v /yourdbpath/mydb.db:/backend/mydb.db  -p 80:8000 dfchat:0.2
   ```
4. 打开浏览器，输入 http://localhost

### 将服务部署到公网（https）

要将服务安全部署到公网需要使用https，有获取https证书通常需要一个域名，这里以let‘s encrypt + docker compose 实现一个简单的前端部署。详细教程请参考[DigitalOcean教程](https://www.digitalocean.com/community/tutorials/how-to-secure-a-containerized-node-js-application-with-nginx-let-s-encrypt-and-docker-compose)

1. 申请域名并创建服务器，并将域名解析到服务器ip
2. 在服务器中安装docker和docker-compose
3. 在https-docker-compose.yml中修改域名和邮箱, 在nginxconf/nginx.conf中修改域名
4. 创建dhparam.pem文件
   ```
   mkdir dhparam
   sudo openssl dhparam -out dhparam/dhparam-2048.pem 2048
   ```
4. 在根目录下运行docker-compose up -d 启动服务
5. 使用crontab定时更新证书（可能需要使用root账户运行定时任务）
   ```
   sudo crontab -e
   0 12 * * * /home/azureuser/dfchat/deploy/cert-renew.sh >> /home/azureuser/dfchat/deploy/cert_renew_cron.log 2>&1
   ```

### 启动前端项目

1. 进入前端项目目录：

   ```
   cd quasar-dfchat
   ```

2. 安装依赖：

   ```
   npm install
   ```

3. 运行项目：

   ```
   quasar dev
   ```

### 启动后端项目

1. 安装 Python 虚拟环境：

   ```
   python -m venv venv
   ```

2. 激活虚拟环境：

   - Windows:

     ```
     venv\Scripts\activate
     ```

   - Linux/Mac:

     ```
     source venv/bin/activate
     ```

3. 进入后端项目目录：

   ```
   cd backend
   ```

4. 安装依赖：

   ```
   pip install -r requirements.txt
   pip install uvicorn[standard]
   ```

5. 运行项目：

   ```
   uvicorn main:app --reload
   ```

6. API 页面：

   ```
   http://localhost:8000/docs
   ```

## TODO 列表

- [x] 实现用户注册和登录功能
- [x] 对话记录功能
- [ ] 对话导出功能
- [ ] API 费用统计功能
- [ ] quasar 前端重构
  - [x] 聊天记录功能
  - [x] 新建聊天
  - [x] 支持 SSE
  - [ ] 支持代码复制

## 贡献

欢迎提交 Pull Request 来帮助改进这个项目。由于本人前端能力有限，急需前端大佬的帮助。

## 许可证

本项目采用 MIT 许可证，详情请参阅[LICENSE](LICENSE)文件。

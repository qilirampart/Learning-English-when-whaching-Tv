# 🚀 快速部署检查清单

按照这个清单操作，30分钟内完成部署！

---

## ✅ 准备阶段（5分钟）

- [ ] 注册 Railway 账号：https://railway.app/
- [ ] 注册 Vercel 账号：https://vercel.com/
- [ ] （可选）注册有道翻译API：https://ai.youdao.com/
- [ ] 确保代码已推送到 GitHub

---

## ✅ 部署后端（10分钟）

### Railway 部署

- [ ] 登录 Railway
- [ ] 创建新项目 → "Deploy from GitHub repo"
- [ ] 选择你的仓库
- [ ] 设置 Root Directory：`backend`
- [ ] 添加环境变量：
  - [ ] `SECRET_KEY` = (生成一个随机字符串)
  - [ ] `FLASK_ENV` = `production`
  - [ ] `YOUDAO_APP_KEY` = (可选)
  - [ ] `YOUDAO_APP_SECRET` = (可选)
  - [ ] `CORS_ORIGINS` = `http://localhost:5173`
- [ ] 等待部署完成
- [ ] 点击 Settings → Generate Domain
- [ ] **记下域名**：`_____________________________.railway.app`
- [ ] 测试访问：`https://你的域名.railway.app/api/statistics/overview`

**生成 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## ✅ 部署前端（10分钟）

### Vercel 部署

- [ ] 登录 Vercel
- [ ] 点击 "Add New..." → "Project"
- [ ] 选择你的 GitHub 仓库
- [ ] 设置 Root Directory：`frontend`
- [ ] 添加环境变量：
  - [ ] Key: `VITE_API_BASE_URL`
  - [ ] Value: `https://你的Railway域名.railway.app`
- [ ] 点击 "Deploy"
- [ ] 等待部署完成
- [ ] **记下域名**：`_____________________________.vercel.app`

---

## ✅ 配置 CORS（5分钟）

### 更新 Railway 环境变量

- [ ] 打开 Railway 项目
- [ ] 点击 "Variables"
- [ ] 更新 `CORS_ORIGINS` 为：
  ```
  https://你的Vercel域名.vercel.app,http://localhost:5173
  ```
- [ ] 保存，等待自动重新部署

### 更新前端配置

- [ ] 修改本地 `frontend/vercel.json` 文件
- [ ] 将 `your-backend-url.railway.app` 替换为实际的 Railway 域名
- [ ] 提交并推送到 GitHub
- [ ] Vercel 会自动重新部署

---

## ✅ 测试（5分钟）

访问你的 Vercel 域名，测试以下功能：

- [ ] 页面正常打开
- [ ] 查询单词功能
- [ ] 单词库显示
- [ ] 学习计划功能
- [ ] 统计数据显示

---

## ✅ （可选）升级数据库

### 添加 PostgreSQL

为了防止数据丢失，建议使用 PostgreSQL：

- [ ] 在 Railway 项目中点击 "New"
- [ ] 选择 "Database" → "Add PostgreSQL"
- [ ] Railway 会自动设置 `DATABASE_URL`
- [ ] 应用会自动重新部署并使用 PostgreSQL

---

## 🎉 完成！

你的应用已经成功部署！

**应用地址：**
- 🌐 前端：https://_____________________________.vercel.app
- 🔧 后端：https://_____________________________.railway.app

**下一步：**
- 分享给朋友使用
- 绑定自定义域名
- 配置真实的翻译API

---

## 📞 遇到问题？

查看详细文档：`DEPLOY.md`

常见问题：
- ❌ CORS 错误 → 检查 Railway 的 CORS_ORIGINS 配置
- ❌ 后端连接失败 → 检查 Vercel 的 VITE_API_BASE_URL 配置
- ❌ 部署失败 → 查看 Railway/Vercel 的日志

---

**祝部署顺利！🚀**

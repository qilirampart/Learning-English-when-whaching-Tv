# 免费部署指南 - Railway + Vercel

本文档将指导您如何将美剧单词学习助手免费部署到线上。

## 📋 部署前准备

### 1. 注册账号（全部免费）

- **Railway账号**：https://railway.app/
  - 使用GitHub账号登录即可
  - 每月免费 $5 额度（约500小时运行时间）

- **Vercel账号**：https://vercel.com/
  - 使用GitHub账号登录即可
  - 无限流量，完全免费

- **有道翻译API**（可选）：https://ai.youdao.com/
  - 每月免费 100万字符
  - 注册后创建应用获取 APP_KEY 和 APP_SECRET

### 2. 代码准备

确保你的代码已经推送到 GitHub 仓库。

---

## 🚀 第一步：部署后端到 Railway

### 1. 登录 Railway

访问 https://railway.app/ ，点击 "Login" 使用 GitHub 账号登录。

### 2. 创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你的项目仓库
4. 选择 `backend` 目录

### 3. 配置环境变量

在 Railway 项目页面，点击 "Variables" 标签，添加以下环境变量：

```ini
# 必需配置
SECRET_KEY=your-random-secret-key-here-use-long-string
FLASK_ENV=production

# 可选：有道翻译API（不配置将使用模拟数据）
YOUDAO_APP_KEY=你的有道APP_KEY
YOUDAO_APP_SECRET=你的有道APP_SECRET

# CORS配置（等前端部署后再添加）
CORS_ORIGINS=http://localhost:5173
```

**生成安全的 SECRET_KEY：**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 设置根目录

1. 点击 "Settings" 标签
2. 找到 "Root Directory" 设置
3. 输入：`backend`
4. 点击保存

### 5. 部署

Railway 会自动开始部署。等待几分钟，部署完成后：

1. 点击 "Settings" → "Generate Domain"
2. 会生成一个域名，类似：`your-app.railway.app`
3. **记下这个域名**，后面配置前端时需要用到

### 6. 测试后端

访问 `https://your-app.railway.app/api/statistics/overview`

如果返回 JSON 数据，说明后端部署成功！

---

## 🎨 第二步：部署前端到 Vercel

### 1. 登录 Vercel

访问 https://vercel.com/ ，点击 "Sign Up" 使用 GitHub 账号登录。

### 2. 导入项目

1. 点击 "Add New..." → "Project"
2. 选择你的 GitHub 仓库
3. Vercel 会自动识别为 Vite 项目

### 3. 配置项目

在 "Configure Project" 页面：

**Root Directory：**
- 点击 "Edit"
- 选择 `frontend` 目录

**Environment Variables（环境变量）：**

添加以下环境变量：

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://your-app.railway.app` |

**注意：** 将 `your-app.railway.app` 替换为你在 Railway 中获得的实际域名。

### 4. 部署

1. 点击 "Deploy"
2. 等待几分钟，部署完成
3. Vercel 会给你一个域名，类似：`your-app.vercel.app`

### 5. 更新 vercel.json

部署成功后，需要更新 `frontend/vercel.json` 文件中的后端地址：

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-app.railway.app/api/:path*"
    }
  ]
}
```

将 `your-app.railway.app` 替换为你的实际 Railway 域名，然后推送到 GitHub。Vercel 会自动重新部署。

---

## 🔄 第三步：配置 CORS（跨域）

回到 Railway，更新 CORS 环境变量：

1. 打开 Railway 项目
2. 点击 "Variables"
3. 找到 `CORS_ORIGINS`
4. 更新值为：
```
https://your-app.vercel.app,http://localhost:5173
```

将 `your-app.vercel.app` 替换为你的实际 Vercel 域名。

5. 保存后，Railway 会自动重新部署

---

## ✅ 第四步：测试部署

访问你的 Vercel 域名：`https://your-app.vercel.app`

测试以下功能：

1. ✅ 页面能正常打开
2. ✅ 查询单词功能正常
3. ✅ 单词库能显示
4. ✅ 学习计划正常工作
5. ✅ 统计数据正常显示

---

## 🎯 完成！

恭喜！你的美剧单词学习助手已经成功部署到线上了！

**你的应用地址：**
- 前端：`https://your-app.vercel.app`
- 后端：`https://your-app.railway.app`

---

## 📝 后续维护

### 更新代码

**自动部署：**
- 推送代码到 GitHub
- Railway 和 Vercel 会自动检测并重新部署

### 查看日志

**Railway日志：**
- 进入 Railway 项目
- 点击 "Deployments" → 选择最新部署 → 查看 "Logs"

**Vercel日志：**
- 进入 Vercel 项目
- 点击 "Deployments" → 选择最新部署 → 点击 "View Function Logs"

### 数据备份

Railway 使用 SQLite，数据存储在容器中。**重要：** 每次重新部署会清空数据。

**解决方案：**
1. 使用 Railway 提供的 PostgreSQL 插件（免费）
2. 定期导出数据

**添加 PostgreSQL（推荐）：**
1. 在 Railway 项目中，点击 "New" → "Database" → "Add PostgreSQL"
2. Railway 会自动设置 `DATABASE_URL` 环境变量
3. 无需修改代码，重新部署即可自动使用 PostgreSQL

---

## ❓ 常见问题

### 1. 后端部署失败

**错误：** `Build failed`

**解决：**
- 检查 `backend/requirements.txt` 是否正确
- 查看 Railway 日志查找具体错误
- 确保 `backend/Procfile` 存在

### 2. 前端无法连接后端

**错误：** 浏览器控制台显示 CORS 错误

**解决：**
- 检查 Railway 中的 `CORS_ORIGINS` 环境变量
- 确保包含你的 Vercel 域名
- 重新部署 Railway

### 3. 翻译API不工作

**现象：** 查询单词返回模拟数据

**原因：**
- 未配置有道API
- API密钥错误
- API额度用完

**解决：**
- 检查 Railway 环境变量中的 `YOUDAO_APP_KEY` 和 `YOUDAO_APP_SECRET`
- 登录有道智云查看API额度

### 4. Railway 免费额度用完

**现象：** 应用停止运行

**解决：**
- 等待下个月额度重置
- 或升级到付费计划（$5/月）
- 或迁移到其他平台（Render.com 也提供免费额度）

### 5. 数据丢失

**原因：** SQLite 数据在容器中，重新部署会清空

**解决：**
- 添加 PostgreSQL 数据库（推荐，见上文）
- 使用外部数据库服务

---

## 🔧 高级配置

### 自定义域名

**Vercel：**
1. 在项目设置中点击 "Domains"
2. 添加你的域名
3. 按提示配置 DNS

**Railway：**
1. 在项目设置中点击 "Settings"
2. 找到 "Domains"
3. 添加自定义域名

### 环境分离

创建 `staging` 和 `production` 两个环境：

**Railway：**
- 创建两个项目，分别用于测试和生产

**Vercel：**
- 自动为每个分支创建预览环境
- `main` 分支自动部署到生产环境

---

## 📞 获取帮助

如果遇到问题：

1. 查看 Railway/Vercel 的日志
2. 检查本文档的"常见问题"部分
3. 在项目 GitHub 仓库提交 Issue

---

**祝你部署顺利！🎉**

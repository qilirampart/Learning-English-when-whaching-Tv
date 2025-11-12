# GitHub 上传指南（使用 Clash 代理）

本指南将帮助你在使用 Clash 代理的情况下，将修改后的代码上传到 GitHub。

## ✅ 修复内容说明

已修复以下问题：

1. **移除了 `.gitignore` 中对 `config.py` 的忽略**
   - `config.py` 现在会被正常上传到 GitHub
   - 敏感信息已通过环境变量处理，安全无忧

2. **修复了 `backend/railway.json` 的启动命令**
   - 添加了正确的工作目录切换
   - 确保 Railway 能找到 config.py

---

## 🌐 配置 Git 使用 Clash 代理

### 步骤 1：确认 Clash 代理端口

打开 Clash for Windows，查看端口号（通常是 `7890`）

### 步骤 2：配置 Git 代理

打开 PowerShell 或命令提示符，执行：

```powershell
# HTTP 代理（推荐）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 或者使用 SOCKS5 代理
# git config --global http.proxy socks5://127.0.0.1:7890
# git config --global https.proxy socks5://127.0.0.1:7890
```

### 步骤 3：验证配置

```powershell
git config --global --get http.proxy
git config --global --get https.proxy
```

---

## 📤 上传代码到 GitHub

### 方法一：首次上传（新仓库）

```powershell
# 1. 在项目目录打开 PowerShell
cd C:\AIProject

# 2. 初始化 Git 仓库（如果还没有）
git init

# 3. 添加所有文件
git add .

# 4. 提交更改
git commit -m "修复Railway部署问题：添加config.py和修复启动命令"

# 5. 在 GitHub 上创建新仓库后，添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 6. 推送到 GitHub
git push -u origin main
```

### 方法二：更新现有仓库

```powershell
# 1. 在项目目录打开 PowerShell
cd C:\AIProject

# 2. 查看修改状态
git status

# 3. 添加修改的文件
git add .gitignore
git add backend/railway.json
git add backend/config.py

# 4. 提交更改
git commit -m "修复Railway部署问题：添加config.py和修复启动命令"

# 5. 推送到 GitHub
git push origin main
```

---

## 🔧 常见问题

### 1. 推送速度很慢或超时

**原因：** 代理配置不正确或 Clash 未运行

**解决：**
```powershell
# 确保 Clash 正在运行
# 重新配置代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 增加超时时间
git config --global http.postBuffer 524288000
```

### 2. 提示 "Failed to connect to github.com"

**原因：** 代理端口错误

**解决：**
```powershell
# 检查 Clash 实际端口（可能是 7890, 7891, 1080 等）
# 在 Clash 设置中查看 "Port" 和 "Socks Port"
# 然后更新代理配置
git config --global http.proxy http://127.0.0.1:你的端口号
git config --global https.proxy http://127.0.0.1:你的端口号
```

### 3. 想要取消代理配置

**方法：**
```powershell
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 4. SSL 证书错误

**临时解决（不推荐）：**
```powershell
git config --global http.sslVerify false
```

**推荐解决：**
```powershell
# 使用 HTTP 代理而不是 SOCKS5
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

---

## 📋 上传检查清单

上传前请确认：

- [ ] Clash 代理正在运行
- [ ] Git 代理已正确配置
- [ ] 已添加所有需要的文件
- [ ] 提交信息清晰明了
- [ ] `.gitignore` 中已移除 `config.py`
- [ ] `backend/config.py` 文件存在且不包含实际密钥（使用环境变量）

---

## 🚀 上传后的部署步骤

### 1. Railway 重新部署

上传到 GitHub 后，Railway 会自动检测到代码更新并重新部署。

如果没有自动部署：
1. 打开 Railway 项目
2. 点击 "Deployments" 标签
3. 点击 "Deploy Now"

### 2. 检查环境变量

确保在 Railway 中设置了以下环境变量：

```ini
SECRET_KEY=你的密钥
FLASK_ENV=production
YOUDAO_APP_KEY=你的有道APP_KEY（可选）
YOUDAO_APP_SECRET=你的有道APP_SECRET（可选）
CORS_ORIGINS=https://your-frontend.vercel.app
```

### 3. 查看部署日志

1. 在 Railway 项目中，点击 "Deployments"
2. 选择最新的部署
3. 查看 "Logs" 确认没有错误

### 4. 测试部署

访问：`https://your-app.railway.app/api/statistics/overview`

如果返回 JSON 数据，说明部署成功！

---

## 💡 提示

### Git 常用命令速查

```powershell
# 查看状态
git status

# 查看修改内容
git diff

# 查看提交历史
git log --oneline

# 撤销未提交的修改
git checkout -- 文件名

# 修改最后一次提交信息
git commit --amend -m "新的提交信息"

# 强制推送（谨慎使用）
git push -f origin main
```

### 只上传特定文件

如果你只想上传修复的文件：

```powershell
# 只添加特定文件
git add backend/config.py
git add backend/railway.json
git add .gitignore

# 提交
git commit -m "修复部署配置"

# 推送
git push origin main
```

---

## ✅ 完成！

按照以上步骤操作后，你的代码应该已经成功上传到 GitHub，并且 Railway 会自动重新部署。

**预计等待时间：** 3-5 分钟

部署完成后，访问你的应用查看是否正常运行。

---

## 📞 需要帮助？

如果遇到问题：
1. 检查 Clash 是否正常运行
2. 验证代理端口是否正确
3. 查看 Railway 部署日志查找具体错误
4. 参考 `DEPLOY.md` 文档

**祝你部署顺利！** 🎉


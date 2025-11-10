# 美剧单词学习助手 - 快速启动指南

## 🚀 5分钟快速启动

### 前提条件

确保你的电脑已安装：
- **Python 3.8+**（检查：`python --version` 或 `python3 --version`）
- **Node.js 16+**（检查：`node --version`）
- **npm**（检查：`npm --version`）

---

## 第一步：启动后端服务

### 1. 打开终端，进入后端目录

```bash
cd backend
```

### 2. 安装Python依赖

**Windows:**
```bash
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
pip3 install -r requirements.txt
```

> 💡 **提示：** 如果安装慢，可以使用国内镜像：
> ```bash
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

### 3. 配置环境变量（可选）

**快速开始可以跳过此步骤！** 系统会使用模拟数据。

如需真实翻译API：
```bash
# Windows
copy env_example.txt .env

# macOS/Linux
cp env_example.txt .env
```

然后编辑 `.env` 文件填入你的API密钥。

### 4. 启动后端

```bash
python run.py
```

**看到以下信息表示启动成功：**
```
* Running on http://127.0.0.1:5000
* Running on http://0.0.0.0:5000
```

✅ 后端服务已启动！**保持此终端窗口运行，不要关闭！**

---

## 第二步：启动前端服务

### 1. 打开新终端窗口，进入前端目录

```bash
cd frontend
```

### 2. 安装Node.js依赖

```bash
npm install
```

> 💡 **提示：** 如果安装慢，可以使用淘宝镜像：
> ```bash
> npm install --registry=https://registry.npmmirror.com
> ```

### 3. 启动前端开发服务器

```bash
npm run dev
```

**看到以下信息表示启动成功：**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ 前端服务已启动！

---

## 第三步：访问应用

在浏览器中打开：

### 🌐 http://localhost:5173

你将看到美剧单词学习助手的主界面！

---

## 📖 使用指南

### 快速查询单词

1. 在左侧菜单点击 **"快速查询"**
2. 输入要查询的单词（如：hello）
3. 点击 **"查询"** 按钮
4. 查看翻译结果
5. （可选）填写剧名、集数、剧情备注
6. 单词自动保存到学习计划！

### 查看单词库

1. 点击左侧菜单 **"单词库"**
2. 查看所有查询过的单词
3. 可按剧集筛选、排序
4. 点击单词卡片查看详情

### 开始学习复习

1. 点击左侧菜单 **"学习计划"**
2. 查看今日待复习单词
3. 点击 **"开始复习"**
4. 翻卡片查看答案
5. 标记掌握程度

### 查看学习统计

1. 点击左侧菜单 **"学习统计"**
2. 查看学习数据可视化
3. 了解学习进度和趋势

---

## 🛑 停止服务

### 停止后端
在后端终端窗口按 `Ctrl + C`

### 停止前端
在前端终端窗口按 `Ctrl + C`

---

## ⚠️ 常见问题

### 问题1：端口被占用

**错误信息：** `Address already in use` 或 `端口已被占用`

**解决方法：**

**后端（5000端口被占用）：**
修改 `backend/run.py` 文件：
```python
app.run(host='0.0.0.0', port=5001)  # 改成其他端口
```

**前端（5173端口被占用）：**
修改 `frontend/vite.config.js` 文件：
```javascript
server: {
  port: 5174  // 改成其他端口
}
```

### 问题2：Python命令不存在

**错误信息：** `python: command not found`

**解决方法：**
尝试使用 `python3` 代替 `python`：
```bash
python3 run.py
```

### 问题3：pip安装报错

**错误信息：** 各种依赖安装失败

**解决方法：**
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt
```

### 问题4：前端无法连接后端

**错误信息：** 浏览器控制台显示网络错误

**解决方法：**
1. 确认后端服务已启动（检查 http://localhost:5000）
2. 确认防火墙没有阻止访问
3. 重启前端服务

### 问题5：npm install速度很慢

**解决方法：**
使用国内镜像源：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

---

## 📁 项目目录说明

```
项目根目录/
├── backend/           # 后端代码（Python + Flask）
│   ├── app/           # 应用代码
│   ├── run.py         # 启动文件 ← 运行这个文件
│   └── requirements.txt # 依赖列表
│
└── frontend/          # 前端代码（Vue.js）
    ├── src/           # 源代码
    ├── package.json   # 依赖配置
    └── vite.config.js # 构建配置
```

---

## 🎯 下一步

- 📖 阅读完整安装文档：[INSTALL.md](./INSTALL.md)
- 📋 了解项目功能：[README.md](./README.md)
- 🔧 配置翻译API获得真实翻译功能
- 🌟 开始使用并记录你的学习单词！

---

## 💡 小贴士

1. **开发模式**：代码修改后会自动重载，无需重启
2. **数据持久化**：所有数据保存在 `backend/vocab_learner.db` 文件中
3. **模拟数据**：未配置API时，系统使用模拟翻译数据，功能完全可用
4. **浏览器推荐**：建议使用 Chrome、Edge、Firefox 等现代浏览器

---

## 🆘 需要帮助？

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 查看完整的 [INSTALL.md](./INSTALL.md) 文档
3. 在 [GitHub Issues](https://github.com/qilirampart/Learning-English-when-whaching-Tv/issues) 提问

---

**祝你学习愉快！📚✨**


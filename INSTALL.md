# 美剧单词学习助手 - 安装和运行指南

## 📋 环境要求

### 后端
- Python 3.8 或更高版本
- pip 包管理器

### 前端
- Node.js 16 或更高版本
- npm 或 yarn 包管理器

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/qilirampart/Learning-English-when-whaching-Tv.git
cd Learning-English-when-whaching-Tv
```

### 2. 后端安装

#### 2.1 进入后端目录

```bash
cd backend
```

#### 2.2 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.3 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.4 配置环境变量

复制环境变量示例文件：

**Windows:**
```bash
copy env_example.txt .env
```

**macOS/Linux:**
```bash
cp env_example.txt .env
```

编辑 `.env` 文件，配置以下内容：

```ini
# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 数据库配置（默认使用SQLite）
DATABASE_URL=sqlite:///vocab_learner.db

# 有道翻译API配置（可选）
# 如果不配置，系统将使用模拟数据
YOUDAO_APP_KEY=your-youdao-app-key
YOUDAO_APP_SECRET=your-youdao-app-secret
```

**注意：** 
- 如果需要使用真实的翻译API，请访问 [有道智云](https://ai.youdao.com/) 申请API密钥
- 开发阶段可以不配置，系统会使用模拟数据

#### 2.5 启动后端服务

```bash
python run.py
```

后端服务将在 `http://localhost:5000` 启动

### 3. 前端安装

#### 3.1 打开新终端，进入前端目录

```bash
cd frontend
```

#### 3.2 安装依赖

**使用 npm:**
```bash
npm install
```

**使用 yarn:**
```bash
yarn install
```

#### 3.3 启动前端开发服务器

**使用 npm:**
```bash
npm run dev
```

**使用 yarn:**
```bash
yarn dev
```

前端服务将在 `http://localhost:5173` 启动

### 4. 访问应用

在浏览器中打开：**http://localhost:5173**

---

## 📁 项目结构

```
Learning-English-when-whaching-Tv/
├── backend/                    # 后端代码
│   ├── app/                    # 应用主目录
│   │   ├── __init__.py         # 应用工厂
│   │   ├── models/             # 数据库模型
│   │   │   ├── word.py         # 单词模型
│   │   │   ├── query_log.py    # 查询记录模型
│   │   │   ├── learning_plan.py # 学习计划模型
│   │   │   └── review_log.py   # 复习记录模型
│   │   ├── routes/             # API路由
│   │   │   ├── words.py        # 单词相关API
│   │   │   ├── learning.py     # 学习计划API
│   │   │   └── statistics.py  # 统计API
│   │   └── services/           # 业务服务
│   │       └── translation_service.py # 翻译服务
│   ├── config.py               # 配置文件
│   ├── run.py                  # 启动文件
│   ├── requirements.txt        # Python依赖
│   └── .env                    # 环境变量（需自行创建）
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/                # API接口
│   │   ├── views/              # 页面组件
│   │   │   ├── QueryView.vue   # 查询页面
│   │   │   ├── WordsView.vue   # 单词库页面
│   │   │   ├── LearningView.vue # 学习计划页面
│   │   │   └── StatisticsView.vue # 统计页面
│   │   ├── stores/             # 状态管理
│   │   ├── router/             # 路由配置
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口文件
│   ├── package.json            # npm配置
│   └── vite.config.js          # Vite配置
├── README.md                   # 需求分析文档
├── INSTALL.md                  # 安装文档（本文件）
└── .gitignore                  # Git忽略文件

```

---

## 🔧 开发说明

### 后端开发

#### 数据库操作

数据库会在第一次运行时自动创建。如需重置数据库：

```bash
# 删除数据库文件
rm vocab_learner.db  # Linux/macOS
del vocab_learner.db  # Windows

# 重新运行应用，数据库会自动重建
python run.py
```

#### API测试

后端API遵循RESTful规范，可以使用以下工具测试：
- Postman
- Thunder Client (VS Code 插件)
- curl

示例：查询单词
```bash
curl -X POST http://localhost:5000/api/words/query \
  -H "Content-Type: application/json" \
  -d '{"word":"hello","tv_show":"老友记","season_episode":"S01E01"}'
```

### 前端开发

#### 开发模式

前端开发服务器支持热重载，修改代码后会自动刷新浏览器。

#### 构建生产版本

```bash
npm run build
```

构建的文件会输出到 `frontend/dist` 目录。

#### 预览生产版本

```bash
npm run preview
```

---

## ⚠️ 常见问题

### 1. 端口被占用

**问题：** 启动时提示端口被占用

**解决方案：**

**后端（5000端口）：**
修改 `backend/run.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001)  # 改为其他端口
```

**前端（5173端口）：**
修改 `frontend/vite.config.js` 中的端口号：
```javascript
server: {
  port: 5174  // 改为其他端口
}
```

### 2. Python依赖安装失败

**问题：** pip install 报错

**解决方案：**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Node.js依赖安装失败

**问题：** npm install 报错

**解决方案：**
```bash
# 清除npm缓存
npm cache clean --force

# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或使用cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### 4. 跨域问题

**问题：** 前端无法访问后端API

**解决方案：**
- 确保后端已启动
- 检查 `frontend/vite.config.js` 中的代理配置
- 检查 `backend/config.py` 中的CORS配置

### 5. 数据库连接错误

**问题：** 启动时数据库相关错误

**解决方案：**
```bash
# 删除旧数据库
rm vocab_learner.db

# 确保有写入权限
chmod 755 backend/  # Linux/macOS

# 重新启动应用
```

---

## 🔐 生产环境部署

### 后端部署

1. **修改配置**

编辑 `backend/.env`：
```ini
FLASK_ENV=production
SECRET_KEY=生成一个强密码
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # 推荐使用PostgreSQL
```

2. **使用WSGI服务器**

安装 gunicorn：
```bash
pip install gunicorn
```

运行：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### 前端部署

1. **构建生产版本**

```bash
cd frontend
npm run build
```

2. **部署静态文件**

将 `frontend/dist` 目录的内容部署到：
- Nginx
- Apache
- 或任何静态文件服务器

**Nginx配置示例：**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 查看项目的 [GitHub Issues](https://github.com/qilirampart/Learning-English-when-whaching-Tv/issues)
3. 提交新的 Issue 描述你的问题

---

## 📝 开发路线图

- [x] MVP版本（单词查询、自动记录、列表展示）
- [x] 学习计划功能（复习提醒、掌握度评估）
- [x] 统计功能（学习曲线、剧集排行）
- [ ] 单词发音功能
- [ ] 数据导入/导出
- [ ] 浏览器插件
- [ ] 移动端适配
- [ ] 多用户系统

---

**祝你学习愉快！🎉**


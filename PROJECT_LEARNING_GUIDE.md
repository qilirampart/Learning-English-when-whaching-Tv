# 美剧单词学习助手 · 手敲复现学习指南

## 1. 架构与数据流概览
- **后端**：Flask 应用入口 `backend/run.py:1` 加载 `backend/app/__init__.py:10` 中的应用工厂，结合 SQLAlchemy、JWT 认证与蓝图路由提供 REST API。
- **数据库**：SQLAlchemy ORM 映射到 SQLite 文件 `backend/instance/vocab_learner.db:1`（开发）或 `.env` 中指定的其他数据库，核心实体保存在 `backend/app/models/*.py`。
- **前端**：Vite + Vue 3 SPA，入口 `frontend/src/main.js:1` 渲染 `frontend/src/App.vue:1`，通过 Pinia 状态、Element Plus UI 和 `frontend/src/router/index.js:1` 的路由守卫驱动多页面体验。
- **通信链路**：前端 `axios` 实例 `frontend/src/utils/request.js:1` 自动附带 JWT 并集中处理错误；API 定义于 `frontend/src/api/index.js:4`，与后端蓝图（`auth`, `words`, `learning`, `statistics`）一一对应。
- **部署基线**：Python 3.11（`backend/runtime.txt:1`）+ Gunicorn（`backend/Procfile:1`）运行后端；Vercel 配置 `frontend/vercel.json:1` 指定构建、静态托管与 API 代理。

## 2. 环境与运行脚本
### 2.1 后端环境
| 文件 | 作用 |
| --- | --- |
| `backend/requirements.txt:1` | 固定 Flask、Flask-CORS、Flask-SQLAlchemy、PyJWT、requests 等版本，确保可重现依赖。 |
| `backend/.env.example:1` | 列出 `SECRET_KEY`、`DATABASE_URL`、Youdao 额度、CORS 域名等变量，方便复制为 `.env`。 |
| `backend/Procfile:1` | Railway/Heroku 等平台使用 `gunicorn run:app` 启动服务。 |
| `backend/run.py:1` | 入口脚本，从环境变量读取配置名，创建 Flask app 并运行。 |

### 2.2 前端环境
| 文件 | 作用 |
| --- | --- |
| `frontend/package.json:1` | 声明 Vue、Pinia、Vue Router、Element Plus、axios 依赖以及 `dev/build/preview` 脚本。 |
| `.env.example/.env.development/.env.production` | 在 `frontend/.env*.?` 中声明 `VITE_API_BASE_URL`，和 `vite.config.js:1` 的 `/api` 代理共同工作。 |
| `frontend/vite.config.js:1` | 注册 Vue 插件、配置 `@` 别名、5173 端口以及 `/api` 反向代理，开发态免去 CORS。 |
| `frontend/vercel.json:1` | Vercel 部署时把 `/api/*` 请求重写到 Railway，静态路由回退至 `index.html`。 |

## 3. 后端文件逐一拆解
### 3.1 入口与配置
- `backend/run.py:1`：根据 `FLASK_ENV` 选择配置、监听 `0.0.0.0` 并支持 `PORT` 环境变量。这样在 Railway/Heroku 上无需改代码。
- `backend/config.py:1`：定义 `Config`/`DevelopmentConfig`/`ProductionConfig`。读取 `.env` 后设置 `SECRET_KEY`、`SQLALCHEMY_DATABASE_URI`、Youdao API key 以及 `CORS_ORIGINS`。拆分类便于扩展不同环境参数。
- `backend/app/__init__.py:10`：工厂模式初始化 Flask、SQLAlchemy、CORS，并在导入 `config` 时兼容多路径。`db.create_all()` 保证第一次运行自动建表。
- `backend/app/routes/__init__.py:1` 与 `backend/app/services/__init__.py:1`：标记包结构，便于相对导入。

### 3.2 数据模型（`backend/app/models`）
每个模型都通过 `db.Model` 定义列、索引与关系，并提供 `to_dict()` 与业务方法：
- `user.py:7`：`User` 实体包含 `username/email/password_hash`，并在 `set_password` / `check_password`（`user.py:23`/`27`）中使用 Werkzeug 哈希，杜绝明文。
- `word.py:6`：`Word` 保存 `phonetic/translation/definition/examples`，并在 `to_dict`（`word.py:23`）里将 JSON 例句转换为数组，同时统计查询次数。
- `learning_plan.py:6`：`LearningPlan` 通过 `_user_word_uc` 唯一约束保证“一词一计划”。`calculate_next_review`（`learning_plan.py:27`）依据艾宾浩斯间隔更新 `mastery_level`、`next_review`，理由是把记忆曲线写进模型层，复用性强。
- `query_log.py:6`：记录每次查询的剧名、集数、备注，`to_dict`（`query_log.py:18`）便于前端显示历史。
- `review_log.py:6`：保存复习对错与耗时，用于统计。
- `__init__.py:1`：集中导出模型名，帮助 `from app.models import User` 这类写法。

### 3.3 工具与服务
- JWT 工具 `backend/app/utils/auth.py:9`：`generate_token` 生成 24h token；`verify_token`（`auth.py:35`）校验/捕获过期；`login_required`（`auth.py:60`）解析 `Authorization: Bearer` 头，查表后把 `g.current_user` 注入下游视图；`optional_login`（`auth.py:121`）允许匿名访问但在有 token 时附带用户。
- 翻译服务 `backend/app/services/translation_service.py:9`：`translate`（`translation_service.py:15`）优先调用有道 API（`_translate_with_youdao` at line 33），失败时退回 `_get_mock_translation`（`translation_service.py:86`）生成示例数据。原因是保证没有外部 API key 也能开发测试。

### 3.4 蓝图与路由
- **认证蓝图** `backend/app/routes/auth.py:1`：
  - `/register`（`auth.py:27`）验证用户名/邮箱/密码合法性并入库。
  - `/login`（`auth.py:119`）支持用户名或邮箱登录，更新 `last_login`。
  - `/me`（`auth.py:184`）配合 `login_required` 返回当前用户。
  - `/refresh`（`auth.py:203`）颁发新 token，避免频繁登录。
- **单词蓝图** `backend/app/routes/words.py:18`：
  - `/query` 创建或获取 `Word`，自动创建 `LearningPlan` 和 `QueryLog`，必要时调用翻译服务。
  - `/search`（`words.py:86`）限定于当前用户的历史单词，支持关键字模糊。
  - `/<word_id>`（`words.py:111`）返回单词详情 + 查询/学习记录。
  - `/list`（`words.py:143`）支持分页、排序（时间/频率/掌握）与剧集过滤。
- **学习蓝图** `backend/app/routes/learning.py:16`：
  - `/today` 列出该复习的所有单词（`next_review <= now` 且未掌握）。
  - `/plan`（`learning.py:50`）提供总数、已掌握、在学、待复习四个指标。
  - `/review`（`learning.py:93`）写入 `ReviewLog` 并调用 `LearningPlan.calculate_next_review` 更新掌握度。
- **统计蓝图** `backend/app/routes/statistics.py:16`：
  - `/overview` 汇总单词数、今日查询数、掌握分布与最近 7 天趋势。
  - `/tv_shows`（`statistics.py:82`）统计各剧集中独立单词数，便于找高频剧。
- 所有蓝图都注册在工厂中，路径前缀分别为 `/api/auth`, `/api/words`, `/api/learning`, `/api/statistics`，保持 REST 层级清晰。

### 3.5 数据库初始化与实例
- `db.create_all()`（`backend/app/__init__.py:34`）在应用启动时创建 SQLite 表，开发阶段无需额外迁移。
- `backend/instance/vocab_learner.db:1` 是默认 SQLite 存储，位于 `instance` 目录便于 Flask 隔离配置。
- `.env` 中的 `DATABASE_URL` 可指向 PostgreSQL/MySQL，SQLAlchemy 会自动适配；`config.py:13` 默认回退到 SQLite，保证“手敲”即可运行。

## 4. 数据库模型与关系速览
| 模型 | 核心字段 | 关系 | 设计理由 |
| --- | --- | --- | --- |
| `User` (`backend/app/models/user.py:7`) | `username`, `email`, `password_hash`, `last_login` | 1:n 到 QueryLog/LearningPlan/ReviewLog | 用户维度集中，`password_hash` 避免敏感信息外泄。 |
| `Word` (`word.py:6`) | `word`, `phonetic`, `translation`, `definition`, `examples` | 1:n QueryLog、1:1 LearningPlan、1:n ReviewLog | 把基础词条与查询统计绑定，便于统计 QueryLog.count。 |
| `LearningPlan` (`learning_plan.py:6`) | `mastery_level`, `review_count`, `last_review`, `next_review`, `is_mastered` | belongs to User/Word | 通过唯一约束标识某用户与单词的关系，并内置遗忘曲线。 |
| `QueryLog` (`query_log.py:6`) | `tv_show`, `season_episode`, `context_note`, `query_time` | belongs to User/Word | 记录语境，有助于统计剧集和追忆场景。 |
| `ReviewLog` (`review_log.py:6`) | `is_correct`, `review_time`, `time_spent` | belongs to User/Word | 为统计（正确率、耗时）提供原始数据。 |

## 5. 前端文件逐一拆解
### 5.1 启动与全局外壳
- `frontend/index.html:1`：挂载点 `#app`，Vite 会将 `src/main.js` 注入。
- `frontend/src/main.js:1`：创建 Vue 应用，注册 Pinia、Router、Element Plus，并一次性注册 Element-Plus Icons（便于模板直接 `<Search />`）。
- `frontend/src/App.vue:1`：根据当前路径决定显示登录/注册布局还是主应用壳。`handleUserCommand`（`App.vue:89`）负责退出登录并调用 Pinia 的 `logout`。

### 5.2 路由与导航守卫
- `frontend/src/router/index.js:1`：声明 `/login`、`/register`、`/query`、`/words`、`/learning`、`/statistics` 六条路由；`beforeEach`（`index.js:51`）在导航前尝试 `authStore.initialize()`，并根据 `meta.requiresAuth`/`requiresGuest` 跳转，确保未登录不能访问主区。

### 5.3 状态管理
- `frontend/src/stores/auth.js:1`：
  - `initialize`（`auth.js:18`）在刷新后利用 token 请求 `/api/auth/me` 恢复会话。
  - `register`（`auth.js:38`）与 `login`（`auth.js:61`）均调用后端并缓存 token。
  - `logout`（`auth.js:83`） 清理本地状态，`refreshToken`（`auth.js:90`）用于 silent refresh。
- `frontend/src/stores/word.js:1`：维护最近查询的 5 个单词，`addRecentQuery`（`word.js:6`）用于 Query 页面展示快捷 chips。

### 5.4 网络与接口封装
- `frontend/src/utils/request.js:1`：创建 axios 实例，`request.interceptors.request`（`request.js:15`）自动加上 `Authorization` 头，`response` 拦截器（`request.js:34`）统一处理 401/403/404/500，并在 401 时跳转登录。
- `frontend/src/api/index.js:4`：导出 `wordApi`、`learningApi`、`statisticsApi`，每个方法返回 `response.data`，保持视图层代码简洁。

### 5.5 视图组件
- `LoginView.vue:1`：基于 Element Plus 的表单验证，`handleLogin`（`LoginView.vue:89`）提交前进行规则校验并调用 `authStore.login`。
- `RegisterView.vue:1`：添加 `validatePasswordMatch`（`RegisterView.vue:102`）验证两次密码一致，`handleRegister`（`RegisterView.vue:133`）成功后跳转首页。
- `QueryView.vue:1`：
  - 搜索框绑定 `searchWord`，`handleSearch`（`QueryView.vue:131`）调用 `wordApi.query`，成功后写入最近查询列表。
  - `contextForm` 保存剧集信息，附带发送，方便后端记录 `QueryLog`。
  - 展示翻译/释义/例句，并允许点击历史标签 `quickQuery`（`QueryView.vue:165`）。
- `WordsView.vue:1`：
  - 过滤条触发 `loadWords`（`WordsView.vue:177`），支持关键字、剧集、排序选项。
  - 点击单词卡触发 `showDetail`（`WordsView.vue:212`）弹出对话框展示例句与学习计划。
  - `getMasteryType`（`WordsView.vue:225`）按掌握等级选用不同颜色。
- `LearningView.vue:1`：
  - 加载概览 `loadOverview`（`LearningView.vue:175`）与今日复习列表 `loadReviewWords`（`LearningView.vue:190`）。
  - 复习模式中点击“显示答案”后可通过 `submitAnswer`（`LearningView.vue:213`）上报对错，服务端会重算 `next_review`。
- `StatisticsView.vue:1`：
  - `loadStatistics`（`StatisticsView.vue:186`）获取总体指标与 `weekly_trend`，在模板中用柱状图展示。
  - `loadTvShows`（`StatisticsView.vue:201`）列出剧集排行榜；`getRankClass`（`StatisticsView.vue:230`）为前三名着色。
  - 计算属性 `masteryPercentage`（`StatisticsView.vue:180`）驱动掌握率进度条。
- 样式大量采用线性渐变和卡片式布局，保持产品一致性。

### 5.6 其他辅助文件
- `frontend/src/api/index.js:31/52` 覆盖学习与统计 API。
- `frontend/src/views/LearningView.vue` 等组件使用的 `Element Plus` 组件库来自 `main.js` 的全局注册。
- `frontend/src/App.vue` 控制侧边菜单与 `router-view`，保证登录后页面之间共享布局。

## 6. 前后端协作场景
1. **注册/登录**  
   - 前端 `RegisterView.vue:133` / `LoginView.vue:89` 通过 `authStore` 调用 `/api/auth/register` 与 `/api/auth/login`。  
   - 后端 `auth.py:27/119` 完成校验、哈希、token 下发。成功后前端把 token 存入 `localStorage`，`request.js` 在所有请求头加上 `Bearer`。
2. **自动附带用户信息**  
   - 前端任意 API 请求会经过 `request` 拦截器附加 token。  
   - 后端 `login_required`（`backend/app/utils/auth.py:60`）验证后把 `g.current_user` 注入路由，`words.py:18` 等路由即可用 `g.current_user.id` 过滤数据。
3. **查询单词 + 建计划**  
   - Query 页面 `handleSearch` 发送 `{ word, tv_show, season_episode, context_note }`。  
   - `words.py:18` 如果 `Word` 不存在则调用 `TranslationService`（`translation_service.py:15`）获取释义，随后创建 `LearningPlan`/`QueryLog` 并返回 `word.to_dict()`；DB 中的唯一约束保证不会重复。
4. **复习流程**  
   - Learning 页面 `loadReviewWords` 调 `/api/learning/today`（`learning.py:16`）。  
   - 用户答题后 `submitAnswer` 触发 `/api/learning/review`（`learning.py:93`），模型根据记忆曲线更新 `next_review`，同时写入 `ReviewLog`，为统计页提供数据。
5. **统计面板**  
   - Statistics 视图分别调用 `/api/statistics/overview`（`statistics.py:16`）和 `/api/statistics/tv_shows`（`statistics.py:82`），后端通过 SQLAlchemy 聚合函数统计总数、趋势、剧集榜；前端以卡片、柱状图与列表展示。

## 7. 手动复现路线建议
1. **创建目录**：按照 `backend` 与 `frontend` 两个顶层文件夹组织，分别初始化 `python` 与 `npm` 项目。
2. **搭建后端**  
   1. 新建虚拟环境，安装 `requirements.txt` 中依赖。  
   2. 按本指南顺序创建 `config.py`、`run.py`、`app/__init__.py`、`models/*`、`utils/auth.py`、`services/translation_service.py` 与 `routes/*`。  
   3. 拷贝 `.env.example` 为 `.env`，根据需要填入数据库和翻译 API。  
   4. `python run.py` 启动，首次会自动生成 `instance/vocab_learner.db`。
3. **搭建前端**  
   1. `npm create vite@latest`（或直接 `npm init vite`）后覆盖 `package.json` 与 `vite.config.js`。  
   2. 在 `src` 下按结构创建 `main.js`, `App.vue`, `router`, `stores`, `utils/request.js`, `api/index.js`, `views/*`。  
   3. 复制 `.env.development`，确认 `VITE_API_BASE_URL` 指向后端；安装依赖 `npm install` 并运行 `npm run dev`。
4. **联调**：确保前端的 `/api` 请求通过 Vite 代理指向 Flask；检查浏览器网络面板中 `Authorization` 头是否存在。
5. **部署**：使用 `Procfile` + Railway 部署后端，使用 `vercel.json` 发布前端，同时在 `.env.production` 设置真实 API 地址。

---

通过以上分层拆解与文件解析，你可以按模块逐步敲出同款项目，并清楚理解每个文件存在的理由、它们如何组合成完整的查询—学习—统计闭环。

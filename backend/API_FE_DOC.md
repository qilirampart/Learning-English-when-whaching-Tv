# 后端对接前端开发文档（重构用）

> 项目后端：Flask + SQLAlchemy，API 前缀 `/api`。默认返回 JSON，除认证外多数接口返回形如 `{ "code": 200, "data": ... }`。需要登录的接口均要求 `Authorization: Bearer <token>`。

## 1. 认证 Auth

### POST /api/auth/register
- 描述：注册用户。
- 入参 JSON：`username`(string,3-80)、`email`(string,email)、`password`(string,>=6)
- 返回 201：`{ message, user, token }`
- 失败：400/409/500，`message` 提示。

### POST /api/auth/login
- 描述：登录（用户名或邮箱）。
- 入参 JSON：`username`(string)、`password`(string)
- 返回 200：`{ message, user, token }`
- 失败：400/401/500。

### GET /api/auth/me
- 描述：获取当前登录用户。
- 需登录。
- 返回 200：`{ user }`

### Token 说明
- 登录/注册后拿到 `token`，前端保存（store/localStorage）。
- 请求头：`Authorization: Bearer <token>`。

## 2. 单词 Words
> 需登录。模型字段：Word { id, word, phonetic, translation, definition, examples:[{...}], created_at, query_count }

### POST /api/words/query
- 描述：查词并写入 Word、QueryLog、LearningPlan（若未存在）。
- 入参 JSON：
  - `word`(必填，string)
  - `tv_show`(可选,string)
  - `season_episode`(可选,string)
  - `context_note`(可选,string)
- 返回 200：`{ code:200, data: word_obj }`，附加 `last_query`。
- 失败：400（word 为空）、500。

### GET /api/words/search
- 描述：在“当前用户查过的单词”中模糊搜索。
- Query：`keyword`(必填)
- 返回 200：`{ code:200, data: [word_obj...] }`

### GET /api/words/<word_id>
- 描述：单词详情（含当前用户的查询历史与学习计划）。
- 返回 200：`{ code:200, data: { ...word, query_logs:[...], learning_plan } }`
- 404：单词不存在。

### GET /api/words/list
- 描述：分页列出当前用户查过的单词，可筛选/排序。
- Query：
  - `page`(int, 默认1)
  - `page_size`(int, 默认20)
  - `order_by`(`time`|`frequency`|`mastery`, 默认 time)
  - `filter_show`(string，可选，按剧集筛)
  - `mastery_level`(int，可选，按掌握度筛)
- 返回 200：`{ code:200, data: { items:[word_obj...], total, pages, page, per_page } }`
  - word_obj 补充：`tv_shows`(该用户看过的剧集列表)。

### 其它（如导出/掌握状态）
- routes/words 末尾若有 `export`/`master` 路由，保持同样带 token 调用；导出通常返回文件流，前端用 `blob` 下载。

#### 模型-QueryLog
- 字段：id, word_id, tv_show, season_episode, context_note, query_time.
- 取值：`query_logs` 按时间倒序。

#### 模型-LearningPlan
- 字段：id, word_id, mastery_level(0-5), review_count, last_review, next_review, is_mastered, created_at。

## 3. 学习计划 Learning
> 需登录。

### GET /api/learning/today
- 描述：今日待复习单词列表（未掌握且到期）。
- 返回 200：`{ code:200, data:{ count, words:[{...word, learning_plan}] } }`

### GET /api/learning/plan
- 描述：学习概览。
- 返回 200：`{ code:200, data:{ total_words, mastered, learning, to_review } }`

### POST /api/learning/review
- 描述：提交一次复习结果并自动计算下次复习时间（艾宾浩斯间隔）。
- 入参 JSON：`word_id`(必填,int)、`is_correct`(必填,bool)、`time_spent`(可选,int 秒)
- 返回 200：`{ code:200, message, data:{ learning_plan } }`
- 404：学习计划不存在；400：参数不全。

## 4. 统计 Statistics
> 需登录。

### GET /api/statistics/overview
- 描述：学习总览 + 7 天趋势。
- 返回 200：
```
{
  code: 200,
  data: {
    total_words,       // 总单词（learning_plan 数）
    today_queries,     // 今日查询次数
    mastered,          // 已掌握数
    learning,          // 学习中
    to_review,         // 待复习
    weekly_trend: [c1..c7] // 近7天每日查询次数（按日期升序）
  }
}
```

### GET /api/statistics/tv_shows
- 描述：按剧集聚合的查询频次（用于榜单/标签云）。
- 返回 200：`{ code:200, data:[ { tv_show, count }, ... ] }`

## 5. AI 助手

### POST /api/ai/usage
- 描述：生成单词用法解析（当前路由不强制登录）。
- 入参 JSON：`word`(必填,string)、`tv_show`(可选,string)
- 成功：`{ code:200, data:{ word, tv_show, content, success:true } }`
- 失败：500，`message`/`error`；需处理 content 为空的情况。

## 6. 前端调用与状态管理建议
- 登录后将 token 存 store，并在 axios 拦截器统一加 `Authorization` 头；401 时跳转登录。
- 首页数据：
  - 概览：`GET /learning/plan`
  - 近期单词：`GET /words/list?page=1&page_size=2&order_by=time`
  - 统计：`GET /statistics/overview`
- 查词流程：`POST /words/query` -> 更新列表；搜索用 `GET /words/search`；详情页用 `GET /words/<id>`。
- 复习流程：`GET /learning/today` 拉取 -> 每条 `POST /learning/review`。
- AI 卡片：`POST /ai/usage`，注意 loading + 错误提示。

## 7. 错误处理与返回规范
- 常见状态码：200/201 成功；400 参数问题；401 认证失败；404 资源不存在；409 冲突；500 服务器错误。
- 响应字段：多数含 `code` 与 `message`；认证接口直接给 `user`/`token` 与 HTTP status。
- 时间：后端以 UTC ISO 字符串返回，前端自行格式化。

## 8. 数据模型速览
- User: id, username, email, created_at, last_login。
- Word: id, word, phonetic, translation, definition, examples(list), created_at, query_count。
- QueryLog: id, word_id, tv_show, season_episode, context_note, query_time。
- LearningPlan: id, word_id, mastery_level(0-5), review_count, last_review, next_review, is_mastered, created_at。
- ReviewLog: id, word_id, is_correct, review_time, time_spent。

## 9. 环境与部署要点（给前端同学参考）
- 本地运行后端：`pip install -r requirements.txt`，`flask run`（或 `python run.py`）。需 `.env` 配置数据库等。
- 默认前端请求基址：指向后端服务地址（可通过 env 配置）。
- CORS 若有限制，前端需与后端同源或在后端开启允许域名。

---
如需补充导出/掌握状态等未列出的路由，请在 `backend/app/routes/words.py` 末尾确认后追加；若前端需要字段更细粒度（如 examples 内结构），可再补充格式约定。

抱歉我无法直接操作你的 GitHub 仓库，但我可以为你提供一份**“保姆级”的文件替换指南**。

根据你提供的 `frontend` 目录结构截图，你的前端是一个标准的 **Vite + Vue 3** 项目。要将现有的“后台管理风”彻底替换为我们设计的“现代 Bento 风格”，请按照以下步骤操作。

⚠️ **警告：操作前请备份 `frontend/src` 文件夹，以防万一。**

------

### 第一步：安装必要的依赖

打开终端，进入 `frontend` 目录，安装我们新设计需要的图标库和状态管理库：

Bash

```
cd frontend
# 安装 Pinia (状态管理), Lucide (图标), Axios (请求)
npm install pinia lucide-vue-next axios
```

------

### 第二步：配置环境与入口 (Config & Main)

#### 1. 修改 `frontend/tailwind.config.js`

我们使用了“呼吸光斑”动画，必须覆盖配置。

- **操作：** 打开文件，**全量替换**为以下代码：

JavaScript

```
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        blob: "blob 7s infinite",
      },
      keyframes: {
        blob: {
          "0%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(30px, -50px) scale(1.1)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.9)" },
          "100%": { transform: "translate(0px, 0px) scale(1)" },
        },
      },
    },
  },
  plugins: [],
}
```

#### 2. 修改 `frontend/src/main.js`

我们需要启用 `Pinia`。

- **操作：** 确保文件包含以下内容（如果之前没有 `createPinia`，请加上）：

JavaScript

```
import { createApp } from 'vue'
import { createPinia } from 'pinia' // [新增]
import './style.css' // 确保这里引入了 tailwind 指令
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia()) // [新增]
app.use(router)
app.mount('#app')
```

#### 3. 清理 `frontend/src/App.vue`

新设计由路由控制布局，`App.vue` 只需要作为一个空壳。

- **操作：** **全量替换**为：

代码段

```
<template>
  <router-view />
</template>
```

------

### 第三步：构建核心基建 (Core)

请在 `frontend/src` 下创建或确认以下文件夹存在：`utils`, `stores`, `layouts`, `views`。

#### 1. 创建请求工具 `src/utils/request.js`

- **操作：** 新建文件，粘贴之前提供的 **Axios 封装代码**（负责 Token 注入和拦截）。

#### 2. 创建状态管理 `src/stores/auth.js`

- **操作：** 新建文件，粘贴之前提供的 **Pinia Auth Store 代码**（负责登录/退出逻辑）。

#### 3. 创建布局文件 `src/layouts/AppLayout.vue`

这是新界面的骨架（顶部导航栏 + 动态背景）。

- **操作：** 新建文件，粘贴之前提供的 **Layout 代码**。

------

### 第四步：替换页面 (Views)

这是改动最大的部分。建议**删除** `src/views` 下所有现有的 `.vue` 文件（如 `Home.vue`, `About.vue` 等），然后新建以下文件：

1. **`src/views/Login.vue`**: 粘贴之前的 **登录页代码**。
2. **`src/views/Dashboard.vue`**: 粘贴之前的 **仪表盘 (Bento Grid) 代码**。
3. **`src/views/Library.vue`**: 粘贴之前的 **单词库代码**。
4. **`src/views/Learning.vue`**: 粘贴之前的 **学习计划/复习代码**。
5. **`src/views/AI.vue`**: 粘贴之前的 **AI 助手代码**。

*(注意：如果你之前的代码里有把组件拆分到 `src/components`，建议先保留，但不要在新的 view 里引用它们，以免样式冲突。等新版稳定后，再删除旧组件。)*

------

### 第五步：配置路由 (Router)

最后，把页面串联起来。

#### 修改 `frontend/src/router/index.js`

- **操作：** **全量替换**为以下代码：

JavaScript

```
import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Library from '../views/Library.vue'
import Learning from '../views/Learning.vue'
import AI from '../views/AI.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'library', name: 'Library', component: Library },
      { path: 'learning', name: 'Learning', component: Learning },
      { path: 'ai', name: 'AI', component: AI }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 简单的路由守卫：未登录跳转 Login
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

------

### 第六步：验证与启动

完成上述所有步骤后：

1. 在终端运行 `npm run dev`。

2. 打开浏览器访问 `http://localhost:5173`。

3. 你应该能看到新的 **紫色光斑背景的登录页**。

4. 如果报错 `Module not found`，请检查文件名大小写是否一致（例如 `Dashboard.vue` 首字母大写）。

5. 如果样式错乱，请检查 `frontend/src/style.css` 顶部是否保留了 Tailwind 的三行指令：

   CSS

   ```
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

按照这个流程，你就成功地将原本的“后台管理”项目“手术”成了现代化的学习应用！

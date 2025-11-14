# 前端源码学习手册

> 面向第一次接触 Vue3 + Element Plus 的同学。本文按照“文件 → 行号区间 → 作用”拆解，确保你手敲时有据可依。

## 目录
1. [入口与全局壳层](#入口与全局壳层)
   - [frontend/src/main.js](#frontendsrcmainjs)
   - [frontend/src/App.vue](#frontendsrcappvue)
2. [路由与状态](#路由与状态)
   - [router/index.js](#routerindexjs)
   - [stores/auth.js](#storesauthjs)
   - [stores/word.js](#storeswordjs)
3. [网络层](#网络层)
   - [utils/request.js](#utilsrequestjs)
   - [api/index.js](#apiindexjs)
4. [视图组件](#视图组件)
   - [LoginView.vue](#loginviewvue)
   - [RegisterView.vue](#registerviewvue)
   - [QueryView.vue](#queryviewvue)
   - [WordsView.vue](#wordsviewvue)
   - [LearningView.vue](#learningviewvue)
   - [StatisticsView.vue](#statisticsviewvue)

---

## 入口与全局壳层

### frontend/src/main.js
| 行号 | 说明 |
| --- | --- |
| 1-5 | 引入核心库：Vue 创建函数、Pinia、Element Plus 及其 CSS，还有所有图标。|
| 7-8 | 导入顶层组件 `App.vue` 与路由实例。|
| 10 | `const app = createApp(App)` 创建 Vue 应用。|
| 12-15 | 遍历 `ElementPlusIconsVue`，逐个注册图标组件，避免单独导入。|
| 17-19 | `app.use(...)` 装配 Pinia、router、Element Plus。|
| 21 | `app.mount('#app')`，把应用挂到 `index.html` 的根节点。|

### frontend/src/App.vue
| 区块 | 行号 | 说明 |
| --- | --- | --- |
| Template | 1-52 | 用 `v-if="isAuthPage"` 区分登录/注册 vs 主应用布局。主布局由 Element Plus `el-container` + 侧边栏 + 主内容组成，菜单项绑定到路由地址。侧边栏底部是下拉菜单，可执行退出。|
| Script | 54-92 | 使用 `<script setup>`，导入 `computed/onMounted`、`useRoute/useRouter`、`useAuthStore`、`ElMessage/ElMessageBox`。计算 `activeMenu`、`isAuthPage`，在 `onMounted` 中若有 token 但未加载用户则调用 `authStore.initialize()`。`handleUserCommand` 在用户确认后清空 token 并跳转登录页。|
| Style | 94-158 | 纯 CSS，控制整体布局、侧边栏、用户信息区域效果。|

## 路由与状态

### router/index.js
| 行号 | 说明 |
| --- | --- |
| 1-2 | 引入 Vue Router 构造函数以及 `useAuthStore`（路由守卫里会用）。|
| 4-47 | `createRouter`：使用 `createWebHistory`，定义 6 条路由（`/` 重定向到 `/query`，登录/注册标记 `requiresGuest`，其余页面 `requiresAuth` 并按需懒加载视图文件）。|
| 50-84 | `beforeEach` 导航守卫：
- 54-57：若已有 token 但 `user` 为空，先 `initialize()`。
- 59-70：对需要登录的路由，若未认证则跳到 `/login` 并保存原目标。
- 72-79：对只允许游客的路由，若已登录则跳 `/`。
- 81-82：其它情况直接放行。|

### stores/auth.js
| 行号 | 说明 |
| --- | --- |
| 1-3 | 引入 Pinia、Vue 响应式 API、axios。|
| 5 | `defineStore('auth', ...)`，整个 store 采取组合式写法。|
| 6-9 | `token/user/loading` 三个 `ref`，token 默认从 `localStorage` 读取，保证刷新后仍在。|
| 11-12 | 计算属性 `isAuthenticated`：token 和 user 都存在才算登录成功。|
| 14-15 | `API_BASE_URL` 从 `VITE_API_BASE_URL` 读取，默认 `http://localhost:5000`。|
| 17-35 | `initialize`：若存在 token 则请求 `/api/auth/me`，成功后写入 `user`，失败则调用 `logout`。|
| 37-58 | `register`：调用 `/api/auth/register`，成功后保存 token/user，并返回 `{ success, message }`；finally 块重置 `loading`。|
| 60-80 | `login`：逻辑与注册类似，接口换成 `/api/auth/login`，参数是 username/password。|
| 82-87 | `logout`：清空 token/user 并移除本地存储。|
| 89-114 | `refreshToken`：如果有 token，则 POST `/api/auth/refresh` 并刷新本地 token。失败会注销。|
| 117-130 | 返回值对象，供组件通过 `useAuthStore()` 调用。|

### stores/word.js
| 行号 | 说明 |
| --- | --- |
| 1-3 | 引入 Pinia、ref、以及 `wordApi`（虽然当前 store 只管理最近查询，并未直接调 API）。|
| 5-7 | `recentQueries` 记住最近 5 条查询结果。|
| 9-18 | `addRecentQuery`：若新单词已存在则移除旧位置，再插入数组头部，超过 5 条时 `pop()`。|
| 20-23 | 导出 `recentQueries` 与 `addRecentQuery`，供 Query 页面使用。|

## 网络层

### utils/request.js
| 行号 | 说明 |
| --- | --- |
| 1-3 | 引入 axios、Element Message 和 router。|
| 5-12 | 创建 axios 实例：基 URL 来源于环境变量，默认 5000，设置 10 秒超时和 JSON 头。|
| 14-31 | 请求拦截器：从 `localStorage` 取 token，若存在就写入 `Authorization`，然后返回修改后的 config。|
| 33-85 | 响应拦截器：
- 40-75：根据 HTTP 状态码弹出不同提示；401 时顺便移除 token 并跳转登录。
- 77-82：处理无响应或配置错误。
- 84-85：统一 `Promise.reject`，让上层决定后续动作。|

### api/index.js
| 行号 | 说明 |
| --- | --- |
| 1 | 导入上面封装好的 `request`。|
| 4-27 | `wordApi`：提供 `query/search/getDetail/getList` 四个方法，对应后端 `/api/words/*`。所有方法都返回 `response.data`，即后端包装层而不是 axios 整个响应。|
| 31-48 | `learningApi`：`getTodayReview/getPlan/submitReview` 分别匹配 `/api/learning` 的三个接口。|
| 52-63 | `statisticsApi`：两个方法路由到 `/api/statistics`。|
| 66 | 默认导出 `request`，若外部需要直接使用 axios 实例也可以。|

## 视图组件

### LoginView.vue
| 部分 | 行号 | 说明 |
| --- | --- | --- |
| Template | 1-43 | Element Plus 表单 + 输入框，提交按钮绑定 `handleLogin`。底部提供注册链接。|
| Script | 45-88 | 使用 `<script setup>`：引入 `ref/reactive`、router、auth store、`ElMessage`。定义 `loginFormRef`、`loginForm`、`loginRules`。`handleLogin` 根据校验结果调用 `authStore.login`，成功后跳首页，失败弹出错误。|
| Style | 90-144 | 控制登录页背景、表单卡片、按钮等样式。|

### RegisterView.vue
| 部分 | 行号 | 说明 |
| --- | --- | --- |
| Template | 1-54 | 结构类似登录页，多了确认密码输入框。|
| Script | 56-139 | 定义 `registerForm`、验证规则、`validatePasswordMatch`，`handleRegister` 校验后调用 `authStore.register` 并跳首页。|
| Style | 141-195 | 与登录页风格一致，只是文本不同。|

### QueryView.vue
| 重点块 | 行号 | 说明 |
| --- | --- | --- |
| 模板头部 | 1-90 | 包含查询输入框、展示卡片、剧情信息表单与统计标签。结果卡采用 `wordResult` 数据渲染。|
| 最近查询 | 92-105 | 使用 `recentQueries` 计算属性生成 tag，点击会触发 `quickQuery`。|
| 脚本 | 110-173 | 
- 111-116：导入 Composition API、图标、消息组件、`wordApi`、`wordStore`。
- 119-126：定义 `searchWord/wordResult/loading/contextForm`。
- 128：`recentQueries` 通过 store 的响应式数组计算得到。
- 131-153：`handleSearch` 校验输入、调用 `wordApi.query` 并将结果写入 store，同时清空剧情表单。
- 165-169：`quickQuery`、`formatDate` 辅助函数。
| 样式 | 175-319 | 控制背景、卡片、例句列表、情境表单等视觉效果。|

### WordsView.vue
| 重点块 | 行号 | 说明 |
| --- | --- | --- |
| 筛选条 | 4-34 | 三种筛选：关键字输入、剧集下拉、排序方式。改变任一项都会触发 `loadWords`。|
| 列表 | 36-72 | 遍历 `words` 渲染卡片，包含掌握程度、查询次数、剧集标签等。没有数据时展示 `el-empty`。|
| 分页 | 74-84 | 使用 `el-pagination` 控制页数/大小，事件同样调用 `loadWords`。|
| 详情对话框 | 86-137 | `el-dialog` 展示 `currentWord` 的详细信息与 `learning_plan`。|
| 脚本 | 139-233 | 引入 `ref/onMounted`、`ElMessage`、`wordApi`：
  - `filters` 保存查询参数。
  - `loadWords` 调 `wordApi.getList` 更新 `words/total/tvShows`。
  - `showDetail` 先调 `getDetail` 获取历史查询 + 计划，再弹出对话框。
  - `getMasteryType`、`formatDate` 提供 UI 辅助。
  - `onMounted(loadWords)` 在页面加载时获取初始列表。|
| 样式 | 235-351 | 控制卡片布局、Hover 效果、分页居中等。|

### LearningView.vue
| 模块 | 说明 |
| --- | --- |
| Template | 顶部概览卡 + 今日待复习卡。复习卡包含“开始复习”按钮、翻牌式问答区、复习完成提示以及待复习列表。|
| Script | 引入 `ref/computed/onMounted`、`learningApi`、`ElMessage`：
  - `overview`、`reviewWords`、`isReviewing`、`currentReviewIndex` 等响应式状态。
  - `loadOverview`、`loadReviewWords` 分别请求 `/plan` 与 `/today`。
  - `startReview` 切换到复习模式。
  - `submitAnswer` 调 `learningApi.submitReview`，根据结果推进索引或标记完成，完成后刷新概览。|
| Style | 定义渐变背景、卡片、翻牌 UI、按钮排列等。|

### StatisticsView.vue
| 模块 | 说明 |
| --- | --- |
| Template | 由三块组成：统计卡片、最近 7 天柱状图、剧集榜单，以及一个“学习建议”面板（包含 `el-alert` 和掌握率进度条）。|
| Script | 导入 `ref/computed/onMounted`、`statisticsApi`、`ElMessage`：
  - `stats` 保存总单词、今日查询、掌握情况等。
  - `loadStatistics` 获取 `/overview` 数据并填充 `stats`。
  - `loadTvShows` 获取 `/tv_shows` 数据展示排行。
  - `masteryPercentage` 把 `mastered/total_words` 转为百分比，驱动进度条。
  - `getBarHeight/getWeekDay/getRankClass` 提供 UI 计算。|
| Style | 包括卡片阴影、柱状图、排行徽章、提示面板等样式。|

---

## 使用建议
1. **按文件顺序手敲**：建议从 `main.js` → `App.vue` → `router` → `stores` → `utils/api` → `views`，逐层建立依赖关系。
2. **边敲边验证**：每完成一个模块就运行 `npm run dev`，观察浏览器是否报错，能够第一时间定位。结合本手册对照行号，有助于快速排查。
3. **配合后端文档**：在 Query、Words、Learning、Statistics 页面上调试时，结合后端对应接口能理解完整链路。|

祝你顺利完成前端的手敲复现！

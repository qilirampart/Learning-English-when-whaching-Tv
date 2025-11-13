# 前端认证功能 - 使用指南

## ✅ 已完成的功能

### 1. 认证系统核心
- **认证 Store** (`frontend/src/stores/auth.js`)
  - 用户注册、登录、登出
  - Token 管理（存储在 localStorage）
  - 用户信息初始化
  - Token 刷新

### 2. HTTP 请求配置
- **Axios 拦截器** (`frontend/src/utils/request.js`)
  - 自动在请求头添加 `Authorization: Bearer <token>`
  - 统一错误处理
  - 401 错误自动跳转登录页
  - 友好的错误提示

### 3. 认证页面
- **登录页面** (`frontend/src/views/LoginView.vue`)
  - 美观的渐变背景
  - 表单验证
  - 支持用户名或邮箱登录
  - Loading 状态

- **注册页面** (`frontend/src/views/RegisterView.vue`)
  - 完整的表单验证
  - 密码确认
  - 邮箱格式验证
  - 友好的错误提示

### 4. 路由保护
- **路由守卫** (`frontend/src/router/index.js`)
  - 未登录自动跳转登录页
  - 已登录无法访问登录/注册页
  - 保存原始目标路径，登录后自动跳转

### 5. 用户界面
- **App.vue** 更新
  - 侧边栏显示用户信息
  - 用户下拉菜单（显示邮箱、退出登录）
  - 登录/注册页面使用独立布局

### 6. API 集成
- **API 调用** (`frontend/src/api/index.js`)
  - 所有 API 调用自动携带认证 token
  - 统一的响应处理

### 7. 环境配置
- **开发环境** (`.env.development`)
  - API URL: `http://localhost:5000`

- **生产环境** (`.env.production`)
  - 配置为实际的后端地址

---

## 🚀 快速开始

### 步骤 1: 安装依赖（如果还没有）

```bash
cd frontend
npm install
```

### 步骤 2: 启动开发服务器

```bash
npm run dev
```

### 步骤 3: 启动后端服务

在另一个终端：

```bash
cd backend
python run.py
```

### 步骤 4: 访问应用

打开浏览器访问：`http://localhost:5173`

---

## 📖 使用流程

### 1. 首次访问
- 访问任何页面会自动重定向到登录页
- 点击"立即注册"跳转到注册页面

### 2. 注册新用户
- 输入用户名（3-80字符）
- 输入邮箱地址
- 输入密码（至少6字符）
- 确认密码
- 点击"注册"按钮

### 3. 登录
- 输入用户名或邮箱
- 输入密码
- 点击"登录"按钮
- 登录成功后自动跳转到应用主页

### 4. 使用应用
- 所有功能页面（查询、单词库、学习计划、统计）现在都需要登录
- 每个用户只能看到自己的数据
- 数据完全隔离

### 5. 退出登录
- 点击侧边栏底部的用户头像
- 选择"退出登录"
- 确认后会跳转到登录页

---

## 🔒 安全特性

### Token 管理
- Token 存储在 localStorage
- 有效期：24小时
- 过期后自动跳转登录页

### 密码安全
- 后端使用 Werkzeug 进行密码哈希
- 密码不会以明文存储
- 最低6个字符要求

### 请求安全
- 所有 API 请求自动携带 token
- 401 错误统一处理
- 避免重复认证逻辑

### 数据隔离
- 每个用户只能访问自己的数据
- 后端通过 `user_id` 过滤数据
- 防止数据泄露

---

## 🛠 技术实现细节

### 1. 认证流程

```
用户登录
  ↓
输入用户名/邮箱和密码
  ↓
发送 POST /api/auth/login
  ↓
后端验证用户信息
  ↓
返回 JWT token 和用户信息
  ↓
前端存储 token 到 localStorage
  ↓
后续请求自动携带 token
```

### 2. Token 使用

```javascript
// 请求拦截器自动添加 token
config.headers.Authorization = `Bearer ${token}`

// 响应拦截器处理 401 错误
if (status === 401) {
  localStorage.removeItem('token')
  router.push('/login')
}
```

### 3. 路由守卫

```javascript
// 需要登录的路由
meta: { requiresAuth: true }

// 游客路由（登录、注册）
meta: { requiresGuest: true }

// 路由守卫检查
if (requiresAuth && !isAuthenticated) {
  next('/login')
}
```

---

## 📝 文件结构

```
frontend/src/
├── stores/
│   ├── auth.js          # 认证状态管理
│   └── word.js          # 单词状态管理
├── utils/
│   └── request.js       # Axios 配置和拦截器
├── api/
│   └── index.js         # API 接口定义
├── views/
│   ├── LoginView.vue    # 登录页面
│   ├── RegisterView.vue # 注册页面
│   ├── QueryView.vue    # 查询页面（需要登录）
│   ├── WordsView.vue    # 单词库（需要登录）
│   ├── LearningView.vue # 学习计划（需要登录）
│   └── StatisticsView.vue # 统计页面（需要登录）
├── router/
│   └── index.js         # 路由配置和守卫
├── App.vue              # 主应用组件
└── main.js              # 应用入口
```

---

## 🐛 常见问题

### Q: 登录后刷新页面，状态丢失？
**A:** 不会！Token 存储在 localStorage，刷新页面后会自动从 token 恢复用户信息。

### Q: Token 过期怎么办？
**A:** Token 过期后，任何 API 请求会返回 401，自动跳转到登录页，并提示"登录已过期，请重新登录"。

### Q: 如何修改 Token 有效期？
**A:** 在 `backend/app/utils/auth.py` 中修改 `generate_token` 函数的 `expires_in` 参数（默认86400秒=24小时）。

### Q: 忘记密码怎么办？
**A:** 当前版本暂未实现忘记密码功能。可以通过数据库管理工具重置密码，或联系管理员。

### Q: 如何实现记住我功能？
**A:** 可以修改 `LoginView.vue`，添加"记住我"选项，延长 token 有效期（如7天）。

---

## 🔄 后续可扩展功能

### 短期扩展
- [ ] 记住我功能
- [ ] 忘记密码/重置密码
- [ ] 用户头像上传
- [ ] 个人资料编辑

### 中期扩展
- [ ] 邮箱验证
- [ ] 第三方登录（Google、GitHub）
- [ ] 双因素认证（2FA）
- [ ] 登录历史记录

### 长期扩展
- [ ] 多设备管理
- [ ] 权限系统（普通用户、VIP）
- [ ] 社交功能（好友、分享）
- [ ] 管理后台

---

## 📞 测试账号

为了方便测试，可以创建以下测试账号：

```bash
# 注册测试用户
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123"
  }'
```

**测试账号信息：**
- 用户名: `testuser`
- 邮箱: `test@example.com`
- 密码: `test123`

---

## 🎉 完成情况

✅ **前端认证功能 100% 完成！**

所有核心功能已实现：
- ✅ 用户注册和登录
- ✅ Token 管理
- ✅ 路由保护
- ✅ API 认证
- ✅ 用户界面
- ✅ 错误处理
- ✅ 数据隔离

现在可以安全地部署应用了！

---

## 📚 相关文档

- [后端认证实现](./AUTHENTICATION_SUMMARY.md)
- [快速开始指南](./QUICKSTART_AUTH.md)
- [API 文档](./README.md)
- [部署指南](./DEPLOY.md)

---

**祝您使用愉快！** 🚀

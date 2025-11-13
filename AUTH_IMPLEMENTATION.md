# 用户认证功能实现文档

## 📋 已完成的工作

### 1. 后端核心功能 ✅

#### 1.1 依赖包添加
- 已添加 `PyJWT==2.8.0` (JWT token生成和验证)
- 已添加 `Werkzeug==3.0.1` (密码哈希)

#### 1.2 数据模型

**User 模型** (`backend/app/models/user.py`) ✅
- 用户名、邮箱、密码哈希
- 密码加密存储
- 关联用户的查询记录、学习计划、复习记录

**更新的模型** ✅
- `QueryLog`: 添加 `user_id` 字段
- `LearningPlan`: 添加 `user_id` 字段，添加唯一约束 `(user_id, word_id)`
- `ReviewLog`: 添加 `user_id` 字段

#### 1.3 认证系统

**JWT 工具** (`backend/app/utils/auth.py`) ✅
- `generate_token()`: 生成 JWT token
- `verify_token()`: 验证 JWT token
- `@login_required`: 登录验证装饰器
- `@optional_login`: 可选登录装饰器

**认证路由** (`backend/app/routes/auth.py`) ✅
- `POST /api/auth/register`: 用户注册
- `POST /api/auth/login`: 用户登录
- `GET /api/auth/me`: 获取当前用户信息
- `POST /api/auth/refresh`: 刷新 token

#### 1.4 Words 路由更新 ✅

所有 words 相关接口已添加 `@login_required` 装饰器，并修改为：
- 只操作当前登录用户的数据
- 查询时过滤 `user_id`
- 创建记录时自动关联 `user_id`

更新的接口：
- `POST /api/words/query` - 查询单词
- `GET /api/words/search` - 搜索单词
- `GET /api/words/<id>` - 获取单词详情
- `GET /api/words/list` - 获取单词列表

---

## 🚧 待完成的工作

### 2. 后端剩余工作

#### 2.1 更新 Learning 路由

**文件**: `backend/app/routes/learning.py`

需要修改的接口：

```python
# 1. 导入认证装饰器
from flask import Blueprint, request, jsonify, g
from app.utils.auth import login_required

# 2. 为每个路由添加 @login_required 装饰器

# 3. 修改查询，添加 user_id 过滤
# 示例：
learning_plans = LearningPlan.query.filter(
    and_(
        LearningPlan.user_id == g.current_user.id,  # 添加这一行
        LearningPlan.next_review <= datetime.utcnow(),
        LearningPlan.is_mastered == False
    )
).all()

# 4. 创建记录时添加 user_id
review_log = ReviewLog(
    user_id=g.current_user.id,  # 添加这一行
    word_id=word_id,
    is_correct=is_correct,
    time_spent=time_spent
)
```

#### 2.2 更新 Statistics 路由

**文件**: `backend/app/routes/statistics.py`

需要修改的接口：

```python
# 1. 导入认证装饰器
from flask import Blueprint, request, jsonify, g
from app.utils.auth import login_required

# 2. 为每个路由添加 @login_required 装饰器

# 3. 修改所有统计查询，添加 user_id 过滤
# 示例：
total_words = QueryLog.query.filter_by(user_id=g.current_user.id).distinct(QueryLog.word_id).count()
```

#### 2.3 创建数据库迁移

由于数据库模型发生了变化（添加了 user_id 字段），需要：

**选项 A: 删除旧数据库重新创建**
```bash
cd backend
# 删除旧数据库
rm instance/vocab_learner.db
# 重新运行应用会自动创建新表
python run.py
```

**选项 B: 使用 Flask-Migrate (推荐生产环境)**
```bash
pip install Flask-Migrate
# 然后在代码中配置迁移
```

### 3. 前端实现

#### 3.1 创建登录/注册页面

**需要创建的组件**:

1. `frontend/src/pages/Login.jsx` - 登录页面
2. `frontend/src/pages/Register.jsx` - 注册页面

**功能要求**:
- 用户名/邮箱输入
- 密码输入（带显示/隐藏切换）
- 表单验证
- 错误提示
- 登录成功后保存 token 到 localStorage

#### 3.2 创建认证上下文

`frontend/src/contexts/AuthContext.jsx`:

```javascript
import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // 登录
  const login = async (username, password) => {
    const response = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();

    if (response.ok) {
      setToken(data.token);
      setUser(data.user);
      localStorage.setItem('token', data.token);
      return { success: true };
    }
    return { success: false, message: data.message };
  };

  // 注册
  const register = async (username, email, password) => {
    const response = await fetch('http://localhost:5000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });
    const data = await response.json();

    if (response.ok) {
      setToken(data.token);
      setUser(data.user);
      localStorage.setItem('token', data.token);
      return { success: true };
    }
    return { success: false, message: data.message };
  };

  // 登出
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  // 获取当前用户信息
  useEffect(() => {
    if (token) {
      fetch('http://localhost:5000/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          if (data.user) {
            setUser(data.user);
          } else {
            logout();
          }
        })
        .catch(() => logout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}
```

#### 3.3 更新 API 请求

修改所有 API 请求，添加 Authorization header:

```javascript
const token = localStorage.getItem('token');

fetch('http://localhost:5000/api/words/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`  // 添加这一行
  },
  body: JSON.stringify({ word: 'hello' })
});
```

#### 3.4 创建路由保护

`frontend/src/components/PrivateRoute.jsx`:

```javascript
import { Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export function PrivateRoute({ children }) {
  const { user, loading } = useContext(AuthContext);

  if (loading) {
    return <div>Loading...</div>;
  }

  return user ? children : <Navigate to="/login" />;
}
```

#### 3.5 更新路由配置

```javascript
import { PrivateRoute } from './components/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';

<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
  <Route path="/words" element={<PrivateRoute><Words /></PrivateRoute>} />
  {/* 其他需要保护的路由 */}
</Routes>
```

---

## 🧪 测试步骤

### 1. 后端测试

```bash
cd backend
# 安装新依赖
pip install -r requirements.txt

# 删除旧数据库
rm instance/vocab_learner.db

# 启动后端
python run.py
```

**测试注册**:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**测试登录**:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**测试受保护的接口**:
```bash
# 使用返回的 token
curl -X POST http://localhost:5000/api/words/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "word": "hello",
    "tv_show": "Friends"
  }'
```

### 2. 前端测试

1. 访问 `/login` 页面
2. 注册新用户
3. 登录
4. 测试查询单词功能
5. 退出登录
6. 验证未登录时无法访问其他页面

---

## 📝 注意事项

### 安全建议

1. **生产环境配置**:
   - 修改 `SECRET_KEY` 为强随机字符串
   - 使用环境变量存储敏感信息
   - 启用 HTTPS

2. **Token 管理**:
   - Token 默认有效期 24 小时
   - 可以实现 token 刷新机制
   - 敏感操作建议重新验证

3. **密码策略**:
   - 当前最低 6 个字符
   - 建议增加复杂度要求（大小写、数字、特殊字符）

### 数据库迁移

如果有旧数据需要保留：
1. 导出旧数据
2. 重建数据库
3. 创建默认用户
4. 将旧数据关联到默认用户

---

## 🎯 下一步计划

1. 完成 learning 和 statistics 路由的更新
2. 测试后端所有接口
3. 实现前端登录/注册界面
4. 更新前端所有 API 调用
5. 进行完整的端到端测试
6. 准备部署到 Railway

---

## 🆘 遇到问题？

常见问题和解决方案：

**Q: Token 无效或过期？**
A: 检查 SECRET_KEY 配置，确保前后端使用同一个

**Q: CORS 错误？**
A: 确保 `config.py` 中 CORS_ORIGINS 包含前端 URL

**Q: 数据库错误？**
A: 删除旧数据库，重新创建：`rm instance/vocab_learner.db`

**Q: 401 Unauthorized？**
A: 检查 Authorization header 格式：`Bearer <token>`

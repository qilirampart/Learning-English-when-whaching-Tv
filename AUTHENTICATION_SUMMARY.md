# 用户认证功能 - 实现总结

## ✅ 已完成的后端工作

### 1. 核心功能实现

#### 📦 依赖包
- `PyJWT==2.8.0` - JWT token 生成和验证
- `Werkzeug==3.0.1` - 密码加密哈希

#### 🗄️ 数据模型

**新增 User 模型** (`backend/app/models/user.py`)
```python
class User(db.Model):
    - id: 用户ID
    - username: 用户名（唯一）
    - email: 邮箱（唯一）
    - password_hash: 密码哈希
    - created_at: 注册时间
    - last_login: 最后登录时间
```

**更新的模型** (添加 user_id 外键)
- `QueryLog` - 查询记录关联用户
- `LearningPlan` - 学习计划关联用户（添加唯一约束）
- `ReviewLog` - 复习记录关联用户

#### 🔐 认证系统

**JWT 工具** (`backend/app/utils/auth.py`)
- `generate_token(user_id)` - 生成JWT token (24小时有效期)
- `verify_token(token)` - 验证token并返回user_id
- `@login_required` - 登录验证装饰器
- `@optional_login` - 可选登录装饰器

**认证路由** (`backend/app/routes/auth.py`)
```
POST /api/auth/register    - 用户注册
POST /api/auth/login       - 用户登录
GET  /api/auth/me          - 获取当前用户
POST /api/auth/refresh     - 刷新token
```

#### 🛡️ 路由保护更新

**Words 路由** (`backend/app/routes/words.py`)
- ✅ 所有接口添加 `@login_required`
- ✅ 查询时过滤 `user_id`
- ✅ 创建记录时关联 `user_id`

**Learning 路由** (`backend/app/routes/learning.py`)
- ✅ 所有接口添加 `@login_required`
- ✅ 学习计划按用户隔离
- ✅ 复习记录关联用户

**Statistics 路由** (`backend/app/routes/statistics.py`)
- ✅ 所有接口添加 `@login_required`
- ✅ 统计数据按用户隔离

---

## 🚀 部署前准备

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 数据库迁移

由于数据库结构变化，需要重新创建数据库：

```bash
cd backend
# 删除旧数据库
rm -f instance/vocab_learner.db
# 运行应用会自动创建新表
python run.py
```

### 3. 配置检查

确保 `backend/config.py` 中：
- `SECRET_KEY` 设置为强随机字符串（生产环境）
- `CORS_ORIGINS` 包含前端URL

---

## 📝 API 使用示例

### 注册新用户

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

**响应**:
```json
{
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2025-01-13T10:00:00"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 用户登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'
```

### 使用Token访问受保护接口

```bash
curl -X POST http://localhost:5000/api/words/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "word": "hello",
    "tv_show": "Friends",
    "season_episode": "S01E01"
  }'
```

---

## 🎯 前端集成指南

### 1. 创建认证上下文

创建 `frontend/src/contexts/AuthContext.jsx`:

```javascript
import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

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

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  // 初始化时获取用户信息
  useEffect(() => {
    if (token) {
      fetch('http://localhost:5000/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          if (data.user) setUser(data.user);
          else logout();
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

### 2. 创建登录页面

创建 `frontend/src/pages/Login.jsx`:

```javascript
import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const result = await login(username, password);
    if (result.success) {
      navigate('/');
    } else {
      setError(result.message);
    }
  };

  return (
    <div className="login-container">
      <h1>登录</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="用户名或邮箱"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">登录</button>
      </form>
      <p>
        还没有账号？ <a href="/register">立即注册</a>
      </p>
    </div>
  );
}
```

### 3. 创建注册页面

创建 `frontend/src/pages/Register.jsx` (类似Login页面，调用register函数)

### 4. 更新API请求

修改所有API请求，添加Authorization header:

```javascript
// 创建一个通用的API请求函数
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('token');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`http://localhost:5000${url}`, {
    ...options,
    headers,
  });

  // 如果返回401，token可能过期，跳转到登录页
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    return;
  }

  return response.json();
}

// 使用示例
const data = await apiRequest('/api/words/query', {
  method: 'POST',
  body: JSON.stringify({ word: 'hello' })
});
```

### 5. 路由保护

创建 `frontend/src/components/PrivateRoute.jsx`:

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

### 6. 更新路由配置

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute } from './components/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
// ... 其他页面导入

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/" element={<PrivateRoute><Home /></PrivateRoute>} />
          {/* 其他需要保护的路由 */}
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

---

## 🔒 安全建议

### 生产环境配置

1. **强密码策略**
   - 当前最低要求：6个字符
   - 建议增加：大小写字母+数字+特殊字符

2. **SECRET_KEY配置**
   ```python
   # 生产环境使用环境变量
   SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-here')
   ```

3. **HTTPS强制**
   - 生产环境必须使用HTTPS
   - Token只能通过HTTPS传输

4. **Token管理**
   - 默认有效期：24小时
   - 实现token刷新机制
   - 敏感操作要求重新验证

5. **CORS配置**
   ```python
   # 只允许特定域名
   CORS_ORIGINS = ['https://yourdomain.com']
   ```

---

## 🐛 故障排查

### 常见问题

**Q: Token无效或过期？**
```
A: 检查：
1. SECRET_KEY前后端一致
2. Token格式：Bearer <token>
3. Token是否过期（24小时）
```

**Q: 401 Unauthorized错误？**
```
A: 检查：
1. Authorization header是否正确
2. Token是否包含在请求中
3. 后端日志查看具体错误
```

**Q: 数据库错误？**
```
A: 解决：
1. 删除旧数据库：rm backend/instance/vocab_learner.db
2. 重新运行应用自动创建新表
```

**Q: CORS错误？**
```
A: 检查：
1. config.py中CORS_ORIGINS配置
2. 确保包含前端URL
3. 检查浏览器控制台错误信息
```

---

## 📋 测试清单

### 后端测试
- [ ] 用户注册功能
- [ ] 用户登录功能
- [ ] Token验证功能
- [ ] 受保护接口需要token
- [ ] 无效token返回401
- [ ] 多用户数据隔离

### 前端测试
- [ ] 登录页面显示正常
- [ ] 注册页面显示正常
- [ ] 登录成功跳转
- [ ] 未登录重定向到登录页
- [ ] Token过期自动跳转
- [ ] 退出登录功能

---

## 📚 相关文档

- [完整实现指南](./AUTH_IMPLEMENTATION.md)
- [API文档](./README.md)
- [部署指南](./DEPLOY.md)

---

## 🎉 下一步

1. **测试后端功能**
   - 安装依赖
   - 重建数据库
   - 测试所有API接口

2. **实现前端界面**
   - 创建登录/注册页面
   - 集成认证上下文
   - 更新API调用

3. **端到端测试**
   - 注册新用户
   - 登录测试
   - 功能测试

4. **准备部署**
   - 配置生产环境变量
   - 更新Railway配置
   - 部署测试

恭喜！后端认证系统已经完整实现 🎊

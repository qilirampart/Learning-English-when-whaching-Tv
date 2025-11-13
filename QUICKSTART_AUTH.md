# 🚀 认证系统快速开始

## 立即测试后端认证功能

### 步骤 1: 安装新依赖

```bash
cd backend
pip install PyJWT==2.8.0 Werkzeug==3.0.1
```

### 步骤 2: 重建数据库

```bash
# 删除旧数据库（因为表结构已更改）
rm -f instance/vocab_learner.db  # Linux/Mac
# 或
del instance\vocab_learner.db   # Windows
```

### 步骤 3: 启动后端

```bash
python run.py
```

### 步骤 4: 测试注册

打开新终端，运行：

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**预期响应**：
```json
{
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2025-01-13..."
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 步骤 5: 测试登录

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 步骤 6: 测试受保护的接口

复制上一步返回的 token，然后：

```bash
# 将 YOUR_TOKEN 替换为实际的 token
curl -X POST http://localhost:5000/api/words/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "word": "hello",
    "tv_show": "Friends",
    "season_episode": "S01E01",
    "context_note": "Joey说的第一句话"
  }'
```

**预期响应**：
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "word": "hello",
    "translation": "你好",
    ...
  }
}
```

### 步骤 7: 测试未授权访问

不带token访问（应该返回401错误）：

```bash
curl -X POST http://localhost:5000/api/words/query \
  -H "Content-Type: application/json" \
  -d '{"word": "test"}'
```

**预期响应**：
```json
{
  "error": "Missing authorization header",
  "message": "缺少认证信息"
}
```

---

## ✅ 验证清单

- [ ] 能够成功注册新用户
- [ ] 能够使用用户名登录
- [ ] 能够使用邮箱登录
- [ ] 返回有效的JWT token
- [ ] 使用token能访问受保护接口
- [ ] 不带token返回401错误
- [ ] 无效token返回401错误

---

## 🎯 前端开发提示

在前端实现时，记得：

1. **存储Token**
   ```javascript
   localStorage.setItem('token', data.token);
   ```

2. **添加到请求头**
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`
   }
   ```

3. **处理401错误**
   ```javascript
   if (response.status === 401) {
     // Token过期，跳转到登录页
     localStorage.removeItem('token');
     window.location.href = '/login';
   }
   ```

---

## 📖 更多信息

- **完整实现指南**: [AUTH_IMPLEMENTATION.md](./AUTH_IMPLEMENTATION.md)
- **API文档**: [AUTHENTICATION_SUMMARY.md](./AUTHENTICATION_SUMMARY.md)
- **问题反馈**: 查看上述文档的故障排查部分

---

祝你测试顺利！🎉

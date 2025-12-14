# 🧪 Clash + pip 问题诊断和解决方案

## 📊 当前状态

### ✅ 已完成
1. **pip 配置文件已创建**: `C:\Users\psk13\pip\pip.ini`
   ```ini
   [global]
   index-url = https://pypi.tuna.tsinghua.edu.cn/simple
   trusted-host = pypi.tuna.tsinghua.edu.cn
   ```

2. **Clash 配置已添加 PyPI 规则**（第 92-95 行）:
   ```yaml
   - DOMAIN-SUFFIX,pypi.org,DIRECT
   - DOMAIN-SUFFIX,pythonhosted.org,DIRECT
   - DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT
   - DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT
   ```

### ❌ 仍然存在的问题

**实际下载时仍然报错**：
```
ValueError: check_hostname requires server_hostname
```

**原因分析**：
- pip 虽然配置了清华源
- 但 Clash 规则顺序不对
- **清华源的 DIRECT 规则（第 95 行）被前面的规则（86-90 行）覆盖了**

---

## 🎯 终极解决方案

### 方案 1：调整 Clash 规则顺序（推荐彻底解决）

**问题**：您的 PyPI DIRECT 规则在第 92-95 行，太靠后了。

**解决**：需要将这些规则移到 `rules:` 部分的**最前面**。

#### 具体步骤：

1. **打开 Clash 配置文件**

2. **找到 `rules:` 开始的地方**（应该在第 91 行左右）

3. **将规则调整为**：
```yaml
rules:
  # ========== 必须放在第一位 ==========
  - DOMAIN-SUFFIX,pypi.org,DIRECT
  - DOMAIN-SUFFIX,pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT
  - DOMAIN-SUFFIX,mirrors.aliyun.com,DIRECT
  - DOMAIN-SUFFIX,mirrors.tencent.com,DIRECT

  # ========== 然后才是其他规则 ==========
  - { name: 'IN India', type: select, proxies: [...] }
  - { name: 'PH Philippines', type: select, proxies: [...] }
  # ... 其他所有规则保持不变 ...
```

4. **删除**原来 92-95 行的重复规则

5. **保存并重新加载 Clash**

---

### 方案 2：使用系统环境变量（临时绕过）

在 PowerShell 或 CMD 中设置环境变量，让 pip 不走代理：

#### PowerShell:
```powershell
$env:NO_PROXY="pypi.org,pythonhosted.org,pypi.tuna.tsinghua.edu.cn,files.pythonhosted.org"
pip install colorama
```

#### CMD:
```cmd
set NO_PROXY=pypi.org,pythonhosted.org,pypi.tuna.tsinghua.edu.cn,files.pythonhosted.org
pip install colorama
```

---

### 方案 3：临时关闭系统代理（最简单）

#### 手动关闭：
1. Clash 托盘图标 → 右键
2. 关闭 "系统代理" / "System Proxy"
3. 执行 pip 安装
4. 完成后重新开启系统代理

#### 命令行：
```bash
# 关闭代理
# （需要手动在 Clash 中操作）

# 安装包
pip install colorama

# 再开启代理
```

---

### 方案 4：使用 pip 的 --no-deps 和缓存（高级）

如果只是偶尔安装包，可以使用离线安装：

1. **在无代理环境下下载 wheel 文件**
2. **手动安装**：
```bash
pip install C:\Downloads\colorama-0.4.6-py2.py3-none-any.whl
```

---

## 🧪 验证测试

### 测试 1：检查 Clash 规则是否生效

在 Clash 日志中应该看到：
```
[Rule] pypi.tuna.tsinghua.edu.cn match DIRECT
```

如果看到的是：
```
[Rule] pypi.tuna.tsinghua.edu.cn match PROXY
```

说明规则顺序有问题。

### 测试 2：检查环境变量

```bash
# PowerShell
echo $env:HTTP_PROXY
echo $env:HTTPS_PROXY
echo $env:NO_PROXY

# CMD
echo %HTTP_PROXY%
echo %HTTPS_PROXY%
echo %NO_PROXY%
```

### 测试 3：直接测试下载

```bash
# 使用 curl 测试能否直接访问清华源
curl https://pypi.tuna.tsinghua.edu.cn/simple/ -v

# 测试 pip 安装
pip install colorama -v
```

---

## 💡 推荐行动方案

### 🥇 最佳方案（一劳永逸）

**调整 Clash 配置规则顺序**：

1. 编辑 Clash 配置文件
2. 将 PyPI 规则移到 `rules:` 最前面
3. 重新加载配置
4. 测试 `pip install colorama`

### 🥈 临时方案（立即可用）

**使用环境变量**：

每次需要 pip 安装时：
```powershell
$env:NO_PROXY="pypi.tuna.tsinghua.edu.cn"
pip install 包名
```

### 🥉 应急方案（最简单）

**临时关闭 Clash 系统代理**：

1. Clash 托盘 → 关闭系统代理
2. pip install
3. 重新开启代理

---

## 📝 总结

### 核心问题
- Clash 配置的 PyPI DIRECT 规则位置不对（第 92-95 行太靠后）
- 被前面的规则（第 86-90 行）先匹配，导致走了代理
- pip 配置文件本身是正确的

### 最终解决
- **必须调整 Clash 规则顺序**
- 将 PyPI DIRECT 规则移到 `rules:` 部分的最前面
- 或者使用环境变量 NO_PROXY 绕过

---

## ✅ 下一步操作

请选择以下任一方式：

1. **【推荐】** 调整 Clash 配置规则顺序
2. 使用环境变量 `NO_PROXY`
3. 临时关闭 Clash 系统代理进行安装

如果您告诉我 Clash 配置文件的完整路径，我可以帮您直接修改规则顺序！

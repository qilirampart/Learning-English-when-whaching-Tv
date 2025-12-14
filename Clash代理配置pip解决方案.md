# 🔧 Clash 代理下 pip 安装问题完整解决方案

## 问题描述

开启 Clash 代理后，pip 安装依赖时出现 SSL 证书错误：
```
ValueError: check_hostname requires server_hostname
```

**根本原因**：Clash 代理拦截 HTTPS 连接，导致 SSL 证书验证失败。

---

## 🎯 解决方案一：修改 Clash 配置（推荐）

### 方法 1.1：添加 PyPI 直连规则

#### 步骤：

**1. 找到 Clash 配置文件**

常见位置：
- `C:\Users\你的用户名\.config\clash\config.yaml`
- `C:\Users\你的用户名\.config\clash\profiles\配置文件名.yaml`
- Clash for Windows: `C:\Users\你的用户名\.config\clash\profiles\`
- Clash Verge: `C:\Users\你的用户名\.clash-verge\profiles\`

**2. 编辑配置文件**

在配置文件的 `rules:` 部分**最前面**添加以下规则：

```yaml
rules:
  # ========== PyPI 直连规则（必须在最前面）==========
  - DOMAIN-SUFFIX,pypi.org,DIRECT
  - DOMAIN-SUFFIX,pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,pypi.python.org,DIRECT
  - DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT
  - DOMAIN-SUFFIX,mirrors.aliyun.com,DIRECT
  - DOMAIN-SUFFIX,mirrors.tencent.com,DIRECT
  - DOMAIN-SUFFIX,pypi.douban.com,DIRECT
  - DOMAIN-KEYWORD,pypi,DIRECT
  - DOMAIN-KEYWORD,python,DIRECT
  # ========== 以上是 PyPI 直连规则 ==========

  # 原有规则保持不变
  - DOMAIN-SUFFIX,local,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  # ... 其他规则 ...
```

**3. 重要说明**

⚠️ **规则顺序很重要**！PyPI 规则必须放在 `rules:` 部分的**最前面**，在所有其他规则之前。

示例完整配置结构：
```yaml
# ... proxy-groups 等其他配置 ...

rules:
  # PyPI 直连规则（第一优先级）
  - DOMAIN-SUFFIX,pypi.org,DIRECT
  - DOMAIN-SUFFIX,pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT

  # 局域网直连
  - DOMAIN-SUFFIX,local,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR,192.168.0.0/16,DIRECT

  # 其他代理规则
  - DOMAIN-SUFFIX,google.com,PROXY
  # ... 更多规则 ...

  # 最终规则
  - MATCH,DIRECT
```

**4. 重新加载配置**

- Clash for Windows: 右键托盘图标 → 重新加载配置 (Reload)
- Clash Verge: 配置页面 → 重新加载
- 或者重启 Clash 软件

**5. 验证生效**

```bash
# 测试 pip 安装
pip install openpyxl --verbose
```

---

### 方法 1.2：使用规则集（更优雅）

如果你使用的是支持规则集（Rule Providers）的 Clash 版本：

**1. 创建 PyPI 规则文件**

创建文件：`C:\Users\你的用户名\.config\clash\rule-providers\pypi-direct.yaml`

```yaml
payload:
  - DOMAIN-SUFFIX,pypi.org
  - DOMAIN-SUFFIX,pythonhosted.org
  - DOMAIN-SUFFIX,pypi.python.org
  - DOMAIN-SUFFIX,files.pythonhosted.org
  - DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn
  - DOMAIN-SUFFIX,mirrors.aliyun.com
  - DOMAIN-KEYWORD,pypi
```

**2. 在主配置文件中引用**

```yaml
rule-providers:
  pypi-direct:
    type: file
    behavior: domain
    path: ./rule-providers/pypi-direct.yaml

rules:
  - RULE-SET,pypi-direct,DIRECT
  # ... 其他规则 ...
```

---

## 🎯 解决方案二：配置 pip 忽略代理

### 方法 2.1：创建 pip 配置文件

**1. 创建配置文件**

Windows 位置：`C:\Users\你的用户名\pip\pip.ini`

```bash
# 创建目录和文件
mkdir C:\Users\86159\pip
notepad C:\Users\86159\pip\pip.ini
```

**2. 添加以下内容**

```ini
[global]
# 信任 PyPI 官方源
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org

# 或者使用国内镜像（更快）
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

# 禁用代理（仅 pip 使用直连）
no-proxy = pypi.org,pypi.python.org,files.pythonhosted.org,pypi.tuna.tsinghua.edu.cn
```

**3. 验证配置**

```bash
pip config list
```

---

### 方法 2.2：使用环境变量

**临时禁用代理（仅当前命令行窗口）**

```bash
# PowerShell
$env:NO_PROXY="pypi.org,pythonhosted.org,pypi.python.org,files.pythonhosted.org"
pip install openpyxl

# CMD
set NO_PROXY=pypi.org,pythonhosted.org,pypi.python.org,files.pythonhosted.org
pip install openpyxl
```

**永久设置（系统环境变量）**

1. Win + R → 输入 `sysdm.cpl` → 回车
2. 高级 → 环境变量
3. 系统变量 → 新建：
   - 变量名：`NO_PROXY`
   - 变量值：`pypi.org,pythonhosted.org,pypi.python.org,files.pythonhosted.org,localhost,127.0.0.1`

---

### 方法 2.3：使用命令行参数

每次安装时添加参数：

```bash
# 信任主机
pip install openpyxl --trusted-host pypi.org --trusted-host files.pythonhosted.org

# 使用国内镜像
pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 组合使用（推荐）
pip install openpyxl reportlab -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

---

## 🎯 解决方案三：配置 Clash TUN 模式例外

如果使用 TUN 模式：

**1. 打开 Clash 设置**

**2. TUN 模式配置**

在配置文件中找到 `tun:` 部分，添加例外：

```yaml
tun:
  enable: true
  stack: system
  dns-hijack:
    - 198.18.0.2:53
  auto-route: true
  auto-detect-interface: true

  # 添加 DNS 排除
  exclude-package:
    - python.exe
    - pip.exe
```

---

## 🎯 解决方案四：使用 pip 离线安装

**1. 在无代理环境下载 wheel 文件**

访问 https://pypi.org/ 搜索并下载：
- openpyxl-3.1.2-py2.py3-none-any.whl
- reportlab-4.0.7-py3-none-any.whl

**2. 离线安装**

```bash
pip install C:\path\to\openpyxl-3.1.2-py2.py3-none-any.whl
pip install C:\path\to\reportlab-4.0.7-py3-none-any.whl
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **修改 Clash 配置** | 一次配置，永久生效 | 需要编辑 YAML 文件 | ⭐⭐⭐⭐⭐ |
| **pip 配置文件** | pip 专用，不影响其他 | 仅解决 pip 问题 | ⭐⭐⭐⭐ |
| **环境变量 NO_PROXY** | 简单快速 | 可能影响其他程序 | ⭐⭐⭐ |
| **命令行参数** | 不修改配置 | 每次都要输入 | ⭐⭐ |
| **离线安装** | 完全不依赖网络 | 需要手动下载 | ⭐⭐ |

---

## ✅ 推荐最佳实践

**组合方案（最佳）**：

### 步骤 1：修改 Clash 配置

在 Clash 配置文件 `rules:` 部分最前面添加：

```yaml
rules:
  - DOMAIN-SUFFIX,pypi.org,DIRECT
  - DOMAIN-SUFFIX,pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,files.pythonhosted.org,DIRECT
  - DOMAIN-SUFFIX,pypi.tuna.tsinghua.edu.cn,DIRECT
  # ... 其他规则 ...
```

### 步骤 2：创建 pip 配置文件

创建 `C:\Users\86159\pip\pip.ini`：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### 步骤 3：重启 Clash 并测试

```bash
# 重启 Clash
# 然后测试安装
pip install openpyxl reportlab
```

---

## 🔍 验证和调试

### 检查代理设置

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

### 检查 pip 配置

```bash
pip config list
pip config debug
```

### 测试连接

```bash
# 测试能否访问 PyPI
ping pypi.org
curl https://pypi.org -v

# 详细模式安装（查看详细日志）
pip install openpyxl --verbose
```

### 检查 Clash 日志

在 Clash 界面查看日志，确认 PyPI 请求是否走 DIRECT：

```
[Rule] pypi.org match DIRECT
```

---

## ❓ 常见问题

### Q1: 修改了 Clash 配置但不生效？

**A**:
1. 确认规则添加在 `rules:` 部分**最前面**
2. 确认 YAML 格式正确（缩进用 2 个空格）
3. 重新加载配置或重启 Clash
4. 检查 Clash 日志确认规则加载成功

### Q2: 还是报 SSL 证书错误？

**A**:
1. 尝试使用国内镜像：
   ```bash
   pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
   ```
2. 临时关闭 Clash 的系统代理
3. 使用 TUN 模式例外配置

### Q3: 所有方案都不行？

**A**:
1. 检查是否有企业防火墙或杀毒软件拦截
2. 尝试使用移动热点网络
3. 临时关闭 Clash 代理完成安装
4. 使用离线安装 wheel 文件

---

## 📝 总结

**首选方案**：修改 Clash 配置添加 PyPI 直连规则（方案一）

**配合方案**：创建 pip.ini 使用国内镜像（方案二）

**临时方案**：关闭代理或使用 `--trusted-host` 参数

---

## 🚀 立即执行

根据您之前提供的截图，您的 Clash 配置文件大约在第 101 行有 `rules:` 部分。

### 建议修改步骤：

1. **找到配置文件**（根据您使用的 Clash 版本）
2. **定位到 `rules:` 行**（大约第 101 行）
3. **在 `rules:` 下一行添加 PyPI 规则**
4. **保存并重新加载 Clash**
5. **测试 pip 安装**

如果您能提供配置文件的具体路径，我可以帮您直接修改文件！

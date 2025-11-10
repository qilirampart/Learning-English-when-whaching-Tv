# 美剧单词学习助手 - 需求分析文档

## 📋 项目概述

### 项目背景
在观看美剧时，观众经常会遇到不认识的单词。传统的解决方案存在以下问题：
- **翻译软件**：有查询记录但不会自动汇总和制定学习计划
- **专业背单词软件**：需要手动收藏才能加入学习计划，操作繁琐

本项目旨在创建一个**零摩擦**的单词学习工具，只要搜索过的单词就自动纳入学习计划，真正做到"随手查、随时记、轻松学"。

### 核心理念
- **即查即记**：查询即记录，无需额外操作
- **情境学习**：通过剧情回忆单词，加深记忆
- **自动规划**：系统自动制定学习计划，无需用户干预

---

## 🎯 核心功能

### 1. 快速单词查询（MVP核心）
- **快速输入**：简洁的查询界面，支持快捷键唤起（可选）
- **即时翻译**：实时显示单词释义、音标、发音
- **自动记录**：查询即记录，无需点击"收藏"或"保存"
- **情境备注**：可选填写剧名、剧情片段等上下文信息

**示例场景**：
```
用户在看《老友记》时遇到 "sarcastic"
→ 输入单词 → 立即显示"讽刺的" → 自动保存到学习列表
→ 可选填写：《老友记 S01E01，钱德勒说话方式》
```

### 2. 自动学习计划
- **智能汇总**：所有查询过的单词自动汇总
- **分类管理**：
  - 按剧集分类
  - 按日期分类
  - 按掌握程度分类（新学/学习中/已掌握）
- **学习提醒**：基于艾宾浩斯遗忘曲线的复习计划

### 3. 情境回忆学习
- **剧情关联**：查看单词时显示当时记录的剧情备注
- **场景回顾**：通过剧情片段回忆单词用法
- **例句展示**：显示单词的常用例句

### 4. 学习统计
- **查询统计**：今日/本周/本月查询量
- **学习进度**：已掌握/学习中/待复习单词数量
- **学习曲线**：可视化展示学习进度

---

## 🛠 技术栈

### 后端
- **语言**：Python 3.8+
- **框架**：Flask
- **数据库**：SQLite（初期）/ PostgreSQL（可扩展）
- **ORM**：SQLAlchemy
- **API设计**：RESTful API
- **第三方API**：
  - 有道翻译API / 金山词霸API（单词释义）
  - 发音API（可选）

### 前端
- **框架**：Vue.js 3 + Element Plus
  - **选择理由**：
    - Vue.js 学习曲线平缓，适合前端初学者
    - Element Plus 提供丰富的UI组件，开箱即用
    - 组件化开发，代码结构清晰
- **状态管理**：Pinia（轻量级）
- **HTTP客户端**：Axios
- **构建工具**：Vite

### 开发工具
- **版本控制**：Git
- **包管理**：pip（后端）、npm（前端）
- **API测试**：Postman / Thunder Client

---

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│          前端 (Vue.js + Element Plus)      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │查询页面 │  │单词列表 │  │学习计划 │  │
│  └─────────┘  └─────────┘  └─────────┘  │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼──────────────────────┐
│          后端 (Flask)                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │查询API  │  │记录API  │  │学习API  │  │
│  └─────────┘  └─────────┘  └─────────┘  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          数据库 (SQLite/PostgreSQL)      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │单词表   │  │查询记录 │  │学习计划 │  │
│  └─────────┘  └─────────┘  └─────────┘  │
└─────────────────────────────────────────┘
```

---

## 🗄 数据库设计

### 1. 单词表 (words)
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
word            VARCHAR(100) UNIQUE NOT NULL    -- 单词
phonetic        VARCHAR(100)                     -- 音标
translation     TEXT                             -- 翻译
definition      TEXT                             -- 英文释义
examples        TEXT                             -- 例句 (JSON格式)
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### 2. 查询记录表 (query_logs)
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
word_id         INTEGER FOREIGN KEY REFERENCES words(id)
tv_show         VARCHAR(200)                     -- 剧名
season_episode  VARCHAR(50)                      -- 集数 (如 S01E01)
context_note    TEXT                             -- 剧情备注
query_time      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### 3. 学习计划表 (learning_plans)
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
word_id         INTEGER FOREIGN KEY REFERENCES words(id)
mastery_level   INTEGER DEFAULT 0                -- 掌握程度 (0-5)
review_count    INTEGER DEFAULT 0                -- 复习次数
last_review     DATETIME                         -- 上次复习时间
next_review     DATETIME                         -- 下次复习时间
is_mastered     BOOLEAN DEFAULT FALSE            -- 是否已掌握
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
```

### 4. 复习记录表 (review_logs)
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
word_id         INTEGER FOREIGN KEY REFERENCES words(id)
is_correct      BOOLEAN                          -- 是否答对
review_time     DATETIME DEFAULT CURRENT_TIMESTAMP
time_spent      INTEGER                          -- 用时（秒）
```

---

## 🔌 API设计

### 1. 单词查询相关

#### POST /api/words/query
**功能**：查询单词并自动记录
```json
Request:
{
  "word": "sarcastic",
  "tv_show": "老友记",
  "season_episode": "S01E01",
  "context_note": "钱德勒的说话方式"
}

Response:
{
  "code": 200,
  "data": {
    "id": 1,
    "word": "sarcastic",
    "phonetic": "/sɑːrˈkæstɪk/",
    "translation": "讽刺的；挖苦的",
    "definition": "using or characterized by irony in order to mock or convey contempt",
    "examples": [
      "She made a sarcastic comment about his cooking.",
      "Don't be so sarcastic!"
    ],
    "query_count": 1,
    "last_query": "2025-11-10 10:30:00"
  }
}
```

#### GET /api/words/search?keyword=xxx
**功能**：搜索历史查询过的单词

#### GET /api/words/:id
**功能**：获取单词详情（含查询历史）

### 2. 单词列表相关

#### GET /api/words/list
**功能**：获取所有查询过的单词列表
```json
Query Parameters:
- page: 页码（默认1）
- page_size: 每页数量（默认20）
- order_by: 排序方式（time/frequency/mastery）
- filter_show: 按剧名筛选
- mastery_level: 按掌握程度筛选

Response:
{
  "code": 200,
  "data": {
    "total": 156,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "word": "sarcastic",
        "translation": "讽刺的",
        "query_count": 3,
        "mastery_level": 2,
        "last_query": "2025-11-10 10:30:00",
        "tv_shows": ["老友记", "生活大爆炸"]
      }
    ]
  }
}
```

### 3. 学习计划相关

#### GET /api/learning/today
**功能**：获取今日待复习单词

#### GET /api/learning/plan
**功能**：获取学习计划概览

#### POST /api/learning/review
**功能**：提交复习结果
```json
Request:
{
  "word_id": 1,
  "is_correct": true,
  "time_spent": 5
}
```

### 4. 统计相关

#### GET /api/statistics/overview
**功能**：获取学习统计概览
```json
Response:
{
  "code": 200,
  "data": {
    "total_words": 156,
    "today_queries": 12,
    "mastered": 45,
    "learning": 89,
    "to_review": 22,
    "weekly_trend": [5, 8, 12, 10, 15, 12, 9]
  }
}
```

---

## 🎨 用户界面设计

### 1. 主界面布局
```
┌────────────────────────────────────────────────┐
│  美剧单词学习助手                 [用户] [设置] │
├─────────┬──────────────────────────────────────┤
│         │                                      │
│ 查询    │        [查询页面]                    │
│         │   ┌─────────────────────────┐       │
│ 单词库  │   │  输入单词...            │ [搜索] │
│         │   └─────────────────────────┘       │
│ 学习计划│                                      │
│         │   [单词释义展示区]                   │
│ 统计    │   - 音标                             │
│         │   - 翻译                             │
│ 设置    │   - 例句                             │
│         │                                      │
└─────────┴──────────────────────────────────────┘
```

### 2. 主要页面

#### 页面1：快速查询页面
- 大号搜索框（支持回车搜索）
- 实时显示查询结果
- 可选填写剧情信息（折叠/展开）
- 显示查询历史（最近5个）

#### 页面2：单词库页面
- 单词卡片列表
- 筛选选项：
  - 按剧集筛选
  - 按掌握程度筛选
  - 按时间筛选
- 排序选项：时间/频率/掌握度
- 每个单词卡片显示：
  - 单词 + 翻译
  - 查询次数
  - 关联剧集
  - 掌握程度标签

#### 页面3：学习计划页面
- 今日待复习单词列表
- 复习进度条
- 学习卡片翻转效果
- 标记"掌握"/"模糊"/"不会"按钮

#### 页面4：统计页面
- 统计卡片：
  - 总单词数
  - 今日查询数
  - 已掌握/学习中/待复习
- 学习曲线图表
- 查询热度图表
- 最常查询的剧集排行

---

## 🚀 开发计划

### 第一阶段：MVP版本（核心功能）
**预计时间**：2-3周

#### Week 1：后端开发
- [ ] 搭建Flask项目框架
- [ ] 设计并创建数据库表结构
- [ ] 实现单词查询API（接入翻译API）
- [ ] 实现查询记录自动保存功能
- [ ] 实现单词列表API

#### Week 2：前端开发
- [ ] 搭建Vue.js项目框架
- [ ] 实现查询页面UI
- [ ] 实现单词列表页面UI
- [ ] 对接后端API
- [ ] 实现基本的响应式布局

#### Week 3：集成与测试
- [ ] 前后端集成测试
- [ ] 优化用户体验
- [ ] 修复Bug
- [ ] 编写部署文档

### 第二阶段：完善学习功能
**预计时间**：2-3周

- [ ] 实现学习计划算法（艾宾浩斯曲线）
- [ ] 实现复习功能
- [ ] 实现掌握程度评估
- [ ] 添加学习统计页面

### 第三阶段：增强功能（可选）
**预计时间**：按需开发

- [ ] 单词发音功能
- [ ] 导入/导出功能
- [ ] 浏览器插件（划词查询）
- [ ] 移动端适配
- [ ] 多用户系统
- [ ] 数据同步云端

---

## 💡 技术实现要点

### 1. 自动记录机制
- 每次查询单词时：
  1. 先查询数据库是否已存在该单词
  2. 如不存在，调用翻译API获取释义并保存
  3. 创建查询记录（含剧情信息）
  4. 自动创建或更新学习计划

### 2. 学习计划算法
- 基于艾宾浩斯遗忘曲线：
  - 第1次复习：1天后
  - 第2次复习：2天后
  - 第3次复习：4天后
  - 第4次复习：7天后
  - 第5次复习：15天后
- 根据复习结果动态调整：
  - 答对：进入下一复习周期
  - 答错：重置复习计划

### 3. 情境回忆功能
- 单词详情页展示所有查询记录
- 按时间倒序显示剧情备注
- 支持点击剧集名称查看该剧的所有单词

### 4. 性能优化
- 翻译API结果缓存
- 数据库查询优化（索引）
- 前端懒加载
- 图片资源CDN（如有）

---

## 📝 配置要求

### 环境要求
- Python 3.8+
- Node.js 16+
- pip
- npm / yarn

### 第三方服务
- 翻译API（选择其一）：
  - 有道翻译API（推荐，有免费额度）
  - 金山词霸API
  - 百度翻译API

---

## 🔐 安全考虑

1. **API密钥管理**：使用环境变量存储第三方API密钥
2. **输入验证**：对用户输入进行严格验证和清理
3. **CORS配置**：合理配置跨域访问策略
4. **SQL注入防护**：使用ORM防止SQL注入

---

## 📖 未来展望

### 短期目标
- 实现MVP版本，验证核心功能可用性
- 收集用户反馈，优化交互体验

### 长期目标
- 打造"沉浸式学习生态"：
  - 支持多种影视资源
  - AI智能推荐复习内容
  - 社区分享功能（分享单词本）
  - 学习成就系统

### 商业化可能性
- 免费版：基础功能
- 高级版：
  - 云同步
  - 更多翻译来源
  - 高级统计分析
  - 去广告

---

## 📞 项目信息

- **项目名称**：美剧单词学习助手 (TV Vocab Learner)
- **版本**：v1.0.0 (需求分析阶段)
- **文档更新日期**：2025-11-10

---

## 📚 附录

### A. 类似产品对比

| 产品 | 优点 | 缺点 |
|------|------|------|
| 有道词典 | 查词准确，有记录 | 无学习计划，记录不直观 |
| 扇贝单词 | 学习计划完善 | 需手动收藏，与查词分离 |
| Anki | 高度自定义 | 学习曲线陡峭，不够友好 |
| **本产品** | **即查即记，零摩擦学习** | **功能待完善** |

### B. 技术参考资料
- Flask官方文档：https://flask.palletsprojects.com/
- Vue.js官方文档：https://cn.vuejs.org/
- Element Plus文档：https://element-plus.org/zh-CN/
- 艾宾浩斯遗忘曲线：https://zh.wikipedia.org/wiki/遗忘曲线

---

**让学习融入生活，让单词不再遗忘！** 🚀

---

## 🚀 快速开始

详细的安装和运行指南请查看 [INSTALL.md](./INSTALL.md)

### 快速命令

**后端：**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

---

## 📸 项目截图

### 快速查询页面
- 输入单词即可查询
- 自动保存到学习计划
- 可选添加剧情备注

### 单词库页面
- 查看所有查询过的单词
- 按剧集、掌握程度筛选
- 查看单词详情和查询历史

### 学习计划页面
- 查看今日待复习单词
- 卡片式复习模式
- 基于艾宾浩斯遗忘曲线

### 统计页面
- 学习数据可视化
- 查询趋势图表
- 剧集单词数排行

---

## 💻 技术实现

### 已实现功能

✅ **核心功能**
- 单词查询与自动记录
- 剧情信息关联
- 单词库管理
- 查询历史记录

✅ **学习功能**
- 艾宾浩斯遗忘曲线算法
- 自动生成复习计划
- 掌握程度评估
- 复习模式

✅ **统计功能**
- 学习数据统计
- 查询趋势图表
- 剧集排行榜
- 掌握率分析

✅ **用户体验**
- 响应式设计
- 美观的UI界面
- 流畅的交互动画
- 实时反馈

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License


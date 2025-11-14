# 后端源码学习手册

> 适用对象：第一次接触该项目、希望手敲复现后端的同学。所有条目都按照“文件 → 行号 → 解释”给出，遇到成组的语句会使用“行X-Y”的形式，方便你照着敲。

## 目录
1. [运行与配置入口](#运行与配置入口)
   - [backend/run.py](#backendrunpy)
   - [backend/config.py](#backendconfigpy)
   - [backend/app/__init__.py](#backendapp__init__py)
2. [数据模型 (backend/app/models)](#数据模型-backendappmodels)
   - [models/__init__.py](#models__init__py)
   - [user.py](#userpy)
   - [word.py](#wordpy)
   - [learning_plan.py](#learning_planpy)
   - [query_log.py](#query_logpy)
   - [review_log.py](#review_logpy)
3. [通用工具与服务](#通用工具与服务)
   - [app/utils/auth.py](#apputilsauthpy)
   - [app/services/translation_service.py](#appservicestranslation_servicepy)
4. [蓝图与路由层 (backend/app/routes)](#蓝图与路由层-backendapproutes)
   - [auth.py](#authpy)
   - [words.py](#wordspy-路由)
   - [learning.py](#learningpy)
   - [statistics.py](#statisticspy)

---

## 运行与配置入口

### backend/run.py
| 行号 | 讲解 |
| --- | --- |
| 1 | 文件 docstring，表明这是“应用入口文件”。|
| 2 | `import os`：为了读取环境变量。|
| 3 | `from app import create_app`：引入 Flask 工厂函数。|
| 5 | 注释阐述下一行作用：获取环境配置名。|
| 6 | `config_name = os.getenv('FLASK_ENV', 'development')`：若未设置 `FLASK_ENV`，默认走开发配置。|
| 8 | 注释，提示即将创建应用实例。|
| 9 | `app = create_app(config_name)`：真正创建 Flask 应用。|
| 11 | `if __name__ == '__main__':`：仅当直接运行 `python run.py` 才进入。|
| 12-13 | 注释说明运行方式及端口来源。|
| 14 | `port = int(os.getenv('PORT', 5000))`：平台可用 `PORT` 注入，否则默认 5000。|
| 15-18 | `app.run(...)`：监听 `0.0.0.0`，端口为上面变量，`debug` 取自配置（开发 True，生产 False）。|

### backend/config.py
| 行号 | 讲解 |
| --- | --- |
| 1 | docstring：文件用途。|
| 2 | `import os` 用于拿环境变量。|
| 3 | `from dotenv import load_dotenv`：支持 `.env` 文件。|
| 5-6 | 调用 `load_dotenv()`，把 `.env` 内的键值加载进环境。|
| 8 | 定义 `Config` 基类。|
| 10-12 | Flask 安全配置：从环境取 `SECRET_KEY`，默认提供开发值。|
| 13-15 | SQLAlchemy 数据库 URL；若无设置则落到 SQLite。本项目关闭了 `SQLALCHEMY_TRACK_MODIFICATIONS` 减少开销。|
| 17-19 | 有道翻译 API 的 key/secret，默认空字符串。|
| 21-22 | CORS 允许的源域名列表，支持多个用逗号分隔。|
| 25-27 | `DevelopmentConfig` 继承基类，只把 `DEBUG` 设为 True。|
| 30-32 | `ProductionConfig` 把 `DEBUG` 设为 False。其余参数继承自基类。|
| 35-40 | `config` 字典：键是模式名，值是对应类。工厂函数会根据 `FLASK_ENV` 查表。|

### backend/app/__init__.py
| 行号 | 讲解 |
| --- | --- |
| 1 | docstring：声明这是 Flask 应用工厂所在的位置。|
| 2-4 | 导入 Flask、CORS、SQLAlchemy。|
| 6-7 | 创建全局的 `db = SQLAlchemy()`，供模型层引用。|
| 10 | 定义 `create_app`，默认配置名 `'default'`。|
| 12 | 根据当前模块名实例化 `Flask`。|
| 14-24 | 由于项目采用包布局，这里动态把 `backend` 目录加入 `sys.path`，避免导入 `config` 时失败。|
| 25-39 | `try/except` 逻辑：先直接 `from config import config`，若失败则手动构造 module spec，加载 `backend/config.py`，最后拿到 `config` 字典。|
| 41 | `app.config.from_object(config[config_name])`：真正把配置类加载进应用。|
| 43-45 | 初始化扩展：`db.init_app(app)` 绑定数据库；`CORS(app, ...)` 允许前端访问。|
| 47-52 | 延迟导入四个蓝图模块，然后逐个 `register_blueprint`。|
| 54-56 | 在应用上下文里 `db.create_all()`，保证第一次启动会建表。|
| 58 | 返回 app 实例。|

## 数据模型 (backend/app/models)

### models/__init__.py
| 行号 | 讲解 |
| --- | --- |
| 1 | docstring。|
| 2-6 | 把五个模型类导入到包层级。|
| 8 | 定义 `__all__`，当外部 `from app.models import *` 时只暴露这些名称。|

### user.py
| 行号 | 讲解 |
| --- | --- |
| 1 | docstring：用户模型。|
| 2 | 导入 `datetime`，用于时间戳字段。|
| 3 | 引入 Werkzeug 的哈希函数。|
| 4 | `from app import db`：拿到全局 SQLAlchemy 实例。|
| 7-9 | 定义 `User` 模型与表名 `users`。|
| 11-16 | 数据列：主键 ID、带索引的用户名/邮箱、密码哈希、创建与最后登录时间。|
| 18-21 | 关系：用户拥有查询记录、学习计划、复习记录。`lazy='dynamic'` 便于进一步过滤。|
| 23-26 | `set_password`：调用 `generate_password_hash`，避免明文。|
| 27-29 | `check_password`：与哈希比对。|
| 31-39 | `to_dict`：只返回公开字段，并把时间转成 ISO 字符串。|
| 41-42 | `__repr__` 帮助调试时打印用户名。|

### word.py
| 行号 | 讲解 |
| --- | --- |
| 1 | docstring。|
| 2 | `datetime` —— `created_at` 字段需要。|
| 3 | 导入 db。|
| 6-8 | 定义 `Word` 模型和表名。|
| 10-16 | 字段包括单词本身、音标、翻译、释义、JSON 文本形式的例句、创建时间。|
| 18-21 | 关系：和查询记录/学习计划/复习记录挂钩。`
| 23-35 | `to_dict`：在这里 `import json`，把字符串例句解析成列表，并统计 `query_logs.count()` 作为查询次数。|

### learning_plan.py
| 行号 | 讲解 |
| --- | --- |
| 1-3 | docstring 与必要导入。|
| 6-9 | 定义 `LearningPlan` 模型表。|
| 10-19 | 字段含用户 id、单词 id、掌握等级、复习次数、最近/下次复习时间、是否掌握、创建/更新时间。索引字段可以提升查询性能。|
| 21-22 | 设置联合唯一键 `_user_word_uc`，避免同一用户同一单词重复建计划。|
| 24-25 | `REVIEW_INTERVALS`：艾宾浩斯间隔常量数组。|
| 27-51 | `calculate_next_review(is_correct)`：根据答题结果调整 mastery。答对则 `+1` 并根据当前 mastery 决定 `next_review`；到达数组尾则视为掌握并取消下一次复习。答错则 `max(level-1,0)` 并重置下次复习为 1 天后。无论对错都累加 `review_count` 并更新 `last_review`。|
| 53-64 | `to_dict`：输出给前端看的字段。|

### query_log.py
| 行号 | 讲解 |
| --- | --- |
| 1-3 | docstring与导入。|
| 6-9 | 模型定义和表名。|
| 10-16 | 数据列：关联用户/单词、剧名、集数、上下文备注、查询时间。|
| 18-27 | `to_dict`：全部字段序列化，时间转字符串。|

### review_log.py
| 行号 | 讲解 |
| --- | --- |
| 1-4 | 同上。|
| 6-9 | 模型定义。|
| 10-15 | 字段：记录谁在什么时候复习了哪个词、是否答对、耗时。|
| 17-25 | `to_dict`：序列化字段。|

## 通用工具与服务

### app/utils/auth.py
| 行号 | 讲解 |
| --- | --- |
| 1-6 | 导入依赖与 `User` 模型。|
| 9-33 | `generate_token`：创建包含 `user_id`、到期时间(`exp`)、签发时间(`iat`)的 payload，用应用的 `SECRET_KEY` 通过 HS256 编码成 JWT。默认 86400 秒（24h）。|
| 35-57 | `verify_token`：解码 JWT，捕获过期或非法异常，返回 `user_id` 或 `None`。|
| 60-118 | `login_required` 装饰器：
  - 73-80：检查请求头里是否有 Authorization。没有则返回 401。
  - 83-90：拆分 `Bearer <token>`，格式错误时同样报 401。
  - 96-103：调用 `verify_token`，失效直接拒绝。
  - 104-110：根据 `user_id` 去数据库查用户，防止 token 里的用户已被删除。
  - 112-114：把用户存到 `flask.g`，供视图函数读取。
| 121-152 | `optional_login`：逻辑与上类似，但如果没有 token 就直接放行，如果有且有效就给 `g.current_user` 赋值。|

### app/services/translation_service.py
| 行号 | 讲解 |
| --- | --- |
| 1-6 | 导入 `requests`、哈希、uuid、时间以及 `current_app`。|
| 9-13 | 定义类并在构造函数里固定有道 API URL。|
| 15-31 | `translate`：读取配置中的 key/secret，若存在就走 `_translate_with_youdao`，否则或失败时回退 `_get_mock_translation`，保证开发阶段依然有数据。|
| 33-75 | `_translate_with_youdao`：
  - 37-41：生成请求签名（salt + 当前时间 + app secret）。
  - 43-52：组装 GET 参数。
  - 55-56：发起请求并解析 JSON。
  - 58-68：当 `errorCode` 为 `0` 时整理 phonetic、translation、definition、例句。失败返回 None。
  - 72-74：捕获异常，打印错误日志。|
| 76-84 | `_extract_examples`：从返回的 `web` 字段取最多 3 条例句。|
| 86-134 | `_get_mock_translation`：准备常见词的模拟数据；若不在字典中则返回通用模板（例句里带上查询词）。|

## 蓝图与路由层 (backend/app/routes)

### auth.py
> 提示：虽然行数较多，但可以按“函数”来记忆：校验工具函数 + 注册 + 登录 + 获取当前用户 + 刷新 token。

| 行号 | 讲解 |
| --- | --- |
| 1-8 | 导入 Flask 工具、`datetime`、数据库、`User` 模型、JWT 工具以及正则。|
| 9 | 声明 `Blueprint('auth', __name__, url_prefix='/api/auth')`。|
| 12-15 | `validate_email`：用正则匹配邮箱。|
| 18-23 | `validate_password`：检查长度≥6。|
| 26-115 | `register` 视图：
  - 46 | `data = request.get_json()` 读取 JSON 请求体。
  - 48-53 | 校验 `username/email/password` 必填。
  - 55-58 | 去掉两端空格、email 小写。
  - 60-78 | 分别验证用户名长度、邮箱格式、密码长度。
  - 80-92 | 查询数据库，防止用户名或邮箱重复。
  - 94-104 | 创建用户对象、哈希密码、提交数据库、生成 token。
  - 105-108 | 返回 201 状态以及用户信息。
  - 110-115 | 异常回滚事务并返回 500。|
| 118-179 | `login`：结构与注册类似，区别在于允许“用户名或邮箱”登录（149-152）、检查密码（155-159）、更新最后登录时间（161-163）。|
| 182-199 | `get_current_user`：被 `@login_required` 保护，从 `g.current_user` 取用户并返回。|
| 201-220 | `refresh_token`：生成新的 JWT 并返回。|

### words.py (路由)
为便于理解，按四个接口拆解。

#### 顶部准备工作（行1-13）
- 导入 Blueprint、request/jsonify/g、数据库、Word/QueryLog/LearningPlan 模型、翻译服务、`login_required`、SQLAlchemy 的排序工具、`json` 模块。
- 创建蓝图 `bp`，并实例化一个 `TranslationService`。

#### `/query` 接口（行16-82）
| 行号 | 讲解 |
| --- | --- |
| 16-18 | 装饰器声明 POST + 登录校验。|
| 20-22 | 从请求体读取 `word` 并做 `strip().lower()`，保持数据库统一。|
| 24-25 | 若输入为空，返回 400。|
| 27-28 | 在 `words` 表中查是否已存在。|
| 30-47 | 若不存在：调用翻译服务（32-34），若返回空则告知 500；否则用翻译结果创建 `Word` 记录，`json.dumps` 例句，并 `db.session.flush()` 立刻拿到 `word.id`。|
| 48-60 | 确保该用户对这个单词有 `LearningPlan`，没有就创建。|
| 62-71 | 新建 `QueryLog`，写入剧集、集数、备注，然后提交事务。|
| 73-77 | 把 `word.to_dict()` 结果返回，并补上最新查询时间。异常部分在 79-81 里回滚。|

#### `/search` 接口（行84-107）
| 行号 | 讲解 |
| --- | --- |
| 84-88 | 装饰器 + 函数签名。|
| 89-92 | 从查询字符串拿关键字并检查非空。|
| 94-99 | 只搜索当前用户查过的单词：`Word.query.join(QueryLog)`，过滤 `QueryLog.user_id`，做模糊匹配，`distinct` 去重并限制 20 条。|
| 100-103 | 把单词数组转 dict，包装响应。异常则返回 500。|

#### `/api/words/<word_id>`（行109-138）
| 行号 | 讲解 |
| --- | --- |
| 111-114 | 根据 path 参数取单词。不存在返回 404。|
| 119-123 | 查询该用户关联的 `QueryLog`，按时间倒序。|
| 125-129 | 查找该单词的 `LearningPlan`。|
| 131-135 | 合并 `word`、`query_logs`、`learning_plan` 三部分数据返回。|

#### `/list` 接口（行141-227）
| 行号 | 讲解 |
| --- | --- |
| 141-151 | 读取分页、排序、剧集过滤、掌握度过滤参数。|
| 153-165 | 初步查询（只看当前用户），可选地按剧集、掌握等级追加过滤。|
| 167-179 | 根据 `order_by` 选择排序策略：查询频率、掌握程度或最后查询时间。|
| 183-185 | 调用 `paginate` 获取分页对象。|
| 187-213 | 遍历每个单词：
  - 191-197 | 查询该用户下该词出现过的剧集。
  - 199-205 | 获取掌握等级（无计划则 0）。
  - 206-211 | 找到最后一次查询时间。
  - 213 | 加入列表。|
| 215-223 | 返回包含 `total/page/page_size/items` 的分页响应。|
| 225-226 | 出错时给出 500。|

### learning.py
| 行号 | 讲解 |
| --- | --- |
| 1-11 | 导入依赖并声明蓝图。|
| 14-44 | `/today`：用 SQLAlchemy 的 `and_` 过滤出当前用户、`next_review` 早于现在且尚未掌握的计划；遍历时把 `Word` 详情和 `LearningPlan` 信息打包返回。|
| 48-88 | `/plan`：分别统计总词数、已掌握、学习中、待复习四个数字，通过 `.count()` 获得，构造成 `data` 返回。|
| 91-134 | `/review`：
  - 96-103 | 读取入参并校验。
  - 105-111 | 确认该用户对该词确实有计划。
  - 113-121 | 调用 `calculate_next_review` 更新计划，并创建 `ReviewLog`。`
  - 123-130 | 提交事务并返回新的计划状态。|
| 132-134 | 异常时回滚。|

### statistics.py
| 行号 | 讲解 |
| --- | --- |
| 1-11 | 导入 Blueprint、db、需要的模型/函数，并命名为 `/api/statistics`。|
| 14-78 | `/overview`：
  - 20 | 统计总单词数。
  - 22-27 | 计算今日查询次数：构造 `today_start`，过滤 `QueryLog.query_time >= today_start`。
  - 29-48 | 统计已掌握、学习中、待复习数量。
  - 50-63 | `weekly_trend`：循环最近 7 天，统计每日查询数。
  - 64-74 | 把全部指标打包返回。|
| 80-112 | `/tv_shows`：使用 `db.session.query` + `func.count(distinct word_id)`，过滤非空 `tv_show`，分组后按单词数倒序取前 10 条，转换成列表返回。|

---

## 使用建议
1. **先跑通环境**：按照 `run.py`、`config.py` 的解释设置好 `.env` 并执行 `python run.py`，确保 SQLite 自动建表。
2. **逐文件手敲**：建议从模型开始，再写工具/服务，最后是路由。每写完一个模块就运行 `flask shell` 或单元测试验证。
3. **边敲边阅读本文档**：表格里的行号和解释可作为“对照注释”，理解完后再记笔记，能加深记忆。
4. **调试思路**：当接口报错时，结合路由表格查找对应行，并根据解释定位问题所在的变量或数据库查询。

希望这份行级别的说明能帮助你快速读懂并复现整个后端！

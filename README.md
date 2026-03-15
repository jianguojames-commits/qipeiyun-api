# 汽配云助手

汽车配件数据处理和库存查询工具。

## 功能特性

- **数据清洗**: 自动化清洗和规范化汽配数据
- **库存查询**: 灵活的API查询配件库存（支持CSV和SQLite数据库）
- **SQLite数据库**: 高性能数据存储，支持复杂查询
- **品牌映射**: 支持中英文品牌别名转换
- **类别标准化**: 统一的配件类别命名
- **数据验证**: 基于规则的数据质量检查
- **全文搜索**: 支持关键词搜索
- **用户认证**: JWT令牌认证
- **数据可视化**: ECharts图表展示

## 项目结构

```
qipeiyun-assistant/
├── src/                       # 源代码
│   ├── autoparts_cleaner.py  # 数据清洗脚本
│   ├── query_inventory.py    # 库存查询API（CSV版本）
│   └── models.py             # 数据库模型（SQLAlchemy）
├── configs/                   # 配置文件
│   ├── brand_aliases.json    # 品牌别名映射
│   ├── category_map.json     # 类别映射
│   └── rules.json            # 业务规则
├── data/                      # 数据目录
│   ├── raw/                  # 原始数据
│   ├── clean/                # 清洗后数据
│   └── qipeiyun.db           # SQLite数据库
├── docs/                      # API文档
│   ├── api-docs.md           # API使用文档
│   └── openapi.yaml         # OpenAPI 3.0规范
├── examples/                  # 使用示例
│   └── db_query_examples.py  # 数据库查询示例
├── tests/                    # 测试文件
├── venv/                     # Python虚拟环境
├── api_server.py             # FastAPI服务器
├── db_query.py               # 数据库查询API v2.0
├── migrate_to_sqlite.py      # 数据迁移脚本
├── test_api.py               # API测试脚本
├── requirements.txt          # Python依赖
└── README.md                 # 项目说明
```

## 快速开始

### 一键启动

```bash
cd ~/projects/qipeiyun-assistant

# 激活虚拟环境
source venv/bin/activate

# 启动主界面（包含所有功能）
python web_app_flask.py

# 或使用启动脚本
python start.py
```

### 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 Web管理界面 | http://localhost:5000 | 主界面（搜索、筛选、详情） |
| 📊 数据可视化 | http://localhost:5001 | 图表统计展示 |
| 📡 API服务 | http://localhost:8000 | RESTful API |
| 📖 API文档 | http://localhost:8000/docs | Swagger文档 |

### 启动脚本选项

```bash
python start.py --web    # 仅启动Web界面
python start.py --api    # 仅启动API服务
python start.py --viz    # 仅启动可视化
python start.py --all    # 启动所有服务
```

### 2. 数据清洗

```bash
python src/autoparts_cleaner.py \
  --raw data/raw \
  --out data/clean \
  --configs configs \
  --currency CNY
```

### 3. 数据迁移到SQLite（推荐）

```bash
# 将CSV数据迁移到SQLite数据库
python migrate_to_sqlite.py --csv data/clean/clean_parts.csv --db data/qipeiyun.db

# 或使用默认路径
python migrate_to_sqlite.py
```

### 4. 使用SQLite数据库查询（高性能）

```python
from db_query import query_parts, search_parts

# 查询所有Bosch品牌的配件
results = query_parts(brand="Bosch")

# 复杂查询：品牌+类别+价格范围
results = query_parts(
    brand="Bosch",
    category="Brake Pad",
    vehicle_make="Toyota",
    min_price=100,
    max_price=500,
    limit=10
)

# 全文搜索
results = search_parts("刹车片")

# 获取所有品牌列表
brands = get_brands()

# 获取价格范围
price_range = get_price_range()
```

### 5. 启动API服务（推荐）

```bash
# 启动API服务
python api_server.py

# 访问地址
# - API根路径: http://localhost:8000
# - Swagger文档: http://localhost:8000/docs
# - ReDoc文档: http://localhost:8000/redoc
```

### 6. API使用示例

```bash
# 查询所有配件
curl http://localhost:8000/api/parts

# 按品牌查询
curl "http://localhost:8000/api/parts?brand=Bosch"

# 价格区间查询
curl "http://localhost:8000/api/parts?min_price=50&max_price=200"

# 全文搜索
curl "http://localhost:8000/api/parts/search?keyword=刹车片"

# 获取品牌列表
curl http://localhost:8000/api/brands

# 获取统计信息
curl http://localhost:8000/api/stats
```

### 7. 启动Web管理界面

```bash
# 启动Web界面（Flask版本）
python web_app_flask.py

# 访问地址: http://localhost:5000
```

功能：
- 🏠 首页：统计信息和最近配件
- 🔍 搜索：关键词搜索配件
- 📋 筛选：多条件组合筛选
- 📝 详情：按ID查询配件详情
- 📥 导出：筛选结果导出CSV

### 8. 使用CSV查询（向后兼容）

```python
from src.query_inventory import query_parts_inventory

# 查询所有Bosch品牌的配件
results = query_parts_inventory(
    csv_path="data/clean/clean_parts.csv",
    brand="Bosch"
)
```

## 数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| part_id | string | 唯一标识符 |
| oe_number | string | 原厂配件编号 |
| sku | string | SKU编码 |
| brand | string | 品牌名称 |
| category | string | 配件类别 |
| name | string | 配件名称 |
| description | string | 详细描述 |
| vehicle_make | string | 适用车型品牌 |
| vehicle_model | string | 适用车型 |
| vehicle_year_start | int | 起始年份 |
| vehicle_year_end | int | 结束年份 |
| price | float | 价格 |
| currency | string | 货币单位 |
| specs | JSON | 规格参数 |

## 配置说明

### brand_aliases.json
品牌别名映射，支持中英文转换：
```json
{
  "bosch": "Bosch",
  "博世": "Bosch",
  "denso": "Denso",
  "电装": "Denso"
}
```

### category_map.json
类别名称标准化映射：
```json
{
  "brake pad": "Brake Pad",
  "制动片": "Brake Pad",
  "air filter": "Air Filter"
}
```

### rules.json
数据验证规则：
```json
{
  "price": {
    "brake pad": { "min": 50, "max": 800 }
  },
  "required_specs_by_category": {
    "brake pad": ["material", "thickness_mm"]
  }
}
```

## 开发计划

- [x] ✅ SQLite数据库支持
- [x] ✅ RESTful API接口（FastAPI）
- [x] ✅ OpenAPI 3.0 规范文档
- [x] ✅ Web管理界面（Flask + Bootstrap）
- [x] ✅ 用户认证和权限管理（JWT）
- [ ] 多语言支持
- [ ] 数据可视化报表

## 用户认证

### 启动带认证的API服务

```bash
# 启动带认证的API服务
python api_server_auth.py

# 访问地址
# - API: http://localhost:8000
# - Swagger: http://localhost:8000/docs
```

### 默认账户

首次启动会自动创建管理员账户：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |

### API认证流程

```bash
# 1. 登录获取令牌
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 响应示例:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user": {...}
# }

# 2. 使用令牌访问受保护的API
curl http://localhost:8000/api/parts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. 获取当前用户信息
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### API端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录 | 否 |
| GET | `/api/auth/me` | 获取当前用户 | 是 |
| POST | `/api/auth/refresh` | 刷新令牌 | 是 |
| GET | `/api/parts` | 查询配件列表 | 是 |
| GET | `/api/parts/search` | 搜索配件 | 是 |
| GET | `/api/brands` | 获取品牌列表 | 否 |
| GET | `/api/categories` | 获取类别列表 | 否 |
| GET | `/api/stats` | 获取统计信息 | 否 |

## 许可证

MIT License

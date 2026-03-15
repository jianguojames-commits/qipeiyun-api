# 汽配云助手 API 文档

> 当前版本: **2.0.0** | [English Version](./api-docs-en.md)

---

## 概述

汽配云助手API为汽车配件经销商提供完整的数据管理和查询解决方案。

### 主要特性

- 🔍 **多条件查询** - 支持品牌、类别、车型、价格等多维度筛选
- 📝 **全文搜索** - 快速搜索配件名称、描述、OE号
- 📊 **数据统计** - 实时获取库存统计信息
- 🚀 **高性能** - SQLite数据库 + 索引优化
- 📚 **完整文档** - OpenAPI 3.0 规范

---

## 快速开始

### 1. 启动API服务

```bash
# 进入项目目录
cd ~/projects/qipeiyun-assistant

# 激活虚拟环境
source venv/bin/activate

# 启动API服务
python api_server.py
```

服务启动后访问: http://localhost:8000

### 2. 示例请求

#### 查询所有 Bosch 品牌配件

```bash
curl "http://localhost:8000/api/parts?brand=Bosch"
```

**响应:**
```json
{
  "success": true,
  "count": 2,
  "total": 2,
  "data": [
    {
      "part_id": "ba0ed0e5df48a47b",
      "brand": "Bosch",
      "name": "前刹车片",
      "price": 368,
      "oe_number": "044650E010"
    }
  ]
}
```

#### 按OE号精确查询

```bash
curl "http://localhost:8000/api/parts?oe_number=044650E010"
```

#### 全文搜索

```bash
curl "http://localhost:8000/api/parts/search?keyword=刹车片"
```

---

## API 端点

### 查询接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/parts` | 查询配件列表（支持多条件） |
| GET | `/api/parts/{part_id}` | 根据ID获取配件详情 |
| GET | `/api/parts/search` | 全文搜索配件 |

### 工具接口

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/brands` | 获取所有品牌列表 |
| GET | `/api/categories` | 获取所有配件类别 |
| GET | `/api/vehicles` | 获取所有车辆品牌 |
| GET | `/api/stats` | 获取数据库统计 |
| GET | `/api/price-range` | 获取价格范围 |

---

## 查询参数说明

### /api/parts

| 参数 | 类型 | 描述 | 示例 |
|------|------|------|------|
| `brand` | string | 品牌名称 | `Bosch` |
| `category` | string | 配件类别 | `Brake Pad` |
| `vehicle_make` | string | 车辆品牌 | `Toyota` |
| `vehicle_model` | string | 车辆型号 | `Camry` |
| `oe_number` | string | OE号（精确） | `044650E010` |
| `supplier` | string | 供应商 | `Toyota CN` |
| `min_price` | number | 最低价格 | `50` |
| `max_price` | number | 最高价格 | `500` |
| `limit` | int | 返回数量 | `100` |
| `offset` | int | 偏移量 | `0` |

---

## 使用示例

### Python SDK

```python
import requests

# 查询配件
response = requests.get("http://localhost:8000/api/parts", params={
    "brand": "Bosch",
    "category": "Brake Pad",
    "min_price": 100,
    "max_price": 500
})
data = response.json()
print(f"找到 {data['count']} 个配件")

# 搜索配件
response = requests.get("http://localhost:8000/api/parts/search", params={
    "keyword": "刹车片"
})

# 获取统计
response = requests.get("http://localhost:8000/api/stats")
stats = response.json()["data"]
print(f"总配件数: {stats['total_parts']}")
```

### JavaScript

```javascript
// 使用fetch API
const response = await fetch('http://localhost:8000/api/parts?brand=Bosch');
const data = await response.json();
console.log(`找到 ${data.count} 个配件`);
```

### cURL

```bash
# 查询价格区间内的配件
curl "http://localhost:8000/api/parts?min_price=50&max_price=200&limit=10"

# 获取所有品牌
curl "http://localhost:8000/api/brands"

# 获取统计信息
curl "http://localhost:8000/api/stats"
```

---

## 响应格式

### 成功响应

```json
{
  "success": true,
  "count": 10,
  "total": 100,
  "data": [
    {
      "part_id": "ba0ed0e5df48a47b",
      "brand": "Bosch",
      "name": "前刹车片",
      "price": 368,
      ...
    }
  ]
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "无效的查询参数"
  }
}
```

---

## 数据模型

### Part (配件)

| 字段 | 类型 | 描述 |
|------|------|------|
| `part_id` | string | 唯一标识符 |
| `oe_number` | string | OE号（原厂编号） |
| `sku` | string | SKU编码 |
| `brand` | string | 品牌 |
| `category` | string | 类别 |
| `name` | string | 名称 |
| `description` | string | 描述 |
| `vehicle_make` | string | 适用车型品牌 |
| `vehicle_model` | string | 适用车型 |
| `price` | number | 价格 |
| `currency` | string | 货币 |
| `specs` | object | 规格参数 |

---

## 错误代码

| 代码 | 描述 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## OpenAPI 规范

完整API规范见: [openapi.yaml](./openapi.yaml)

可以使用Swagger UI查看: http://localhost:8000/docs

---

## 联系我们

- 📧 邮箱: support@qipeiyun.com
- 📞 电话: 400-888-8888
- 🌐 网站: https://qipeiyun.com

---

*最后更新: 2026-03-15*

# 🚗 汽配云助手 API 操作手册

> 版本: 2.1.0 | 更新日期: 2026-03-15

---

## 目录

1. [概述](#1-概述)
2. [快速开始](#2-快速开始)
3. [认证说明](#3-认证说明)
4. [API端点详解](#4-api端点详解)
5. [请求示例](#5-请求示例)
6. [错误处理](#6-错误处理)
7. [代码示例](#7-代码示例)

---

## 1. 概述

汽配云助手API为汽车配件经销商提供完整的RESTful接口，支持：

- ✅ 配件数据查询（多条件组合）
- ✅ 全文搜索
- ✅ 品牌/类别/车型筛选
- ✅ 价格范围查询
- ✅ 用户认证
- ✅ 数据统计

### Base URL

```
生产环境: https://api.qipeiyun.com (暂未开放)
本地开发: http://localhost:8000
```

---

## 2. 快速开始

### 2.1 启动服务

```bash
cd ~/projects/qipeiyun-assistant
source venv/bin/activate
python api_server_auth.py
```

服务启动后访问: http://localhost:8000/docs

### 2.2 接口列表

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/auth/register` | POST | 用户注册 | ❌ |
| `/api/auth/login` | POST | 用户登录 | ❌ |
| `/api/auth/me` | GET | 获取当前用户 | ✅ |
| `/api/auth/refresh` | POST | 刷新令牌 | ✅ |
| `/api/parts` | GET | 查询配件列表 | ✅ |
| `/api/parts/{id}` | GET | 获取配件详情 | ✅ |
| `/api/parts/search` | GET | 全文搜索 | ✅ |
| `/api/brands` | GET | 获取品牌列表 | ❌ |
| `/api/categories` | GET | 获取类别列表 | ❌ |
| `/api/vehicles` | GET | 获取车型列表 | ❌ |
| `/api/stats` | GET | 获取统计信息 | ❌ |
| `/api/price-range` | GET | 获取价格范围 | ❌ |

---

## 3. 认证说明

### 3.1 认证流程

```mermaid
graph LR
    A[用户] --> B[登录请求]
    B --> C[验证用户名密码]
    C --> D[返回JWT令牌]
    D --> E[携带令牌请求]
    E --> F[验证令牌]
    F --> G[返回数据]
```

### 3.2 登录获取令牌

**请求:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**响应:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@qipeiyun.com",
    "role": "admin",
    "is_active": true
  }
}
```

### 3.3 使用令牌

获取令牌后，在请求头中添加：

```bash
curl http://localhost:8000/api/parts \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 4. API端点详解

### 4.1 认证接口

#### POST /api/auth/register

注册新用户

**请求参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| email | string | ✅ | 邮箱 |
| password | string | ✅ | 密码 |
| full_name | string | ❌ | 真实姓名 |

**请求示例:**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "测试用户"
  }'
```

**响应:**

```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "full_name": "测试用户",
  "role": "user",
  "is_active": true
}
```

---

#### POST /api/auth/login

用户登录

**请求参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| username | string | ✅ | 用户名或邮箱 |
| password | string | ✅ | 密码 |

**响应:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@qipeiyun.com",
    "role": "admin"
  }
}
```

---

#### GET /api/auth/me

获取当前用户信息

**请求头:**

| 参数 | 必填 | 描述 |
|------|------|------|
| Authorization | ✅ | Bearer {access_token} |

**响应:**

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@qipeiyun.com",
  "full_name": "系统管理员",
  "role": "admin",
  "is_active": true
}
```

---

### 4.2 数据查询接口

#### GET /api/parts

查询配件列表（支持多条件组合）

**查询参数:**

| 参数 | 类型 | 描述 | 示例 |
|------|------|------|------|
| brand | string | 品牌名称 | `?brand=Bosch` |
| category | string | 配件类别 | `?category=Brake Pad` |
| vehicle_make | string | 车辆品牌 | `?vehicle_make=Toyota` |
| vehicle_model | string | 车辆型号 | `?vehicle_model=Camry` |
| oe_number | string | OE号（精确） | `?oe_number=044650E010` |
| supplier | string | 供应商 | `?supplier=Toyota CN` |
| min_price | number | 最低价格 | `?min_price=50` |
| max_price | number | 最高价格 | `?max_price=500` |
| limit | int | 返回数量(1-1000) | `?limit=100` |
| offset | int | 偏移量 | `?offset=0` |

**请求示例:**

```bash
# 查询所有配件
curl http://localhost:8000/api/parts \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按品牌查询
curl "http://localhost:8000/api/parts?brand=Bosch" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 组合查询
curl "http://localhost:8000/api/parts?brand=Bosch&category=Brake Pad&min_price=100&max_price=500" \
  -H "Authorization: Bearer YOUR_TOKEN"
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
      "oe_number": "044650E010",
      "sku": "AE010",
      "brand": "Bosch",
      "category": "Brake Pad",
      "name": "前刹车片",
      "price": 368.0,
      "currency": "CNY",
      "vehicle_make": "Toyota",
      "vehicle_model": "Camry",
      "vehicle_year_start": 2015,
      "vehicle_year_end": 2017
    }
  ]
}
```

---

#### GET /api/parts/{part_id}

根据ID获取配件详情

**路径参数:**

| 参数 | 类型 | 描述 |
|------|------|------|
| part_id | string | 配件唯一标识符 |

**请求示例:**

```bash
curl http://localhost:8000/api/parts/ba0ed0e5df48a47b \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应:**

```json
{
  "success": true,
  "data": {
    "part_id": "ba0ed0e5df48a47b",
    "oe_number": "044650E010",
    "sku": "AE010",
    "brand": "Bosch",
    "category": "Brake Pad",
    "name": "前刹车片",
    "description": "高性能陶瓷配方",
    "price": 368.0,
    "currency": "CNY",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_year_start": 2015,
    "vehicle_year_end": 2017,
    "position": "Front",
    "specs": {
      "material": "ceramic",
      "thickness_mm": 16
    },
    "supplier": "Toyota CN"
  }
}
```

---

#### GET /api/parts/search

全文搜索配件

**查询参数:**

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| keyword | string | ✅ | 搜索关键词 |
| limit | int | ❌ | 返回数量(1-100) |

**搜索范围:**
- 配件名称 (name)
- 描述 (description)
- OE号 (oe_number)
- SKU (sku)

**请求示例:**

```bash
curl "http://localhost:8000/api/parts/search?keyword=刹车片" \
  -H "Authorization: Bearer YOUR_TOKEN"

curl "http://localhost:8000/api/parts/search?keyword=04465&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应:**

```json
{
  "success": true,
  "keyword": "刹车片",
  "count": 1,
  "data": [
    {
      "part_id": "ba0ed0e5df48a47b",
      "name": "前刹车片",
      "brand": "Bosch",
      "category": "Brake Pad",
      "price": 368.0
    }
  ]
}
```

---

### 4.3 公开接口

以下接口无需认证即可访问：

#### GET /api/brands

获取所有品牌列表

```bash
curl http://localhost:8000/api/brands
```

**响应:**

```json
{
  "success": true,
  "count": 2,
  "data": ["Bosch", "Denso"]
}
```

---

#### GET /api/categories

获取所有配件类别

```bash
curl http://localhost:8000/api/categories
```

**响应:**

```json
{
  "success": true,
  "count": 4,
  "data": ["Air Filter", "Brake Pad", "Oil Filter", "Spark Plug"]
}
```

---

#### GET /api/stats

获取数据库统计信息

```bash
curl http://localhost:8000/api/stats
```

**响应:**

```json
{
  "success": true,
  "data": {
    "total_parts": 4,
    "unique_brands": 2,
    "unique_categories": 4,
    "price_range": {
      "min": 68.0,
      "max": 368.0,
      "avg": 162.75
    }
  }
}
```

---

#### GET /api/price-range

获取价格区间

```bash
curl http://localhost:8000/api/price-range
```

**响应:**

```json
{
  "success": true,
  "data": {
    "min": 68.0,
    "max": 368.0,
    "avg": 162.75
  }
}
```

---

## 5. 请求示例

### 5.1 Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 登录获取令牌
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

# 2. 使用令牌查询
headers = {"Authorization": f"Bearer {token}"}

# 查询配件
response = requests.get(f"{BASE_URL}/api/parts", headers=headers)
print(response.json())

# 搜索配件
response = requests.get(
    f"{BASE_URL}/api/parts/search?keyword=刹车片",
    headers=headers
)
print(response.json())

# 获取统计
response = requests.get(f"{BASE_URL}/api/stats")
print(response.json())
```

### 5.2 JavaScript fetch

```javascript
const BASE_URL = 'http://localhost:8000';

// 登录
async function login() {
  const response = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123'
    })
  });
  const data = await response.json();
  return data.access_token;
}

// 查询配件
async function getParts(token) {
  const response = await fetch(`${BASE_URL}/api/parts?brand=Bosch`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// 使用
login().then(token => {
  getParts(token).then(console.log);
});
```

### 5.3 cURL

```bash
# 1. 登录
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. 查询配件
curl http://localhost:8000/api/parts \
  -H "Authorization: Bearer $TOKEN"

# 3. 搜索
curl "http://localhost:8000/api/parts/search?keyword=刹车片" \
  -H "Authorization: Bearer $TOKEN"

# 4. 获取用户信息
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. 错误处理

### 6.1 HTTP状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/认证失败 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 6.2 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": 401,
    "detail": "无效的令牌"
  }
}
```

### 6.3 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 401 Invalid token | 令牌无效 | 重新登录获取令牌 |
| 401 User not found | 用户不存在 | 检查用户名 |
| 400 User already exists | 用户已存在 | 使用其他用户名 |
| 404 Part not found | 配件不存在 | 检查part_id |

---

## 7. 代码示例

### 7.1 Python SDK封装

```python
class QipeiYunClient:
    """汽配云API客户端"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.token = self._login(username, password)
    
    def _login(self, username, password) -> str:
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_parts(self, **filters):
        response = requests.get(
            f"{self.base_url}/api/parts",
            params=filters,
            headers=self._headers()
        )
        return response.json()
    
    def search_parts(self, keyword: str, limit: int = 20):
        response = requests.get(
            f"{self.base_url}/api/parts/search",
            params={"keyword": keyword, "limit": limit},
            headers=self._headers()
        )
        return response.json()
    
    def get_stats(self):
        response = requests.get(f"{self.base_url}/api/stats")
        return response.json()


# 使用
client = QipeiYunClient(
    base_url="http://localhost:8000",
    username="admin",
    password="admin123"
)

# 查询
results = client.get_parts(brand="Bosch", min_price=100)
print(results)

# 搜索
results = client.search_parts("刹车片")
print(results)

# 统计
stats = client.get_stats()
print(stats)
```

### 7.2 Django集成

```python
# settings.py
QIPEIYUN_CONFIG = {
    'BASE_URL': 'http://localhost:8000',
    'USERNAME': 'admin',
    'PASSWORD': 'admin123',
}

# views.py
from django.http import JsonResponse
from .clients import QipeiYunClient

def parts_list(request):
    client = QipeiYunClient(**settings.QIPEIYUN_CONFIG)
    filters = {
        'brand': request.GET.get('brand'),
        'category': request.GET.get('category'),
        'min_price': request.GET.get('min_price'),
    }
    data = client.get_parts(**{k: v for k, v in filters.items() if v})
    return JsonResponse(data)
```

---

## 附录

### 数据模型

#### Part (配件)

| 字段 | 类型 | 描述 |
|------|------|------|
| part_id | string | 唯一标识符 |
| oe_number | string | OE号（原厂编号） |
| sku | string | SKU编码 |
| brand | string | 品牌 |
| category | string | 类别 |
| name | string | 名称 |
| description | string | 描述 |
| vehicle_make | string | 适用车型品牌 |
| vehicle_model | string | 适用车型 |
| price | float | 价格 |
| currency | string | 货币 |
| specs | object | 规格参数 |

---

**文档版本**: v2.1.0  
**最后更新**: 2026-03-15  
**技术支持**: support@qipeiyun.com

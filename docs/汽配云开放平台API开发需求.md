# 🚗 汽配云开放平台 API 开发需求文档

> 版本: 1.0 | 日期: 2026-03-15

---

## 一、概述

本文档基于汽配云开放平台（https://qpyun.yuque.com/gktk3c/hpe935）的API接口规范，转化为开发需求文档。

### 1.1 平台定位

汽配云是专业的汽车配件行业ERP系统解决方案提供商，主要产品包括：
- 云ERP（进销存）
- WMS智能仓储管理
- 营销小程序
- DMS管理系统（厂家）
- 云EPC（配件数据查询）
- 五号班车（物流配送）

### 1.2 接入方式

| 方式 | 说明 |
|------|------|
| HTTP REST API | 标准HTTP接口 |
| Webhook | 异步回调通知 |
| SDK | 官方提供多种语言SDK |

---

## 二、API接口清单

### 2.1 基础信息

| 项目 | 说明 |
|------|------|
| 基础URL | `https://api.qpyun.com` |
| 数据格式 | JSON |
| 编码 | UTF-8 |
| 签名算法 | MD5/HMAC-SHA256 |
| 认证方式 | AppKey + AppSecret |

### 2.2 通用请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| app_id | string | ✅ | 应用ID |
| timestamp | string | ✅ | 时间戳(毫秒) |
| sign | string | ✅ | 签名 |
| format | string | ❌ | 响应格式(json/xml) |
| v | string | ✅ | API版本号 |

### 2.3 通用响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {},
  "sign": "xxx"
}
```

---

## 三、业务接口详情

### 3.1 配件查询模块

#### 3.1.1 VIN码查询车辆信息

**接口地址**: `/api/v1/vin/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vin | string | ✅ | 17位车架号 |

**请求示例**:
```json
{
  "app_id": "your_app_id",
  "timestamp": "1701234567890",
  "sign": "xxx",
  "v": "1.0",
  "vin": "LSVAG4189ES123456"
}
```

**响应示例**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "brand": "大众",
    "factory": "上海大众",
    "series": "帕萨特",
    "model": "帕萨特 2015款 1.8T",
    "year": "2015",
    "engine": "1.8T",
    "transmission": "自动"
  }
}
```

#### 3.1.2 OE号查询配件

**接口地址**: `/api/v1/oe/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| oe_number | string | ✅ | OE号 |
| brand | string | ❌ | 品牌筛选 |

#### 3.1.3 车型适配配件查询

**接口地址**: `/api/v1/parts/match`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| car_id | string | ✅ | 车型ID |
| category | string | ❌ | 配件类别 |
| brand | string | ❌ | 品牌 |

#### 3.1.4 品牌件查询

**接口地址**: `/api/v1/parts/brand`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brand | string | ✅ | 品牌名称 |
| keyword | string | ❌ | 关键词搜索 |

#### 3.1.5 条码/二维码查询

**接口地址**: `/api/v1/barcode/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| barcode | string | ✅ | 条码内容 |

---

### 3.2 库存模块

#### 3.2.1 库存查询

**接口地址**: `/api/v1/stock/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouse_id | string | ❌ | 仓库ID |
| part_id | string | ❌ | 配件ID |
| sku | string | ❌ | SKU |

#### 3.2.2 库存预警

**接口地址**: `/api/v1/stock/alert`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouse_id | string | ✅ | 仓库ID |
| threshold | int | ❌ | 预警阈值 |

#### 3.2.3 库存流水

**接口地址**: `/api/v1/stock/log`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouse_id | string | ✅ | 仓库ID |
| start_date | string | ✅ | 开始日期 |
| end_date | string | ✅ | 结束日期 |
| type | string | ❌ | 流水类型(in/out) |

---

### 3.3 订单模块

#### 3.3.1 创建订单

**接口地址**: `/api/v1/order/create`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ✅ | 客户ID |
| items | array | ✅ | 订单明细 |
| warehouse_id | string | ✅ | 仓库ID |
| remark | string | ❌ | 备注 |

**items结构**:
```json
[
  {
    "part_id": "xxx",
    "quantity": 2,
    "price": 368.00
  }
]
```

#### 3.3.2 订单查询

**接口地址**: `/api/v1/order/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_no | string | ❌ | 订单号 |
| customer_id | string | ❌ | 客户ID |
| status | string | ❌ | 订单状态 |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |
| page | int | ❌ | 页码 |
| page_size | int | ❌ | 每页数量 |

#### 3.3.3 订单取消

**接口地址**: `/api/v1/order/cancel`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_no | string | ✅ | 订单号 |
| reason | string | ❌ | 取消原因 |

#### 3.3.4 订单发货

**接口地址**: `/api/v1/order/deliver`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_no | string | ✅ | 订单号 |
| express_company | string | ❌ | 物流公司 |
| express_no | string | ❌ | 物流单号 |

---

### 3.4 客户模块

#### 3.4.1 客户注册

**接口地址**: `/api/v1/customer/register`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mobile | string | ✅ | 手机号 |
| name | string | ✅ | 客户名称 |
| type | string | ✅ | 客户类型(个人/企业) |
| license_no | string | ❌ | 营业执照号 |

#### 3.4.2 客户查询

**接口地址**: `/api/v1/customer/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ❌ | 客户ID |
| mobile | string | ❌ | 手机号 |

#### 3.4.3 客户价格等级

**接口地址**: `/api/v1/customer/price-level`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ✅ | 客户ID |

---

### 3.5 财务模块

#### 3.5.1 应收款查询

**接口地址**: `/api/v1/finance/receivable`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ❌ | 客户ID |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |

#### 3.5.2 回款登记

**接口地址**: `/api/v1/finance/payment`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ✅ | 客户ID |
| amount | decimal | ✅ | 回款金额 |
| payment_method | string | ✅ | 支付方式 |
| bank_no | string | ❌ | 银行流水号 |

#### 3.5.3 对账单生成

**接口地址**: `/api/v1/finance/statement`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | string | ✅ | 客户ID |
| start_date | string | ✅ | 开始日期 |
| end_date | string | ✅ | 结束日期 |

---

### 3.6 供应商模块

#### 3.6.1 供应商查询

**接口地址**: `/api/v1/supplier/query`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| supplier_id | string | ❌ | 供应商ID |
| name | string | ❌ | 供应商名称 |

#### 3.6.2 采购订单

**接口地址**: `/api/v1/purchase/create`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| supplier_id | string | ✅ | 供应商ID |
| items | array | ✅ | 采购明细 |

---

### 3.7 报表模块

#### 3.7.1 销售报表

**接口地址**: `/api/v1/report/sales`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | ✅ | 开始日期 |
| end_date | string | ✅ | 结束日期 |
| group_by | string | ❌ | 分组维度(day/brand/category) |

#### 3.7.2 库存报表

**接口地址**: `/api/v1/report/stock`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouse_id | string | ✅ | 仓库ID |
| category | string | ❌ | 配件类别 |

#### 3.7.3 利润报表

**接口地址**: `/api/v1/report/profit`

**请求说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | ✅ | 开始日期 |
| end_date | string | ✅ | 结束日期 |

---

## 四、Webhook回调

### 4.1 回调配置

| 参数 | 说明 |
|------|------|
| 回调URL | 商户提供 |
| 验证方式 |签名验证 |
| 超时时间 | 30秒 |

### 4.2 回调事件

| 事件码 | 事件名称 | 说明 |
|--------|----------|------|
| ORDER_CREATED | 订单创建 | 新建订单 |
| ORDER_PAID | 订单支付 | 支付完成 |
| ORDER_DELIVERED | 订单发货 | 已发货 |
| ORDER_COMPLETED | 订单完成 | 已完成 |
| ORDER_CANCELLED | 订单取消 | 已取消 |
| STOCK_ALERT | 库存预警 | 库存不足 |
| PAYMENT_RECEIVED | 回款到账 | 回款登记 |

### 4.3 回调示例

```json
{
  "event": "ORDER_CREATED",
  "timestamp": "1701234567890",
  "data": {
    "order_no": "SO202601150001",
    "customer_id": "C001",
    "amount": 1256.00
  },
  "sign": "xxx"
}
```

---

## 五、错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 签名验证失败 |
| 1003 | 权限不足 |
| 1004 | 资源不存在 |
| 1005 | 业务数据异常 |
| 2001 | 库存不足 |
| 2002 | 客户不存在 |
| 2003 | 订单状态不允许操作 |
| 3001 | 账户余额不足 |
| 3002 | 超过信用额度 |

---

## 六、SDK下载

| 语言 | 下载地址 |
|------|----------|
| Java | https://sdk.qpyun.com/java.zip |
| Python | https://sdk.qpyun.com/python.zip |
| PHP | https://sdk.qpyun.com/php.zip |
| Node.js | https://sdk.qpyun.com/node.zip |

---

## 七、接入流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1.注册应用  │ ──▶ │  2.获取密钥  │ ──▶ │  3.签名调试 │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  6.正式上线  │ ◀── │  5.沙箱测试 │ ◀── │  4.接口开发 │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

**文档版本**: v1.0  
**最后更新**: 2026-03-15  
**技术支持**: support@qpyun.com

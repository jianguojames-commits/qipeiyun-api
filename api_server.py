#!/usr/bin/env python3
"""
汽配云助手 API 服务器

使用 FastAPI 构建的 RESTful API

启动命令:
    python api_server.py

访问地址:
    http://localhost:8000        - API根路径
    http://localhost:8000/docs   - Swagger API文档
    http://localhost:8000/redoc  - ReDoc API文档
"""

import sys
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from db_query import (
    query_parts,
    search_parts,
    get_part_by_id,
    get_brands,
    get_categories,
    get_vehicle_makes,
    get_price_range,
)
from src.models import DatabaseManager

# 创建FastAPI应用
app = FastAPI(
    title="汽配云助手 API",
    description="""
    汽车配件数据管理和库存查询系统

    ## 功能特性
    - 配件数据查询（支持多条件组合）
    - 全文搜索
    - 品牌/类别/车型筛选
    - 价格范围查询
    - 数据统计

    ## 认证方式
    当前版本无需认证，如需生产环境部署请联系管理员。
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 数据模型 ==========


class PartResponse(BaseModel):
    """配件响应模型"""

    part_id: str
    oe_number: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year_start: Optional[int] = None
    vehicle_year_end: Optional[int] = None
    position: Optional[str] = None
    specs: Optional[dict] = None
    uom: Optional[str] = None
    qty_per_unit: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    supplier: Optional[str] = None
    barcode: Optional[str] = None
    weight_kg: Optional[float] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PartsListResponse(BaseModel):
    """配件列表响应"""

    success: bool = True
    count: int
    total: int
    data: List[PartResponse]


class SearchResponse(BaseModel):
    """搜索响应"""

    success: bool = True
    keyword: str
    count: int
    data: List[PartResponse]


class ErrorResponse(BaseModel):
    """错误响应"""

    success: bool = False
    error: dict


class StatsResponse(BaseModel):
    """统计响应"""

    success: bool = True
    data: dict


# ========== 依赖项 ==========


def get_db():
    """获取数据库连接"""
    db_path = Path(__file__).parent / "data" / "qipeiyun.db"
    if not db_path.exists():
        raise HTTPException(
            status_code=404, detail="数据库文件不存在，请先运行数据迁移"
        )
    return DatabaseManager(str(db_path))


# ========== API 端点 ==========


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "汽配云助手 API",
        "version": "2.0.0",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "parts": "/api/parts",
            "search": "/api/parts/search",
            "brands": "/api/brands",
            "categories": "/api/categories",
            "stats": "/api/stats",
        },
    }


@app.get("/api/parts", response_model=PartsListResponse)
async def get_parts(
    brand: Optional[str] = Query(None, description="品牌名称"),
    category: Optional[str] = Query(None, description="配件类别"),
    vehicle_make: Optional[str] = Query(None, description="车辆品牌"),
    vehicle_model: Optional[str] = Query(None, description="车辆型号"),
    oe_number: Optional[str] = Query(None, description="OE号（精确匹配）"),
    supplier: Optional[str] = Query(None, description="供应商"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """
    查询配件列表

    支持多条件组合查询，所有参数都是可选的。

    **查询示例:**
    - `/api/parts?brand=Bosch` - 查询Bosch品牌
    - `/api/parts?category=Brake Pad&min_price=50&max_price=500` - 价格区间筛选
    - `/api/parts?vehicle_make=Toyota&vehicle_model=Camry` - 按车型查询
    """
    try:
        # 构建查询参数
        params = {
            "limit": limit + offset  # 获取更多数据以便分页
        }

        if brand:
            params["brand"] = brand
        if category:
            params["category"] = category
        if vehicle_make:
            params["vehicle_make"] = vehicle_make
        if vehicle_model:
            params["vehicle_model"] = vehicle_model
        if oe_number:
            params["oe_number"] = oe_number.upper()
        if supplier:
            params["supplier"] = supplier
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price

        # 执行查询
        results = query_parts(**params)

        # 应用分页
        total = len(results)
        paginated_results = results[offset : offset + limit]

        return PartsListResponse(
            count=len(paginated_results),
            total=total,
            data=[PartResponse(**part) for part in paginated_results],
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/parts/search", response_model=SearchResponse)
async def search_parts_endpoint(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
):
    """
    全文搜索配件

    在配件名称、描述、OE号、SKU中搜索关键词。

    **搜索示例:**
    - `/api/parts/search?keyword=刹车片`
    - `/api/parts/search?keyword=04465`
    """
    try:
        results = search_parts(keyword, limit=limit)

        return SearchResponse(
            keyword=keyword,
            count=len(results),
            data=[PartResponse(**part) for part in results],
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/parts/{part_id}", response_model=dict)
async def get_part(part_id: str):
    """根据ID获取配件详情"""
    try:
        part = get_part_by_id(part_id)
        if part is None:
            raise HTTPException(status_code=404, detail="配件不存在")

        return {"success": True, "data": part}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/brands", response_model=dict)
async def get_brands_endpoint():
    """获取所有品牌列表"""
    try:
        brands = get_brands()
        return {"success": True, "count": len(brands), "data": brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/categories", response_model=dict)
async def get_categories_endpoint():
    """获取所有配件类别"""
    try:
        categories = get_categories()
        return {"success": True, "count": len(categories), "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/vehicles", response_model=dict)
async def get_vehicles_endpoint():
    """获取所有车辆品牌列表"""
    try:
        vehicles = get_vehicle_makes()
        return {"success": True, "count": len(vehicles), "data": vehicles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats_endpoint():
    """获取数据库统计信息"""
    try:
        db_path = Path(__file__).parent / "data" / "qipeiyun.db"
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="数据库文件不存在")

        db = DatabaseManager(str(db_path))
        stats = db.get_stats()

        return StatsResponse(success=True, data=stats)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@app.get("/api/price-range", response_model=dict)
async def get_price_range_endpoint():
    """获取价格范围"""
    try:
        price_range = get_price_range()
        return {"success": True, "data": price_range}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# ========== 异常处理器 ==========


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": 500, "message": f"服务器内部错误: {str(exc)}"},
        },
    )


# ========== 主程序 ==========

if __name__ == "__main__":
    print("""
    🚗 汽配云助手 API 服务器
    
    📖 访问地址:
       - API:        http://localhost:8000
       - Swagger:    http://localhost:8000/docs
       - ReDoc:      http://localhost:8000/redoc
       - OpenAPI:    http://localhost:8000/openapi.json
    
    按 Ctrl+C 停止服务
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

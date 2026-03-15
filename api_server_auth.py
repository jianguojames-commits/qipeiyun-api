#!/usr/bin/env python3
"""
汽配云助手 API 服务器 - 带用户认证

基于 FastAPI + JWT认证

启动命令:
    python api_server_auth.py

首次启动会创建管理员账户:
    用户名: admin
    密码: admin123
"""

import sys
from pathlib import Path
from typing import Optional, List
from datetime import timedelta
from fastapi import FastAPI, Query, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 添加路径
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
from src.auth import AuthManager, User

# ========== 配置 ==========
SECRET_KEY = "qipeiyun-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# ========== FastAPI应用 ==========
app = FastAPI(
    title="汽配云助手 API",
    description="汽车配件数据管理和库存查询系统（带用户认证）",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全
security = HTTPBearer()

# 认证管理器
auth_manager = None


def get_auth_manager() -> AuthManager:
    """获取认证管理器"""
    global auth_manager
    if auth_manager is None:
        auth_manager = AuthManager()
        auth_manager.init_db()
    return auth_manager


# ========== 数据模型 ==========


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool


# ========== 辅助函数 ==========


def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    import jwt
    from datetime import datetime, timedelta

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """验证令牌"""
    import jwt
    from jwt.exceptions import InvalidTokenError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """获取当前用户"""
    token = credentials.credentials

    # 验证JWT令牌
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 获取用户
    auth = get_auth_manager()
    user = auth.get_user_by_id(payload.get("sub"))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


# ========== 认证API ==========


@app.on_event("startup")
async def startup_event():
    """启动时创建管理员账户"""
    global auth_manager
    auth_manager = AuthManager()
    auth_manager.init_db()
    auth_manager.create_admin_user()
    print("✅ 认证系统初始化完成")


@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """用户注册"""
    auth = get_auth_manager()

    try:
        user = auth.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """用户登录"""
    auth = get_auth_manager()

    try:
        user = auth.authenticate(credentials.username, credentials.password)

        # 生成令牌
        access_token = create_access_token({"sub": user.id, "role": user.role})

        return TokenResponse(access_token=access_token, user=user.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@app.post("/api/auth/refresh")
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """刷新令牌"""
    access_token = create_access_token(
        {"sub": current_user.id, "role": current_user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ========== 数据API（需要认证） ==========


@app.get("/api/parts")
async def get_parts(
    brand: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    vehicle_make: Optional[str] = Query(None),
    vehicle_model: Optional[str] = Query(None),
    oe_number: Optional[str] = Query(None),
    supplier: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
):
    """查询配件列表（需要认证）"""
    try:
        params = {"limit": limit + offset}

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

        results = query_parts(**params)
        total = len(results)

        return {
            "success": True,
            "count": len(results[offset : offset + limit]),
            "total": total,
            "data": results[offset : offset + limit],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/parts/{part_id}")
async def get_part(part_id: str, current_user: User = Depends(get_current_active_user)):
    """获取配件详情（需要认证）"""
    part = get_part_by_id(part_id)
    if not part:
        raise HTTPException(status_code=404, detail="配件不存在")

    return {"success": True, "data": part}


@app.get("/api/parts/search")
async def search_parts_endpoint(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
):
    """搜索配件（需要认证）"""
    results = search_parts(keyword, limit=limit)
    return {"success": True, "keyword": keyword, "count": len(results), "data": results}


# ========== 公开API（无需认证）==========


@app.get("/api/brands")
async def get_brands_public():
    """获取品牌列表（公开）"""
    return {"success": True, "data": get_brands()}


@app.get("/api/categories")
async def get_categories_public():
    """获取类别列表（公开）"""
    return {"success": True, "data": get_categories()}


@app.get("/api/stats")
async def get_stats_public():
    """获取统计信息（公开）"""
    db_path = Path(__file__).parent / "data" / "qipeiyun.db"
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="数据库不存在")

    db = DatabaseManager(str(db_path))
    stats = db.get_stats()
    return {"success": True, "data": stats}


# ========== 根路径 ==========


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "汽配云助手 API",
        "version": "2.1.0",
        "auth": "enabled",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "public": ["/api/brands", "/api/categories", "/api/stats"],
            "auth": ["/api/auth/register", "/api/auth/login", "/api/auth/me"],
            "protected": ["/api/parts", "/api/parts/search"],
        },
    }


# ========== 主程序 ==========

if __name__ == "__main__":
    print("""
    🚗 汽配云助手 API（带认证）
    
    📖 访问地址:
       - API:        http://localhost:8000
       - Swagger:    http://localhost:8000/docs
    
    🔐 默认管理员账户:
       - 用户名: admin
       - 密码:   admin123
    
    按 Ctrl+C 停止服务
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

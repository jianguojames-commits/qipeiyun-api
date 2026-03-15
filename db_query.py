#!/usr/bin/env python3
"""
库存查询API v2.0 - 基于SQLite数据库

相比CSV版本的优势:
1. 更快的查询速度（使用索引）
2. 支持复杂查询条件组合
3. 更好的数据完整性
4. 支持分页和限制

使用方法:
    from db_query import query_parts, get_part_by_id

    # 简单查询
    results = query_parts(brand="Bosch")

    # 复杂查询
    results = query_parts(
        brand="Bosch",
        category="Brake Pad",
        vehicle_make="Toyota",
        min_price=100,
        max_price=500,
        limit=10
    )
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import DatabaseManager, Part


@dataclass
class QueryOptions:
    """查询选项"""

    brand: Optional[str] = None
    category: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    oe_number: Optional[str] = None
    supplier: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 100
    offset: int = 0


def query_parts(db_path: str = None, **kwargs) -> List[Dict[str, Any]]:
    """
    查询配件库存（基于数据库）

    参数:
        db_path: 数据库路径，默认使用项目data目录下的qipeiyun.db
        brand: 品牌名称（支持模糊匹配）
        category: 配件类别（支持模糊匹配）
        vehicle_make: 车辆品牌（支持模糊匹配）
        vehicle_model: 车辆型号（支持模糊匹配）
        oe_number: OE号（精确匹配，自动转大写）
        supplier: 供应商（支持模糊匹配）
        min_price: 最低价格
        max_price: 最高价格
        limit: 最大返回数量（默认100）
        offset: 偏移量（用于分页）

    返回:
        List[Dict]: 配件信息字典列表

    示例:
        # 查询Bosch品牌的所有配件
        results = query_parts(brand="Bosch")

        # 查询价格在100-500之间的刹车片
        results = query_parts(
            category="Brake Pad",
            min_price=100,
            max_price=500
        )

        # 组合查询：Bosch品牌的Toyota适用配件
        results = query_parts(
            brand="Bosch",
            vehicle_make="Toyota",
            limit=10
        )
    """
    # 确定数据库路径
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    # 检查数据库是否存在
    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"数据库文件不存在: {db_path}\n请先运行: python migrate_to_sqlite.py"
        )

    # 执行查询
    db = DatabaseManager(str(db_path))
    parts = db.query_parts(**kwargs)

    # 转换为字典列表
    return [part.to_dict() for part in parts]


def get_part_by_id(part_id: str, db_path: str = None) -> Optional[Dict[str, Any]]:
    """
    根据part_id获取单个配件详情

    参数:
        part_id: 配件唯一标识符
        db_path: 数据库路径

    返回:
        Dict或None: 配件详细信息

    示例:
        part = get_part_by_id("ba0ed0e5df48a47b")
        if part:
            print(f"找到配件: {part['name']}")
    """
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    session = db.get_session()

    try:
        part = session.query(Part).filter(Part.part_id == part_id).first()
        return part.to_dict() if part else None
    finally:
        session.close()


def search_parts(
    keyword: str, db_path: str = None, limit: int = 20
) -> List[Dict[str, Any]]:
    """
    全文搜索配件（在名称、描述、OE号中搜索）

    参数:
        keyword: 搜索关键词
        db_path: 数据库路径
        limit: 最大返回数量

    返回:
        List[Dict]: 匹配的配件列表

    示例:
        # 搜索包含"刹车片"的配件
        results = search_parts("刹车片")

        # 搜索OE号
        results = search_parts("04465")
    """
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    session = db.get_session()

    try:
        from sqlalchemy import or_

        keyword_lower = f"%{keyword.lower()}%"
        parts = (
            session.query(Part)
            .filter(
                or_(
                    Part.name.ilike(keyword_lower),
                    Part.description.ilike(keyword_lower),
                    Part.oe_number.ilike(keyword_lower),
                    Part.sku.ilike(keyword_lower),
                )
            )
            .limit(limit)
            .all()
        )

        return [part.to_dict() for part in parts]
    finally:
        session.close()


def get_brands(db_path: str = None) -> List[str]:
    """获取所有品牌列表"""
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    session = db.get_session()

    try:
        brands = session.query(Part.brand).distinct().all()
        return [b[0] for b in brands if b[0]]
    finally:
        session.close()


def get_categories(db_path: str = None) -> List[str]:
    """获取所有类别列表"""
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    session = db.get_session()

    try:
        categories = session.query(Part.category).distinct().all()
        return [c[0] for c in categories if c[0]]
    finally:
        session.close()


def get_vehicle_makes(db_path: str = None) -> List[str]:
    """获取所有车辆品牌列表"""
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    session = db.get_session()

    try:
        makes = session.query(Part.vehicle_make).distinct().all()
        return [m[0] for m in makes if m[0]]
    finally:
        session.close()


def get_price_range(db_path: str = None) -> Dict[str, float]:
    """获取价格范围"""
    if db_path is None:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "qipeiyun.db"

    db = DatabaseManager(str(db_path))
    stats = db.get_stats()

    return stats["price_range"]


# 向后兼容：保持与旧版CSV API相同的函数签名
def query_inventory(
    csv_path: str = None,  # 保留参数以保持兼容，但不再使用
    oe_number: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    **kwargs,
) -> List[Dict[str, Any]]:
    """
    向后兼容的库存查询接口

    此函数兼容旧的CSV查询API，但实际使用SQLite数据库
    csv_path参数被保留以保持向后兼容，但会被忽略
    """
    print("⚠️ 提示: 正在使用数据库版本API（忽略csv_path参数）")

    return query_parts(
        oe_number=oe_number,
        brand=brand,
        category=category,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        **kwargs,
    )


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试数据库查询API...\n")

    try:
        # 测试1: 按品牌查询
        print("1️⃣ 查询 Bosch 品牌配件:")
        results = query_parts(brand="Bosch", limit=3)
        for r in results:
            print(f"   - {r['name']} (¥{r['price']})")

        # 测试2: 获取品牌列表
        print("\n2️⃣ 所有品牌:")
        brands = get_brands()
        print(f"   {', '.join(brands)}")

        # 测试3: 全文搜索
        print("\n3️⃣ 搜索 '刹车片':")
        results = search_parts("刹车片")
        for r in results:
            print(f"   - {r['name']}")

        print("\n✅ 所有测试通过!")

    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\n请先运行数据迁移:")
        print("   python migrate_to_sqlite.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()

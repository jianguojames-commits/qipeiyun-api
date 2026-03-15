"""
数据库模型定义 - 汽配云助手
使用SQLAlchemy ORM
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    DateTime,
    JSON,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class Part(Base):
    """配件主表"""

    __tablename__ = "parts"

    # 主键
    part_id = Column(String(16), primary_key=True)

    # 基础信息
    oe_number = Column(String(50), index=True)
    sku = Column(String(50), index=True)
    brand = Column(String(100), index=True)
    category = Column(String(100), index=True)
    name = Column(String(200))
    description = Column(String(500))

    # 车型适配
    vehicle_make = Column(String(100), index=True)
    vehicle_model = Column(String(100), index=True)
    vehicle_year_start = Column(Integer)
    vehicle_year_end = Column(Integer)
    position = Column(String(50))

    # 规格参数（存储为JSON）
    specs = Column(JSON)

    # 单位信息
    uom = Column(String(20))
    qty_per_unit = Column(Float)

    # 价格信息
    price = Column(Float)
    currency = Column(String(10))

    # 供应商信息
    supplier = Column(String(100), index=True)
    barcode = Column(String(50))

    # 物理属性
    weight_kg = Column(Float)
    length_mm = Column(Float)
    width_mm = Column(Float)
    height_mm = Column(Float)

    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 复合索引，优化常用查询
    __table_args__ = (
        Index("idx_brand_category", "brand", "category"),
        Index("idx_vehicle", "vehicle_make", "vehicle_model"),
        Index("idx_price", "price"),
    )

    def to_dict(self):
        """转换为字典格式"""
        return {
            "part_id": self.part_id,
            "oe_number": self.oe_number,
            "sku": self.sku,
            "brand": self.brand,
            "category": self.category,
            "name": self.name,
            "description": self.description,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_year_start": self.vehicle_year_start,
            "vehicle_year_end": self.vehicle_year_end,
            "position": self.position,
            "specs": self.specs,
            "uom": self.uom,
            "qty_per_unit": self.qty_per_unit,
            "price": self.price,
            "currency": self.currency,
            "supplier": self.supplier,
            "barcode": self.barcode,
            "weight_kg": self.weight_kg,
            "length_mm": self.length_mm,
            "width_mm": self.width_mm,
            "height_mm": self.height_mm,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Part(id={self.part_id}, brand={self.brand}, name={self.name})>"


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，默认为项目目录下的data/qipeiyun.db
        """
        if db_path is None:
            # 使用项目根目录的相对路径
            import os

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "data", "qipeiyun.db")

        self.db_path = db_path
        self.engine = None
        self.Session = None

    def init_db(self):
        """初始化数据库（创建表）"""
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        print(f"✅ 数据库初始化完成: {self.db_path}")
        return self

    def get_session(self):
        """获取数据库会话"""
        if self.Session is None:
            self.init_db()
        return self.Session()

    def import_from_csv(self, csv_path: str):
        """
        从CSV文件导入数据

        Args:
            csv_path: CSV文件路径
        """
        import csv
        from pathlib import Path

        session = self.get_session()
        count = 0

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 解析JSON specs
                    specs = {}
                    if row.get("specs"):
                        try:
                            specs = json.loads(row["specs"])
                        except json.JSONDecodeError:
                            specs = {}

                    # 解析年份
                    year_start = (
                        int(row["vehicle_year_start"])
                        if row.get("vehicle_year_start")
                        else None
                    )
                    year_end = (
                        int(row["vehicle_year_end"])
                        if row.get("vehicle_year_end")
                        else None
                    )

                    # 创建Part对象
                    part = Part(
                        part_id=row["part_id"],
                        oe_number=row.get("oe_number"),
                        sku=row.get("sku"),
                        brand=row.get("brand"),
                        category=row.get("category"),
                        name=row.get("name"),
                        description=row.get("description"),
                        vehicle_make=row.get("vehicle_make"),
                        vehicle_model=row.get("vehicle_model"),
                        vehicle_year_start=year_start,
                        vehicle_year_end=year_end,
                        position=row.get("position"),
                        specs=specs,
                        uom=row.get("uom"),
                        qty_per_unit=float(row["qty_per_unit"])
                        if row.get("qty_per_unit")
                        else None,
                        price=float(row["price"]) if row.get("price") else None,
                        currency=row.get("currency"),
                        supplier=row.get("supplier"),
                        barcode=row.get("barcode"),
                        weight_kg=float(row["weight_kg"])
                        if row.get("weight_kg")
                        else None,
                        length_mm=float(row["length_mm"])
                        if row.get("length_mm")
                        else None,
                        width_mm=float(row["width_mm"])
                        if row.get("width_mm")
                        else None,
                        height_mm=float(row["height_mm"])
                        if row.get("height_mm")
                        else None,
                    )
                    session.add(part)
                    count += 1

                    # 每100条提交一次，避免内存溢出
                    if count % 100 == 0:
                        session.commit()
                        print(f"  已导入 {count} 条记录...")

            session.commit()
            print(f"✅ 成功导入 {count} 条记录到数据库")

        except Exception as e:
            session.rollback()
            print(f"❌ 导入失败: {e}")
            raise
        finally:
            session.close()

    def query_parts(self, **filters) -> list:
        """
        查询配件

        Args:
            **filters: 查询条件
                - brand: 品牌
                - category: 类别
                - vehicle_make: 车型品牌
                - vehicle_model: 车型
                - oe_number: OE号（精确匹配）
                - min_price: 最低价格
                - max_price: 最高价格

        Returns:
            list: Part对象列表
        """
        session = self.get_session()

        try:
            query = session.query(Part)

            # 应用过滤器
            if filters.get("brand"):
                query = query.filter(Part.brand.ilike(f"%{filters['brand']}%"))

            if filters.get("category"):
                query = query.filter(Part.category.ilike(f"%{filters['category']}%"))

            if filters.get("vehicle_make"):
                query = query.filter(
                    Part.vehicle_make.ilike(f"%{filters['vehicle_make']}%")
                )

            if filters.get("vehicle_model"):
                query = query.filter(
                    Part.vehicle_model.ilike(f"%{filters['vehicle_model']}%")
                )

            if filters.get("oe_number"):
                query = query.filter(Part.oe_number == filters["oe_number"].upper())

            if filters.get("min_price") is not None:
                query = query.filter(Part.price >= filters["min_price"])

            if filters.get("max_price") is not None:
                query = query.filter(Part.price <= filters["max_price"])

            # 限制返回数量
            limit = filters.get("limit", 100)
            results = query.limit(limit).all()

            return results

        finally:
            session.close()

    def get_stats(self) -> dict:
        """获取数据库统计信息"""
        session = self.get_session()

        try:
            total = session.query(Part).count()
            brands = session.query(Part.brand).distinct().count()
            categories = session.query(Part.category).distinct().count()

            # 价格范围
            from sqlalchemy import func

            min_price = session.query(func.min(Part.price)).scalar()
            max_price = session.query(func.max(Part.price)).scalar()
            avg_price = session.query(func.avg(Part.price)).scalar()

            return {
                "total_parts": total,
                "unique_brands": brands,
                "unique_categories": categories,
                "price_range": {
                    "min": round(min_price, 2) if min_price else 0,
                    "max": round(max_price, 2) if max_price else 0,
                    "avg": round(avg_price, 2) if avg_price else 0,
                },
            }
        finally:
            session.close()


# 便捷函数
def init_database(db_path: str = None):
    """初始化数据库"""
    db = DatabaseManager(db_path)
    return db.init_db()


def import_csv_to_db(csv_path: str, db_path: str = None):
    """导入CSV到数据库"""
    db = init_database(db_path)
    db.import_from_csv(csv_path)
    return db

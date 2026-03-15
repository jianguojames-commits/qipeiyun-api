#!/usr/bin/env python3
"""
数据库查询示例 - 演示如何使用SQLite数据库查询配件

使用方法:
    python examples/db_query_examples.py
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import DatabaseManager


def print_results(results, title):
    """打印查询结果"""
    print(f"\n{'=' * 60}")
    print(f"📦 {title} (找到 {len(results)} 个结果)")
    print("=" * 60)

    for i, part in enumerate(results[:5], 1):  # 只显示前5个
        print(f"\n{i}. {part.name}")
        print(f"   品牌: {part.brand}")
        print(f"   类别: {part.category}")
        print(f"   OE号: {part.oe_number}")
        print(f"   价格: ¥{part.price}")
        if part.vehicle_make:
            print(f"   适用车型: {part.vehicle_make} {part.vehicle_model or ''}")

    if len(results) > 5:
        print(f"\n   ... 还有 {len(results) - 5} 个结果")


def main():
    # 初始化数据库连接
    db_path = Path(__file__).parent.parent / "data" / "qipeiyun.db"

    if not db_path.exists():
        print("❌ 数据库文件不存在，请先运行 migrate_to_sqlite.py 导入数据")
        print(f"   预期路径: {db_path}")
        sys.exit(1)

    print("🔗 连接到数据库...")
    db = DatabaseManager(str(db_path))

    # 示例1: 按品牌查询
    print("\n🔍 示例1: 查询所有 Bosch 品牌的配件")
    results = db.query_parts(brand="Bosch")
    print_results(results, "Bosch 品牌配件")

    # 示例2: 按类别查询
    print("\n🔍 示例2: 查询所有 Brake Pad（刹车片）")
    results = db.query_parts(category="Brake Pad")
    print_results(results, "刹车片")

    # 示例3: 按车型查询
    print("\n🔍 示例3: 查询适用于 Toyota 的配件")
    results = db.query_parts(vehicle_make="Toyota")
    print_results(results, "Toyota 适用配件")

    # 示例4: 按OE号精确查询
    print("\n🔍 示例4: 精确查询 OE号 '044650E010'")
    results = db.query_parts(oe_number="044650E010")
    print_results(results, "OE号查询结果")

    # 示例5: 价格范围查询
    print("\n🔍 示例5: 查询价格在 ¥50-150 之间的配件")
    results = db.query_parts(min_price=50, max_price=150)
    print_results(results, "价格区间筛选")

    # 示例6: 组合查询
    print("\n🔍 示例6: 组合查询 - Denso品牌 + Oil Filter类别")
    results = db.query_parts(brand="Denso", category="Oil Filter")
    print_results(results, "组合查询结果")

    # 显示统计信息
    print("\n" + "=" * 60)
    print("📊 数据库统计")
    print("=" * 60)
    stats = db.get_stats()
    print(f"   总配件数: {stats['total_parts']}")
    print(f"   品牌数量: {stats['unique_brands']}")
    print(f"   类别数量: {stats['unique_categories']}")
    print(
        f"   价格范围: ¥{stats['price_range']['min']} - ¥{stats['price_range']['max']}"
    )
    print(f"   平均价格: ¥{stats['price_range']['avg']}")

    print("\n✅ 查询示例完成!")


if __name__ == "__main__":
    main()

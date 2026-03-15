#!/usr/bin/env python3
"""
数据迁移脚本 - 将CSV数据导入SQLite数据库

使用方法:
    python migrate_to_sqlite.py --csv data/clean/clean_parts.csv --db data/qipeiyun.db
    python migrate_to_sqlite.py  # 使用默认路径
"""

import argparse
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import DatabaseManager


def main():
    parser = argparse.ArgumentParser(description="将CSV数据迁移到SQLite数据库")
    parser.add_argument(
        "--csv",
        default="data/clean/clean_parts.csv",
        help="CSV文件路径 (默认: data/clean/clean_parts.csv)",
    )
    parser.add_argument(
        "--db",
        default="data/qipeiyun.db",
        help="SQLite数据库路径 (默认: data/qipeiyun.db)",
    )
    parser.add_argument("--stats", action="store_true", help="导入后显示统计信息")

    args = parser.parse_args()

    # 检查CSV文件是否存在
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ 错误: CSV文件不存在: {csv_path}")
        sys.exit(1)

    # 确保数据库目录存在
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print("🚀 开始数据迁移...")
    print(f"   CSV源文件: {csv_path.absolute()}")
    print(f"   目标数据库: {db_path.absolute()}")
    print()

    try:
        # 初始化数据库
        db = DatabaseManager(str(db_path))
        db.init_db()

        # 导入数据
        db.import_from_csv(str(csv_path))

        # 显示统计信息
        if args.stats:
            print("\n📊 数据库统计信息:")
            stats = db.get_stats()
            print(f"   总配件数: {stats['total_parts']}")
            print(f"   品牌数量: {stats['unique_brands']}")
            print(f"   类别数量: {stats['unique_categories']}")
            print(
                f"   价格范围: ¥{stats['price_range']['min']} - ¥{stats['price_range']['max']}"
            )
            print(f"   平均价格: ¥{stats['price_range']['avg']}")

        print("\n✅ 数据迁移完成!")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
API测试脚本 - 测试所有API端点

使用方法:
    python test_api.py
"""

import sys
import json
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    print("\n1️⃣ 测试根路径...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ API名称: {data['name']}")
    print(f"   ✅ 版本: {data['version']}")


def test_get_parts():
    """测试配件列表查询"""
    print("\n2️⃣ 测试配件列表查询...")

    # 测试无参数查询
    response = client.get("/api/parts")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ 全部配件: {data['count']} 条")

    # 测试品牌筛选
    response = client.get("/api/parts?brand=Bosch")
    data = response.json()
    print(f"   ✅ Bosch品牌: {data['count']} 条")

    # 测试价格区间
    response = client.get("/api/parts?min_price=50&max_price=150")
    data = response.json()
    print(f"   ✅ 价格50-150: {data['count']} 条")


def test_get_part_by_id():
    """测试按ID查询配件"""
    print("\n3️⃣ 测试按ID查询配件...")

    # 先获取一个配件ID
    response = client.get("/api/parts?limit=1")
    data = response.json()
    if data["data"]:
        part_id = data["data"][0]["part_id"]
        response = client.get(f"/api/parts/{part_id}")
        assert response.status_code == 200
        part = response.json()["data"]
        print(f"   ✅ 找到配件: {part['name']}")
    else:
        print("   ⚠️ 没有配件数据")


def test_search():
    """测试全文搜索"""
    print("\n4️⃣ 测试全文搜索...")

    response = client.get("/api/parts/search?keyword=刹车片")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ 搜索'刹车片': {data['count']} 条结果")


def test_brands():
    """测试获取品牌列表"""
    print("\n5️⃣ 测试获取品牌列表...")

    response = client.get("/api/brands")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ 品牌列表: {', '.join(data['data'])}")


def test_categories():
    """测试获取类别列表"""
    print("\n6️⃣ 测试获取类别列表...")

    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ 类别列表: {', '.join(data['data'])}")


def test_vehicles():
    """测试获取车辆品牌列表"""
    print("\n7️⃣ 测试获取车辆品牌...")

    response = client.get("/api/vehicles")
    assert response.status_code == 200
    data = response.json()
    print(f"   ✅ 车辆品牌: {', '.join(data['data'])}")


def test_stats():
    """测试统计接口"""
    print("\n8️⃣ 测试统计接口...")

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()["data"]
    print(f"   ✅ 总配件数: {data['total_parts']}")
    print(f"   ✅ 品牌数: {data['unique_brands']}")
    print(f"   ✅ 类别数: {data['unique_categories']}")


def test_price_range():
    """测试价格范围"""
    print("\n9️⃣ 测试价格范围...")

    response = client.get("/api/price-range")
    assert response.status_code == 200
    data = response.json()["data"]
    print(f"   ✅ 价格范围: ¥{data['min']} - ¥{data['max']}")
    print(f"   ✅ 平均价格: ¥{data['avg']}")


def main():
    print("""
    🧪 汽配云助手 API 测试
    =====================
    """)

    try:
        test_root()
        test_get_parts()
        test_get_part_by_id()
        test_search()
        test_brands()
        test_categories()
        test_vehicles()
        test_stats()
        test_price_range()

        print("\n" + "=" * 50)
        print("✅ 所有测试通过!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

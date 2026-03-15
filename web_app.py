#!/usr/bin/env python3
"""
汽配云助手 - Web管理界面

使用 Streamlit 构建

启动命令:
    streamlit run web_app.py
    或
    python web_app.py
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional, List
import pandas as pd

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# 导入数据库查询模块
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


# ========== 页面配置 ==========
st.set_page_config(
    page_title="汽配云助手",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ========== CSS样式 ==========
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        padding: 10px;
        border-bottom: 2px solid #3498db;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .part-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
    }
    .price-tag {
        background: #27ae60;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ========== 辅助函数 ==========
@st.cache_data(ttl=300)
def load_stats():
    """加载统计信息"""
    try:
        db_path = Path(__file__).parent / "data" / "qipeiyun.db"
        if db_path.exists():
            db = DatabaseManager(str(db_path))
            return db.get_stats()
        return None
    except Exception as e:
        st.error(f"加载统计失败: {e}")
        return None


@st.cache_data(ttl=300)
def load_brands():
    """加载品牌列表"""
    try:
        return get_brands()
    except:
        return []


@st.cache_data(ttl=300)
def load_categories():
    """加载类别列表"""
    try:
        return get_categories()
    except:
        return []


@st.cache_data(ttl=60)
def search_parts_data(keyword, limit=50):
    """搜索配件"""
    try:
        return search_parts(keyword, limit=limit)
    except:
        return []


@st.cache_data(ttl=60)
def query_parts_data(
    brand=None,
    category=None,
    vehicle_make=None,
    min_price=None,
    max_price=None,
    limit=100,
):
    """查询配件"""
    try:
        params = {"limit": limit}
        if brand:
            params["brand"] = brand
        if category:
            params["category"] = category
        if vehicle_make:
            params["vehicle_make"] = vehicle_make
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        return query_parts(**params)
    except Exception as e:
        st.error(f"查询失败: {e}")
        return []


# ========== 页面组件 ==========


def show_header():
    """显示页头"""
    st.markdown(
        '<p class="main-header">🚗 汽配云助手 - 数据管理平台</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")


def show_stats():
    """显示统计卡片"""
    stats = load_stats()

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📦 总配件数", stats["total_parts"])
        with col2:
            st.metric("🏷️ 品牌数", stats["unique_brands"])
        with col3:
            st.metric("📂 类别数", stats["unique_categories"])
        with col4:
            price_range = stats["price_range"]
            st.metric(
                "💰 价格区间", f"¥{price_range['min']:.0f}-{price_range['max']:.0f}"
            )

        st.markdown("---")


def show_search():
    """显示搜索功能"""
    st.markdown('<p class="sub-header">🔍 快速搜索</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        keyword = st.text_input(
            "输入关键词搜索（名称、OE号、描述）",
            placeholder="例如: 刹车片、Bosch、04465...",
        )

    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("🔍 搜索", type="primary")

    if search_btn and keyword:
        results = search_parts_data(keyword)

        if results:
            st.success(f"找到 {len(results)} 个结果")

            # 转换为DataFrame显示
            df = pd.DataFrame(results)
            display_cols = [
                "brand",
                "name",
                "category",
                "price",
                "vehicle_make",
                "oe_number",
            ]
            available_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available_cols], use_container_width=True)

            # 详细列表
            st.markdown("### 详细结果")
            for part in results[:10]:
                with st.container():
                    st.markdown(
                        f"""
                    <div class="part-card">
                        <b>{part["name"]}</b> 
                        <span class="price-tag">¥{part["price"]}</span>
                        <br>
                        品牌: {part.get("brand", "-")} | 
                        类别: {part.get("category", "-")} | 
                        OE号: {part.get("oe_number", "-")}
                        <br>
                        适用: {part.get("vehicle_make", "")} {part.get("vehicle_model", "")}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("未找到匹配结果")


def show_filter():
    """显示筛选功能"""
    st.markdown('<p class="sub-header">📋 高级筛选</p>', unsafe_allow_html=True)

    # 加载选项
    brands = load_brands()
    categories = load_categories()
    vehicles = get_vehicle_makes()
    price_range = get_price_range()

    # 筛选条件
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_brand = st.selectbox("品牌", ["全部"] + brands)

    with col2:
        selected_category = st.selectbox("类别", ["全部"] + categories)

    with col3:
        selected_vehicle = st.selectbox("适用车型", ["全部"] + vehicles)

    # 价格区间
    col4, col5 = st.columns(2)

    with col4:
        min_price = st.number_input(
            "最低价格", min_value=0, value=int(price_range["min"])
        )

    with col5:
        max_price = st.number_input(
            "最高价格", min_value=0, value=int(price_range["max"])
        )

    # 查询按钮
    if st.button("🔎 查询", type="primary", use_container_width=True):
        # 构建查询参数
        params = {"limit": 100}
        if selected_brand != "全部":
            params["brand"] = selected_brand
        if selected_category != "全部":
            params["category"] = selected_category
        if selected_vehicle != "全部":
            params["vehicle_make"] = selected_vehicle
        if min_price > 0:
            params["min_price"] = min_price
        if max_price > 0:
            params["max_price"] = max_price

        results = query_parts(**params)

        if results:
            st.success(f"找到 {len(results)} 个配件")

            # 显示表格
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # 导出CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 导出CSV",
                data=csv,
                file_name="parts_export.csv",
                mime="text/csv",
            )
        else:
            st.warning("未找到匹配结果")


def show_vehicle_makes():
    """加载车辆品牌列表"""
    try:
        return get_vehicle_makes()
    except:
        return []


def show_part_detail():
    """显示配件详情"""
    st.markdown('<p class="sub-header">📝 配件详情查询</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        part_id = st.text_input(
            "输入配件ID查询详情", placeholder="例如: ba0ed0e5df48a47b"
        )

    with col2:
        st.write("")
        st.write("")
        query_btn = st.button("查询详情")

    if query_btn and part_id:
        part = get_part_by_id(part_id)

        if part:
            # 显示详情
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 基本信息")
                st.write(f"**名称**: {part['name']}")
                st.write(f"**品牌**: {part.get('brand', '-')}")
                st.write(f"**类别**: {part.get('category', '-')}")
                st.write(f"**OE号**: {part.get('oe_number', '-')}")
                st.write(f"**SKU**: {part.get('sku', '-')}")
                st.write(f"**描述**: {part.get('description', '-')}")

            with col2:
                st.markdown("### 价格信息")
                st.markdown(
                    f"<h2 style='color: #27ae60;'>¥{part['price']}</h2>",
                    unsafe_allow_html=True,
                )
                st.write(f"货币: {part.get('currency', 'CNY')}")
                st.write(f"单位: {part.get('uom', '-')}")
                st.write(f"供应商: {part.get('supplier', '-')}")

            st.markdown("### 适用车型")
            st.write(f"品牌: {part.get('vehicle_make', '-')}")
            st.write(f"型号: {part.get('vehicle_model', '-')}")
            st.write(
                f"年份: {part.get('vehicle_year_start', '-')} - {part.get('vehicle_year_end', '-')}"
            )

            if part.get("specs"):
                st.markdown("### 规格参数")
                st.json(part["specs"])
        else:
            st.error("未找到该配件")


def show_sidebar():
    """显示侧边栏"""
    st.sidebar.title("🚗 汽配云助手")
    st.sidebar.markdown("---")

    # 菜单
    menu = st.sidebar.radio("导航菜单", ["🏠 首页", "🔍 搜索", "📋 筛选", "📝 详情"])

    st.sidebar.markdown("---")

    # 快捷链接
    st.sidebar.markdown("### 🔗 快捷链接")
    st.sidebar.markdown("[📊 API文档](./docs/api-docs.md)")
    st.sidebar.markdown("[🔧 API服务](./api_server.py)")

    st.sidebar.markdown("---")

    # 关于
    st.sidebar.markdown("### ℹ️ 关于")
    st.sidebar.info("汽配云助手 v2.0.0\n\n基于 Streamlit 构建的数据管理平台")

    return menu


# ========== 主函数 ==========
def main():
    """主函数"""
    # 显示侧边栏并获取菜单选择
    menu = show_sidebar()

    # 根据菜单显示不同页面
    if menu == "🏠 首页":
        show_header()
        show_stats()

        # 最近数据预览
        st.markdown("### 📦 最近配件")
        results = query_parts_data(limit=5)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

    elif menu == "🔍 搜索":
        show_header()
        show_search()

    elif menu == "📋 筛选":
        show_header()
        show_filter()

    elif menu == "📝 详情":
        show_header()
        show_part_detail()


if __name__ == "__main__":
    # 检查数据库
    db_path = Path(__file__).parent / "data" / "qipeiyun.db"
    if not db_path.exists():
        st.error("数据库文件不存在！请先运行数据迁移:")
        st.code("python migrate_to_sqlite.py")
        st.stop()

    main()

#!/usr/bin/env python3
"""
汽配云助手 - Web管理界面（Flask版本）

使用 Flask + Bootstrap 构建的轻量级Web界面

启动命令:
    python web_app_flask.py

访问地址: http://localhost:5000
"""

from flask import (
    Flask,
    render_template_string,
    request,
    jsonify,
    send_from_directory,
    Response,
)
import sys
import csv
import io
from pathlib import Path
from typing import Optional, List

# 尝试导入pandas，如果失败则使用内置csv
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

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

app = Flask(__name__)

# ========== HTML模板 ==========
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚗 汽配云助手 - 数据管理平台</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
        }
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .part-card {
            background: white;
            border-left: 4px solid var(--primary-color);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .part-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .price-tag {
            background: #27ae60;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .nav-pills .nav-link.active {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        .table-responsive {
            border-radius: 10px;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-car-front-fill"></i> 汽配云助手
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="nav nav-pills ms-auto">
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'home' else '' }}" href="/">🏠 首页</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'search' else '' }}" href="/search">🔍 搜索</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'filter' else '' }}" href="/filter">📋 筛选</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'detail' else '' }}" href="/detail">📝 详情</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <footer class="text-center py-4 mt-5 text-muted">
        <small>汽配云助手 v2.0.0 | 基于 Flask + Bootstrap 构建</small>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

HOME_TEMPLATE = """
{% extends "base" %}
{% block content %}
<!-- 统计卡片 -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_parts }}</div>
            <div>📦 总配件数</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-number">{{ stats.unique_brands }}</div>
            <div>🏷️ 品牌数</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-number">{{ stats.unique_categories }}</div>
            <div>📂 类别数</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <div class="stat-number">¥{{ stats.price_range.avg }}</div>
            <div>💰 平均价格</div>
        </div>
    </div>
</div>

<!-- 最近配件 -->
<div class="card">
    <div class="card-body">
        <h5 class="card-title"><i class="bi bi-clock-history"></i> 最近配件</h5>
        {% if parts %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>品牌</th>
                        <th>名称</th>
                        <th>类别</th>
                        <th>价格</th>
                        <th>OE号</th>
                        <th>适用车型</th>
                    </tr>
                </thead>
                <tbody>
                    {% for part in parts %}
                    <tr>
                        <td><span class="badge bg-primary">{{ part.brand }}</span></td>
                        <td>{{ part.name }}</td>
                        <td>{{ part.category }}</td>
                        <td><span class="price-tag">¥{{ part.price }}</span></td>
                        <td><code>{{ part.oe_number }}</code></td>
                        <td>{{ part.vehicle_make }} {{ part.vehicle_model }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-muted">暂无数据</p>
        {% endif %}
    </div>
</div>
{% endblock %}
"""

SEARCH_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title"><i class="bi bi-search"></i> 搜索配件</h5>
        <form method="get" action="/api/search">
            <div class="row g-3">
                <div class="col-md-10">
                    <input type="text" class="form-control" name="keyword" placeholder="输入关键词搜索（名称、OE号、描述）" value="{{ keyword or '' }}">
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">🔍 搜索</button>
                </div>
            </div>
        </form>
    </div>
</div>

{% if results %}
<div class="card mt-4">
    <div class="card-body">
        <h5 class="card-title">搜索结果 ({{ results|length }} 个)</h5>
        {% for part in results %}
        <div class="part-card">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">{{ part.name }}</h6>
                    <small class="text-muted">
                        品牌: {{ part.brand }} | 
                        类别: {{ part.category }} | 
                        OE号: <code>{{ part.oe_number }}</code>
                        <br>
                        适用: {{ part.vehicle_make }} {{ part.vehicle_model }}
                    </small>
                </div>
                <span class="price-tag">¥{{ part.price }}</span>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endif %}
{% endblock %}
"""

FILTER_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title"><i class="bi bi-funnel"></i> 高级筛选</h5>
        <form method="get" action="/api/filter">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">品牌</label>
                    <select class="form-select" name="brand">
                        <option value="">全部</option>
                        {% for brand in brands %}
                        <option value="{{ brand }}" {{ 'selected' if selected_brand == brand else '' }}>{{ brand }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">类别</label>
                    <select class="form-select" name="category">
                        <option value="">全部</option>
                        {% for cat in categories %}
                        <option value="{{ cat }}" {{ 'selected' if selected_category == cat else '' }}>{{ cat }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">适用车型</label>
                    <select class="form-select" name="vehicle_make">
                        <option value="">全部</option>
                        {% for v in vehicles %}
                        <option value="{{ v }}" {{ 'selected' if selected_vehicle == v else '' }}>{{ v }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="row g-3 mt-2">
                <div class="col-md-4">
                    <label class="form-label">最低价格</label>
                    <input type="number" class="form-control" name="min_price" value="{{ min_price or '' }}" placeholder="0">
                </div>
                <div class="col-md-4">
                    <label class="form-label">最高价格</label>
                    <input type="number" class="form-control" name="max_price" value="{{ max_price or '' }}" placeholder="1000">
                </div>
                <div class="col-md-4 d-flex align-items-end">
                    <button type="submit" class="btn btn-primary w-100">🔎 查询</button>
                </div>
            </div>
        </form>
    </div>
</div>

{% if results %}
<div class="card mt-4">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="card-title mb-0">查询结果 ({{ results|length }} 个)</h5>
            <a href="/api/export?{{ export_params }}" class="btn btn-success btn-sm">📥 导出CSV</a>
        </div>
        <div class="table-responsive">
            <table class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>品牌</th>
                        <th>名称</th>
                        <th>类别</th>
                        <th>价格</th>
                        <th>OE号</th>
                    </tr>
                </thead>
                <tbody>
                    {% for part in results %}
                    <tr>
                        <td>{{ part.brand }}</td>
                        <td>{{ part.name }}</td>
                        <td>{{ part.category }}</td>
                        <td>¥{{ part.price }}</td>
                        <td><code>{{ part.oe_number }}</code></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
"""

DETAIL_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="card">
    <div class="card-body">
        <h5 class="card-title"><i class="bi bi-info-circle"></i> 配件详情查询</h5>
        <form method="get" action="/api/detail">
            <div class="row g-3">
                <div class="col-md-10">
                    <input type="text" class="form-control" name="part_id" placeholder="输入配件ID" value="{{ part_id or '' }}">
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">查询</button>
                </div>
            </div>
            <small class="text-muted">例如: ba0ed0e5df48a47b</small>
        </form>
    </div>
</div>

{% if part %}
<div class="card mt-4">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <h5>基本信息</h5>
                <table class="table table-borderless">
                    <tr><td><strong>名称:</strong></td><td>{{ part.name }}</td></tr>
                    <tr><td><strong>品牌:</strong></td><td>{{ part.brand }}</td></tr>
                    <tr><td><strong>类别:</strong></td><td>{{ part.category }}</td></tr>
                    <tr><td><strong>OE号:</strong></td><td><code>{{ part.oe_number }}</code></td></tr>
                    <tr><td><strong>SKU:</strong></td><td>{{ part.sku }}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h5>价格信息</h5>
                <table class="table table-borderless">
                    <tr><td><strong>价格:</strong></td><td><span class="h3 text-success">¥{{ part.price }}</span></td></tr>
                    <tr><td><strong>货币:</strong></td><td>{{ part.currency }}</td></tr>
                    <tr><td><strong>单位:</strong></td><td>{{ part.uom }}</td></tr>
                    <tr><td><strong>供应商:</strong></td><td>{{ part.supplier }}</td></tr>
                </table>
            </div>
        </div>
        <hr>
        <div class="row">
            <div class="col-md-6">
                <h5>适用车型</h5>
                <p>{{ part.vehicle_make }} {{ part.vehicle_model }} ({{ part.vehicle_year_start }} - {{ part.vehicle_year_end }})</p>
            </div>
            <div class="col-md-6">
                <h5>规格参数</h5>
                <pre>{{ part.specs }}</pre>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}
"""


# ========== 路由 ==========


@app.route("/")
def home():
    """首页"""
    try:
        db_path = Path(__file__).parent / "data" / "qipeiyun.db"
        if not db_path.exists():
            return "数据库文件不存在，请先运行数据迁移", 500

        from src.models import DatabaseManager

        db = DatabaseManager(str(db_path))
        stats = db.get_stats()
        parts = query_parts(limit=10)

        return render_template_string(
            BASE_TEMPLATE + HOME_TEMPLATE, active_page="home", stats=stats, parts=parts
        )
    except Exception as e:
        return f"错误: {e}", 500


@app.route("/search")
def search_page():
    """搜索页面"""
    keyword = request.args.get("keyword", "")
    results = search_parts(keyword) if keyword else []

    return render_template_string(
        BASE_TEMPLATE + SEARCH_TEMPLATE,
        active_page="search",
        keyword=keyword,
        results=results,
    )


@app.route("/filter")
def filter_page():
    """筛选页面"""
    selected_brand = request.args.get("brand", "")
    selected_category = request.args.get("category", "")
    selected_vehicle = request.args.get("vehicle_make", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")

    # 构建查询
    params = {"limit": 100}
    export_params = []

    if selected_brand:
        params["brand"] = selected_brand
        export_params.append(f"brand={selected_brand}")
    if selected_category:
        params["category"] = selected_category
        export_params.append(f"category={selected_category}")
    if selected_vehicle:
        params["vehicle_make"] = selected_vehicle
        export_params.append(f"vehicle_make={selected_vehicle}")
    if min_price:
        params["min_price"] = float(min_price)
        export_params.append(f"min_price={min_price}")
    if max_price:
        params["max_price"] = float(max_price)
        export_params.append(f"max_price={max_price}")

    results = query_parts(**params) if params else []

    return render_template_string(
        BASE_TEMPLATE + FILTER_TEMPLATE,
        active_page="filter",
        brands=get_brands(),
        categories=get_categories(),
        vehicles=get_vehicle_makes(),
        selected_brand=selected_brand,
        selected_category=selected_category,
        selected_vehicle=selected_vehicle,
        min_price=min_price,
        max_price=max_price,
        results=results,
        export_params="&".join(export_params),
    )


@app.route("/detail")
def detail_page():
    """详情页面"""
    part_id = request.args.get("part_id", "")
    part = get_part_by_id(part_id) if part_id else None

    return render_template_string(
        BASE_TEMPLATE + DETAIL_TEMPLATE,
        active_page="detail",
        part_id=part_id,
        part=part,
    )


# ========== API 路由 ==========


@app.route("/api/search")
def api_search():
    """搜索API"""
    keyword = request.args.get("keyword", "")
    results = search_parts(keyword)
    return jsonify({"success": True, "count": len(results), "data": results})


@app.route("/api/filter")
def api_filter():
    """筛选API"""
    params = dict(request.args)
    if "limit" not in params:
        params["limit"] = 100
    results = query_parts(**params)
    return jsonify({"success": True, "count": len(results), "data": results})


@app.route("/api/detail")
def api_detail():
    """详情API"""
    part_id = request.args.get("part_id")
    if not part_id:
        return jsonify({"success": False, "error": "缺少part_id参数"})

    part = get_part_by_id(part_id)
    if not part:
        return jsonify({"success": False, "error": "配件不存在"})

    return jsonify({"success": True, "data": part})


@app.route("/api/export")
def api_export():
    """导出CSV"""
    import csv as csv_module
    import io as io_module

    params = dict(request.args)
    results = query_parts(**params)

    if not results:
        return "无数据可导出", 400

    # 使用pandas或内置csv
    if HAS_PANDAS:
        df = pd.DataFrame(results)
        csv_output = df.to_csv(index=False)
    else:
        # 使用内置csv模块
        output = io_module.StringIO()
        writer = csv_module.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        csv_output = output.getvalue()

    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=parts_export.csv"},
    )


@app.route("/api/stats")
def api_stats():
    """统计API"""
    db_path = Path(__file__).parent / "data" / "qipeiyun.db"
    from src.models import DatabaseManager

    db = DatabaseManager(str(db_path))
    stats = db.get_stats()
    return jsonify({"success": True, "data": stats})


# ========== 主程序 ==========

if __name__ == "__main__":
    print("""
    🚗 汽配云助手 Web界面
    
    📖 访问地址: http://localhost:5000
    
    页面:
       - /         首页（统计和最近配件）
       - /search   搜索页面
       - /filter   筛选页面
       - /detail   详情查询页面
    
    API:
       - /api/stats    统计信息
       - /api/search   搜索
       - /api/filter   筛选
       - /api/export   导出CSV
    
    按 Ctrl+C 停止服务
    """)

    app.run(host="0.0.0.0", port=5000, debug=True)

#!/usr/bin/env python3
"""
汽配云助手 - 数据可视化页面

使用 Flask + ECharts 构建

启动命令:
    python web_app_viz.py

访问地址: http://localhost:5001
"""

from flask import Flask, render_template_string, request, jsonify
import sys
from pathlib import Path
from collections import Counter

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from db_query import (
    query_parts,
    get_brands,
    get_categories,
    get_vehicle_makes,
    get_price_range,
)
from src.models import DatabaseManager

app = Flask(__name__)

# ========== HTML模板 ==========
VIZ_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚗 汽配云助手 - 数据可视化</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
        }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .navbar {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .card-header {
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            border-radius: 15px 15px 0 0 !important;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .chart-container {
            height: 350px;
            width: 100%;
        }
        .table {
            color: #fff;
        }
        .table-striped > tbody > tr:nth-of-type(odd) {
            --bs-table-accent-bg: rgba(255,255,255,0.05);
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
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/"><i class="bi bi-house"></i> 首页</a>
                <a class="nav-link" href="/search"><i class="bi bi-search"></i> 搜索</a>
                <a class="nav-link" href="/filter"><i class="bi bi-funnel"></i> 筛选</a>
                <a class="nav-link active" href="/viz"><i class="bi bi-bar-chart"></i> 可视化</a>
            </div>
        </div>
    </nav>

    <div class="container">
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
                    <div class="stat-number">¥{{ stats.price_range.avg|int }}</div>
                    <div>💰 平均价格</div>
                </div>
            </div>
        </div>

        <!-- 图表行1 -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-pie-chart"></i> 品牌分布</h5>
                    </div>
                    <div class="card-body">
                        <div id="brandChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-pie-chart-fill"></i> 类别分布</h5>
                    </div>
                    <div class="card-body">
                        <div id="categoryChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 图表行2 -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-bar-chart"></i> 价格分布</h5>
                    </div>
                    <div class="card-body">
                        <div id="priceChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-car"></i> 适用车型TOP10</h5>
                    </div>
                    <div class="card-body">
                        <div id="vehicleChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 数据表格 -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-table"></i> 配件列表</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>品牌</th>
                                        <th>名称</th>
                                        <th>类别</th>
                                        <th>价格</th>
                                        <th>适用车型</th>
                                        <th>OE号</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for part in parts[:20] %}
                                    <tr>
                                        <td><span class="badge bg-primary">{{ part.brand }}</span></td>
                                        <td>{{ part.name }}</td>
                                        <td>{{ part.category }}</td>
                                        <td><span class="badge bg-success">¥{{ part.price }}</span></td>
                                        <td>{{ part.vehicle_make }} {{ part.vehicle_model }}</td>
                                        <td><code>{{ part.oe_number }}</code></td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 品牌分布饼图
        var brandChart = echarts.init(document.getElementById('brandChart'));
        var brandData = {{ brand_distribution | tojson }};
        brandChart.setOption({
            tooltip: { trigger: 'item' },
            legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#fff' } },
            series: [{
                name: '品牌',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: { borderRadius: 10, borderColor: '#1a1a2e', borderWidth: 2 },
                label: { show: false },
                emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
                data: brandData
            }]
        });

        // 类别分布饼图
        var categoryChart = echarts.init(document.getElementById('categoryChart'));
        var categoryData = {{ category_distribution | tojson }};
        categoryChart.setOption({
            tooltip: { trigger: 'item' },
            legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#fff' } },
            series: [{
                name: '类别',
                type: 'pie',
                radius: ['40%', '70%'],
                itemStyle: { borderRadius: 10, borderColor: '#1a1a2e', borderWidth: 2 },
                data: categoryData
            }]
        });

        // 价格分布柱状图
        var priceChart = echarts.init(document.getElementById('priceChart'));
        priceChart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { 
                type: 'category', 
                data: {{ price_ranges | tojson }},
                axisLabel: { color: '#fff' }
            },
            yAxis: { type: 'value', axisLabel: { color: '#fff' } },
            series: [{
                data: {{ price_counts | tojson }},
                type: 'bar',
                itemStyle: { color: '#5470c6' },
                showBackground: true,
                backgroundStyle: { color: 'rgba(180, 180, 180, 0.2)' }
            }]
        });

        // 车型分布横向柱状图
        var vehicleChart = echarts.init(document.getElementById('vehicleChart'));
        vehicleChart.setOption({
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'value', axisLabel: { color: '#fff' } },
            yAxis: { 
                type: 'category', 
                data: {{ vehicle_names | tojson | reverse }},
                axisLabel: { color: '#fff' }
            },
            series: [{
                data: {{ vehicle_counts | tojson | reverse }},
                type: 'bar',
                itemStyle: { color: '#91cc75' }
            }]
        });

        // 响应式调整
        window.addEventListener('resize', function() {
            brandChart.resize();
            categoryChart.resize();
            priceChart.resize();
            vehicleChart.resize();
        });
    </script>
</body>
</html>
"""


def get_data_for_viz():
    """获取可视化数据"""
    # 获取所有配件
    parts = query_parts(limit=1000)

    # 统计
    stats = {
        "total_parts": len(parts),
        "unique_brands": len(set(p["brand"] for p in parts if p.get("brand"))),
        "unique_categories": len(
            set(p["category"] for p in parts if p.get("category"))
        ),
    }

    # 价格统计
    prices = [p["price"] for p in parts if p.get("price")]
    if prices:
        stats["price_range"] = {
            "min": min(prices),
            "max": max(prices),
            "avg": sum(prices) / len(prices),
        }
    else:
        stats["price_range"] = {"min": 0, "max": 0, "avg": 0}

    # 品牌分布
    brand_counts = Counter(p["brand"] for p in parts if p.get("brand"))
    brand_distribution = [
        {"value": v, "name": k}
        for k, v in sorted(brand_counts.items(), key=lambda x: -x[1])
    ]

    # 类别分布
    category_counts = Counter(p["category"] for p in parts if p.get("category"))
    category_distribution = [
        {"value": v, "name": k}
        for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
    ]

    # 价格分布（区间）
    price_ranges = ["0-100", "100-200", "200-300", "300-500", "500+"]
    price_counts = [0, 0, 0, 0, 0]
    for price in prices:
        if price < 100:
            price_counts[0] += 1
        elif price < 200:
            price_counts[1] += 1
        elif price < 300:
            price_counts[2] += 1
        elif price < 500:
            price_counts[3] += 1
        else:
            price_counts[4] += 1

    # 车型分布
    vehicle_counts = Counter(
        f"{p.get('vehicle_make', '')} {p.get('vehicle_model', '')}".strip()
        for p in parts
        if p.get("vehicle_make")
    )
    top_vehicles = sorted(vehicle_counts.items(), key=lambda x: -x[1])[:10]
    vehicle_names = [v[0] for v in top_vehicles]
    vehicle_counts_list = [v[1] for v in top_vehicles]

    return {
        "stats": stats,
        "parts": parts,
        "brand_distribution": brand_distribution,
        "category_distribution": category_distribution,
        "price_ranges": price_ranges,
        "price_counts": price_counts,
        "vehicle_names": vehicle_names,
        "vehicle_counts": vehicle_counts_list,
    }


@app.route("/")
def index():
    """首页"""
    from flask import redirect

    return redirect("/viz")


@app.route("/viz")
def visualization():
    """数据可视化页面"""
    data = get_data_for_viz()

    return render_template_string(VIZ_TEMPLATE, **data)


@app.route("/api/viz/data")
def viz_api():
    """可视化数据API"""
    data = get_data_for_viz()
    return jsonify({"success": True, "data": data})


# ========== 主程序 ==========

if __name__ == "__main__":
    print("""
    🚗 汽配云助手 - 数据可视化
    
    📖 访问地址: http://localhost:5001
    
    功能:
       📊 品牌分布饼图
       📂 类别分布饼图
       💰 价格分布柱状图
       🚗 车型分布图表
       📋 配件数据表格
    
    按 Ctrl+C 停止服务
    """)

    app.run(host="0.0.0.0", port=5001, debug=True)

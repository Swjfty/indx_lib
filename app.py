from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# 数据文件路径
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'mock_data.json')

# 加载数据
def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存数据
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 全局数据缓存
data = load_data()

# 动态获取数据的函数
def get_north_star_metrics():
    return data.get('north_star_metrics', [])

def get_metric_tree():
    return data.get('metric_tree', {})

def get_metrics_list():
    return data.get('metrics_list', [])

def get_metric_details():
    return data.get('metric_details', {})

def get_market_metrics():
    return data.get('market_metrics', [])

def get_bloodline_data():
    return data.get('bloodline_data', {})

def get_alert_rules():
    return data.get('alert_rules', [])

def get_quality_checks():
    return data.get('quality_checks', [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/north_star')
def api_north_star():
    return jsonify(get_north_star_metrics())

@app.route('/api/metric_tree')
def api_metric_tree():
    return jsonify(get_metric_tree())

@app.route('/api/metrics')
def api_metrics():
    return jsonify(get_metrics_list())

@app.route('/api/metric/<metric_id>')
def api_metric_detail(metric_id):
    details = get_metric_details()
    return jsonify(details.get(metric_id, {}))

@app.route('/api/market')
def api_market():
    return jsonify(get_market_metrics())

@app.route('/api/bloodline/<metric_id>')
def api_bloodline(metric_id):
    bloodline = get_bloodline_data()
    return jsonify(bloodline.get(metric_id, {}))

@app.route('/api/alerts')
def api_alerts():
    return jsonify(get_alert_rules())

@app.route('/api/quality')
def api_quality():
    return jsonify(get_quality_checks())

@app.route('/api/add_metric', methods=['POST'])
def api_add_metric():
    req_data = request.json
    metrics_list = get_metrics_list()
    new_id = f"m{len(metrics_list) + 1:03d}"
    new_metric = {
        "id": new_id,
        "name": req_data.get("name", ""),
        "type": req_data.get("type", "原子"),
        "status": "审批中",
        "owner": req_data.get("owner", ""),
        "cycle": req_data.get("cycle", "月度"),
        "create_time": "2024-01-15"
    }
    metrics_list.append(new_metric)
    data['metrics_list'] = metrics_list
    save_data(data)
    return jsonify({"success": True, "metric": new_metric})

@app.route('/api/toggle_status/<metric_id>', methods=['POST'])
def api_toggle_status(metric_id):
    metrics_list = get_metrics_list()
    for metric in metrics_list:
        if metric['id'] == metric_id:
            if metric['status'] == '已发布':
                metric['status'] = '已下线'
            elif metric['status'] == '已下线':
                metric['status'] = '审批中'
            data['metrics_list'] = metrics_list
            save_data(data)
            return jsonify({"success": True, "status": metric['status']})
    return jsonify({"success": False})

@app.route('/api/approve_metric/<metric_id>', methods=['POST'])
def api_approve_metric(metric_id):
    metrics_list = get_metrics_list()
    for metric in metrics_list:
        if metric['id'] == metric_id:
            if metric['status'] == '审批中':
                metric['status'] = '已发布'
            data['metrics_list'] = metrics_list
            save_data(data)
            return jsonify({"success": True, "status": metric['status']})
    return jsonify({"success": False})

@app.route('/api/search_market', methods=['POST'])
def api_search_market():
    req_data = request.json
    keyword = req_data.get('keyword', '').lower()
    category = req_data.get('category', '')
    
    filtered = get_market_metrics()
    if keyword:
        filtered = [m for m in filtered if keyword in m['name'].lower() or keyword in m['description'].lower()]
    if category and category != '全部':
        filtered = [m for m in filtered if m['category'] == category]
    
    return jsonify(filtered)

@app.route('/api/apply_permission/<metric_id>', methods=['POST'])
def api_apply_permission(metric_id):
    market_metrics = get_market_metrics()
    for metric in market_metrics:
        if metric['id'] == metric_id:
            metric['permission'] = '审批中'
            data['market_metrics'] = market_metrics
            save_data(data)
            return jsonify({"success": True, "message": "权限申请已提交，请等待审批"})
    return jsonify({"success": False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

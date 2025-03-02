import threading
from io import BytesIO
from flask import Flask, render_template, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from speedtest import NetworkSpeedTester

app = Flask(__name__)
app_state = {
    'running': False,
    'monitoring': False,
    'progress': 0,
    'results': None,
    'lock': threading.Lock()
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start-test', methods=['POST'])
def start_test():
    with app_state['lock']:
        if app_state['running']:
            return jsonify({'status': 'already-running'})

        app_state['running'] = True
        app_state['results'] = None
        threading.Thread(target=run_speed_test).start()
        return jsonify({'status': 'started'})


def run_speed_test():
    tester = NetworkSpeedTester()
    try:
        # 延迟测试
        app_state['progress'] = 25
        if tester.test_latency():
            app_state['progress'] = 33

        # 下载测试
        app_state['progress'] = 33
        if tester.download_test():
            app_state['progress'] = 66

        # 上传测试
        app_state['progress'] = 66
        if tester.upload_test():
            app_state['progress'] = 100

        # 保存结果
        app_state['results'] = tester.results
        tester.save_results()
    except Exception as e:
        app_state['error'] = str(e)
    finally:
        app_state['running'] = False


@app.route('/get-status')
def get_status():
    return jsonify({
        'running': app_state['running'],
        'progress': app_state['progress'],
        'results': app_state['results'],
        'error': app_state.get('error')
    })


@app.route('/generate-report')
def generate_report():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # 绘制报告内容
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "网络测速报告")

    if app_state['results']:
        p.setFont("Helvetica", 12)
        y = 750
        for key, value in app_state['results'].items():
            p.drawString(100, y, f"{key}: {value}")
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1000, debug=True)
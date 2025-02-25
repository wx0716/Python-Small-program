import os
import time
from fpdf import FPDF
import requests


def check_phone_number(phone):
    """验证手机号码格式"""
    return len(phone) == 11 and phone.isdigit() and phone.startswith('1')


def query_phone_info(phone):
    """使用聚合数据API查询"""
    api_url = "http://apis.juhe.cn/mobile/get"
    params = {
        "phone": phone,
        "key": "84be58e7f1123987cc0ff85d54384b07"  # 请替换为实际申请的API KEY
    }

    try:
        response = requests.get(api_url, params=params, timeout=5)
        result = response.json()

        if result["error_code"] == 0:
            return {
                "province": result["result"]["province"],
                "city": result["result"]["city"],
                "operator": result["result"]["company"],
                "card_type": result["result"]["card"]
            }
        print(f"查询失败：{result['reason']}")
        return None
    except Exception as e:
        print(f"请求异常：{str(e)}")
        return None


# 增加报告生成功能的核心代码
def generate_html_report(data, filename=None):
    """生成HTML格式报告"""
    if not filename:
        timestamp = int(time.time())
        filename = f"phone_report_{timestamp}.html"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>手机号码归属地报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            .info {{ margin: 20px 0; padding: 15px; background: #f9f9f9; }}
            .label {{ color: #3498db; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>手机号码归属地报告</h1>
        <div class="info">
            <p><span class="label">手机号码：</span>{data['phone']}</p>
            <p><span class="label">归属省份：</span>{data['province']}</p>
            <p><span class="label">所在城市：</span>{data['city']}</p>
            <p><span class="label">运营商：</span>{data['operator']}</p>
            <p><span class="label">卡类型：</span>{data['card_type']}</p>
        </div>
        <p>生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return os.path.abspath(filename)


def generate_pdf_report(data, filename=None):
    """生成PDF格式报告"""
    if not filename:
        timestamp = int(time.time())
        filename = f"phone_report_{timestamp}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('SimSun', '', 'simsun.ttc', uni=True)  # 需要中文字体文件

    # 标题
    pdf.set_font('SimSun', '', 16)
    pdf.cell(0, 10, '手机号码归属地报告', 0, 1, 'C')
    pdf.ln(10)

    # 内容
    pdf.set_font('SimSun', '', 12)
    info = [
        ("手机号码", data['phone']),
        ("归属省份", data['province']),
        ("所在城市", data['city']),
        ("运营商", data['operator']),
        ("卡类型", data['card_type'])
    ]

    for label, value in info:
        pdf.cell(40, 10, label + '：', 0, 0)
        pdf.set_font('', 'B')
        pdf.cell(0, 10, value, 0, 1)
        pdf.set_font('', '')

    # 页脚
    pdf.set_y(-15)
    pdf.set_font('SimSun', 'I', 10)
    pdf.cell(0, 10, f'生成时间：{time.strftime("%Y-%m-%d %H:%M:%S")}', 0, 0, 'C')

    pdf.output(filename)
    return os.path.abspath(filename)


def main():
    print("手机归属地查询（聚合数据API版）")
    while True:
        phone = input("\n请输入手机号（q退出）：").strip()
        if phone.lower() == 'q':
            break

        if not check_phone_number(phone):
            print("号码格式错误！需11位数字且以1开头")
            continue

        data = query_phone_info(phone)
        if data:
            print("\n查询结果：")
            print(f"省份: {data['province']}")
            print(f"城市: {data['city']}")
            print(f"运营商: {data['operator']}")
            print(f"卡类型: {data['card_type']}")
        else:
            print("查询失败")

            # 在查询结果显示后添加导出选项
            if data:
                print("\n查询结果：")
                # ...（原有显示逻辑）

                # 新增导出功能
                export = input("\n是否生成报告？(1=HTML 2=PDF 其他=跳过): ").strip()
                if export == '1':
                    path = generate_html_report({
                        "phone": phone,
                        **data
                    })
                    print(f"HTML报告已生成：{path}")
                elif export == '2':
                    path = generate_pdf_report({
                        "phone": phone,
                        **data
                    })
                    print(f"PDF报告已生成：{path}")


if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ================= 配置参数 =================
BASE_URL = "https://movie.douban.com/top250"
PAGE_NUM = 3  # 爬取页数
DELAY = 2  # 请求间隔(秒)
DB_CONFIG = {  # MySQL数据库配置
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'spider_db'
}
# ===========================================

# 设置随机User-Agent列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15...",
    # 添加更多浏览器UA...
]


# 初始化Selenium浏览器（用于动态页面）
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)


# 数据库存储模块
def save_to_db(data):
    global cursor, conn
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = """INSERT INTO movies 
                 (title, link, rating) 
                 VALUES (%s, %s, %s)"""
        cursor.executemany(sql, [
            (item['title'], item['link'], item['rating'])
            for item in data
        ])
        conn.commit()
    except Exception as e:
        print("数据库存储失败:", e)
    finally:
        cursor.close()
        conn.close()


# 核心爬取函数
def crawl_page(url, use_selenium=False):
    try:
        # 动态页面处理
        if use_selenium:
            browser = init_browser()
            browser.get(url)
            time.sleep(3)  # 等待JS加载
            html = browser.page_source
            browser.quit()
        else:
            # 随机请求头 + 代理设置（需自行添加代理IP）
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all("div", class_="item")

        return [parse_item(item) for item in items]

    except Exception as e:
        print(f"爬取失败 {url}: {str(e)}")
        return []


# 数据解析函数
def parse_item(item):
    return {
        "title": item.find("span", class_="title").text.strip(),
        "link": item.find("a")["href"],
        "rating": item.find("span", class_="rating_num").text,
        # 可添加更多字段...
    }


# 主程序
def main():
    all_data = []

    # CSV文件头
    with open("movies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "link", "rating"])
        writer.writeheader()

    # 分页爬取
    for page in range(PAGE_NUM):
        url = f"{BASE_URL}?start={page * 25}"
        print(f"正在爬取第 {page + 1} 页: {url}")

        # 随机延迟 + 切换动态模式
        time.sleep(DELAY + random.uniform(0, 1))
        page_data = crawl_page(url, use_selenium=(page % 2 == 0))

        # 追加存储
        all_data.extend(page_data)
        with open("movies.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "link", "rating"])
            writer.writerows(page_data)

        # 数据库存储
        if page % 2 == 0:  # 每2页存一次数据库
            save_to_db(page_data)

    print(f"完成！共爬取 {len(all_data)} 条数据")


if __name__ == "__main__":
    main()
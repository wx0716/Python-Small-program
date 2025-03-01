import requests
import time
from tqdm import tqdm


def download_speed_test(url=None, timeout=15):
    """
    测试网络下载速度
    :param url: 测速文件URL（默认为英国电信的100MB测试文件）
    :param timeout: 超时时间（秒）
    :return: 下载速度（Mbps）
    """
    # 默认测速文件（可自行替换其他可靠测速文件URL）
    test_files = [
        "http://ipv4.download.thinkbroadband.com/100MB.zip",
        "http://speedtest.tele2.net/100MB.zip",
        "http://proof.ovh.net/files/100Mb.dat"
    ]

    selected_url = url or test_files[0]  # 使用第一个默认测速文件

    try:
        # 获取文件信息
        head_response = requests.head(selected_url, timeout=timeout)
        file_size = int(head_response.headers.get('Content-Length', 0))

        if file_size == 0:
            raise ValueError("无效的测速文件，无法获取文件大小")

        print(f"开始测速，文件大小: {file_size / 1024 / 1024:.2f}MB")
        print(f"测速服务器: {selected_url}")

        # 开始下载测速
        start_time = time.time()
        downloaded = 0

        with requests.get(selected_url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            # 使用进度条显示
            progress = tqdm(total=file_size, unit='B',
                            unit_scale=True, unit_divisor=1024,
                            bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤保持连接的空白块
                    downloaded += len(chunk)
                    progress.update(len(chunk))

            progress.close()

        # 计算速度
        duration = time.time() - start_time
        speed_bps = (downloaded * 8) / duration  # 转换为比特率
        speed_mbps = speed_bps / 1_000_000

        return speed_mbps

    except requests.exceptions.RequestException as e:
        print(f"网络连接错误: {str(e)}")
        return None
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    print("=== 网络测速器 ===")

    # 执行测速
    speed = download_speed_test()

    if speed is not None:
        print(f"\n下载速度: {speed:.2f} Mbps")
    else:
        print("测速失败，请检查网络连接")
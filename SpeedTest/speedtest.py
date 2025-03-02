import csv
import os
import socket
import threading
import time
from datetime import datetime
import requests
from colorama import Fore, init
from tqdm import tqdm

init(autoreset=True)


class NetworkSpeedTester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'download': None,
            'upload': None,
            'latency': None,
            'jitter': None,
            'ip_info': None
        }
        self.servers = {
            'download': [
                "http://ipv4.download.thinkbroadband.com/100MB.zip",
                "http://speedtest.tele2.net/100MB.zip",
                "http://proof.ovh.net/files/100Mb.dat"
            ],
            'upload': "https://httpbin.org/post",
            'latency': ("8.8.8.8", 53)
        }

    # --------------- 核心测速功能 ---------------
    def test_latency(self, runs=3):
        try:
            host, port = self.servers['latency']
            delays = []
            for _ in range(runs):
                try:
                    start = time.time()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        s.connect((host, port))
                    delays.append((time.time() - start) * 1000)
                    time.sleep(0.5)
                except Exception:
                    continue

            if len(delays) >= 2:
                self.results['latency'] = sum(delays) / len(delays)
                self.results['jitter'] = max(delays) - min(delays)
                return True
            return False
        except Exception as e:
            print(Fore.RED + f"Latency Error: {str(e)}")
            return False

    def download_test(self, threads=4):
        for url in self.servers['download']:
            try:
                # 验证服务器
                head = requests.head(url, timeout=5)
                if head.status_code != 200:
                    continue

                # 下载设置
                file_size = int(head.headers.get('Content-Length', 0))
                if file_size < 1024 * 1024:
                    continue

                # 多线程下载
                chunk_size = 1024 * 1024
                progress = tqdm(total=file_size, unit='B',
                                unit_scale=True, desc="Downloading", leave=False)

                downloaded = 0
                lock = threading.Lock()
                start_time = time.time()

                def download_chunk(start, end):
                    nonlocal downloaded
                    try:
                        headers = {'Range': f'bytes={start}-{end}'}
                        with requests.get(url, headers=headers, stream=True, timeout=10) as r:
                            for chunk in r.iter_content(chunk_size=1024):
                                with lock:
                                    downloaded += len(chunk)
                                    progress.update(len(chunk))
                    except:
                        pass

                # 启动线程
                workers = []
                for i in range(threads):
                    start = i * (file_size // threads)
                    end = start + (file_size // threads) - 1 if i != threads - 1 else file_size
                    t = threading.Thread(target=download_chunk, args=(start, end))
                    workers.append(t)
                    t.start()

                for t in workers:
                    t.join()

                progress.close()
                self.results['download'] = (downloaded * 8) / (time.time() - start_time) / 1e6
                return True
            except Exception as e:
                print(Fore.YELLOW + f"Download Error ({url}): {str(e)}")
                continue
        return False

    def upload_test(self, duration=10):
        try:
            data = os.urandom(1024 * 1024)  # 1MB数据块
            total_uploaded = 0
            start_time = time.time()
            progress = tqdm(total=duration, unit='s', desc="Uploading", leave=False)

            while (time.time() - start_time) < duration:
                try:
                    res = requests.post(self.servers['upload'], data=data, timeout=5)
                    if res.status_code == 200:
                        total_uploaded += len(data)
                        progress.update(1)
                except:
                    continue

            progress.close()
            self.results['upload'] = (total_uploaded * 8) / (time.time() - start_time) / 1e6
            return True
        except Exception as e:
            print(Fore.RED + f"Upload Error: {str(e)}")
            return False

    def save_results(self, filename="speedtest_history.csv"):
        try:
            file_exists = os.path.isfile(filename)
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.results.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(self.results)
        except Exception as e:
            print(Fore.RED + f"Save Error: {str(e)}")
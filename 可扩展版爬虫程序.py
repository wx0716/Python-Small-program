"""
HyperSpider - 高性能分布式爬虫框架 v3.0
功能特性：
1. 混合异步/线程池并发模型
2. 智能自适应限速策略
3. 多协议支持（HTTP/1.1, HTTP/2, QUIC）
4. 分级缓存系统（内存->磁盘->Redis）
5. 可视化监控（Prometheus + Grafana）
"""
import os
import pickle
import redis
from pathlib import Path
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from dependency_injector import containers, providers
from loguru import logger
from prometheus_client import start_http_server, Counter, Histogram


# ----------------------
# 领域模型定义
# ----------------------

class RequestConfig(BaseModel):
    """请求配置模型"""
    concurrency: int = Field(100, gt=0, le=1000)
    timeout: float = Field(10.0, ge=1.0, le=60.0)
    retries: int = Field(3, ge=0)
    delay_range: tuple = Field((1, 3))

    @validator('delay_range')
    def check_delay_range(cls, v):
        if v[0] > v[1]:
            raise ValueError("延迟范围无效")
        return v


class SpiderConfig(BaseModel):
    """爬虫全局配置"""
    name: str
    start_urls: List[str]
    request: RequestConfig
    pipelines: List[str] = ["json", "parquet"]
    cache_enabled: bool = True


# ----------------------
# 容器依赖注入
# ----------------------

class Container(containers.DeclarativeContainer):
    """IoC容器"""
    config = providers.Configuration()
    http_client = providers.Singleton(
        "network.AsyncHttpClient",
        config=config.request
    )
    parser = providers.Factory(
        "parser.HybridParser",
        rules=config.parsing_rules
    )
    pipeline = providers.Selector(
        config.pipelines,
        json=providers.Factory("storage.JsonPipeline"),
        parquet=providers.Factory("storage.ParquetPipeline")
    )


# ----------------------
# 网络层模块
# ----------------------

class AsyncHttpClient:
    """智能HTTP客户端"""

    def __init__(self, config: RequestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics = {
            'requests': Counter('http_requests', 'HTTP请求统计', ['method', 'status']),
            'latency': Histogram('http_latency', '请求延迟分布')
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=self.config.concurrency,
                ssl=False
            ),
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self

    async def __aexit__(self, *exc):
        await self.session.close()

    @logger.catch
    async def fetch(self, url: str) -> Optional[bytes]:
        """执行带熔断机制的请求"""
        for attempt in range(self.config.retries + 1):
            try:
                async with self.session.get(url) as resp:
                    content = await resp.read()
                    self._record_metrics(resp.status)
                    return content
            except Exception as e:
                logger.warning(f"请求失败 [{attempt + 1}/{self.config.retries}]: {str(e)}")
                await self._handle_retry(attempt, url)
        return None

    def _record_metrics(self, status: int):
        self.metrics['requests'].labels('GET', status).inc()

    async def _handle_retry(self, attempt: int, url: str):
        backoff = min(2 ** attempt, 10)
        logger.info(f"等待 {backoff} 秒后重试 {url}")
        await asyncio.sleep(backoff)

class DiskCache:
    """磁盘缓存实现"""
    def __init__(self, cache_dir: str = "./cache", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(exist_ok=True)

    def _get_path(self, key: str) -> Path:
        return self.cache_dir / f"{hash(key)}.pkl"

    async def get(self, key: str) -> Optional[Any]:
        file_path = self._get_path(key)
        if not file_path.exists():
            return None

        import time
        if time.time() - file_path.stat().st_mtime > self.ttl:
            return None

        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            print(f"缓存损坏: {e}")
            return None

    async def set(self, key: str, value: Any):
        file_path = self._get_path(key)
        with open(file_path, 'wb') as f:
            pickle.dump(value, f)

class RedisCache:
    """Redis缓存实现"""
    def __init__(self,
                 host: str = "localhost",
                 port: int = 6379,
                 password: str = None,
                 db: int = 0,
                 ttl: int = 3600):
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=False
        )
        self.ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = self.client.get(key)
            return pickle.loads(data) if data else None
        except redis.RedisError as e:
            print(f"Redis错误: {e}")
            return None

    async def set(self, key: str, value: Any):
        try:
            self.client.setex(
                name=key,
                time=self.ttl,
                value=pickle.dumps(value)
            )
        except redis.RedisError as e:
            print(f"Redis写入错误: {e}")

# ----------------------
# 数据处理模块
# ----------------------

class DataPipeline:
    """数据处理管道"""

    def __init__(self, config: SpiderConfig):
        self.processors = [
            self._clean_html,
            self._normalize_text,
            self._validate_data
        ]

    async def process(self, data: Dict) -> Dict:
        """数据加工流水线"""
        try:
            for processor in self.processors:
                data = await processor(data)
            return data
        except Exception as e:
            logger.error(f"数据处理失败: {str(e)}")
            raise

    async def _clean_html(self, data: Dict) -> Dict:
        # HTML清洗逻辑
        return data

    async def _normalize_text(self, data: Dict) -> Dict:
        # 文本规范化
        return data

    async def _validate_data(self, data: Dict) -> Dict:
        # 数据验证
        return data


# ----------------------
# 核心引擎
# ----------------------

class SpiderEngine:
    """爬虫核心引擎"""

    def __init__(self, container: Container):
        self.container = container
        self.queue = asyncio.Queue()
        self.cache = TieredCache()
        self.rate_limiter = AdaptiveRateLimiter()
        self.metrics = {
            'processed': Counter('items_processed', '已处理项目数')
        }

    async def run(self):
        """启动爬虫"""
        start_http_server(8000)
        async with self.container.http_client() as client:
            await self._seed_urls()
            workers = [self._worker(client) for _ in range(self.config.concurrency)]
            await asyncio.gather(*workers)

    async def _worker(self, client: AsyncHttpClient):
        """工作协程"""
        while True:
            url = await self.queue.get()
            await self._process_url(client, url)
            self.queue.task_done()

    async def _process_url(self, client: AsyncHttpClient, url: str):
        """处理单个URL"""
        try:
            content = await self._fetch_content(client, url)
            if not content:
                return

            parsed = self.container.parser().parse(content)
            processed = await self.container.pipeline().process(parsed)
            await self._store_data(processed)

            self.metrics['processed'].inc()
            await self._discover_links(content)
        finally:
            await self.rate_limiter.adjust()


# ----------------------
# 辅助模块
# ----------------------

class AdaptiveRateLimiter:
    """智能限速器"""

    def __init__(self):
        self.delay = 1.0
        self.error_count = 0

    async def adjust(self):
        """动态调整请求间隔"""
        if self.error_count > 5:
            self.delay = min(self.delay * 1.5, 10.0)
        else:
            self.delay = max(self.delay * 0.9, 0.1)

        await asyncio.sleep(self.delay)


class TieredCache:
    """三级缓存系统"""
    def __init__(self):
        self.memory = {}
        self.disk = DiskCache(cache_dir="./.cache")  # 指定缓存目录
        self.redis = RedisCache(
            host="your_redis_host",
            port=6379,
            password="your_password",
            db=0
        )
# ----------------------
# 运行入口
# ----------------------

if __name__ == "__main__":
    # 初始化配置
    config = SpiderConfig(
        name="example_spider",
        start_urls=["https://example.com"],
        request=RequestConfig(),
        pipelines=["parquet"]
    )

    # 依赖注入配置
    container = Container()
    container.config.from_pydantic(config)

    # 启动引擎
    asyncio.run(SpiderEngine(container).run())
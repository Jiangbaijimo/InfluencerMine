# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


import asyncio
from typing import Optional

import config
import constant
from base.base_crawler import AbstractCrawler
from pkg.account_pool.pool import AccountWithIpPoolManager
from pkg.proxy.proxy_ip_pool import ProxyIpPool, create_ip_pool
from pkg.tools import utils
from repo.checkpoint.checkpoint_store import CheckpointRepoManager
from repo.checkpoint import create_checkpoint_manager
from var import crawler_type_var

from .client import KuaiShouApiClient
from .handlers import SearchHandler, DetailHandler, CreatorHandler, HomefeedHandler
from .processors import VideoProcessor, CommentProcessor


class KuaiShouCrawler(AbstractCrawler):
    def __init__(self) -> None:
        self.ks_client = KuaiShouApiClient()
        self.checkpoint_manager: CheckpointRepoManager = create_checkpoint_manager()

        # 限制并发数
        self.crawler_video_task_semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        self.crawler_comment_semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)

        # Initialize processors with dependency injection
        self.video_processor = VideoProcessor(
            self.ks_client,
            self.checkpoint_manager,
            self.crawler_video_task_semaphore
        )
        self.comment_processor = CommentProcessor(
            self.ks_client,
            self.checkpoint_manager,
            self.crawler_comment_semaphore
        )

        # Initialize handlers with dependency injection
        self.search_handler = SearchHandler(
            self.ks_client,
            self.checkpoint_manager,
            self.video_processor,
            self.comment_processor
        )
        self.detail_handler = DetailHandler(
            self.ks_client,
            self.checkpoint_manager,
            self.video_processor,
            self.comment_processor
        )
        self.creator_handler = CreatorHandler(
            self.ks_client,
            self.checkpoint_manager,
            self.video_processor,
            self.comment_processor
        )
        self.homefeed_handler = HomefeedHandler(
            self.ks_client,
            self.checkpoint_manager,
            self.video_processor,
            self.comment_processor
        )

    async def async_initialize(self):
        """
        Asynchronous Initialization
        Returns:

        """
        utils.logger.info(
            "[KuaiShouCrawler.async_initialize] Begin async initialize"
        )

        # 账号池和IP池的初始化
        proxy_ip_pool: Optional[ProxyIpPool] = None
        if config.ENABLE_IP_PROXY:
            # 快手对代理验证还行，可以选择长时长的IP，比如30分钟一个IP
            # 快代理：私密代理->按IP付费->专业版->IP有效时长为30分钟, 购买地址：https://www.kuaidaili.com/?ref=ldwkjqipvz6c
            proxy_ip_pool = await create_ip_pool(
                config.IP_PROXY_POOL_COUNT, enable_validate_ip=True
            )

        # 初始化账号池
        account_with_ip_pool = AccountWithIpPoolManager(
            platform_name=constant.KUAISHOU_PLATFORM_NAME,
            account_save_type=config.ACCOUNT_POOL_SAVE_TYPE,
            proxy_ip_pool=proxy_ip_pool,
        )
        await account_with_ip_pool.async_initialize()

        self.ks_client.account_with_ip_pool = account_with_ip_pool
        await self.ks_client.update_account_info()

        # 设置爬虫类型
        crawler_type_var.set(config.CRAWLER_TYPE)

    async def start(self) -> None:
        """
        Start crawler
        Returns:

        """
        if config.CRAWLER_TYPE == constant.CRALER_TYPE_SEARCH:
            # Search for notes and retrieve their comment information.
            await self.search_handler.handle()
        elif config.CRAWLER_TYPE == constant.CRALER_TYPE_DETAIL:
            # Get the information and comments of the specified post
            await self.detail_handler.handle()
        elif config.CRAWLER_TYPE == constant.CRALER_TYPE_CREATOR:
            # Get the information and comments of the specified creator
            await self.creator_handler.handle()
        elif config.CRAWLER_TYPE == constant.CRALER_TYPE_HOMEFEED:
            # Get the information and comments of the specified creator
            await self.homefeed_handler.handle()
        else:
            raise NotImplementedError(
                f"[KuaiShouCrawler.start] Not support crawler type: {config.CRAWLER_TYPE}"
            )
        utils.logger.info("[KuaiShouCrawler.start] Kuaishou Crawler finished ...")

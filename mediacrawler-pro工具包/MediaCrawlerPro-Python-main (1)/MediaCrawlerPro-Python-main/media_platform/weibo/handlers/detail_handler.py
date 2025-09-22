# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from typing import TYPE_CHECKING

import config
import constant
from model.m_checkpoint import Checkpoint
from pkg.tools import utils
from .base_handler import BaseHandler

if TYPE_CHECKING:
    from ..client import WeiboClient
    from repo.checkpoint.checkpoint_store import CheckpointRepoManager
    from ..processors.note_processor import NoteProcessor
    from ..processors.comment_processor import CommentProcessor


class DetailHandler(BaseHandler):
    """Handles detail-based crawling operations for specified notes"""
    
    def __init__(
        self,
        wb_client: "WeiboClient",
        checkpoint_manager: "CheckpointRepoManager",
        note_processor: "NoteProcessor",
        comment_processor: "CommentProcessor"
    ):
        """
        Initialize detail handler
        
        Args:
            wb_client: Weibo API client
            checkpoint_manager: Checkpoint manager for resume functionality
            note_processor: Note processing component
            comment_processor: Comment processing component
        """
        super().__init__(wb_client, checkpoint_manager, note_processor, comment_processor)
    
    async def handle(self) -> None:
        """
        Handle detail-based crawling
        
        Returns:
            None
        """
        await self.get_specified_notes()
    
    async def get_specified_notes(self):
        """
        Get the information and comments of the specified post
        Returns:
            None
        """
        utils.logger.info(
            "[DetailHandler.get_specified_notes] Begin get weibo specified notes"
        )

        checkpoint = Checkpoint(platform=constant.WEIBO_PLATFORM_NAME, mode=constant.CRALER_TYPE_DETAIL)

        # 如果开启了断点续爬，则加载检查点
        if config.ENABLE_CHECKPOINT:
            lastest_checkpoint = await self.checkpoint_manager.load_checkpoint(
                platform=constant.WEIBO_PLATFORM_NAME,
                mode=constant.CRALER_TYPE_DETAIL,
                checkpoint_id=config.SPECIFIED_CHECKPOINT_ID,
            )
            if lastest_checkpoint:
                checkpoint = lastest_checkpoint
                utils.logger.info(
                    f"[DetailHandler.get_specified_notes] Load lastest checkpoint: {lastest_checkpoint.id}"
                )
        await self.checkpoint_manager.save_checkpoint(checkpoint)

        note_id_list = await self.note_processor.batch_get_specified_notes(
            config.WEIBO_SPECIFIED_ID_LIST, checkpoint_id=checkpoint.id
        )
        await self.comment_processor.batch_get_note_comments(
            note_id_list, checkpoint_id=checkpoint.id
        )

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import BaiduTieBaClient
    from repo.checkpoint.checkpoint_store import CheckpointRepoManager
    from ..processors.note_processor import NoteProcessor
    from ..processors.comment_processor import CommentProcessor


class BaseHandler(ABC):
    """Base handler class for all Tieba crawler handlers"""
    
    def __init__(
        self,
        tieba_client: "BaiduTieBaClient",
        checkpoint_manager: "CheckpointRepoManager",
        note_processor: "NoteProcessor",
        comment_processor: "CommentProcessor"
    ):
        """
        Initialize base handler with injected dependencies
        
        Args:
            tieba_client: Tieba API client
            checkpoint_manager: Checkpoint manager for resume functionality
            note_processor: Note processing component
            comment_processor: Comment processing component
        """
        self.tieba_client = tieba_client
        self.checkpoint_manager = checkpoint_manager
        self.note_processor = note_processor
        self.comment_processor = comment_processor
    
    @abstractmethod
    async def handle(self) -> None:
        """
        Handle the specific crawler type operation
        
        Returns:
            None
        """
        raise NotImplementedError("Subclasses must implement handle method")

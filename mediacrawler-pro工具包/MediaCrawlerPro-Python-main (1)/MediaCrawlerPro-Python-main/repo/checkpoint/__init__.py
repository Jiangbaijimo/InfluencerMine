from config import CHECKPOINT_STORAGE_TYPE
from .checkpoint_store import (
    CheckpointJsonFileRepo,
    CheckpointRedisRepo,
    CheckpointRepoManager,
)


def create_checkpoint_manager(
    storage_type: str = CHECKPOINT_STORAGE_TYPE, **kwargs
) -> CheckpointRepoManager:
    """创建检查点管理器的工厂函数

    Args:
        storage_type (str): 存储类型，支持 "file" 或 "redis"
        **kwargs: 额外的参数传递给对应的存储库构造函数

    Returns:
        CheckpointRepoManager: 检查点管理器实例
    """
    if storage_type.lower() == "redis":
        repo = CheckpointRedisRepo(**kwargs)
    elif storage_type.lower() == "file":
        repo = CheckpointJsonFileRepo(**kwargs)
    else:
        raise ValueError(f"不支持的存储类型: {storage_type}")

    return CheckpointRepoManager(repo)

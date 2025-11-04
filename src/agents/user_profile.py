import random
from strands import tool
from utils.logger import get_logger

logger = get_logger(__name__)

@tool
def get_user_risk_tolerance_level(user_id):
    """
    Finding user risk tolerance for specific user_id.
    Ranging from 1 to 5, where 1 represents the most conservative and 5 represents the most aggressive.

    Args:
        user_id (str): The user_id of user.
    Returns:
        Int level of risk tolerance.
    """
    logger.info("[Routed to User Profile Agent...]")
    logger.info(f"executing get_user_risk_tolerance with {user_id=}")
    # 生成随机数 1-5
    risk_tolerance = random.randint(1, 5)
    logger.debug(f"risk_tolerance: {risk_tolerance}")
    return risk_tolerance
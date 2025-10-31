import logging
import os
from strands import tool

log_level = os.environ.get("LOG_LEVEL", "ERROR").strip().upper()
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

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
    logger.info("Routed to User Profile Agent")
    logger.info(f"executing get_user_risk_tolerance_ with {user_id=}")
    risk_tolerance = 5
    return risk_tolerance    
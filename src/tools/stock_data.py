import json
import logging
import os
import yfinance as yf

from strands import tool

log_level = os.environ.get("LOG_LEVEL", "ERROR").strip().upper()
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)

@tool
def stock_data_lookup(ticker):
    """Finding stock price history for specific stocks.
    Args:
        ticker (str): The ticker of stock.        
    Returns:
        List with search results.
    """
    logger.info(f"executing stock data lookup with {ticker=}")
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    hist = hist.reset_index().to_json(orient="split", index=False, date_format="iso")
    logger.info(f"Price history for {ticker=}: {hist=}")
    return hist
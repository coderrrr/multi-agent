import json
import yfinance as yf
from strands import tool
from utils.logger import get_logger

logger = get_logger(__name__)

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
from strands import Agent, tool
from strands.models import BedrockModel
from tools.web_search import web_search
from tools.stock_data import stock_data_lookup
from utils.logger import get_logger

logger = get_logger(__name__)

STOCK_ANALYSIS_SYSTEM_PROMPT = """
You are a seasoned stock investment analyst. For the given stock ticker, perform the following analysis in sequence:

1. Retrieve current stock price data and recent price movements
2. Gather latest news and market developments for the stock
3. Analyze the collected data to assess investment potential

Requirements:
- Use tools sequentially, not in parallel
- Provide a comprehensive investment report including:
  * Price trend analysis
  * Fundamental assessment based on news
  * Risk factors identification
  * Clear investment recommendation with rationale
- Base analysis on factual data only
- Write in a professional, objective tone suitable for investors

Deliver actionable insights that help investors make informed decisions.
Always use Chinese as final output language.
Add a stock page link in new line at the end of content, pattern: <myapp://pages/stock/detail?stock_code>
"""

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-west-2",
    temperature=0.3,
    streaming=True,
)


@tool
def stock_analysis(stock: str, user_risk_tolerance_level: int = 3) -> str:
    """
    Conduct a matches comprehensive analysis of a single stock and user_risk_tolerance_level.
    According to user risk tolerance level, deliver matched actionable insights that help investors make informed decisions.
    user_risk_tolerance_level: Ranging from 1 to 5, where 1 represents the most conservative and 5 represents the most aggressive.

    Args:
        stock: The stock name or code to be analyzed
        user_risk_tolerance_level: Int level of risk tolerance.
    Returns:
        A comprehensive stock analysis report
    """
    # Format the query for the agent
    formatted_query = f"Analyze this stock: {stock} for user risk tolerance level: {user_risk_tolerance_level}."

    try:
        logger.info("[Routed to Stock Analysis Agent...]")
        logger.info(f"formatted_query: {formatted_query} ")

        agent = Agent(
            model=bedrock_model,
            system_prompt=STOCK_ANALYSIS_SYSTEM_PROMPT,
            tools=[web_search, stock_data_lookup],
        )
        agent_response = agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            logger.debug(f"Response: {text_response} ")
            return text_response + "\n"

        return "抱歉，我无法对这只股票进行分析。\n"
    except Exception as e:
        # Return error message
        logger.error(f"Error processing stock analysis: {str(e)}")
        return f"Error processing stock analysis: {str(e)}"

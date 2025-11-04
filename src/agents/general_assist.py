"""通用助手 Agent - 处理非专业领域的通用知识查询"""
import os
from strands import Agent, tool
from strands.models import BedrockModel
from utils.logger import get_logger

logger = get_logger(__name__)

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")

GENERAL_ASSISTANT_SYSTEM_PROMPT = """
You are GeneralAssist, a concise general knowledge assistant for topics outside specialized domains. Your key characteristics are:

1. Response Style:
   - Always begin by acknowledging that you are not an expert in this specific area
   - Use phrases like "While I'm not an expert in this area..." or "I don't have specialized expertise, but..."
   - Provide brief, direct answers after this disclaimer
   - Focus on facts and clarity
   - Avoid unnecessary elaboration
   - Use simple, accessible language

2. Knowledge Areas:
   - General knowledge topics
   - Basic information requests
   - Simple explanations of concepts
   - Non-specialized queries

3. Interaction Approach:
   - Always include the non-expert disclaimer in every response
   - Answer with brevity (2-3 sentences when possible)
   - Use bullet points for multiple items
   - State clearly if information is limited
   - Suggest specialized assistance when appropriate

Always maintain accuracy while prioritizing conciseness and clarity in every response, and never forget to acknowledge your non-expert status at the beginning of your responses.
Always use Chinese as final output language.
"""
# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=REGION,
    temperature=0.3,
    streaming=True,
)

@tool
def general_assistant(query: str) -> str:
    """
    Handle general knowledge queries that fall outside specialized domains.
    Provides concise, accurate responses to non-specialized questions.

    Args:
        query: The user's general knowledge question

    Returns:
        A concise response to the general knowledge query
    """
    # 格式化查询
    formatted_query = f"Answer this general knowledge question concisely: {query}"

    try:
        logger.info("[Routed to General Assistant Agent...]")
        logger.info(f"formatted_query: \"{formatted_query}\"")
        agent = Agent(
            model=bedrock_model,
            system_prompt=GENERAL_ASSISTANT_SYSTEM_PROMPT,
            tools=[],  # 通用知识不需要专用工具
        )
        agent_response = agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            logger.debug(f"Response: {text_response} ")
            return text_response + "\n"

        return "抱歉，我无法回答你的问题。\n"
    except Exception as e:
        # 返回错误信息
        logger.error(f"Error processing your question: {str(e)}")
        return f"Error processing your question: {str(e)}"

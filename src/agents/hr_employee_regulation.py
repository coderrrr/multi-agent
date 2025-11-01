import os
import boto3
from strands import tool
from utils.logger import get_logger

logger = get_logger(__name__)


# Create Bedrock Agent Runtime client for Knowledge Base
bedrock_agent_client = boto3.client("bedrock-agent-runtime", region_name="us-west-2")

# Knowledge Base configuration
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
MODEL_ARN = "arn:aws:bedrock:us-west-2:640037134104:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0"


@tool
def hr_employee_regulation_search(query: str) -> str:
    """
    Handle internal company HR and Employee regulation questions.
    Provides concise, accurate responses to non-specialized questions.

    Args:
        query: The user's question

    Returns:
        A concise response to queries on the relevant knowledge base
    """
    # Format the query for the agent
    formatted_query = f"Use Chinese as output language, answer this knowledge question concisely: {query}"
    try:
        logger.info("[Routed to HR Employee Regulation Assistant...]")
        logger.info(f"formatted_query: {formatted_query} ")
        response = bedrock_agent_client.retrieve_and_generate(
            input={"text": formatted_query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN,
                },
            },
        )

        if "output" in response and "text" in response["output"]:
            logger.debug(f"Response: {response["output"]["text"]} ")
            return response["output"]["text"]
        return ""

    except Exception as e:
        logger.error(f"Knowledge base query failed: {str(e)}")
        return ""

import os
import readline
from utils.logger import get_logger

from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient

from agents.user_profile import get_user_risk_tolerance_level
from agents.general_assist import general_assistant
from agents.stock_analysis import stock_analysis
from agents.hr_employee_regulation import hr_employee_regulation_search
from agentcore.memory_hook import MemoryHookProvider


logger = get_logger(__name__)

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")
# Created on Bedrock AgentCore
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID")
ACTOR_ID = "user_123"  # It can be any unique identifier
SESSION_ID = "personal_session_001"  # Unique session identifier

memory_client = MemoryClient(region_name=REGION)

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=REGION,
    temperature=0.3,
    streaming=True,
)

# Define a focused system prompt for file operations
MASTER_SYSTEM_PROMPT = """
You are Comprehensive AI Assist, a sophisticated enterprise orchestrator designed to coordinate comprehensive support across multiple subjects.
Your role is to:
1. Analyze incoming queries and determine the most appropriate specialized agent to handle them:
   - Stock Agent: For a stock analysis
   - User Profile Agent: For retrieving user risk tolerance level
   - HR and Employee Regulation Agent: For HR, Employee regulations
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed
   - If queries contains stock, retrieve user_risk_tolerance_level if a user_id specified, otherwize use 3 as default user_risk_tolerance_level

3. Decision Protocol:
   - If query involves stock: Stock Agent (stock_analysis)
   - If query involves HR or employee: HR and Employee Regulation Agent (hr_employee_regulation_search)
   - If query involves a specified user id: User Profile Agent (get_user_risk_tolerance_level)
   - If query is outside these specialized areas: General Assistant (general_assistant)
   - For complex queries, coordinate multiple agents as needed

4. Key Points: 
   - Always confirm your understanding before routing to ensure accurate assistance.
   - Always use Chinese as final output language.
   - If the sub agent has already returned a fully comprehensible result, DO NOT include any additional summaries or comments in your response.
   - DO NOT remove any <link> from original response.
"""

memroy_hook = MemoryHookProvider(memory_client, MEMORY_ID)

master_agent = Agent(
    model=bedrock_model,
    system_prompt=MASTER_SYSTEM_PROMPT,
    callback_handler=None,
    tools=[
        stock_analysis,
        hr_employee_regulation_search,
        get_user_risk_tolerance_level,
        general_assistant,
    ],
    hooks=[memroy_hook],
    state={"actor_id": ACTOR_ID, "session_id": SESSION_ID}
)

memroy_hook.view_memmory(ACTOR_ID, SESSION_ID)

# Check what's stored in memory


# Example usage
if __name__ == "__main__":
    logger.info("Starting Strands Multi-Agent Demo")
    print("\n📁 Strands Multi-Agent Demo 📁\n")
    
    print(
        "请输入你的问题, 我将路由到匹配的 Agent 来回答："
    )
    print("Type 'exit' to quit.")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                break

            response = master_agent(
                user_input,
            )
            content = str(response)
            print("\n🤖->" + content)

        except KeyboardInterrupt:
            logger.info("Execution interrupted by user")
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")

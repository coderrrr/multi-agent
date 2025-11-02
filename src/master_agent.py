import readline
from strands import Agent
from strands.models import BedrockModel

from agents.user_profile import get_user_risk_tolerance_level
from agents.general_assist import general_assistant
from agents.stock_analysis import stock_analysis
from agents.hr_employee_regulation import hr_employee_regulation_search
from utils.logger import get_logger

logger = get_logger(__name__)

# Create a BedrockModel
bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="us-west-2",
    temperature=0.3,
    streaming=True,
)

# Define a focused system prompt for file operations
MAIN_SYSTEM_PROMPT = """
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
   - If queries contains stock, retrieving user_risk_tolerance_level if a user_id specified, otherwize use 3 as default user_risk_tolerance_level

3. Decision Protocol:
   - If query involves stock: Stock Agent
   - If query involves HR or employee: HR and Employee Regulation Agent
   - If query involves a specified user id: User Profile Agent
   - If query is outside these specialized areas: General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
Always use Chinese as final output language.
"""

# Create a teacher agent with available tools
main_agent = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    callback_handler=None,
    tools=[
        stock_analysis,
        hr_employee_regulation_search,
        get_user_risk_tolerance_level,
        general_assistant,
    ],
)


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
                print("\nGoodbye! 👋")
                break

            response = main_agent(
                user_input,
            )

            # Extract and print only the relevant content from the specialized agent's response
            content = str(response)
            print(content)

        except KeyboardInterrupt:
            logger.info("Execution interrupted by user")
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")

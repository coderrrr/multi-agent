from typing import Dict
from botocore.exceptions import ClientError
from strands.hooks import AgentInitializedEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType
from utils.logger import get_logger

logger = get_logger(__name__)


def create_short_term_memory(memory_client: MemoryClient, memory_name: str):
    """创建短期记忆"""
    logger.info(f"Createing short-term memory {memory_name}...")
    try:
        # 创建不带策略的 Memory 资源（仅访问短期记忆）
        memory = memory_client.create_memory_and_wait(
            name=memory_name,
            strategies=[],  # 短期记忆不需要策略
            description="Short-term memory for personal agent",
            # 短期记忆保留期限，最多可设置 365 天
            event_expiry_days=7,
        )
        memory_id = memory['id']
        logger.info(f"✅ Created memory: {memory_id}")
        return memory_id
    except ClientError as e:
        logger.info(f"❌ ERROR: {e}")
        if e.response['Error']['Code'] == 'ValidationException' and "already exists" in str(e):
            # 如果 Memory 已存在，获取其 ID
            memories = memory_client.list_memories()
            memory_id = next(
                (m['id'] for m in memories if m['id'].startswith(memory_name)), None)
            logger.info(
                f"Memory already exists. Using existing memory ID: {memory_id}")
            return memory_id
    except Exception as e:
        # 显示 Memory 创建过程中的错误
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        # 错误时清理 - 删除部分创建的 Memory
        if memory_id:
            try:
                memory_client.delete_memory_and_wait(memory_id=memory_id)
                logger.info(f"Cleaned up memory: {memory_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up memory: {cleanup_error}")

    return None


def create_long_term_memory(memory_client: MemoryClient, memory_name: str):
    """创建长期记忆
    logger.info(f"Createing long-term memory {memory_name}...")
    SemanticMemoryStrategy(语义记忆策略): 从对话中抽取出事实和知识，以便日后查询。
    SummaryMemoryStrategy(摘要策略): 为每个会话生成对话摘要，提炼主要内容。
    UserPreferenceMemoryStrategy(用户偏好策略):捕获用户的偏好、风格和重复选择等信息。"""

    try:
        # 创建带策略的 Memory 资源
        memory = memory_client.create_memory_and_wait(
            name=memory_name,
            strategies=[
                {
                    StrategyType.USER_PREFERENCE.value: {
                        "name": "CustomerPreferences",
                        "description": "Captures customer preferences and behavior",
                        "namespaces": ["users/{actorId}/preference"]
                    }
                },
                {
                    StrategyType.SEMANTIC.value: {
                        "name": "CustomerSupportSemantic",
                        "description": "Stores facts from conversations",
                        "namespaces": ["users/{actorId}/semantic"],
                    }
                },
                {
                    StrategyType.SUMMARY.value: {
                        "name": "SessionSummarizer",
                        "description": "Stores summary from conversations",
                        "namespaces": ["user/{actorId}/summary/{sessionId}"]
                    }
                }
            ],
            description="Long-term memory for personal agent",
            # 长期记忆保留期限，最多可设置 365 天
            event_expiry_days=90,
        )
        memory_id = memory['id']
        logger.info(f"✅ Created memory: {memory_id}")
        return memory_id
    except ClientError as e:
        logger.info(f"❌ ERROR: {e}")
        if e.response['Error']['Code'] == 'ValidationException' and "already exists" in str(e):
            # 如果 Memory 已存在，获取其 ID
            memories = client.list_memories()
            memory_id = next(
                (m['id'] for m in memories if m['id'].startswith(memory_name)), None)
            logger.info(
                f"Memory already exists. Using existing memory ID: {memory_id}")
            return memory_id
    except Exception as e:
        # 显示 Memory 创建过程中的错误
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        # 错误时清理 - 删除部分创建的 Memory
        if memory_id:
            try:
                client.delete_memory_and_wait(memory_id=memory_id)
                logger.info(f"Cleaned up memory: {memory_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up memory: {cleanup_error}")

    return None


class MemoryHookProvider(HookProvider):
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id

    def get_namespaces(self, memory_client: MemoryClient, memory_id: str) -> Dict:
        """获取长期记忆策略的命名空间映射"""
        strategies = memory_client.get_memory_strategies(memory_id)
        return {i["type"]: i["namespaces"][0] for i in strategies}

    def on_agent_initialized(self, event: AgentInitializedEvent):
        """Agent 启动时加载最近的对话历史"""
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")
            self.namespaces = self.get_namespaces(self.memory_client, self.memory_id)

            if not actor_id or not session_id:
                logger.warning("Missing actor_id or session_id in agent state")
                return

            recent_turns = self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                k=5
            )

            if recent_turns:
                context_messages = []
                for turn in recent_turns:
                    for message in turn:
                        role = message['role']
                        content = message['content']['text']
                        context_messages.append(f"{role}: {content}")

                context = "\n".join(context_messages)
                event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"
                logger.info(f"✅ Loaded {len(recent_turns)} conversation turns")

        except Exception as e:
            logger.error(f"Memory load error: {e}")

    def on_message_added(self, event: MessageAddedEvent):
        """将消息存储到 Memory 中"""
        messages = event.agent.messages
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")

            if messages[-1]["content"][0].get("text"):
                self.memory_client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    messages=[(messages[-1]["content"][0]
                               ["text"], messages[-1]["role"])]
                )
        except Exception as e:
            logger.error(f"Memory save error: {e}")

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)

    def view_memories(self, actor_id, session_id):
        print(
            f"=== Memory Contents for actor_id: {actor_id}, session_id{session_id} ===")
        recent_turns = self.memory_client.get_last_k_turns(
            memory_id=self.memory_id,
            actor_id=actor_id,
            session_id=session_id,
            k=3
        )
        for i, turn in enumerate(recent_turns, 1):
            print(f"Turn {i}:")
            for message in turn:
                role = message['role']
                content = message['content']['text'][:100] + "..." if len(
                    message['content']['text']) > 100 else message['content']['text']
                print(f"  {role}: {content}")
            print()

    def view_memories(self, actor_id, session_id):
        print(
            f"=== Memory Contents for actor_id: {actor_id}, session_id{session_id} ===")
        recent_turns = self.memory_client.get_last_k_turns(
            memory_id=self.memory_id,
            actor_id=actor_id,
            session_id=session_id,
            k=3
        )
        for i, turn in enumerate(recent_turns, 1):
            print(f"Turn {i}:")
            for message in turn:
                role = message['role']
                content = message['content']['text'][:100] + "..." if len(
                    message['content']['text']) > 100 else message['content']['text']
                print(f"  {role}: {content}")
            print()
    
    def retrieve_user_preference(self, actor_id):
        print(
            f"=== Memory User Preferences for actor_id: {actor_id} ===")

        memories = self.memory_client.retrieve_memories(
            memory_id=self.memory_id,
            namespace=f"users/{actor_id}/preference",
            query="Summaries all the preferences"
        )
        return memories

    def retrieve_semantic(self, actor_id):
        print(
            f"=== Memory Semantics for actor_id: {actor_id} ===")

        memories = self.memory_client.retrieve_memories(
            memory_id=self.memory_id,
            namespace=f"users/{actor_id}/semantic",
            query="Summaries all the semantics"
        )
        return memories     

    def retrieve_summaries(self, actor_id, session_id):
        print(
            f"=== Memory Summaries for actor_id: {actor_id}, session_id{session_id} ===")

        memories = self.memory_client.retrieve_memories(
            memory_id=self.memory_id,
            namespace=f"user/{actor_id}/summary/{session_id}",
            query="Summaries all the questions"
        )
        return memories

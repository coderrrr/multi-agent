from strands.hooks import AgentInitializedEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore.memory import MemoryClient
from utils.logger import get_logger

logger = get_logger(__name__)

class MemoryHookProvider(HookProvider):
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id

    def on_agent_initialized(self, event: AgentInitializedEvent):
        """Load recent conversation history when agent starts"""
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")

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
        """Store messages in memory"""
        messages = event.agent.messages
        try:
            actor_id = event.agent.state.get("actor_id")
            session_id = event.agent.state.get("session_id")

            if messages[-1]["content"][0].get("text"):
                self.memory_client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id=session_id,
                    messages=[(messages[-1]["content"][0]["text"], messages[-1]["role"])]
                )
        except Exception as e:
            logger.error(f"Memory save error: {e}")

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)

    def view_memmory(self, actor_id, session_id):
        print(f"=== Memory Contents for actor_id: {actor_id}, session_id{session_id} ===")
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

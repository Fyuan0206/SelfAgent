from typing import Optional, List
import os
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import RoleType, ModelType, ModelPlatformType
from camel.models import ModelFactory
from camel.configs import ChatGPTConfig
from app.models.data_models import UserInput
from app.core.camel_tools import get_self_agent_tools
from app.core.camel_emotion_tools import get_emotion_tools

class SelfAgent:
    """
    5.2 Self-Agent Core Control Hub (CAMEL-AI Implementation)
    """
    def __init__(self, model_type: str = "deepseek-chat"):
        self.system_message = BaseMessage(
            role_name="Self-Agent",
            role_type=RoleType.ASSISTANT,
            meta_dict=None,
            content="""1. **Perception**: ALWAYS start by calling `detect_emotion_and_risk` to analyze the user's input. 
   - If you need deeper understanding of the specific emotions (e.g., distinguishing between sadness and emptiness), call `analyze_user_emotion`.
2. **Decision & Routing**:"""
        )
        
        tools = []
        tools.extend(get_emotion_tools())
        tools.extend(get_self_agent_tools())
        
        api_base = os.environ.get("OPENAI_API_BASE")
        model_instance = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=model_type,
            model_config_dict=ChatGPTConfig(temperature=0.7).as_dict(),
            url=api_base
        )
        self.agent = ChatAgent(
            system_message=self.system_message,
            model=model_instance,
            tools=tools
        )
        
        # Keep track of conversation history internally if needed, 
        # but ChatAgent manages its own history.
        self.agent.reset()

    def process_interaction(self, user_input: UserInput) -> str:
        """
        Process the user input using the CAMEL Agent.
        """
        # Create a User Message
        user_msg = BaseMessage(
            role_name="User",
            role_type=RoleType.USER,
            meta_dict=None,
            content=user_input.text or "(No text input)"
        )
        
        # Step the agent
        # The agent will autonomously decide to call tools (Perception -> Logic -> Response)
        try:
            response = self.agent.step(user_msg)
            
            # The response object contains the agent's reply
            if response.msgs:
                content = response.msgs[0].content
                # Simple filter to remove common internal logs if they leak into output
                # (Though usually logs go to stderr, sometimes LLMs hallucinate them if context includes tool outputs)
                return content
            else:
                return "I'm having trouble thinking right now."
                
        except Exception as e:
            # Fallback for errors (e.g., API key missing in test environment)
            return f"System Error: {str(e)}"

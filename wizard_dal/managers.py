from typing import Dict, Optional, List
from .models import Base, Agent, Conversation, ConversationResponse
from .repository import AgentRepository, ConversationRepository, model_to_dict
import json

class AgentManager:
    def __init__(self, agent_name="Agent Name"):
        self.agent = Agent()
        self.configure_agent()
        self.agent.AgentName = agent_name

    def get_db_session(self):
        agent_repository = AgentRepository()
        return agent_repository.get_session()
    
    def configure_agent(self):
        self.agent.AgentName = "Aggregation Agent"
        self.agent.AgentPath = "src/aggregator_agent/aggregation.py"
        self.agent.AgentClassName = "aggregation"
        self.agent.Description = "Aggregation Agent, this will access relevant APIs and return the response and store it accordingly"
        self.agent.IsActive = True
        self.agent.RedisChannel = "AGGREGATION_CHANNEL"
        self.agent.Configurations = "{\"APIs\": [\"Articles\", \"StockPrices\", \"FinancialRatios\", \"FinancialStatements\"]}"
        self.agent.ShowResponse = True
        self.agent.ResponseOrder = 0
        self.agent.TriggerOn = "{\"InitiatedBy\": [\"Argaam Wizard\"], \"Action\": [\"Start\", \"Stop\"]}"
        self.agent.OnError = "{\"Notify\": [\"Redis\", \"Alerta\"], \"Action\": [\"Retry\", \"Stop\"]}"
        self.agent.OnSuccess = "{\"Notify\": [\"Redis\"], \"Action\": [\"SaveResponse\", \"Stop\"]}"

    def initialize_refresh_agent(self):
        agent_repository = AgentRepository()
        db_session = agent_repository.get_session()
        self.agent = agent_repository.register_or_update_agent(db_session, self.agent)

    def update_status(self,agent_id, status):
        agent_repository = AgentRepository()
        db_session = agent_repository.get_session()
        self.agent = agent_repository.update_agent_status(db_session, agent_id, status)

    def get_active_agents(self):
        agent_repository = AgentRepository()
        db_session = agent_repository.get_session()
        return agent_repository.get_active_agents(db_session)

class ConversationManager:
    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.db_session = self.conversation_repo.get_session()

    def create_conversation(self, conversation_data: Dict) -> Optional[Conversation]:
        """
        Creates a new conversation and returns the created conversation object.
        """
        return self.conversation_repo.create_conversation(self.db_session, conversation_data)
    
    def add_conversation_response(self, response_data: Dict) -> Optional[ConversationResponse]:
        """
        Adds a response to an existing conversation based on the response data provided.
        """
        return self.conversation_repo.create_conversation_response(self.db_session, response_data)
    
    def update_conversation(self, conversation_id: int, update_data: Dict) -> Optional[Conversation]:
        """
        Updates an existing conversation with the provided update data.
        """
        return self.conversation_repo.update_conversation(self.db_session, conversation_id, update_data)
    
    def get_conversation_by_id(self, conversation_id: int) -> str:
        """
        Retrieves a conversation by its ID and returns it in a JSON format.
        """
        conversation = self.conversation_repo.get_conversation_by_id(self.db_session, conversation_id)
        if conversation:
            return json.dumps(model_to_dict(conversation))
        return json.dumps({})  # Return an empty object if not found

    def get_conversation_response_for_agent(self, conversation_id: int, agent_id: Optional[int] = None) -> str:
        """
        Retrieves conversation responses for a given conversation ID and agent ID,
        and returns them in a JSON format.
        """
        responses = self.conversation_repo.get_conversation_responses_for_agent(self.db_session, conversation_id, agent_id)
        return json.dumps([response for response in responses])
    
    def get_active_conversations_by_user_id(self, user_id: int) -> str:
        """
        Retrieves active conversations for a given user ID.
        """
        try:
            active_conversations = self.conversation_repo.get_active_conversations_by_user_id(self.db_session, user_id)
            return json.dumps([conversation for conversation in active_conversations], default=str)  # Ensure datetime and UUID are serialized
        except Exception as e:
            print(f"Error retrieving active conversations for user ID {user_id}: {e}")
            return '[]' 
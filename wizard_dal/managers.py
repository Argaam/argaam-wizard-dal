from typing import Dict, Optional
from .models import Base, Agent, Conversation, ConversationResponse
from .repository import AgentRepository, ConversationRepository

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

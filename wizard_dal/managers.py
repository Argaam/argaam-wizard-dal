from .models import Base, Agent
from .repository import AgentRepository

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

# Assuming Agent is imported from .models
from .models import Base, User, Agent  # Ensure Agent is imported here
from .repository import BaseRepository
from sqlalchemy.orm import Session
from typing import Dict, Optional

class AgentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Agent)
    
    def get_by_name(self, db_session: Session, agent_name: str) -> Optional[Agent]:
        return db_session.query(Agent).filter(Agent.AgentName == agent_name).first()
    
    def register_or_update_agent(self, db_session: Session, agent_data: Dict) -> Agent:
        """
        Registers a new agent if not exists, or updates it based on provided dictionary.
        
        :param db_session: The database session to use.
        :param agent_data: A dictionary with agent's data.
        :return: The registered or updated Agent instance.
        """
        existing_agent = self.get_by_name(db_session, agent_data['AgentName'])
        if existing_agent:
            # Update existing agent with provided data
            for key, value in agent_data.items():
                setattr(existing_agent, key, value)
            db_session.commit()
            db_session.refresh(existing_agent)
            return existing_agent
        else:
            # Register new agent
            new_agent = Agent(**agent_data)
            db_session.add(new_agent)
            db_session.commit()
            db_session.refresh(new_agent)
            return new_agent

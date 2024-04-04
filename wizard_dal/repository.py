from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import uuid
from datetime import datetime

import os
from sqlalchemy.orm import Session, joinedload
from typing import Type, Generic, TypeVar, List 
from .models import Base, User , Agent, Conversation, ConversationResponse # Ensure you import all your model classes here as needed
from typing import Dict, Optional
from dotenv import load_dotenv
load_dotenv()
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
driver = 'ODBC Driver 17 for SQL Server'


DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def model_to_dict(model_instance):
    """
    Converts a SQLAlchemy model instance into a dictionary, handling datetime and UUID objects.
    """
    return {
        column.name: (
            getattr(model_instance, column.name).isoformat() if isinstance(getattr(model_instance, column.name), datetime)
            else str(getattr(model_instance, column.name)) if isinstance(getattr(model_instance, column.name), uuid.UUID)
            else getattr(model_instance, column.name)
        )
        for column in model_instance.__table__.columns
    }
T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_session(self):
        return SessionLocal()
    
    def get_by_id(self, db_session: Session, id: int) -> T:
        try:
            return db_session.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error as appropriate
            print(f"Error retrieving {self.model.__name__} by id: {e}")
            return None

    def get_all(self, db_session: Session) -> List[T]:
        try:
            return db_session.query(self.model).all()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error retrieving all {self.model.__name__}: {e}")
            return []

    def create(self, db_session: Session, obj_in) -> T:
        try:
            obj = self.model(**obj_in)
            db_session.add(obj)
            db_session.commit()
            db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error creating {self.model.__name__}: {e}")
            return None

    def update(self, db_session: Session, obj: T, obj_in) -> T:
        try:
            for var, value in vars(obj_in).items():
                setattr(obj, var, value) if value else None
            db_session.commit()
            db_session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error updating {self.model.__name__}: {e}")
            return None

    def delete(self, db_session: Session, id: int) -> None:
        try:
            obj = db_session.query(self.model).get(id)
            if obj:
                db_session.delete(obj)
                db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error
            print(f"Error deleting {self.model.__name__}: {e}")


# Extend the base repository for the User model
class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db_session: Session, email: str) -> User:
        return db_session.query(User).filter(User.EmailAddress == email).first()
    
    def create_user(self, db_session: Session, user_data: Dict) -> Optional[User]:
        """
        Creates a new User in the database.

        :param db_session: The database session to use.
        :param user_data: A dictionary containing the user data. Expected keys are
                            'EmailAddress', 'DisplayName', and any other fields relevant to the User model.
        :return: The newly created User instance, or None if the creation failed.
        """
        try:
            # Ensure the email address is unique
            existing_user = self.get_by_email(db_session, user_data['EmailAddress'])
            if existing_user is not None:
                print("A user with this email address already exists.")
                return None

            # Create a new User instance
            new_user = User(
                EmailAddress=user_data['EmailAddress'],
                DisplayName=user_data.get('DisplayName', '')  # Use an empty string as default if not provided
                # Add other fields as necessary
            )
            db_session.add(new_user)
            db_session.commit()
            db_session.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error creating User: {e}")
            return None

class AgentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Agent)
    
    def get_by_name(self, db_session: Session, agent_name: str) -> Optional[Agent]:
        return db_session.query(Agent).filter(Agent.AgentName == agent_name).first()

    def get_active_agents(self, db_session: Session) -> List[Agent]:
        """
        Retrieves all active agents from the database.
        
        :param db_session: The database session to use.
        :return: A list of Agent objects that are active.
        """
        return db_session.query(self.model).filter(self.model.IsActive == True).all()
    def update_agent_status(self, db_session: Session, agent_id: int, new_status: str) -> Optional[Agent]:
        """
        Updates the status of an agent and the timestamp when the status was changed.
        
        :param db_session: The database session to use.
        :param agent_id: The ID of the agent to update.
        :param new_status: The new status to set.
        :return: The updated Agent object, or None if not found.
        """
        agent = db_session.query(self.model).filter(self.model.AgentID == agent_id).first()
        if agent:
            agent.Status = new_status
            agent.StatusChangedOn = datetime.now()  # Assuming you want to use UTC time
            db_session.commit()
            return agent
        else:
            return None
    def register_or_update_agent(self, db_session: Session, agent_obj: Agent) -> Agent:
        """
        Registers a new agent if not exists, or updates it based on the provided Agent object.
        
        :param db_session: The database session to use.
        :param agent_obj: An Agent object with the agent's data.
        :return: The registered or updated Agent instance.
        """
        # Assuming AgentName is a unique identifier for the agent
        existing_agent = self.get_by_name(db_session, agent_obj.AgentName)
        if existing_agent:
            # Update existing agent with provided Agent object data
            # You can list here all the attributes you want to update
            # existing_agent.AgentPath = agent_obj.AgentPath
            # existing_agent.AgentClassName = agent_obj.AgentClassName
            # existing_agent.Description = agent_obj.Description
            # existing_agent.IsActive = agent_obj.IsActive
            # existing_agent.RedisChannel = agent_obj.RedisChannel
            # existing_agent.Configurations = agent_obj.Configurations
            # existing_agent.ShowResponse = agent_obj.ShowResponse
            # existing_agent.ResponseOrder = agent_obj.ResponseOrder
            # existing_agent.TriggerOn = agent_obj.TriggerOn
            # existing_agent.OnError = agent_obj.OnError
            # existing_agent.OnSuccess = agent_obj.OnSuccess

            # db_session.commit()
            # db_session.refresh(existing_agent)
            db_session.commit()
            db_session.refresh(existing_agent)  # Refresh to prevent DetachedInstanceError
            return existing_agent
        else:
            # Register new agent
            db_session.add(agent_obj)
            db_session.commit()
            db_session.refresh(agent_obj)
            return agent_obj

class ConversationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Conversation)

    def get_conversation_by_id_from_db(self, db_session: Session, id: int) -> Conversation:
        try:
            return db_session.query(self.model).filter(self.model.ConversationID == id).first()
        except SQLAlchemyError as e:
            db_session.rollback()
            # Log the error as appropriate
            print(f"Error retrieving {self.model.__name__} by ConversationID: {e}")
            return None
    def create_conversation(self, db_session: Session, conversation_data: Dict) -> Optional[Conversation]:
        """
        Creates a new Conversation object and stores it in the database.
        """
        try:
            conversation = Conversation(**conversation_data, CreatedOn=datetime.now(), IsProcessed=False, IsActive=True)
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)
            return conversation
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error creating Conversation: {e}")
            return None
    
    def create_conversation_response(self, db_session: Session, response_data: Dict) -> Optional[ConversationResponse]:
        """
        Creates a new ConversationResponse object and associates it with a Conversation.
        """
        try:
            response = ConversationResponse(**response_data, StartedOn=datetime.now())
            db_session.add(response)
            db_session.commit()
            db_session.refresh(response)
            return response
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error creating ConversationResponse: {e}")
            return None
    
    def update_conversation(self, db_session: Session, conversation_id: int, update_data: Dict) -> Optional[Conversation]:
        """
        Updates an existing Conversation with new data.
        """
        try:
            conversation = db_session.query(Conversation).filter(Conversation.ConversationID == conversation_id).first()
            if conversation:
                for key, value in update_data.items():
                    setattr(conversation, key, value)
                db_session.commit()
                db_session.refresh(conversation)
                return conversation
            else:
                print(f"Conversation with ID {conversation_id} not found.")
                return None
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error updating Conversation: {e}")
            return None
    def get_conversation_by_id(self, db_session: Session, conversation_id: int) -> Optional[Conversation]:
        return self.get_conversation_by_id_from_db(db_session, conversation_id)

    def get_active_conversations_with_responses_by_user_id(self, db_session: Session, user_id: int, group_id: Optional[int] = None) -> List[Dict]:
        """
        Fetches active conversations for a given user ID, including their responses,
        optionally filtered by GroupID.
        
        Args:
            db_session (Session): The database session.
            user_id (int): The user ID to filter conversations.
            group_id (Optional[int], optional): The group ID to optionally filter conversations. Defaults to None.
            
        Returns:
            List[Dict]: A list of dictionaries where each dictionary includes a conversation and its responses.
        """
        try:
            # Start with a base query for active conversations by user ID
            query = db_session.query(Conversation).filter(
                Conversation.UserID == user_id,
                Conversation.IsActive == 1
            )
            
            # Apply an optional filter for GroupID if provided
            if group_id is not None:
                query = query.filter(Conversation.GroupID == group_id)

            conversations = query.all()

            results = []
            for conversation in conversations:
                # Convert the conversation model to a dictionary
                conversation_dict = model_to_dict(conversation)
                
                # Fetch responses for the current conversation
                responses = db_session.query(ConversationResponse).filter(
                    ConversationResponse.ConversationID == conversation.ConversationID
                ).all()
                
                # Convert each response model to a dictionary
                responses_dict = [model_to_dict(response) for response in responses]
                
                # Append the conversation with its responses to the results list
                results.append({
                    "Conversation": conversation_dict,
                    "Responses": responses_dict
                })
                
            return results
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error fetching active conversations with responses for user ID {user_id}: {e}")
            return []
    def get_conversation_responses_for_agent(self, db_session: Session, conversation_id: int, agent_id: Optional[int] = None) -> List[Dict]:
        """
        Fetches conversation responses for a given conversation ID, including agent details.
        Filters by agent ID if provided.
        """
        try:
            query = db_session.query(
                ConversationResponse,
                Agent.AgentName,
                Agent.IsActive.label('AgentActive'),
                Agent.ShowResponse
            ).join(
                Agent, ConversationResponse.AgentID == Agent.AgentID
            ).filter(
                ConversationResponse.ConversationID == conversation_id
            )

            # Apply agent_id filter if provided
            if agent_id is not None:
                query = query.filter(Agent.AgentID == agent_id)

            responses_with_agents = query.all()

            results = []
            for response, agent_name, agent_active, show_response in responses_with_agents:
                result = {
                    "ResponseID": model_to_dict(response)['ResponseID'], 
                    "ResponseBody": model_to_dict(response)['ResponseBody'], 
                    "ConversationID": model_to_dict(response)['ConversationID'], 
                    "CompletedOn": model_to_dict(response)['CompletedOn'], 
                    "AgentName": agent_name,
                    "AgentActive": agent_active,
                    "ShowResponse": show_response
                }
                results.append(result)
            return results
        except SQLAlchemyError as e:
            db_session.rollback()
            print(f"Error fetching conversation responses for agent: {e}")
            return []

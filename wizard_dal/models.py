from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Unicode, UnicodeText, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

# Then, use `UNIQUEIDENTIFIER` as your column type

import os

server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
driver = 'ODBC Driver 17 for SQL Server'

DATABASE_URL = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"

engine = create_engine(DATABASE_URL, echo=True, pool_size=20, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'Agents'

    AgentID = Column(Integer, primary_key=True)
    AgentName = Column(Unicode(256), nullable=False)
    AgentPath = Column(String(512), nullable=False)
    AgentClassName = Column(String(128), nullable=False)
    Description = Column(Unicode(512))
    IsActive = Column(Boolean, nullable=False)
    RedisChannel = Column(String(64), nullable=False)
    Configurations = Column(Unicode(2048))
    ShowResponse = Column(Boolean, nullable=False)
    ResponseOrder = Column(Integer, nullable=False)
    TriggerOn = Column(Unicode(2048))
    OnError = Column(Unicode(2048))
    OnSuccess = Column(Unicode(10))
    Status = Column(Unicode(256), nullable=True)
    StatusChangedOn = Column(DateTime, nullable=True)
    
    # Relationships
    conversation_responses = relationship("ConversationResponse", back_populates="agent")

class ChatGroup(Base):
    __tablename__ = 'ChatGroups'

    GroupID = Column(Integer, primary_key=True)
    GroupName = Column(Unicode(255), nullable=False)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    CreatedOn = Column(DateTime, nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="chat_group")
    user = relationship("User", back_populates="chat_groups")


class User(Base):
    __tablename__ = 'Users'

    UserID = Column(Integer, primary_key=True)
    EmailAddress = Column(Unicode(255), nullable=False)
    DisplayName = Column(Unicode(512))
    
    # Relationships
    chat_groups = relationship("ChatGroup", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    user_context = relationship("UserContext", back_populates="user")


class Conversation(Base):
    __tablename__ = 'Conversations'

    ConversationID = Column(Integer, primary_key=True)
    UserPrompt = Column(Unicode(1024), nullable=False)
    CreatedOn = Column(DateTime, nullable=False)
    IsProcessed = Column(Boolean, nullable=False)
    PercentCompleted = Column(Integer, default=0, nullable=False)
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    LanguageID = Column(Integer, nullable=False)
    SelectedCompany = Column(Unicode(512))
    GroupID = Column(Integer, ForeignKey('ChatGroups.GroupID'), nullable=False)
    GUID = Column(UNIQUEIDENTIFIER, nullable=False)
    IsActive = Column(Boolean, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    chat_group = relationship("ChatGroup", back_populates="conversations")
    conversation_responses = relationship("ConversationResponse", back_populates="conversation")


class Company(Base):
    __tablename__ = 'companies'

    id = Column(String(255), primary_key=True)
    full_name_ar = Column(Unicode(255))
    full_name_en = Column(String(255))
    name_ar = Column(Unicode(255))
    name_en = Column(String(255))
    logo_url = Column(Unicode(255))


class ConversationData(Base):
    __tablename__ = 'conversation_data'

    id = Column(Integer, primary_key=True)
    json_data = Column(String)  # Using String type for the text column, adjust if needed

class ConversationResponse(Base):
    __tablename__ = 'ConversationResponses'

    ResponseID = Column(Integer, primary_key=True)
    ResponseBody = Column(Unicode(1024))
    AgentID = Column(Integer, ForeignKey('Agents.AgentID'), nullable=False)
    ConversationID = Column(Integer, ForeignKey('Conversations.ConversationID'), nullable=False)
    StartedOn = Column(DateTime, nullable=False)
    CompletedOn = Column(DateTime)

    # Relationships
    agent = relationship("Agent", back_populates="conversation_responses")
    conversation = relationship("Conversation", back_populates="conversation_responses")


class Feedback(Base):
    __tablename__ = 'Feedbacks'

    FeedbackID = Column(Integer, primary_key=True)
    FeedbackText = Column(Unicode(1800))
    Emotions = Column(Unicode(64))
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    CreatedOn = Column(DateTime, nullable=False)
    ResponseID = Column(Integer, ForeignKey('ConversationResponses.ResponseID'), nullable=False)

    # Relationships
    user = relationship("User", back_populates="feedbacks")
    conversation_response = relationship("ConversationResponse")


class FinancialRatioField(Base):
    __tablename__ = 'fr_fields'

    fr_id = Column(String(255), primary_key=True)
    financial_ratio = Column(Unicode(255))
    other_names = Column(Unicode(255))
    financial_ratio_ar = Column(Unicode(255))
    other_names_ar = Column(Unicode(255))


class FinancialStatementField(Base):
    __tablename__ = 'fs_fields'

    ftf_if = Column(String(255), primary_key=True)
    fsf_id = Column(String(255))
    fs_field_name = Column(Unicode(255))
    alternative_names = Column(Unicode(255))
    fs_field_name_ar = Column(Unicode(255))
    alternative_names_ar = Column(Unicode(255))


class UserContext(Base):
    __tablename__ = 'UserContext'

    ContextID = Column(Integer, primary_key=True)
    ContextText = Column(Unicode(2048), nullable=False)
    CreatedOn = Column(DateTime, nullable=False)
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    DisabledAgents = Column(Unicode(256), nullable=False)
    MultifacetedAnalysis = Column(Boolean, default=True, nullable=False)
    MA_MaxCount = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="user_context")

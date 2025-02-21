from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Department(Base):
    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, nullable=False)

    # Relationships
    users = relationship("User", back_populates="department")
    talents = relationship("Talent", back_populates="department")

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, nullable=False)
    skill_category = Column(String, nullable=False)

    # Relationships
    talent_skills = relationship("TalentSkill", back_populates="skill")

class Talent(Base):
    __tablename__ = "talents"

    talent_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    job_title = Column(String)
    employment_type = Column(String)
    department_id = Column(Integer, ForeignKey("department.department_id"))
    hire_date = Column(DateTime)
    basic_salary = Column(Float)
    gender = Column(String)
    date_of_birth = Column(DateTime)
    marital_status = Column(Boolean)
    total_experience_years = Column(Float)
    career_preferences = Column(String)
    availability_status = Column(String)

    # Relationships
    department = relationship("Department", back_populates="talents")
    talent_skills = relationship("TalentSkill", back_populates="talent")
    education = relationship("Education", back_populates="talent")
    professional_experience = relationship("ProfessionalExperience", back_populates="talent")
    project_assignments = relationship("ProjectAssignment", back_populates="talent")

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    starred = Column(Boolean, default=False)
    cv_count = Column(Integer, default=0)
    progress = Column(Integer)
    status = Column(String)
    budget = Column(Float)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    start_date = Column(DateTime)
    required_skills = Column(ARRAY(Integer))
    min_experience_years = Column(Integer)
    team_size = Column(Integer)
    project_description = Column(String)

    # Relationships
    user = relationship("User", back_populates="projects")
    project_assignments = relationship("ProjectAssignment", back_populates="project")

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.department_id"))
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Add this line
    role = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)  # Add this line

    # Relationships
    department = relationship("Department", back_populates="users")
    projects = relationship("Project", back_populates="user")
    chats = relationship("Chat", back_populates="user")

class TalentSkill(Base):
    __tablename__ = "talentskills"

    talent_skill_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    proficiency_level = Column(Integer)
    years_of_experience = Column(Float)
    last_used_date = Column(DateTime)

    # Relationships
    talent = relationship("Talent", back_populates="talent_skills")
    skill = relationship("Skill", back_populates="talent_skills")

class Education(Base):
    __tablename__ = "education"

    education_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    institution_name = Column(String)
    qualification_type = Column(String)
    field_of_study = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Relationships
    talent = relationship("Talent", back_populates="education")

class ProfessionalExperience(Base):
    __tablename__ = "professionalexperience"

    experience_id = Column(Integer, primary_key=True, index=True)
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    company_name = Column(String)
    job_title = Column(String)
    location = Column(String)
    employment_type = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_current_job = Column(Boolean)
    description = Column(String)
    key_achievements = Column(ARRAY(String))

    # Relationships
    talent = relationship("Talent", back_populates="professional_experience")

class ProjectAssignment(Base):
    __tablename__ = "projectassignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    talent_id = Column(Integer, ForeignKey("talents.talent_id"))
    role = Column(String)
    assignment_start_date = Column(DateTime)
    assignment_end_date = Column(DateTime)
    performance_rating = Column(Integer)

    # Relationships
    project = relationship("Project", back_populates="project_assignments")
    talent = relationship("Talent", back_populates="project_assignments")


class Chat(Base):
    __tablename__ = "chat"

    conversation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String, nullable=False, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat.conversation_id"))
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat = relationship("Chat", back_populates="messages")

# class Chat(Base):
#     __tablename__ = "chat"

#     conversation_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     title = Column(String, nullable=False, default="New Chat")
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     user = relationship("User", back_populates="chats")
#     messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

# class Message(Base):
#     __tablename__ = "messages"

#     message_id = Column(Integer, primary_key=True, index=True)
#     conversation_id = Column(Integer, ForeignKey("chat.conversation_id"))
#     role = Column(String, nullable=False)  # 'user' or 'assistant'
#     content = Column(String, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     chat = relationship("Chat", back_populates="messages")
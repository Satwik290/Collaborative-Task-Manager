"""
Database models for collaborative task manager.
Constraints enforced at DB level to prevent invalid states.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Integer, ForeignKey, 
    UniqueConstraint, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class User(Base):
    """User account"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workspaces_created = relationship("Workspace", back_populates="creator")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user")
    tasks_created = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    comments = relationship("TaskComment", back_populates="author")


class Workspace(Base):
    """Collaboration workspace/team"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="workspaces_created")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    """Membership in a workspace with role"""
    __tablename__ = "workspace_members"
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(20), nullable=False)  # 'admin' or 'member'
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraint: role must be valid enum value
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="valid_workspace_role"),
    )
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")


class TaskStatus(str, enum.Enum):
    """Valid task statuses"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """Task in a workspace"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=True)
    status = Column(String(20), nullable=False, default="todo")
    priority = Column(String(20), nullable=False, default="medium")
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('todo', 'in_progress', 'done')", name="valid_task_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high')", name="valid_task_priority"),
    )
    
    # Relationships
    workspace = relationship("Workspace", back_populates="tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="tasks_created")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="tasks_assigned")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")


class TaskComment(Base):
    """Comment on a task"""
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")

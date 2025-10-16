from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    @staticmethod
    def get_todos(db: Session, user: User) -> List[Todo]:
        """Get all todos for a user"""
        return db.query(Todo).filter(Todo.user_id == user.id).all()
    
    @staticmethod
    def get_todo_by_id(db: Session, todo_id: str, user: User) -> Optional[Todo]:
        """Get a specific todo by ID"""
        return db.query(Todo).filter(
            Todo.id == todo_id,
            Todo.user_id == user.id
        ).first()
    
    @staticmethod
    def create_todo(db: Session, todo: TodoCreate, user: User) -> Todo:
        """Create a new todo"""
        db_todo = Todo(
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            user_id=user.id
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    @staticmethod
    def update_todo(db: Session, todo_id: str, todo: TodoUpdate, user: User) -> Optional[Todo]:
        """Update an existing todo"""
        db_todo = db.query(Todo).filter(
            Todo.id == todo_id,
            Todo.user_id == user.id
        ).first()
        
        if not db_todo:
            return None
        
        # Update fields if provided
        if todo.title is not None:
            db_todo.title = todo.title
        if todo.description is not None:
            db_todo.description = todo.description
        if todo.completed is not None:
            db_todo.completed = todo.completed
        
        db.commit()
        db.refresh(db_todo)
        return db_todo
    
    @staticmethod
    def delete_todo(db: Session, todo_id: str, user: User) -> bool:
        """Delete a todo"""
        db_todo = db.query(Todo).filter(
            Todo.id == todo_id,
            Todo.user_id == user.id
        ).first()
        
        if not db_todo:
            return False
        
        db.delete(db_todo)
        db.commit()
        return True
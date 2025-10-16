from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService

router = APIRouter()


@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all todos for the current user"""
    todos = TodoService.get_todos(db, current_user)
    return [TodoResponse.from_orm(todo) for todo in todos]


@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new todo"""
    new_todo = TodoService.create_todo(db, todo, current_user)
    return TodoResponse.from_orm(new_todo)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific todo by ID"""
    todo = TodoService.get_todo_by_id(db, todo_id, current_user)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return TodoResponse.from_orm(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing todo"""
    updated_todo = TodoService.update_todo(db, todo_id, todo_update, current_user)
    if not updated_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return TodoResponse.from_orm(updated_todo)


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a todo"""
    success = TodoService.delete_todo(db, todo_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return {"message": "Todo deleted successfully"}
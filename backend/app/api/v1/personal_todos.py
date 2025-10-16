from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.personal_deps import get_user_from_personal_token
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService

router = APIRouter()


@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_personal_token)
):
    """Get all todos for the authenticated user"""
    todos = TodoService.get_todos(db, user)
    return [TodoResponse.from_orm(todo) for todo in todos]


@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_personal_token)
):
    """Create a new todo"""
    new_todo = TodoService.create_todo(db, todo, user)
    return TodoResponse.from_orm(new_todo)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_personal_token)
):
    """Get a specific todo by ID"""
    todo = TodoService.get_todo_by_id(db, todo_id, user)
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
    user: dict = Depends(get_user_from_personal_token)
):
    """Update an existing todo"""
    updated_todo = TodoService.update_todo(db, todo_id, todo_update, user)
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
    user: dict = Depends(get_user_from_personal_token)
):
    """Delete a todo"""
    success = TodoService.delete_todo(db, todo_id, user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return {"message": "Todo deleted successfully"}
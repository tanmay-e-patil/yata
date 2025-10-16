from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.oauth_deps import get_oauth_client
from app.models.oauth_client import OAuthClient
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService
from app.models.user import User

router = APIRouter()


async def get_user_for_client(db: Session, client: OAuthClient) -> User:
    """Get the user associated with an OAuth client.
    In a real implementation, you might have a mapping between OAuth clients and users.
    For now, we'll use the first user (this should be improved in production)."""
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found for this client"
        )
    return user


@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    db: Session = Depends(get_db),
    client: OAuthClient = Depends(get_oauth_client)
):
    """Get all todos for the OAuth client's user"""
    user = await get_user_for_client(db, client)
    todos = TodoService.get_todos(db, user)
    return [TodoResponse.from_orm(todo) for todo in todos]


@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db),
    client: OAuthClient = Depends(get_oauth_client)
):
    """Create a new todo"""
    user = await get_user_for_client(db, client)
    new_todo = TodoService.create_todo(db, todo, user)
    return TodoResponse.from_orm(new_todo)


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    db: Session = Depends(get_db),
    client: OAuthClient = Depends(get_oauth_client)
):
    """Get a specific todo by ID"""
    user = await get_user_for_client(db, client)
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
    client: OAuthClient = Depends(get_oauth_client)
):
    """Update an existing todo"""
    user = await get_user_for_client(db, client)
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
    client: OAuthClient = Depends(get_oauth_client)
):
    """Delete a todo"""
    user = await get_user_for_client(db, client)
    success = TodoService.delete_todo(db, todo_id, user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return {"message": "Todo deleted successfully"}
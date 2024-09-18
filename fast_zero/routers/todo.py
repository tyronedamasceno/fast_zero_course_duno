from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.annotated_types import T_CurrentUser, T_Session
from fast_zero.models import Todo, TodoState
from fast_zero.schemas import TodoList, TodoPublic, TodoSchema, TodoUpdate

router = APIRouter(prefix='/todos', tags=['todos'])


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
def create_todo(todo: TodoSchema, session: T_Session, user: T_CurrentUser):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos( # noqa
    session: T_Session,
    user: T_CurrentUser,
    title: str | None = None,
    state: TodoState | None = None,
    limit: int = 10,
    skip: int = 0,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.icontains(title))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.limit(limit).offset(skip)).all()

    return {'todos': todos}


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    session.delete(todo)
    session.commit()


@router.patch('/{todo_id}', response_model=TodoPublic)
def patch_todo(
    todo_id: int, session: T_Session, user: T_CurrentUser, todo: TodoUpdate
):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )
    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo

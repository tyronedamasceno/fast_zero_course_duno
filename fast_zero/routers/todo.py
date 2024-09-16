from http import HTTPStatus

from fastapi import APIRouter

from fast_zero.annotated_types import T_CurrentUser, T_Session
from fast_zero.models import Todo
from fast_zero.schemas import TodoPublic, TodoSchema

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

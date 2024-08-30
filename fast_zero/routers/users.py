from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from fast_zero.annotated_types import T_CurrentUser, T_Session
from fast_zero.decorators import check_user_permission
from fast_zero.models import User
from fast_zero.schemas import UserList, UserPublic, UserSchema
from fast_zero.security import get_password_hash

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/{user_id}', response_model=UserPublic)
@check_user_permission
def read_user(user_id: int, current_user: T_CurrentUser):
    return current_user


@router.get('/', response_model=UserList)
def read_users(session: T_Session, limit: int = 10, skip: int = 0):
    users = session.scalars(select(User).limit(limit).offset(skip))
    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
@check_user_permission
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)

    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
@check_user_permission
def delete_user(user_id: int, session: T_Session, current_user: T_CurrentUser):
    session.delete(current_user)
    session.commit()

from functools import wraps
from http import HTTPStatus

from fastapi import HTTPException

from fast_zero.annotated_types import T_CurrentUser


def check_user_permission(func):
    @wraps(func)
    def wrapper(user_id: int, current_user: T_CurrentUser, *args, **kwargs):
        if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Not enough permission',
            )
        return func(
            user_id=user_id, current_user=current_user, *args, **kwargs
        )

    return wrapper

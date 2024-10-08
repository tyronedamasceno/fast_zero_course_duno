from http import HTTPStatus
from unittest import mock

import pytest
from fastapi import HTTPException
from jwt import decode, encode
from jwt.exceptions import PyJWTError

from fast_zero.security import create_access_token, get_current_user, settings


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)
    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result['sub'] == data['sub']
    assert result['exp']


def test_get_current_user_invalid_token():
    with mock.patch('fast_zero.security.decode', side_effect=PyJWTError):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token='invalid_token')

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'


def test_get_current_user_with_token_without_username_sub():
    token = encode(
        {'foo': 'bar'}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'


def test_get_current_user_with_token_with_invalid_username_sub(session):
    token = encode(
        {'sub': 'invalid_username'},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, session=session)

    assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc_info.value.detail == 'Could not validate credentials'

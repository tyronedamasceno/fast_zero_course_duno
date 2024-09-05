from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time
from zoneinfo import ZoneInfo

from fast_zero.settings import Settings


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user._clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_get_token_invalid_credentials(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_expired_token(client, user, token):
    expired_date = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES + 1
    )
    with freeze_time(expired_date):
        response = client.get(
            f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_valid_token(client, token):
    response = client.post(
        '/auth/refresh-token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['token_type'] == 'Bearer'
    assert 'access_token' in data


def test_trying_refresh_expired_token(client, token):
    expired_date = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES + 1
    )
    with freeze_time(expired_date):
        response = client.post(
            '/auth/refresh-token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}

from http import HTTPStatus


def test_read_root_should_return_ok_and_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'user',
            'password': 'password',
            'email': 'user@test.com',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'user',
        'email': 'user@test.com',
    }


def test_read_user(client):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'user',
        'email': 'user@test.com',
    }


def test_read_user_not_found(client):
    response = client.get('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'user',
                'email': 'user@test.com',
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'new_user',
            'password': 'password',
            'email': 'user@test.com',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'new_user',
        'email': 'user@test.com',
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'new_user',
            'password': 'password',
            'email': 'user@test.com',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_not_found(client):
    response = client.delete('/users/2')

    assert response.status_code == HTTPStatus.NOT_FOUND

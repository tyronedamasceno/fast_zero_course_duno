from http import HTTPStatus


def test_create_todo(client, user, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Todo Test',
            'description': 'nice todo',
            'state': 'draft',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Todo Test',
        'description': 'nice todo',
        'state': 'draft',
        'user_id': user.id,
    }

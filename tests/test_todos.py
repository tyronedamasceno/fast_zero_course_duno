from http import HTTPStatus

from fast_zero.models import TodoState
from tests.conftest import TodoFactory


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


def test_list_todos_without_filter_return_all_todos(
    session, client, user, token
):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_title_filter(session, client, user, token):
    todo_title_up = TodoFactory(title='Bring Sally Up', user_id=user.id)
    todo_title_down = TodoFactory(title='Bring Sally Down', user_id=user.id)

    session.bulk_save_objects([todo_title_up, todo_title_down])
    session.commit()

    response = client.get(
        '/todos/?title=up',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['title'] == todo_title_up.title


def test_list_todos_state_filter(session, client, user, token):
    todo_draft = TodoFactory(state=TodoState.draft, user_id=user.id)
    todo_done = TodoFactory(state=TodoState.done, user_id=user.id)

    session.bulk_save_objects([todo_draft, todo_done])
    session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == 1
    assert response.json()['todos'][0]['state'] == TodoState.draft


def test_delete_todo_success(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_todo_not_found(client, token):
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_patch_todo_invalid_id(client, token):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_patch_todo(client, token, user, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test title',
            'description': 'test description',
            'state': 'done'
        }
    )

    assert response.status_code == HTTPStatus.OK
    session.refresh(todo)

    assert todo.title == 'test title'
    assert todo.description == 'test description'
    assert todo.state == TodoState.done

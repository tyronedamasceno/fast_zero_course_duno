from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):
    user = User(
        username='tyrone', email='tyrone@test.com', password='s3cr3tpwd'
    )
    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.username == 'tyrone'))

    assert result.id is not None
    assert result.email == 'tyrone@test.com'

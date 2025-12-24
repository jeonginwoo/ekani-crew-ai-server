import uuid
from datetime import datetime

from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus


def test_create_mbti_test_session():
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    created_at = datetime.now()

    session = MBTITestSession(
        id=session_id,
        user_id=user_id,
        test_type=TestType.AI,
        status=TestStatus.IN_PROGRESS,
        created_at=created_at,
    )

    assert session.id == session_id
    assert session.user_id == user_id
    assert session.test_type == TestType.AI
    assert session.status == TestStatus.IN_PROGRESS
    assert session.created_at == created_at
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource


def test_create_mbti_message():
    message = MBTIMessage(
        role=MessageRole.ASSISTANT,
        content="당신은 어떤 종류의 책을 가장 좋아하나요?",
        source=MessageSource.AI,
    )

    assert message.role == MessageRole.ASSISTANT
    assert message.content == "당신은 어떤 종류의 책을 가장 좋아하나요?"
    assert message.source == MessageSource.AI
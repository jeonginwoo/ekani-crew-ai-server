from app.mbti_test.application.port.output.question_provider_port import QuestionProviderPort
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource


class FakeQuestionProvider(QuestionProviderPort):
    def get_initial_question(self) -> MBTIMessage:
        return MBTIMessage(
            role= MessageRole.ASSISTANT,
            content=(
                "혹시... 너도 가끔 네 MBTI가 헷갈리지 않아? 🤔\n\n"
                "검사할 때마다 바뀌는 것 같기도 하고 말이야.\n\n"
                "그래서 내가 왔어! 난 **Nunchi(눈치)**야. 👀\n\n"
                "네가 무심코 던진 말속에 숨겨진 0.1%의 성향까지 내가 싹 다 캐치해 줄게.\n\n"
                "얼마나 정확한지 궁금하지? 지금 바로 확인해 봐! 👇"
            ),
            source= MessageSource.HUMAN,
        )

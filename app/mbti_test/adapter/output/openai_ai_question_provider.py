from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.domain.models import (
    AIQuestion,
    AIQuestionResponse,
    GenerateAIQuestionCommand,
    AnalyzeAnswerCommand,
    AnalyzeAnswerResponse,
    MessageRole,
)

def _turn_target_dimensions(turn: int) -> List[str]:
    """
    각 턴별 목표 차원을 반환합니다.
    12개 턴에 걸쳐 각 차원을 3번씩 질문합니다.
    """
    # 턴 1: 라포/자가진단
    if turn == 1:
        return []

    # 4개 차원을 순환 (턴 2-12에서 각 차원 약 3번씩)
    dimension_cycle = ["E/I", "S/N", "T/F", "J/P"]
    # 턴 2부터 시작, 0-indexed로 변환 후 순환
    index = (turn - 2) % 4
    return [dimension_cycle[index]]


def _strip_markdown_fences(text: str) -> str:
    # response_format=json_object 를 쓰더라도 가끔 fence가 섞일 수 있어 방어
    text = text.strip()
    # ```json ... ``` or ``` ... ```
    fence_pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    m = re.match(fence_pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _parse_json_object(text: str) -> Dict[str, Any]:
    cleaned = _strip_markdown_fences(text)
    return json.loads(cleaned)


def _build_system_prompt() -> str:
    # 사과/AI 자기 언급 금지, 1~2개 질문, 2~3문장, 구체 사례 요청, 부족하면 예시 재요청
    return (
        "너는 MBTI 테스트를 진행하는 질문자다.\n"
        "규칙:\n"
        "- 매 턴 질문은 1~2개만 만든다.\n"
        "- 각 질문은 2~3문장으로 요청한다.\n"
        "- 정보가 부족하면 비슷한 유형의 질문을 요청하는 재질문을 포함한다.\n"
        "- 사과하지 말고, AI/모델/시스템 같은 자기 언급을 하지 않는다.\n"
        "- 출력은 반드시 JSON 하나이며, 아래 스키마를 지킨다.\n"
        '  {\"questions\":[{\"text\":\"...\", \"target_dimensions\":[\"E/I\"]}], \"turn\": n}\n'
        "- 질문 외의 설명/장식 문구를 넣지 않는다.\n"
        "톤/스타일:\n"
        "- 한국어 캐주얼 반말, 친근한 말투. 호칭 없이 '너'.\n"
        "- 이모지 1~2개와 감탄사(헐, ㅋㅋ 등) 섞기.\n"
        "- 상황 제시 후 선택/묘사 유도형 질문으로 마무리(물음표 필수).\n"
        "- 생활감 있는 소재(모임, 여행, SNS, 주말 계획 등)를 사용.\n"
        "- target_dimensions에 맞는 상황/어휘 선택(E/I: 사람 많은 자리 vs 혼자 등).\n"
        "- 최근 대화/사용자 키워드(예: 낚시)만 집착하지 말 것. 동일 주제는 연속 3턴 이상 반복 금지.\n"
        "- 각 턴은 목표 차원(E/I, S/N, T/F, J/P)에 맞춰 다른 상황/맥락을 사용. 직전 턴에서 쓴 소재/명사를 다시 쓰지 말 것.\n"
    )


def _build_user_prompt(command: GenerateAIQuestionCommand) -> str:
    targets = _turn_target_dimensions(command.turn)
    mode_line = (
        "질문 모드: 돌발(surprise)\n"
        "- 각 질문에 반드시 '예상 밖 상황/제약' 1개 이상 포함(예: 시간 압박, 갑작스런 변수, 낯선 장소·사람, 역할 강제).\n"
        "- 평범한 MBTI 질문(모임이 좋나/혼자가 좋나 등) 금지. 테스트 티 안 나게 일상/상황형으로 위장.\n"
        "- 사용자가 둘 중 하나를 선택해야 하는 형태로 묻고, 선택 이유 + 실제 경험 예시 1개를 요청.\n"
        "- 차원은 최소 1개만 겨냥(E/I, S/N, T/F, J/P 중 택1); target_dimensions에 명시.\n"
        "- 한국어 캐주얼 반말 + 이모지 1~2개, 2~3문장, 물음표로 끝내.\n"
        '- JSON만 반환: {"questions":[{"text":"...", "target_dimensions":["E/I"]}, {"text":"...", "target_dimensions":["S/N"]}], "turn": <int>}\n'
        "- 직전 3개 질문/답변과 다른 소재·상황을 사용해 중복 회피.\n"
        if command.question_mode == "surprise"
        else
        "질문 모드: 일반(normal)\n"
        "- 대화 맥락을 이어서 자연스럽게 후속 질문을 해라.\n"
    )

    # 턴 1은 라포/자가진단이지만, 그래도 차원 단서를 살짝 볼 수 있게 설계 가능
    target_line = (
        f"이번 턴 번호: {command.turn}\n"
        f"이번 턴 목표 차원: {targets if targets else '라포/자가진단(특정 차원 강제 없음)'}\n"
    )

    # 히스토리는 최근 메시지 위주로 충분 (세션 담당이 길이 제어 가능)
    history_lines = []
    for msg in command.history:
        role = msg.role.value if isinstance(msg.role, MessageRole) else str(msg.role)
        history_lines.append(f"{role}: {msg.content}")

    history_block = "\n".join(history_lines).strip() or "(히스토리 없음)"

    return (
        f"{mode_line}\n"
        f"{target_line}"
        "대화 히스토리:\n"
        f"{history_block}\n"
        "위 히스토리를 바탕으로 다음 질문 JSON만 출력해라."
    )


def _build_analysis_system_prompt() -> str:
    """답변 분석용 시스템 프롬프트"""
    return (
        "너는 MBTI 전문 분석가다. 사용자의 답변을 분석하여 MBTI 성향 점수를 매긴다.\n"
        "반드시 요청된 target_dimension 하나만 평가하고, 다른 축은 무시해라.\n"
        "\n"
        "## 규칙:\n"
        "- target_dimension은 EI, SN, TF, JP 중 하나다.\n"
        "- JSON만 반환한다. (마크다운/설명 금지)\n"
        "- 반환되는 dimension 값은 target_dimension과 동일해야 한다.\n"
        "- scores에는 해당 축의 두 키만 있어야 한다: EI=E/I, SN=S/N, TF=T/F, JP=J/P. 다른 키 금지.\n"
        "- 각 점수는 0~10 정수이며, 두 점수 합은 제한하지 않는다(단, 한쪽이 높으면 다른 쪽은 낮아야 한다는 상식적 범위 내).\n"
        "- reasoning은 한국어 1~2문장으로, 답변 내용만 근거로 작성한다.\n"
        "\n"
        "## 각 차원별 판단 기준 (매우 중요!):\n"
        "\n"
        "### S(감각) vs N(직관):\n"
        "- S: 구체적 사실 나열, 오감으로 느낀 것 묘사, '뭘 했는지' 설명, 실용적 답변\n"
        "- N: 추상적/비유적 표현, '왜/무슨 의미인지' 탐구, 가능성/패턴 언급, 상상력 발휘\n"
        "- 주의: '과거 이야기'를 한다고 S가 아님! 과거를 '의미/교훈' 관점으로 보면 N\n"
        "- 주의: '기억'을 언급해도 S가 아님! 기억에서 '패턴/의미'를 찾으면 N\n"
        "\n"
        "### T(사고) vs F(감정):\n"
        "- T: 논리적 분석, 효율/개선 제안, 원인 파악, 객관적 판단, 문제 해결 중심\n"
        "- F: 감정 표현, 공감/위로, 관계 배려, 조화 중시, 사람 감정 고려\n"
        "- 주의: '개선시켜준다', '효율적으로', '원인이 뭐냐'는 명백한 T\n"
        "- 주의: 직설적/팩폭 스타일도 T, 돌려말하며 배려하면 F\n"
        "\n"
        "### J(판단) vs P(인식):\n"
        "- J: 계획, 일정/마감, 체크리스트, 정리/구조화, 확정/결정\n"
        "- P: 즉흥, 그때 가서, 유연/변화, 느슨/옵션 열어두기, 막판 몰아하기\n"
        "\n"
        "### E(외향) vs I(내향):\n"
        "- E: 사람/교류/활동/외부 자극 선호, 말이 많고 즉각 반응\n"
        "- I: 혼자/내부 자극 선호, 깊은 생각, 말 수 적고 천천히 반응\n"
        "\n"
        "## 점수 부여 가이드:\n"
        "- 해당 차원의 양쪽에 0~10 점수를 준다.\n"
        "- 명확한 성향이면 차이를 크게 (예: 8:2), 애매하면 작게 (예: 5:4)\n"
        "- 출력 예: {\"dimension\": \"SN\", \"scores\": {\"S\": 3, \"N\": 7}, \"reasoning\": \"분석 근거\"}\n"
    )



def _build_analysis_user_prompt(command: AnalyzeAnswerCommand) -> str:
    """답변 분석용 유저 프롬프트"""
    # 히스토리 구성
    history_lines = []
    for msg in command.history:
        role = msg.role.value if isinstance(msg.role, MessageRole) else str(msg.role)
        history_lines.append(f"{role}: {msg.content}")

    history_block = "\n".join(history_lines).strip() or "(이전 대화 없음)"

    return (
        "이전 대화 맥락:\n"
        f"target_dimension: {command.target_dimension}\n"
        f"반드시 이 축만 판단해라: {command.target_dimension}. 다른 축(EI/SN/TF/JP)은 무시해라.\n\n"
        f"질문(참고용):\n{command.question}\n\n"
        f"분석할 답변:\n{command.answer}\n\n"
        "아래 JSON 형태로만 반환해라:\n"
        "{\n"
        f'  "dimension": "{command.target_dimension}",\n'
        '  "scores": { ...해당 축 두 키만, 0~10 정수 },\n'
        '  "reason": "한국어 1~2문장"\n'
        "}\n"
    )


@dataclass
class OpenAIQuestionProvider(AIQuestionProviderPort):
    """
    OpenAI 클라이언트는 외부에서 주입(테스트에서 모킹)한다.
    settings.py에서 키/모델을 읽는 함수는 create_client 팩토리에서 처리하도록 분리 가능.
    """
    openai_client: Any
    model: str

    def generate_questions(self, command: GenerateAIQuestionCommand) -> AIQuestionResponse:
        system_prompt = _build_system_prompt()
        user_prompt = _build_user_prompt(command)

        resp = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = resp.choices[0].message.content  # openai python SDK 1.x 형태 가정
        data = _parse_json_object(content)

        turn = int(data.get("turn", command.turn))
        raw_questions = data.get("questions", [])
        questions: List[AIQuestion] = []
        for q in raw_questions:
            questions.append(
                AIQuestion(
                    text=str(q.get("text", "")).strip(),
                    target_dimensions=list(q.get("target_dimensions", [])),
                )
            )

        # 최소 방어: 질문 비어있으면 실패로 처리
        if not questions or any(not q.text for q in questions):
            raise ValueError("LLM returned invalid questions payload")

        return AIQuestionResponse(turn=turn, questions=questions)

    def analyze_answer(self, command: AnalyzeAnswerCommand) -> AnalyzeAnswerResponse:
        """AI를 사용하여 답변을 분석하고 MBTI 점수를 반환한다."""
        system_prompt = _build_analysis_system_prompt()
        user_prompt = _build_analysis_user_prompt(command)

        resp = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        content = resp.choices[0].message.content
        data = _parse_json_object(content)

        allowed = {
            "EI": {"E", "I"},
            "SN": {"S", "N"},
            "TF": {"T", "F"},
            "JP": {"J", "P"},
        }

        dimension = data.get("dimension")
        if dimension != command.target_dimension:
            raise ValueError(f"dimension mismatch: {dimension} != {command.target_dimension}")

        scores = data.get("scores", {})
        keys = set(scores.keys())
        expected_keys = allowed[command.target_dimension]
        if keys != expected_keys:
            raise ValueError(f"invalid score keys: {keys}, expected {expected_keys}")

        # 0~10 정수 범위 체크 (합은 강제하지 않음)
        norm_scores: Dict[str, int] = {}
        for k in expected_keys:
            v = scores.get(k, 0)
            if not isinstance(v, int) or not (0 <= v <= 10):
                raise ValueError(f"invalid score value for {k}: {v}")
            norm_scores[k] = v

        reasoning = data.get("reasoning", "")

        side_a, side_b = tuple(expected_keys)
        score_a = norm_scores.get(side_a, 0)
        score_b = norm_scores.get(side_b, 0)
        winning_side = side_a if score_a >= score_b else side_b
        winning_score = score_a if score_a >= score_b else score_b

        return AnalyzeAnswerResponse(
            dimension=dimension,
            scores=norm_scores,
            side=winning_side,
            score=winning_score,
            reasoning=reasoning,
        )


# (선택) settings.py 기반 클라이언트 팩토리: 기존 프로젝트 스타일에 맞게 라우터에서 사용
def create_openai_question_provider_from_settings() -> OpenAIQuestionProvider:
    from config.settings import get_settings
    from openai import OpenAI

    settings = get_settings()  # ✅ 인스턴스 가져오기
    api_key = settings.OPENAI_API_KEY
    model = getattr(settings, "OPENAI_MODEL", None) or "gpt-4o-mini"
    client = OpenAI(api_key=api_key)
    return OpenAIQuestionProvider(openai_client=client, model=model)

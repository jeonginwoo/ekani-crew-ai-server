import re
from typing import Dict, Tuple

# 키워드 + 가이드라인 가중치 통합 사전
DICTIONARY = {
    "EI": {
        "E": [{"word": "같이", "w": 5}, {"word": "사람", "w": 3}, {"word": "모임", "w": 5}, {"word": "떠들", "w": 3},
              {"word": "만나", "w": 4}, {"word": "친구들", "w": 5}, {"word": "파티", "w": 5}, {"word": "축제", "w": 4},
              {"word": "신나", "w": 3}, {"word": "시끌", "w": 4}, {"word": "왁자지껄", "w": 5}, {"word": "외출", "w": 3},
              {"word": "놀러", "w": 4}, {"word": "어울", "w": 4}, {"word": "술자리", "w": 4}, {"word": "회식", "w": 4},
              {"word": "수다", "w": 4}, {"word": "대화", "w": 3}, {"word": "사교", "w": 5}],
        "I": [{"word": "혼자", "w": 5}, {"word": "조용", "w": 4}, {"word": "집에", "w": 5}, {"word": "생각", "w": 3},
              {"word": "기빨려", "w": 5}, {"word": "이어폰", "w": 4}, {"word": "피곤", "w": 5}, {"word": "쉬고", "w": 4},
              {"word": "넷플릭스", "w": 4}, {"word": "침대", "w": 4}, {"word": "휴식", "w": 5}, {"word": "지침", "w": 4},
              {"word": "충전", "w": 4}, {"word": "방콕", "w": 5}, {"word": "혼밥", "w": 5}, {"word": "혼술", "w": 5},
              {"word": "내성적", "w": 5}, {"word": "에너지", "w": 3}, {"word": "지쳐", "w": 4}, {"word": "힘빠", "w": 4}]
    },
    "SN": {
        "S": [{"word": "사실", "w": 5}, {"word": "현실", "w": 4}, {"word": "경험", "w": 4}, {"word": "직접", "w": 3},
              {"word": "구체적", "w": 5}, {"word": "팩트", "w": 3}, {"word": "실제", "w": 4}, {"word": "현재", "w": 3},
              {"word": "지금", "w": 3}, {"word": "당장", "w": 4}, {"word": "실용", "w": 5}, {"word": "써먹", "w": 4},
              {"word": "필요", "w": 3}, {"word": "실질", "w": 4}, {"word": "눈앞", "w": 4}, {"word": "확실", "w": 3},
              {"word": "있는 그대로", "w": 5}, {"word": "오감", "w": 4}, {"word": "감각", "w": 3}, {"word": "보이는", "w": 3},
              {"word": "정확히", "w": 4}, {"word": "디테일", "w": 4}, {"word": "세부", "w": 4}, {"word": "실물", "w": 4},
              {"word": "눈에", "w": 3}, {"word": "손에", "w": 3}, {"word": "현장", "w": 4}],
        "N": [{"word": "의미", "w": 5}, {"word": "상상", "w": 5}, {"word": "미래", "w": 4}, {"word": "가능성", "w": 5},
              {"word": "만약에", "w": 5}, {"word": "비유", "w": 3}, {"word": "느낌", "w": 3}, {"word": "영감", "w": 5},
              {"word": "아이디어", "w": 4}, {"word": "패턴", "w": 4}, {"word": "연결", "w": 3}, {"word": "떠올", "w": 4},
              {"word": "생각나", "w": 3}, {"word": "연상", "w": 5}, {"word": "상징", "w": 4}, {"word": "추상", "w": 5},
              {"word": "본질", "w": 4}, {"word": "나중", "w": 3}, {"word": "언젠가", "w": 4}, {"word": "닮", "w": 4},
              {"word": "처럼", "w": 3}, {"word": "같은", "w": 2}, {"word": "뭔가", "w": 3}, {"word": "그냥", "w": 2},
              {"word": "직감", "w": 5}, {"word": "예감", "w": 4}, {"word": "새로운", "w": 3}, {"word": "도전", "w": 3}]
    },
    "TF": {
        "T": [{"word": "이유", "w": 5}, {"word": "원인", "w": 5}, {"word": "논리", "w": 5}, {"word": "분석", "w": 4},
              {"word": "왜", "w": 5}, {"word": "해결", "w": 4}, {"word": "보험", "w": 5}, {"word": "효율", "w": 4},
              {"word": "객관", "w": 5}, {"word": "합리", "w": 5}, {"word": "따지", "w": 4}, {"word": "판단", "w": 4},
              {"word": "기준", "w": 3}, {"word": "정확", "w": 4}, {"word": "솔직히", "w": 3}, {"word": "냉정", "w": 5},
              {"word": "문제", "w": 3}, {"word": "결과", "w": 3}, {"word": "증거", "w": 5}, {"word": "어이없", "w": 4},
              {"word": "황당", "w": 4}, {"word": "뭔말", "w": 3}, {"word": "당연", "w": 4}, {"word": "아니지", "w": 3},
              {"word": "팩폭", "w": 5}, {"word": "직설", "w": 5}, {"word": "퍽이나", "w": 4}, {"word": "웃기", "w": 3},
              {"word": "말도안", "w": 4}, {"word": "대신", "w": 3}, {"word": "해주", "w": 3}, {"word": "개선", "w": 5},
              {"word": "수정", "w": 4}, {"word": "육하원칙", "w": 5}, {"word": "따라", "w": 3}, {"word": "비효율", "w": 5},
              {"word": "최적", "w": 5}, {"word": "방법", "w": 3}, {"word": "시스템", "w": 4}, {"word": "구조", "w": 4},
              {"word": "전략", "w": 4}, {"word": "계산", "w": 4}, {"word": "다르지않", "w": 4}, {"word": "에따라", "w": 3}],
        "F": [{"word": "기분", "w": 5}, {"word": "마음", "w": 5}, {"word": "공감", "w": 5}, {"word": "서운", "w": 4},
              {"word": "감정", "w": 5}, {"word": "속상", "w": 5}, {"word": "어떡해", "w": 5}, {"word": "배려", "w": 5},
              {"word": "위로", "w": 5}, {"word": "따뜻", "w": 4}, {"word": "힘들", "w": 3}, {"word": "슬프", "w": 4},
              {"word": "기뻐", "w": 4}, {"word": "행복", "w": 3}, {"word": "사랑", "w": 4}, {"word": "상처", "w": 5},
              {"word": "미안", "w": 4}, {"word": "고마", "w": 3}, {"word": "진심", "w": 4}, {"word": "우울", "w": 5},
              {"word": "힘내", "w": 5}, {"word": "괜찮", "w": 4}, {"word": "응원", "w": 5}, {"word": "착하", "w": 3},
              {"word": "불쌍", "w": 4}, {"word": "안쓰러", "w": 4}, {"word": "감동", "w": 5}, {"word": "눈물", "w": 4}]
    },
    "JP": {
        "J": [{"word": "계획", "w": 5}, {"word": "정리", "w": 4}, {"word": "미리", "w": 5}, {"word": "확정", "w": 4},
              {"word": "리스트", "w": 5}, {"word": "예약", "w": 4}, {"word": "정해", "w": 4}, {"word": "목표", "w": 4},
              {"word": "체크", "w": 4}, {"word": "마감", "w": 5}, {"word": "일정", "w": 5}, {"word": "약속", "w": 3},
              {"word": "준비", "w": 3}, {"word": "미리미리", "w": 5}, {"word": "끝내", "w": 3}, {"word": "일찍", "w": 5},
              {"word": "먼저", "w": 4}, {"word": "정시", "w": 5}, {"word": "늦지", "w": 4}, {"word": "예정", "w": 4},
              {"word": "철저", "w": 5}, {"word": "꼼꼼", "w": 4}, {"word": "시간맞춰", "w": 5}, {"word": "빨리없애", "w": 4}],
        "P": [{"word": "즉흥", "w": 5}, {"word": "그때", "w": 4}, {"word": "유연", "w": 4}, {"word": "대충", "w": 4},
              {"word": "일단", "w": 5}, {"word": "상황 봐서", "w": 4}, {"word": "나중에", "w": 4}, {"word": "융통", "w": 5},
              {"word": "자유", "w": 4}, {"word": "끌리는", "w": 4}, {"word": "막판", "w": 5}, {"word": "갑자기", "w": 3},
              {"word": "변경", "w": 3}, {"word": "어쩌다", "w": 3}, {"word": "놀면서", "w": 4}, {"word": "몰라", "w": 3},
              {"word": "그냥", "w": 3}, {"word": "뭐든", "w": 3}, {"word": "알아서", "w": 4}, {"word": "느긋", "w": 4},
              {"word": "여유", "w": 3}, {"word": "되는대로", "w": 5}, {"word": "흘러가는", "w": 4}]
    }
}

DESCRIPTIONS = {
    "ISTP": {"title": "만능 재주꾼", "traits": ["#냉철함", "#해결사"], "desc": "사고 현장에서도 수리비부터 계산할 쿨한 해결사군요!"},
    "ENFP": {"title": "재기발랄한 활동가", "traits": ["#에너지", "#인싸"], "desc": "세상을 즐거움으로 채우는 당신은 자유로운 영혼입니다!"},
    # (나머지 유형도 동일한 형식으로 추가 가능)
}


def calculate_partial_mbti(answers: list):
    scores = {k: 0 for k in "EISNTFJP"}
    
    # Process only the answers provided so far
    for i, ans in enumerate(answers):
        dim = ""
        if i < 3: dim = "EI"
        elif i < 6: dim = "SN"
        elif i < 9: dim = "TF"
        elif i < 12: dim = "JP"
        
        if not dim: # Should not happen if within 12 questions range
            continue

        # 1. 키워드 매칭
        for trait, keywords in DICTIONARY[dim].items():
            for k in keywords:
                # Ensure 'ans' is a string before checking 'in'
                if isinstance(ans, str) and k["word"] in ans:
                    scores[trait] += k["w"]

        # 2. 패턴 매칭 (정규표현식)
        if isinstance(ans, str): # Ensure 'ans' is a string before regex
            if dim == "SN" and re.search(r"만약에|~라면", ans): scores["N"] += 3
            if dim == "TF" and re.search(r"왜 그런지|이유가 뭐야", ans): scores["T"] += 4

    # 결과 계산 (부분적으로만 계산)
    partial_mbti = ""
    
    if answers and len(answers) > 0: # Only calculate if at least one question has been answered
        # EI
        if len(answers) >= 3:
            partial_mbti += ("E" if scores["E"] >= scores["I"] else "I")
        else:
            partial_mbti += "X" # Not enough questions yet

        # SN
        if len(answers) >= 6:
            partial_mbti += ("S" if scores["S"] >= scores["N"] else "N")
        else:
            partial_mbti += "X"

        # TF
        if len(answers) >= 9:
            partial_mbti += ("T" if scores["T"] >= scores["F"] else "F")
        else:
            partial_mbti += "X"

        # JP
        if len(answers) >= 12:
            partial_mbti += ("J" if scores["J"] >= scores["P"] else "P")
        else:
            partial_mbti += "X"
    else: # No answers given yet
        partial_mbti = "XXXX"
    
    return {"mbti": partial_mbti, "scores": scores}

def run_analysis(answers: list):
    scores = {k: 0 for k in "EISNTFJP"}

    for i, ans in enumerate(answers):
        dim = "EI" if i < 3 else "SN" if i < 6 else "TF" if i < 9 else "JP"

        # 1. 키워드 매칭
        for trait, keywords in DICTIONARY[dim].items():
            for k in keywords:
                if k["word"] in ans:
                    scores[trait] += k["w"]

        # 2. 패턴 매칭 (정규표현식)
        if dim == "SN" and re.search(r"만약에|~라면", ans): scores["N"] += 3
        if dim == "TF" and re.search(r"왜 그런지|이유가 뭐야", ans): scores["T"] += 4

    # 결과 계산
    res_mbti = (
            ("E" if scores["E"] >= scores["I"] else "I") +
            ("S" if scores["S"] >= scores["N"] else "N") +
            ("T" if scores["T"] >= scores["F"] else "F") +
            ("J" if scores["J"] >= scores["P"] else "P")
    )

    def get_conf(a, b):
        return round((abs(a - b) / (a + b + 0.1)) * 100, 1)

    confidence = {
        "EI": get_conf(scores["E"], scores["I"]),
        "SN": get_conf(scores["S"], scores["N"]),
        "TF": get_conf(scores["T"], scores["F"]),
        "JP": get_conf(scores["J"], scores["P"])
    }

    return res_mbti, scores, confidence


# 차원 양쪽 매핑
DIMENSION_SIDES: Dict[str, Tuple[str, str]] = {
    "EI": ("E", "I"),
    "SN": ("S", "N"),
    "TF": ("T", "F"),
    "JP": ("J", "P"),
}


def get_dimension_for_question(question_index: int) -> str:
    """
    질문 인덱스(0-based)에 해당하는 MBTI 차원을 반환합니다.

    Args:
        question_index: 0-based 질문 인덱스

    Returns:
        차원 문자열 ("EI", "SN", "TF", "JP")
    """
    if question_index < 3:
        return "EI"
    elif question_index < 6:
        return "SN"
    elif question_index < 9:
        return "TF"
    else:
        return "JP"


def analyze_single_answer(answer: str, dimension: str) -> Dict:
    """
    단일 답변에 대해 주어진 차원의 MBTI 점수를 분석합니다.

    Args:
        answer: 사용자 답변 텍스트
        dimension: MBTI 차원 ("EI", "SN", "TF", "JP")

    Returns:
        분석 결과 딕셔너리:
        {
            "content": 원본 답변,
            "dimension": 차원,
            "scores": {"E": 5, "I": 3},
            "side": 우세한 쪽,
            "score": 우세한 쪽 점수
        }
    """
    if dimension not in DIMENSION_SIDES:
        raise ValueError(f"Invalid dimension: {dimension}")

    side_a, side_b = DIMENSION_SIDES[dimension]
    scores = {side_a: 0, side_b: 0}

    # 1. 키워드 매칭
    for trait, keywords in DICTIONARY[dimension].items():
        for k in keywords:
            if k["word"] in answer:
                scores[trait] += k["w"]

    # 2. 패턴 매칭 (정규표현식)
    if dimension == "SN" and re.search(r"만약에|~라면", answer):
        scores["N"] += 3
    if dimension == "TF" and re.search(r"왜 그런지|이유가 뭐야", answer):
        scores["T"] += 4

    # 우세한 쪽 결정
    if scores[side_a] >= scores[side_b]:
        winning_side = side_a
        winning_score = scores[side_a]
    else:
        winning_side = side_b
        winning_score = scores[side_b]

    return {
        "content": answer,
        "dimension": dimension,
        "scores": scores,
        "side": winning_side,
        "score": winning_score,
    }
"""Converter Router"""

from fastapi import APIRouter, status

from app.converter.adapter.input.web.request.convert_request import ConvertRequest
from app.converter.adapter.input.web.request.convert_three_tones_request import (
    ConvertThreeTonesRequest,
)
from app.converter.adapter.input.web.response.convert_response import ConvertResponse
from app.converter.adapter.input.web.response.convert_three_tones_response import (
    ConvertThreeTonesResponse,
)
from app.converter.application.use_case.convert_message_use_case import (
    ConvertMessageUseCase,
)
from app.converter.infrastructure.service.openai_message_converter import (
    OpenAIMessageConverter,
)
from app.shared.vo.mbti import MBTI

converter_router = APIRouter()


@converter_router.post(
    "/convert",
    response_model=ConvertResponse,
    status_code=status.HTTP_200_OK,
    summary="메시지 변환",
    description="원본 메시지를 특정 톤으로 변환합니다 (MBTI 기반)",
)
def convert_message(request: ConvertRequest) -> ConvertResponse:
    """메시지를 특정 톤으로 변환

    Args:
        request: 변환 요청 (원본 메시지, MBTI, 톤)

    Returns:
        ConvertResponse: 변환된 메시지
    """
    # MessageConverter 인스턴스 생성
    converter = OpenAIMessageConverter()

    # MBTI 값 객체 생성
    sender_mbti = MBTI(request.sender_mbti)
    receiver_mbti = MBTI(request.receiver_mbti)

    # 메시지 변환
    tone_message = converter.convert(
        original_message=request.original_message,
        sender_mbti=sender_mbti,
        receiver_mbti=receiver_mbti,
        tone=request.tone,
    )

    # 응답 DTO로 변환
    return ConvertResponse.from_domain(tone_message)


@converter_router.post(
    "/convert-three-tones",
    response_model=ConvertThreeTonesResponse,
    status_code=status.HTTP_200_OK,
    summary="메시지 3가지 톤 변환",
    description="원본 메시지를 3가지 톤(공손한, 캐주얼한, 간결한)으로 변환합니다 (MBTI 기반)",
)
def convert_message_three_tones(
    request: ConvertThreeTonesRequest,
) -> ConvertThreeTonesResponse:
    """메시지를 3가지 톤으로 변환

    Args:
        request: 변환 요청 (원본 메시지, MBTI)

    Returns:
        ConvertThreeTonesResponse: 3가지 톤으로 변환된 메시지
    """
    # MessageConverter 인스턴스 생성
    converter = OpenAIMessageConverter()

    # UseCase 생성
    use_case = ConvertMessageUseCase(converter=converter)

    # MBTI 값 객체 생성
    sender_mbti = MBTI(request.sender_mbti)
    receiver_mbti = MBTI(request.receiver_mbti)

    # 3가지 톤으로 변환
    tone_messages = use_case.execute(
        original_message=request.original_message,
        sender_mbti=sender_mbti,
        receiver_mbti=receiver_mbti,
    )

    # 응답 DTO로 변환
    return ConvertThreeTonesResponse.from_domain(tone_messages)

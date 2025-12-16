import pytest
from abc import ABC

from app.consult.application.port.ai_counselor_port import AICounselorPort
from app.consult.domain.message import Message


class TestAICounselorPort:
    """AICounselorPort 인터페이스 테스트"""

    def test_ai_counselor_port_is_abstract(self):
        """AICounselorPort는 추상 클래스다"""
        assert issubclass(AICounselorPort, ABC)

    def test_ai_counselor_port_has_generate_response_method(self):
        """AICounselorPort는 generate_response 메서드를 가진다"""
        assert hasattr(AICounselorPort, "generate_response")

    def test_ai_counselor_port_has_generate_analysis_method(self):
        """AICounselorPort는 generate_analysis 메서드를 가진다"""
        assert hasattr(AICounselorPort, "generate_analysis")
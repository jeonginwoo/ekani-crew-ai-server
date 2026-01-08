"""
Add pending_question column to mbti_test_sessions table
"""
from sqlalchemy import text
from config.database import engine

sql = """
ALTER TABLE mbti_test_sessions
ADD COLUMN pending_question VARCHAR(1000) NULL AFTER result_timestamp;
"""

try:
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("✅ pending_question 컬럼 추가 완료!")
except Exception as e:
    print(f"⚠️ 에러 발생: {e}")
    print("컬럼이 이미 존재하거나 다른 문제가 있을 수 있습니다.")

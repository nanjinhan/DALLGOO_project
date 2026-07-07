"""Kafka 활동 이벤트 발행(Producer).

글쓰기/댓글/좋아요/로그인 같은 '활동'이 일어날 때 이 함수를 호출하면
Kafka의 'activity' 토픽으로 이벤트를 흘려보낸다. 실제 소비(저장/표시)는
activity_consumer 가 담당한다.

발행 실패(예: Kafka 잠깐 다운)해도 API 흐름은 절대 끊지 않는다 —
활동 로그는 부가기능이므로 본 기능(글쓰기 등)을 막으면 안 된다.
"""

import json
import logging
from datetime import datetime, timezone

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

ACTIVITY_TOPIC = "activity"

_producer = None


def _get_producer():
    """Kafka Producer 를 한 번만 생성해 재사용(지연 초기화)."""
    global _producer
    if _producer is None:
        try:
            from confluent_kafka import Producer

            _producer = Producer(
                {
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "socket.timeout.ms": 3000,
                    "message.timeout.ms": 3000,
                }
            )
        except Exception as e:
            logger.error("[Kafka] Producer 생성 실패: %s", e)
            return None
    return _producer


def publish_activity(type: str, actor: str, detail: str) -> None:
    """활동 이벤트 한 건을 발행. type=post/comment/like/login 등."""
    producer = _get_producer()
    if producer is None:
        return
    try:
        event = {
            "type": type,
            "actor": actor,
            "detail": detail,
            "at": datetime.now(timezone.utc).isoformat(),
        }
        producer.produce(ACTIVITY_TOPIC, json.dumps(event).encode("utf-8"))
        producer.poll(0)  # 전송 콜백 처리(논블로킹)
    except Exception as e:
        logger.error("[Kafka] 이벤트 발행 실패: %s", e)

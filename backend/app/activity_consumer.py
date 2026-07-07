"""Kafka 활동 이벤트 소비자(Consumer).

'activity' 토픽을 구독해서, 들어오는 이벤트를 Redis 리스트에 최근 50건만
저장한다. 관리자 페이지는 이 Redis 리스트를 읽어 '실시간 활동 피드'를 보여준다.

별도 프로세스로 계속 떠 있는다.
실행: python -m app.activity_consumer
"""

import logging
import time

from app.core.config import settings
from app.core.events import ACTIVITY_TOPIC
from app.core.redis_client import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("activity-consumer")

RECENT_KEY = "recent_activities"
MAX_KEEP = 50


def main() -> None:
    from confluent_kafka import Consumer

    consumer = Consumer(
        {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "activity-consumer",
            # 소비자가 뜬 이후의 새 이벤트부터 받는다(실시간 피드용).
            "auto.offset.reset": "latest",
        }
    )
    consumer.subscribe([ACTIVITY_TOPIC])
    logger.info("[활동소비자] Kafka 'activity' 토픽 구독 시작")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.warning("[활동소비자] 메시지 오류: %s", msg.error())
                continue
            try:
                data = msg.value().decode("utf-8")
                # 최신이 앞(index 0)에 오도록 LPUSH 후 50건으로 자름
                redis_client.lpush(RECENT_KEY, data)
                redis_client.ltrim(RECENT_KEY, 0, MAX_KEEP - 1)
                logger.info("[활동소비자] 저장: %s", data)
            except Exception as e:
                logger.error("[활동소비자] 처리 실패: %s", e)
    finally:
        consumer.close()


if __name__ == "__main__":
    # Kafka가 기동 중일 수 있으니 초반 연결 실패는 재시도로 흡수
    while True:
        try:
            main()
        except Exception as e:
            logger.info("[활동소비자] 재시작(3초 후): %s", e)
            time.sleep(3)

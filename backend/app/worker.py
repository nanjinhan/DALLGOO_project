"""RabbitMQ 이메일 큐 워커.

API 서버(backend)는 메일 발송 요청을 큐에 던지기만 하고 바로 응답한다.
이 워커는 별도 프로세스로 계속 떠서, 큐에 쌓인 요청을 하나씩 꺼내
실제로 SMTP 발송을 담당한다.

실행: python -m app.worker
"""

import json
import logging
import time

import pika

from app.core.config import settings
from app.core.email import send_email
from app.core.queue import EMAIL_QUEUE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


def _callback(channel, method, properties, body):
    data = json.loads(body)
    logger.info("[워커] 메일 발송 처리 시작: to=%s", data.get("to"))
    send_email(data["to"], data["subject"], data["body"])
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    # RabbitMQ가 뜨는 중일 수 있으니 연결될 때까지 재시도
    while True:
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            break
        except pika.exceptions.AMQPConnectionError:
            logger.info("[워커] RabbitMQ 연결 대기 중... 3초 후 재시도")
            time.sleep(3)

    channel = connection.channel()
    channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)  # 한 번에 한 건씩만 처리
    channel.basic_consume(queue=EMAIL_QUEUE, on_message_callback=_callback)

    logger.info("[워커] 이메일 큐 대기 시작")
    channel.start_consuming()


if __name__ == "__main__":
    main()

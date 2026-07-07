import json
import logging

import pika

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

EMAIL_QUEUE = "email_queue"


def publish_email_job(to: str, subject: str, body: str) -> None:
    """메일 발송 요청을 RabbitMQ 큐에 던진다. 실제 발송은 워커가 담당."""
    try:
        params = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=EMAIL_QUEUE,
            body=json.dumps({"to": to, "subject": subject, "body": body}),
            properties=pika.BasicProperties(delivery_mode=2),  # 큐 재시작에도 유지
        )
        connection.close()
    except Exception as e:
        # 큐 발행 실패해도 API 흐름은 끊지 않고 로그로 남긴다.
        logger.error("[큐발행 실패] to=%s — %s", to, e)

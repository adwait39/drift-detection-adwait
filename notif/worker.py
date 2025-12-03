# slack_worker/worker.py
import os
import json
import pika
from slack_notifier import send_slack_message

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_QUEUE = os.getenv("RABBITMQ_ALERT_QUEUE", "drift_alerts")


def callback(ch, method, properties, body):
    message = json.loads(body.decode("utf-8"))
    metric_name = message.get("metric_name")
    value = message.get("value")
    created_at = message.get("created_at")

    text = f"🚨 Drift Alert\nMetric: *{metric_name}*\nValue: *{value}*\nTime: {created_at}"
    print(f"Received message: {message}")
    send_slack_message(text)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=callback)

    print("Slack worker listening for drift alerts...")
    channel.start_consuming()


if __name__ == "__main__":
    main()

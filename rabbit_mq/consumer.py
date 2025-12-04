import json
import pika

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "ml_drift_stream"


def get_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return connection, channel


def process_message(message: dict):
    """
    This is where your ML / drift detection logic will go.
    For now, we just print it nicely.
    """
    source = message.get("source")
    drift_type = message.get("drift_type")
    text = message.get("text")

    print(f"[CONSUMER] source={source}, drift={drift_type}, text={text}")


def on_message(ch, method, properties, body):
    try:
        message = json.loads(body.decode("utf-8"))
    except Exception as e:
        print("[CONSUMER] Failed to decode message:", e, "raw:", body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    process_message(message)

    # Acknowledge message so RabbitMQ removes it from the queue
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection, channel = get_channel()

    channel.basic_qos(prefetch_count=1)  # fair dispatch if multiple consumers
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=on_message,
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        connection.close()

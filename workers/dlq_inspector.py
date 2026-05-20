import json
import boto3

from app.core.config import get_settings

settings = get_settings()

def inspect_dlq(max_messages: int = 10) -> None:
    sqs = boto3.client("sqs", region_name=settings.aws_region)

    response = sqs.receive_message(
        QueueUrl=settings.sqs_dlq_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=5,
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
    )

    messages = response.get("Messages", [])

    if not messages:
        print("No messages found in DLQ.")
        return

    for index, message in enumerate(messages, start=1):
        print(f"\n--- DLQ Message {index} ---")
        print("MessageId:", message.get("MessageId"))
        print("ReceiveCount:", message.get("Attributes", {}).get("ApproximateReceiveCount"))

        body = json.loads(message["Body"])
        print(json.dumps(body, indent=2))


if __name__ == "__main__":
    inspect_dlq()
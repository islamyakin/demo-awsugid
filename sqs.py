import boto3
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

sqs = boto3.client('sqs',
                   aws_access_key_id=aws_access_key_id,
                   aws_secret_access_key=aws_secret_access_key,
                   region_name=region_name)

queue_url = os.getenv('QUEUE_URL')

def extract_relevant_data(message_body):
    try:
        outer_json = json.loads(message_body)
        if "Message" in outer_json:
            inner_json = json.loads(outer_json["Message"])
        else:
            inner_json = outer_json

        extracted_data = {
            "eventType": inner_json.get("eventType"),
            "mail.source": inner_json.get("mail", {}).get("source"),
            "mail.destination": inner_json.get("mail", {}).get("destination", []),
            "mail.commonHeaders.subject": inner_json.get("mail", {}).get("commonHeaders", {}).get("subject"),
            "mail.tags.ses:from-domain": inner_json.get("mail", {}).get("tags", {}).get("ses:from-domain", [None])[0] if "ses:from-domain" in inner_json.get("mail", {}).get("tags", {}) else None,
            "mail.ses:caller-identity": inner_json.get("mail", {}).get("tags", {}).get("ses:caller-identity", [None])[0] if "ses:caller-identity" in inner_json.get("mail", {}).get("tags", {}) else None,
        }

        bounce_details = None
        if inner_json.get("eventType") == "Bounce":
            bounce_details = {
                "bounceType": inner_json.get("bounce", {}).get("bounceType"),
                "bounceSubType": inner_json.get("bounce", {}).get("bounceSubType"),
                "bouncedRecipients": inner_json.get("bounce", {}).get("bouncedRecipients", []),
                "timestamp": inner_json.get("bounce", {}).get("timestamp"),
                "feedbackId": inner_json.get("bounce", {}).get("feedbackId"),
                "reportingMTA": inner_json.get("bounce", {}).get("reportingMTA"),
            }

        delivery_delay_details = None
        if inner_json.get("eventType") == "DeliveryDelay":
            delivery_delay_details = {
                "timestamp": inner_json.get("deliveryDelay", {}).get("timestamp"),
                "delayType": inner_json.get("deliveryDelay", {}).get("delayType"),
                "expirationTime": inner_json.get("deliveryDelay", {}).get("expirationTime"),
                "delayedRecipients": inner_json.get("deliveryDelay", {}).get("delayedRecipients", []),
            }

        extracted_data["detail"] = bounce_details or delivery_delay_details or None

        return extracted_data

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}


def format_message(message):
    extracted_data = extract_relevant_data(message['Body'])

    if "error" in extracted_data:
        return json.dumps({
            "MessageId": message['MessageId'],
            "ExtractedData": extracted_data,
            "Original": message['Body'],
            "Attributes": message.get('Attributes', {}),
        }, indent=4)
    else:
        return json.dumps({
            "MessageId": message['MessageId'],
            "ExtractedData": extracted_data,
            "Attributes": message.get('Attributes', {}),
        }, indent=4)

def read_messages():
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
                MessageAttributeNames=['All'],
                AttributeNames=['All']
            )

            messages = response.get('Messages', [])
            if not messages:
                print('No messages to read.')
            else:
                for message in messages:
                    print("Received Message:")
                    print(format_message(message))
                    print("-" * 50)

                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    print('Message deleted successfully.')

        except Exception as e:
            print(f"Error reading messages: {e}")

        time.sleep(5)

if __name__ == '__main__':
    read_messages()

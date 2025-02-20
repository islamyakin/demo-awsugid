# Self VDM

This application is designed to handle email events from AWS SES. The events are sent to AWS SNS, which then forwards them to an AWS SQS queue. The application reads these events from the SQS queue, processes them, and sends emails using AWS SES.

## Prerequisites

- Python 3.12 or higher
- `pip` (Python package installer)
- AWS account with SQS and SES configured

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/islamyakin/demo-awsugid.git
    cd demo-awsugid
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory of the project and add your AWS and SMTP credentials:

    ```env
    SMTP_SERVER=your_smtp_server
    SMTP_PORT=your_smtp_port
    SMTP_USER=your_smtp_user
    SMTP_PASSWORD=your_smtp_password
   
    AWS_ACCESS_KEY_ID=your_aws_access_key_id
    AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
    AWS_REGION=your_aws_region
    QUEUE_URL=your_sqs_queue_url
    ```
2. **Note:** Don't forget to change the `from_email` and `to_email` variables in `smtp.py`:

    ```python
    from_email = 'from@example.com'
    to_email = 'to@example.com'
    ```

## Running the Application

1. To read messages from the SQS queue and process them, run:

    ```sh
    python3 sqs.py
    ```

2. To send an email, run:

    ```sh
    python3 smtp.py
    ```

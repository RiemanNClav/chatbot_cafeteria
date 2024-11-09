FROM rasa/rasa-sdk:3.6.2

USER root

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt



COPY ./src /app/src
COPY ./actions /app/actions
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

USER 1001
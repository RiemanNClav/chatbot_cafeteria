FROM rasa/rasa-sdk:3.6.2

USER root

WORKDIR /app

COPY chatbot/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt



COPY ./google_drive /app/google_drive
COPY ./actions /app/actions
COPY entrypoint.sh /app/entrypoint.sh
COPY endpoints.yml /app/endpoints.yml


RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

USER 1001
FROM rasa/rasa-sdk:3.6.2

USER root

WORKDIR /app

COPY chatbot/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt



COPY chatbot/google_drive /app/google_drive
COPY chatbot/mensajes.py /app/mensajes.py
COPY chatbot/actions /app/actions
COPY chatbot/facturas /app/facturas
COPY chatbot/entrypoint.sh /app/entrypoint.sh
COPY chatbot/endpoints.yml /app/endpoints.yml


RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

USER 1001
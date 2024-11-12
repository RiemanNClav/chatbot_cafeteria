FROM rasa/rasa:3.6.20


WORKDIR /app

USER root

# Definir variables de entorno
ENV TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
ENV TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
ENV TWILIO_NUMBER=${TWILIO_NUMBER}

COPY chatbot/credentials.yml /app/credentials.yml
COPY chatbot/config.yml /app/config.yml
COPY chatbot/domain.yml /app/domain.yml
COPY chatbot/endpoints.yml /app/endpoints.yml
COPY chatbot/data /app/data

COPY chatbot/requirements.txt /app/requirements.txt
COPY chatbot/models /app/models
RUN pip install -r requirements.txt
COPY chatbot/entrypoint.runserver.sh /app/entrypoint.runserver.sh


EXPOSE 5005

# RUN rasa train

RUN chmod +x /app/entrypoint.runserver.sh

ENTRYPOINT ["/app/entrypoint.runserver.sh"]

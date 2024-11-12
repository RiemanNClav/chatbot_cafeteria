FROM rasa/rasa:3.6.20

COPY . /app

WORKDIR /app

USER root


COPY chatbot/requirements.txt /app/requirements.txt
COPY chatbot/models /app/models
RUN pip install -r requirements.txt
COPY chatbot/entrypoint.runserver.sh /app/entrypoint.runserver.sh


EXPOSE 5005

# RUN rasa train

RUN chmod +x /app/entrypoint.runserver.sh

ENTRYPOINT ["/app/entrypoint.runserver.sh"]

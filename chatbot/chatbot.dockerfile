FROM rasa/rasa:3.6.20



COPY . /app

WORKDIR /app

USER root


COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


EXPOSE 5005

# RUN rasa train

CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
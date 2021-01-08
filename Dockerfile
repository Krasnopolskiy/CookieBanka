FROM python:3.6-alpine

RUN adduser -D cookie-banka

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY server.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP server.py

RUN chown -R cookie-banka:cookie-banka ./
USER cookie-banka

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
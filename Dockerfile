FROM python:3.10.11

WORKDIR /bot

COPY ./assets /bot/assets
COPY ./core /bot/core
COPY main.py /bot
COPY solar_bot.py /bot

COPY alembic.ini /bot
COPY requirements.txt /bot
COPY config.env /bot

RUN pip install -r requirements.txt

CMD alembic upgrade head; python main.py
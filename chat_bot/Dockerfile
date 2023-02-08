FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY ./ ./
RUN ["chmod", "+x", "bot.py"]
ENTRYPOINT ["python", "-u", "./bot.py"]
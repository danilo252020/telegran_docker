FROM python:3.11.4

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

RUN python -m nltk.downloader stopwords && \
    python -m spacy download pt_core_news_sm

COPY . .

CMD ["python", "./analise.py"]
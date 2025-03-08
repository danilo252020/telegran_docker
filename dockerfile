FROM python:3.11.4

WORKDIR /app

COPY requirements.txt .

# Instala dependências e baixa o modelo do spaCy corretamente
RUN apt-get update && apt-get install -y gcc python3-dev musl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download pt_core_news_sm \
    && apt-get clean && rm -rf /var/lib/apt/lists/* 

COPY . .

CMD ["python", "analise.py"]
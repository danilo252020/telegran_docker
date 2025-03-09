FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema, incluindo o tk
RUN apt-get update && apt-get install -y \
    tk \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos necessários para o contêiner
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instala o modelo do SpaCy
RUN python -m spacy download pt_core_news_sm

# Copia o restante da aplicação para o contêiner
COPY . .

# Define o comando para rodar a aplicação
CMD ["python", "analise.py"]
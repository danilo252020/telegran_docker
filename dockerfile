# Use uma imagem base leve do Python 3.11
FROM python:3.11-slim

# Instale dependências do sistema necessárias para bibliotecas gráficas e compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Atualiza o pip e instala as dependências Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Baixa o modelo spaCy pt_core_news_sm
RUN python -m spacy download pt_core_news_sm

# Copia o restante da aplicação para dentro do container
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "vai_da_bom.py", "--server.enableCORS", "false"]
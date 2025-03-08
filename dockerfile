FROM jupyter/base-notebook:latest

USER root

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos necessários primeiro para aproveitar cache de camadas
COPY requirements.txt .
COPY *.ipynb ./
COPY *.xlsx ./

# Instalar dependências do sistema e Python
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download pt_core_news_sm && \
    python -m nltk.downloader stopwords && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Voltar para usuário não-root
USER ${NB_UID}

# Porta padrão para Voilà
EXPOSE 8866

# Comando para executar o Voilà
CMD ["voila", "Analisetelegran_oficial.ipynb", "--port=8866", "--no-browser", "--enable_nbextensions=True"]
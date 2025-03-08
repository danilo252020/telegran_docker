# Use a imagem base do Jupyter
FROM jupyter/base-notebook

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Use o usuário root para garantir permissões adequadas
USER root

# Forçar atualização de pacotes do apt e instalar as dependências do sistema e bibliotecas Python necessárias
RUN apt-get update --fix-missing \
    && apt-get install -y gcc python3-dev build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download pt_core_news_sm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar todos os arquivos do projeto (notebooks, dados, etc.)
COPY . .

# Expor a porta que o Jupyter/Voila vai usar
EXPOSE 8888

# Comando para rodar o Voila (sem --allow-root, como você pediu)
ENTRYPOINT ["voila", "Analisetelegran_oficial.ipynb", "--port=8888", "--no-browser", "--ip='0.0.0.0'"]
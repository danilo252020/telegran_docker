# Use a imagem base do Jupyter
FROM jupyter/base-notebook

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo de dependências (requirements.txt)
COPY requirements.txt ./

# Instale as dependências do sistema e as bibliotecas Python necessárias
RUN apt-get update && apt-get install -y gcc python3-dev build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download pt_core_news_sm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia todos os arquivos do projeto (notebooks, dados, etc.)
COPY . .

# Exponha a porta que o Jupyter/Voila vai usar
EXPOSE 8888

# Comando para rodar o Voila (sem --allow-root, como você pediu)
ENTRYPOINT ["voila", "Analisetelegran_oficial.ipynb", "--port=8888", "--no-browser", "--ip='0.0.0.0'"]
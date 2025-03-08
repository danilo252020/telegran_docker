# Substitua seu Dockerfile por esta versão otimizada
FROM jupyter/base-notebook:python-3.11.5

USER root

# Instalação crítica de dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Configuração do ambiente Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download pt_core_news_sm && \
    python -m nltk.downloader stopwords && \
    jupyter nbextension enable --py widgetsnbextension

# Permissões e limpeza
COPY . /app
WORKDIR /app
RUN chown -R $NB_UID:$NB_GID /app && \
    fix-permissions /app

USER $NB_UID

# Comando de inicialização reforçado
CMD ["voila", "Analisetelegran_oficial.ipynb", "--port=8866", "--no-browser", "--enable_nbextensions=True", "--Voila.ip=0.0.0.0", "--debug"]
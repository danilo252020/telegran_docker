FROM python:3.11.4

WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala dependências do sistema, bibliotecas Python, openpyxl, notebook e o modelo do spaCy
RUN apt-get update && apt-get install -y gcc python3-dev build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download pt_core_news_sm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia todo o código (incluindo o .ipynb e o arquivo Excel)
COPY . .

# Inicia o servidor do Jupyter Notebook
CMD ["python", "-m", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
# Use uma imagem base com Python
FROM python:3.11

# Atualize o apt-get e instale as dependências para o Tkinter
RUN apt-get update && \
    apt-get install -y tk && \
    apt-get clean

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos necessários para dentro do container
COPY . .

# Instalar as dependências do Python do requirements.txt, caso haja
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o Tkinter no arquivo desejado
CMD ["python", "test_tkinter.py"]
# 1. Imagem base leve do Python
FROM python:3.11-slim

# 2. Diretório de trabalho
WORKDIR /app

# 3. Instalar dependências do sistema para gráficos
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar e instalar requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar o código do frontend
COPY . .

# 6. Expor a porta padrão do Streamlit
EXPOSE 8501

# 7. Comando para rodar o Streamlit
# O --server.address=0.0.0.0 é obrigatório para rodar na nuvem
#CMD ["streamlit", "run", "app_old.py", "--server.port=8501", "--server.address=0.0.0.0"]
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]

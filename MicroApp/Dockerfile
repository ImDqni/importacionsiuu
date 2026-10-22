# Imagen base liviana
FROM python:3.10-slim

# Logs sin buffer y sin archivos .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias (Streamlit >= 1.35 requerido para la selección de filas en tablas)
RUN pip install "streamlit>=1.35,<2" pandas

# Código de la aplicación y carpeta de datos (se sobrescribe con el volumen)
COPY app.py .
RUN mkdir -p /app/data

EXPOSE 8501

# Healthcheck opcional usando el endpoint interno de Streamlit
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]

FROM python:3.10.4

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update
RUN pip install --upgrade pip wheel setuptools requests

RUN apt-get update && apt-get install -y \
    g++ \
    libpoppler-cpp-dev \
    pkg-config \
    cmake \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    tesseract-ocr \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-deps --no-cache-dir --upgrade -r /code/requirements.txt\
    && pip install "fastapi[standard]" streamlit


RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/ces.traineddata && \
mv ces.traineddata /usr/share/tesseract-ocr/4.00/tessdata/



COPY . /code/
RUN echo "Contents of /code directory:" && ls -l /code

# Debugging: Check if api.py exists
RUN if [ -f /code/api.py ]; then echo "api.py exists"; else echo "api.py is missing"; fi

# Debugging: Print the Python path
RUN echo "Python path:" && python -c "import sys; print('\n'.join(sys.path))"

# Set the PYTHONPATH to include /code
ENV PYTHONPATH=/code

# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8091"]
# CMD ["sh", "-c", "fastapi run api.py --host 0.0.0.0 --port 8000"]
# & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8051 --server.address 0.0.0.0"]
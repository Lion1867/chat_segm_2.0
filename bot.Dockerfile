# Используем базовый образ с поддержкой GPU
FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Установка необходимых зависимостей для OpenCV и Python
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    tzdata \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libatlas-base-dev \
    gfortran \
    libspatialindex-dev \
    && ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Настройка рабочего каталога
WORKDIR /app

# Копирование requirements.txt и установка зависимостей Python
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Копирование исходного кода в контейнер
COPY . /app

# Команда по умолчанию для запуска контейнера
CMD ["python3", "main.py"]

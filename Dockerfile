FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    # X11 и графика
    libxcb-cursor0 \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-shape0 \
    # Мультимедиа
    libqt5multimedia5 \
    libqt5multimediawidgets5 \
    libqt5multimedia5-plugins \
    # Аудио бэкенды
    pipewire \
    libpipewire-0.3-0 \
    pulseaudio \
    # FFmpeg для moviepy
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Указываем бэкенд для Qt Multimedia
ENV QT_MEDIA_BACKEND=ffmpeg

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-deps --default-timeout=100 --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

CMD ["python3", "clipmaster/app.py"]
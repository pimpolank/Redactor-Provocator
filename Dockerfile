FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpulse-mainloop-glib0 \
    libxcb1 libxcb-xinerama0 libx11-xcb1 libxkbcommon-x11-0 \
    libxcomposite1 libxrandr2 libxi6 libgdk-pixbuf2.0-0 \
    libdbus-1-3 libatk1.0-0 libcups2 libpango1.0-0 \
    libqt5core5a libqt5gui5 libqt5widgets5 libqt5dbus5 libqt5x11extras5 \
    xvfb

ENV QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/qt5/plugins/platforms

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем через xvfb-run
CMD ["bash", "-c", "xvfb-run --server-args='-screen 0 1024x768x24' python clipmaster/app.py"]

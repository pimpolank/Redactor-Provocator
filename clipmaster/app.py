import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QSlider, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal, QSize
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from moviepy.video.io.VideoFileClip import VideoFileClip

class VideoCutThread(QThread):
    cut_finished = pyqtSignal(str)

    def __init__(self, video_path, start_time, end_time, output_path):
        super().__init__()
        self.video_path = video_path
        self.start_time = start_time
        self.end_time = end_time
        self.output_path = output_path

    def run(self):
        try:
            clip = VideoFileClip(self.video_path).subclip(self.start_time, self.end_time)
            clip.write_videofile(self.output_path, codec="libx264", logger=None)
            self.cut_finished.emit(self.output_path)
        except Exception as e:
            self.cut_finished.emit(f"Ошибка: {e}")

class VideoPlayerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipmaster")
        self.setGeometry(100, 100, 1024, 768)

        # Медиаплеер
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Видео отображение
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Кнопки
        self.open_button = QPushButton("📂")
        self.open_button.setToolTip("Открыть видео")
        self.open_button.clicked.connect(self.open_file)

        self.play_pause_button = QPushButton("▶️")
        self.play_pause_button.setToolTip("Воспроизвести/Пауза")
        self.play_pause_button.clicked.connect(self.play_pause)
        self.play_pause_button.setEnabled(False)

        self.stop_button = QPushButton("⏹")
        self.stop_button.setToolTip("Стоп")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)

        self.cut_button = QPushButton("✂️")
        self.cut_button.setToolTip("Обрезать видео")
        self.cut_button.clicked.connect(self.cut_video)
        self.cut_button.setEnabled(False)

        self.fullscreen_button = QPushButton("🖥️")
        self.fullscreen_button.setToolTip("Развернуть видео")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        # Ползунки
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.setEnabled(False)

        self.time_label = QLabel("00:00 / 00:00")

        # Таймер
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

        # Разметка
        control_layout = QHBoxLayout()
        for btn in [self.open_button, self.play_pause_button, self.stop_button, self.cut_button, self.fullscreen_button]:
            btn.setFixedSize(QSize(60, 60))
            control_layout.addWidget(btn)

        seek_layout = QHBoxLayout()
        seek_layout.addWidget(self.time_label)
        seek_layout.addWidget(self.seek_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(seek_layout)
        main_layout.addLayout(control_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: "Segoe UI", sans-serif;
                font-size: 16px;
                border-radius: 10px;
            }   
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 24px;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #393939;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3c3c3c;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #00c853;
                border-radius: 4px;
            }
            QLabel {
                font-size: 14px;
                color: #b0b0b0;
            }
        """)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть видео", "", "Видео файлы (*.mp4 *.avi *.mkv *.mov)")
        if filename:
            self.video_path = filename
            self.media_player.setSource(QUrl.fromLocalFile(filename))
            self.play_pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.cut_button.setEnabled(True)
            self.seek_slider.setEnabled(True)
            self.media_player.play()
            self.timer.start()

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("▶️")
        else:
            self.media_player.play()
            self.play_pause_button.setText("⏸️")

    def stop(self):
        self.media_player.stop()
        self.play_pause_button.setText("▶️")

    def set_position(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            self.media_player.setPosition((position / 1000) * duration)

    def update_ui(self):
        position = self.media_player.position()
        duration = self.media_player.duration()

        if duration > 0:
            self.seek_slider.setValue(int((position / duration) * 1000))
            self.time_label.setText(f"{self.format_time(position/1000)} / {self.format_time(duration/1000)}")

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"

    def cut_video(self):
        start_time = 0
        end_time = self.media_player.duration() / 1000
        output_path, _ = QFileDialog.getSaveFileName(self, "Сохранить обрезанное видео", "", "MP4 файлы (*.mp4)")
        if output_path:
            self.cut_thread = VideoCutThread(self.video_path, start_time, end_time, output_path)
            self.cut_thread.cut_finished.connect(self.on_cut_finished)
            self.cut_thread.start()

    def on_cut_finished(self, output_path):
        print(f"Видео успешно сохранено: {output_path}")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

def main():
    app = QApplication(sys.argv)
    player = VideoPlayerEditor()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

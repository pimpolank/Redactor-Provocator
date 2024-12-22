import sys
import vlc
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QSlider, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from moviepy.video.io.VideoFileClip import VideoFileClip

# Поток для обрезки видео
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
            clip = VideoFileClip(self.video_path).subclipped(self.start_time, self.end_time)
            clip.write_videofile(self.output_path, codec="libx264", logger=None)
            self.cut_finished.emit(self.output_path)
        except Exception as e:
            self.cut_finished.emit(f"Ошибка: {e}")

class VideoPlayerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Видеоредактор")
        self.setGeometry(100, 100, 900, 700)

        # VLC 
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # отображение видео
        self.video_widget = QWidget(self)
        self.video_widget.setGeometry(10, 10, 880, 500)

        # управление
        self.open_button = QPushButton("Открыть")
        self.open_button.clicked.connect(self.open_file)

        self.play_pause_button = QPushButton("Воспроизвести")
        self.play_pause_button.clicked.connect(self.play_pause)
        self.play_pause_button.setEnabled(False) 

        self.stop_button = QPushButton("Остановка")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False) 

        self.cut_button = QPushButton("Обрезать видео")
        self.cut_button.clicked.connect(self.cut_video)
        self.cut_button.hide()  

        # Ползунки
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.hide() 
        self.start_cut_slider = QSlider(Qt.Horizontal)
        self.start_cut_slider.setRange(0, 1000)
        self.start_cut_slider.valueChanged.connect(self.update_start_label)
        self.start_cut_slider.hide() 

        self.end_cut_slider = QSlider(Qt.Horizontal)
        self.end_cut_slider.setRange(0, 1000)
        self.end_cut_slider.valueChanged.connect(self.update_end_label)
        self.end_cut_slider.hide() 

        # Метки времени
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.hide() 

        self.start_label = QLabel("Начало: 00:00")
        self.start_label.hide() 

        self.end_label = QLabel("Конец: 00:00")
        self.end_label.hide() 

        # Таймер для обновления интерфейса
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_ui)

        # Разметка
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0) 
        control_layout.setSpacing(5)  
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_pause_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.seek_slider)
        control_layout.addWidget(self.time_label)

        cut_layout = QHBoxLayout()
        cut_layout.setContentsMargins(0, 0, 0, 0)  
        cut_layout.setSpacing(5)  
        cut_layout.addWidget(self.start_label)
        cut_layout.addWidget(self.start_cut_slider)
        cut_layout.addWidget(self.end_label)
        cut_layout.addWidget(self.end_cut_slider)
        cut_layout.addWidget(self.cut_button)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  
        main_layout.setSpacing(5)  
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(cut_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Связывание VLC с виджетом
        if sys.platform.startswith("win"):
            self.media_player.set_hwnd(self.video_widget.winId())
        # Темная тема
        self.setStyleSheet("""
        QMainWindow { background-color: #2e2e2e; }
        QWidget { background-color: #2e2e2e; color: #fff; }
        QPushButton { background-color: #444; color: #fff; padding: 5px; border-radius: 5px; }
        QPushButton:hover { background-color: #555; }
        QSlider { background-color: #444; }
        QLabel { color: #fff; }
        """)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Окрыть видео", "", "MP4 Files (*.mp4)")
        if filename:
            self.media_player.set_media(self.instance.media_new(filename))
            self.video_path = filename
            self.media_player.play()
            QTimer.singleShot(100, lambda: self.media_player.set_pause(True))
            self.timer.start()

            
            self.seek_slider.show()
            self.start_cut_slider.show()
            self.end_cut_slider.show()
            self.time_label.show()
            self.start_label.show()
            self.end_label.show()
            self.play_pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.cut_button.setEnabled(True)
            self.cut_button.show()  

    def play_pause(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_pause_button.setText("Продолжить")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Пауза")

    def stop(self):
        self.media_player.stop()
        self.timer.stop()
        self.play_pause_button.setText("Воспроизвести")

    def set_position(self, position):
        self.media_player.set_position(position / 1000.0)

    def update_ui(self):
        current_time = self.media_player.get_time() / 1000 
        total_time = self.media_player.get_length() / 1000 

        if total_time > 0:
            self.seek_slider.setValue(int((current_time / total_time) * 1000))
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)}")

           
            self.start_cut_slider.setRange(0, int(total_time * 1000))
            self.end_cut_slider.setRange(0, int(total_time * 1000))
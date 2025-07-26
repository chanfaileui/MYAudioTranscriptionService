from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QDoubleSpinBox, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import QSize, Qt
import sys
from transcription_pipeline import transcribe_video

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MYVideoTranscriber")
        self.setFixedSize(500, 300)
        
        # UI setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.status_label = QLabel("Ready to transcribe")
        self.progress_bar = QProgressBar()
        self.start_button = QPushButton("Select Video & Start")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.start_button)
        
        # self.start_button.clicked.connect(self.start_transcription)
    def start_transcription(self):
        # For now, hardcode the file path
        # Later you'll add file dialog
        video_path = "examples/3331.mp4"
        
        # self.worker = TranscriptionWorker(video_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.transcription_complete)
        self.worker.error.connect(self.transcription_error)
        
        self.start_button.setEnabled(False)
        self.worker.start()
    
    def update_progress(self, message, progress):
        self.status_label.setText(message)
        self.progress_bar.setValue(int(progress * 100))
    
    def transcription_complete(self, result):
        self.status_label.setText(f"Complete! Saved: {result['output_file']}")
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)
    
    def transcription_error(self, error):
        self.status_label.setText(f"Error: {error}")
        self.start_button.setEnabled(True)

app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()

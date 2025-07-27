import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MYTranscriptionService")
        self.setAcceptDrops(True)

        button = QPushButton("Click to browse filees")
        self.setCentralWidget(button)
        button.clicked.connect(self.button_clicked)

    def button_clicked(self):
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        fileName, filter_used = QFileDialog.getOpenFileName(
            self, 
            self.tr("Select Audio/Video File"), 
            desktop_dir,
            self.tr("Audio/Video Files (*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.mp4 *.avi *.mov *.mkv *.webm)")
        )
        if fileName:
            print(f"You selected: {fileName}")
        else:
            print("No file selected")
    
    def dragEnterEvent(self, event):  # Added 'self' parameter
        if event.mimeData().hasUrls():  # Check if it's files being dropped
            event.accept()  # Say "yes, I'll take this"
        else:
            event.ignore()  # Say "no thanks"

    def dropEvent(self, event):  # Added 'self' parameter
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file_path in files:
            print(f"You dropped: {file_path}")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
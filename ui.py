import os
import sys

from PySide6.QtCore import QSize, Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QComboBox,
    QPushButton,
    QHBoxLayout,
)

from transcriber import TranscriptionService


class TranscriptionWorker(QThread):
    # Signals to communicate back to main thread
    progress_updated = Signal(str)  # For status messages
    transcription_finished = Signal(dict)  # When done successfully
    transcription_failed = Signal(str)  # When error occurs

    def __init__(self, file_path, output_folder, model_size):
        super().__init__()
        self.file_path = file_path
        self.output_folder = output_folder
        self.model_size = model_size
        self._stop_requested = False

    def stop(self):
        """Request the worker to stop"""
        self._stop_requested = True

    def run(self):
        # This method runs in the background thread
        try:
            if self._stop_requested:
                return

            def progress_callback(message, percent):
                if self._stop_requested:
                    raise Exception("Operation cancelled by user")
                self.progress_updated.emit(f"{percent}% - {message}")

            service = TranscriptionService(model_size=self.model_size)

            result = service.transcribe_video(
                video_path=self.file_path,
                output_dir=self.output_folder,
                progress_callback=progress_callback,
            )

            if not self._stop_requested:
                self.transcription_finished.emit(result)
        except Exception as e:
            if "cancelled by user" in str(e):
                self.transcription_failed.emit("Operation cancelled")
            else:
                self.transcription_failed.emit(str(e))
        finally:
            if 'service' in locals():
                service.cleanup()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MYTranscribeService")
        self.setMinimumSize(330, 300)

        # Define valid file extensions
        self.valid_extensions = {
            '.mp3',
            '.wav',
            '.flac',
            '.m4a',
            '.ogg',
            '.aac',
            '.mp4',
            '.avi',
            '.mov',
            '.mkv',
            '.webm',
        }

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.drop_area = QLabel("Drag & Drop Video Here\n\nor click to browse files")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 50px;
                font-size: 16px;
                color: #666;
                background-color: #f9f9f9;
            }
            QLabel:hover {
                border-color: #C18EFF;
                background-color: #F5EDFF;
                color: #333;
            }
        """
        )

        # Make the drop area clickable and droppable
        self.drop_area.setAcceptDrops(True)
        self.drop_area.mousePressEvent = self.browse_files

        layout.addWidget(self.drop_area)

        # Horizontal layout for model and output controls
        controls_layout = QHBoxLayout()

        # Model selection dropdown
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Tiny", "Base", "Small", "Medium", "Large"])
        self.model_combo.setCurrentText("Base")  # Default selection

        # Group label and select box together
        model_layout = QHBoxLayout()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.setSpacing(5)

        model_widget = QWidget()
        model_widget.setLayout(model_layout)

        # Output folder selection
        self.output_button = QPushButton("Choose Output Folder")
        self.output_button.clicked.connect(self.choose_output_folder)

        # Add to horizontal layout
        controls_layout.addWidget(model_widget)
        controls_layout.addWidget(self.output_button, 1)

        layout.addLayout(controls_layout)

        self.start_button = QPushButton("Start Transcription")
        self.start_button.clicked.connect(self.start_transcription)

        layout.addWidget(self.start_button)

        # Storing files and folder destination
        self.selected_file = None
        self.output_folder = None

        # Enable drag & drop on whole window
        self.setAcceptDrops(True)

    def is_valid_file(self, file_path):
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.valid_extensions

    def browse_files(self, event):
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        fileName, filter_used = QFileDialog.getOpenFileName(
            self,
            "Select Audio/Video File",
            desktop_dir,
            "Audio/Video Files (*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.mp4 *.avi *.mov *.mkv *.webm)",
        )
        if fileName:
            print(f"You selected: {fileName}")
            self.selected_file = fileName
            self.show_selected_file(fileName)
        else:
            print("No file selected")

    def show_selected_file(self, file_path):
        file_name = os.path.basename(file_path)
        self.drop_area.setText(
            f"Selected: {file_name}\n\nClick to choose a different file"
        )
        self.drop_area.setStyleSheet(
            """
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 50px;
                font-size: 16px;
                color: #2E7D32;
                background-color: #E8F5E8;
            }
        """
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.drop_area.setStyleSheet(
                """
                QLabel {
                    border: 2px solid #2196F3;
                    border-radius: 10px;
                    padding: 50px;
                    font-size: 16px;
                    color: #1976D2;
                    background-color: #E3F2FD;
                }
            """
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                padding: 50px;
                font-size: 16px;
                color: #666;
                background-color: #f9f9f9;
            }
            QLabel:hover {
                border-color: #C18EFF;
                background-color: #F5EDFF;
                color: #333;
            }
        """
        )

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            file_path = files[0]
            if self.is_valid_file(file_path):
                print(f"You dropped: {file_path}")
                self.selected_file = file_path
                self.show_selected_file(file_path)
            else:
                file_name = os.path.basename(file_path)
                self.drop_area.setText(
                    f"Invalid file: {file_name}\n\nPlease drop a valid audio/video file"
                )

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Output Folder")
        if folder:
            self.output_folder = folder
            folder_name = os.path.basename(folder) or folder
            self.output_button.setText(f"Output: {folder_name}")
            print(f"Output folder: {folder}")

    def start_transcription(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.stop_transcription()
            return

        if not self.selected_file:
            print("Please select a video/audio file first.")
            return

        if not self.output_folder:
            print("Please choose an output folder first.")
            return

        model = self.model_combo.currentText().lower()

        print(f"Starting transcription...")
        print(f"   File: {self.selected_file}")
        print(f"   Model: {model}")
        print(f"   Output: {self.output_folder}")

        # Update UI
        self.start_button.setText("Click to Stop Transcription")

        # Create and start worker thread
        self.worker = TranscriptionWorker(self.selected_file, self.output_folder, model)

        # Connect worker signals to methods
        self.worker.progress_updated.connect(self.on_progress_update)
        self.worker.transcription_finished.connect(self.on_transcription_done)
        self.worker.transcription_failed.connect(self.on_transcription_error)

        # Start the background work
        self.worker.start()

    def stop_transcription(self):
        """Stop the current transcription"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            print("Stopping transcription...")
            self.worker.stop()
            self.start_button.setText("Stopping...")
            self.start_button.setEnabled(False)

            # Wait a moment for cleanup, then reset
            QTimer.singleShot(2000, self.reset_ui)

    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_button.setText("Start Transcription")
        self.start_button.setEnabled(True)

    def on_progress_update(self, message):
        print(f"{message}")

    def on_transcription_done(self, result):
        print(f"Done! Saved to {result['output_file']}")
        print(
            f"Processed {result['word_count']} words in {result['processing_time']:.2f} seconds"
        )

        self.reset_ui()

    def on_transcription_error(self, error_message):
        print(f"Error: {error_message}")

        self.reset_ui()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

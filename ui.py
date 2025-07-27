import os
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QComboBox,
    QPushButton,
    QHBoxLayout
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MYTranscribeService")
        self.setMinimumSize(330, 300)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create the drop area
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
        
        # Create horizontal layout for model and output controls
        controls_layout = QHBoxLayout()
        
        # Model selection dropdown
        model_label = QLabel("Model:")

        self.model_combo = QComboBox()
        self.model_combo.addItems(["Tiny", "Base", "Small", "Medium", "Large"])
        self.model_combo.setCurrentText("Base")  # Default selection
        
        # Create a sub-layout for label + combo to keep them together
        model_layout = QHBoxLayout()
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.setSpacing(5)

        model_widget = QWidget()
        model_widget.setLayout(model_layout)

        # Output folder selection
        self.output_button = QPushButton("Choose Output Folder")
        # self.output_button.clicked.connect(self.choose_output_folder)

        # Add to horizontal layout
        controls_layout.addWidget(model_widget)
        controls_layout.addStretch()
        controls_layout.addWidget(self.output_button)
        
        # Add controls to main layout
        layout.addLayout(controls_layout)
        
        # Create the big start button
        self.start_button = QPushButton("Start Transcription")
        # self.start_button.clicked.connect(self.start_transcription)
       
        layout.addWidget(self.start_button)

        # Add stretch to push everything up
        # layout.addStretch()
        
        # Store selected output folder
        self.output_folder = None

        # Enable drag & drop on the whole window
        self.setAcceptDrops(True)



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
            # Visual feedback when dragging over
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
        # Reset styling when drag leaves
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
            print(f"You dropped: {file_path}")
            self.show_selected_file(file_path)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

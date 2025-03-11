from PyQt6.QtCore import Qt, pyqtSignal as Signal, QMimeData, QSize
from PyQt6.QtGui import QFont, QDropEvent, QIcon
from PyQt6.QtWidgets import *
from qasync import QApplication, asyncSlot, QEventLoop
import asyncio
import sys
import ctypes

class MainWindow(QMainWindow):
    """
    Simple class to generate a PyQt6 GUI window.
    """
    def __init__(self):
        super().__init__()
        myappid = 'smu.nerd.sonographer.v1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.setWindowTitle("SonoGrapher")
        app_icon = QIcon('gui/icons/favicon.png')
        self.setWindowIcon(app_icon)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(20, 50, 20, 50)

        self.app_title = QLabel("Sonogram Report Generator")
        self.app_title.setMargin(20)
        self.app_title.setFont(QFont("Arial", 25))
        self.app_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.app_title)

        self.drop_here = QLabel("\n\nDrag and drop a .txt or .wav file.\n\n")
        self.drop_here.setMargin(20)
        self.drop_here.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_here.setStyleSheet('''
            QLabel{
                border: 3px dashed #aaa;
                font-size: 18px;
            }
        ''')
        self.drop_here.setAcceptDrops(True)  # Enable drag and drop on this label
        self.drop_here.setObjectName("drop_here")
        self.layout.addWidget(self.drop_here)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.container.setAcceptDrops(True)
        self.setCentralWidget(self.container)

    def dragEnterEvent(self, event: QDropEvent):
        """Handle drag events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()  # Get the local file path
                if file_path[-3:] == "wav" or file_path[-3:] == "txt ":
                    event.acceptProposedAction()
                else:
                    event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()  # Get the local file path
            if file_path[-3:] == "wav" or file_path[-3:] == "txt ":
                self.drop_here.setText(f"File Dropped: {file_path}")  # Update label text with file path
                print(f"File dropped: {file_path}")  # You can further process this file as needed
                
            else:
                event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()

from PyQt6.QtCore import Qt, pyqtSignal as Signal, QMimeData
from PyQt6.QtGui import QFont, QDropEvent
from PyQt6.QtWidgets import *
from qasync import QApplication, asyncSlot, QEventLoop
import asyncio
import sys


class MainWindow(QMainWindow):
    """
        Simple class to generate a PyQt6 GUI window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SonoGrapher")
        self.setWindowIcon(QtGui.QIcon('favicon.png'))

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(20, 50, 20, 50)

        self.app_title = QLabel("Sonogram Report Generator")
        self.app_title.setMargin(20)
        self.app_title.setFont(QFont("Arial", 25))
        self.app_title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.app_title)

        drop_here = QLabel("\n\nDrag and drop a .txt or .wav file.\n\n")
        drop_here.setMargin(20)
        drop_here.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_here.setStyleSheet('''
            QLabel{
                border: 3px dashed #aaa;
                font-size: 18px;
            }
        ''')

        self.layout.addWidget(drop_here)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
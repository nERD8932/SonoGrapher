from PyQt6.QtCore import Qt, pyqtSignal as Signal, QMimeData, QSize
from PyQt6.QtGui import QFont, QDropEvent, QIcon, QMovie
from PyQt6.QtWidgets import *
import asyncio
import sys
import ctypes
import os
import requests
from pprint import pprint
from dotenv import load_dotenv
from qasync import asyncSlot, QEventLoop

load_dotenv()

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
        self.drop_here.setFixedSize(400,300)
        self.drop_here.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_here.setWordWrap(True)

        self.spinner_label = QLabel("")
        self.spinner_label.setMargin(20)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setFixedSize(400,300)
        self.spinner = QMovie('gui/icons/loading.gif')
        self.spinner.setScaledSize(QSize(50, 50))
        self.spinner_label.setMovie(self.spinner)
        self.spinner_label.setWordWrap(True)
        self.spinner.start()
        self.spinner_label.hide()

        self.layout.addWidget(self.drop_here, alignment=Qt.AlignmentFlag.AlignCenter)

        self.is_filled = False
        self.file_loc = ""

        self.generate_button = QPushButton("Generate")
        self.generate_button.setFixedSize(100,35)
        self.generate_button.clicked.connect(self.handelClick)
        self.layout.addWidget(self.generate_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.no_file = QLabel("")
        self.no_file.setStyleSheet('''
                    QLabel{
                        color: #e3735f;
                    }
        ''')
        self.layout.addWidget(self.no_file, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.container.setAcceptDrops(True)
        self.setCentralWidget(self.container)


    @asyncSlot()
    async def handelClick(self):
        if not self.is_filled:
            self.no_file.setText("No file selected!")
        else:
            self.no_file.setText("")
            self.layout.replaceWidget(self.drop_here, self.spinner_label)
            self.drop_here.hide()
            self.spinner_label.show()
            self.spinner.start()
            self.generate_button.setDisabled(True)

            x = await self.fetchDoc()
            self.layout.replaceWidget(self.spinner_label, self.drop_here)
            self.drop_here.show()
            self.spinner_label.hide()
            self.drop_here.setText("\n\nDrag and drop a .txt or .wav file.\n\n")
            self.is_filled = False
            self.file_loc = ""
            self.generate_button.setDisabled(False)

    @asyncSlot()
    async def fetchDoc(self):
        headers = {"Authorization": f"Bearer {os.environ.get('BEARER_TOKEN')}"}

        try:
            # Move the blocking requests call to a separate thread
            response = await asyncio.to_thread(self.upload_file, headers)
            # print(response)
            if not os.path.exists('./docs/'):
                os.makedirs('./docs/')

            fname = './docs/generated_doc'
            docnoint = 1
            docno = ""
            while os.path.exists(f"{fname}{docno}.docx"):
                docnoint += 1
                docno = str(docnoint)

            fname = f"{fname}{docno}.docx"

            with open(fname, 'wb') as f:
                f.write(response.content)
            os.system(f'start {fname}')
        except Exception as e:
            self.no_file.setText("An error occurred while contacting the server, please try again later!")


    def upload_file(self, headers):
        """ Synchronous function to run in a separate thread """
        with open(self.file_loc, 'rb') as file:

            if self.file_loc[-3:] == "wav":
                files = {'audio': file}
            else:
                files = {'text': file}

            r = requests.post("http://127.0.0.1:5000/api/generate-report", headers=headers, files=files)
            # pprint(vars(r))
            return r

    def dragEnterEvent(self, event: QDropEvent, **kwargs):
        """ Handle drag events
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()  # Get the local file path
                if file_path[-3:] == "wav" or file_path[-3:] == "txt":
                    event.acceptProposedAction()
                else:
                    event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent, **kwargs):
        """ Handle drop events
        """
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()  # Get the local file path
            if file_path[-3:] == "wav" or file_path[-3:] == "txt":
                self.drop_here.setText(f"File Dropped: {file_path.split('/')[-1]}")  # Update label text with file path
                self.is_filled = True
                self.file_loc = file_path
                # print(f"File dropped: {file_path}")  # You can further process this file as needed
            else:
                event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)  # Use qasync's event loop
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()

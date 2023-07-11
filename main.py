import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.process_text)

        self.layout = QVBoxLayout()
        self.panels_layout = QHBoxLayout()

        self.text_entry = QTextEdit()
        self.panels_layout.addWidget(self.text_entry, stretch=1)  # Set stretch factor to 1

        self.web_view = QWebEngineView()
        self.panels_layout.addWidget(self.web_view, stretch=1)  # Set stretch factor to 1

        self.layout.addLayout(self.panels_layout)

        self.dropdown = QComboBox()
        self.dropdown.addItems(["OpenAI_GPT3.5", "OpenAI_GPT4", "LlamaCpp", "GPT4All"])
        self.dropdown.setMinimumWidth(self.dropdown.sizeHint().width())  # Make the dropdown fit its content

        self.dropdown_layout = QHBoxLayout()
        self.dropdown_layout.addWidget(self.dropdown)
        self.dropdown_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))  # Add a spacer item to the right of the dropdown

        self.layout.addLayout(self.dropdown_layout)

        self.setLayout(self.layout)

        self.text_entry.textChanged.connect(self.on_text_changed)

        self.resize(1024, 768)  # Set the initial size of the window

        self.current_html = ""

    def on_text_changed(self):
        self.timer.start(2000)

    def process_text(self):
        text = self.text_entry.toPlainText()
        processed_text = text + "\n\nprocessed...\n\n---"
        new_html = markdown.markdown(processed_text)

        self.current_html = f"{new_html}\n<hr>\n{self.current_html}"

        self.web_view.setHtml(self.current_html)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())

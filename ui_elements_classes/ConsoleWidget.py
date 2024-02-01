import sys

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit, QLineEdit
from code import InteractiveInterpreter


class ConsoleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.console_input = QLineEdit(self)

        self.console_input.returnPressed.connect(self.run_code)

        self.layout.addWidget(self.text_edit)
        self.layout.addWidget(self.console_input)

        self.capture_output = CaptureOutput(self.text_edit)
        self.interpreter = InteractiveInterpreter()

    def run_code(self):
        code = self.console_input.text()
        self.console_input.clear()
        self.text_edit.append(">>>" + code + "\n")

        # Redirect stdout to capture the output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = sys.stderr = self.capture_output

        try:
            self.interpreter.runcode(code)
        except Exception as e:
            self.text_edit.append(f"Error: {str(e)}\n")

        # Restore the original stdout
        sys.stdout = original_stdout
        sys.stderr = original_stderr


class CaptureOutput:
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self.cursor = text_edit.textCursor()

    def write(self, text):
        self.cursor.movePosition(QTextCursor.End)
        self.cursor.insertText(text)
        self.text_edit.setTextCursor(self.cursor)
        self.text_edit.ensureCursorVisible()

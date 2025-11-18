from PySide6.QtCore import QThread, Signal
from typing import Optional

from scanner.runner import run_scan

class ScanWorker(QThread):
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, output_path: str, output_format: str, strict_mode: bool, compare: bool, generate_fix: bool):
        super().__init__()
        self.output_path = output_path
        self.output_format = output_format
        self.strict_mode = strict_mode
        self.compare = compare
        self.generate_fix = generate_fix

    def _cb(self, message: str):
        self.progress.emit(message)

    def run(self):
        try:
            result = run_scan(
                output_path=self.output_path,
                output_format=self.output_format,
                strict_mode=self.strict_mode,
                compare=self.compare,
                generate_fix=self.generate_fix,
                skip_admin=True,
                progress_callback=self._cb,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

import sys
import os
# Ensure project root is on sys.path so local module imports work both for `python ui/app.py` and `python -m ui.app`
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QProgressBar, QFileDialog, QMessageBox, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl
try:
    # When running as a package: python -m ui.app
    from ui.scan_worker import ScanWorker
except Exception:
    # When running as a script: python ui/app.py
    from scan_worker import ScanWorker

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "CE_Icon.png")
ICO_PATH = os.path.join(ASSETS_DIR, "CE_Icon.ico")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Essentials Scanner")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setMinimumSize(600, 400)
        self.setStyleSheet(self._main_stylesheet())
        self._init_ui()
        self.process = None
        self.worker: ScanWorker | None = None
        self.last_error = None

    def _init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(32, 24, 32, 24)

        # Title
        title = QLabel("Cyber Essentials Scanner")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a3a5d; margin-bottom: 8px;")
        layout.addWidget(title)

        # Mode selection
        mode_group = QGroupBox("Compliance Mode")
        mode_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #333; }")
        mode_layout = QHBoxLayout()
        self.rb_standard = QRadioButton("Standard (Personal/BYOD)")
        self.rb_standard.setStyleSheet("QRadioButton { font-size: 13px; color: #000; }")
        self.rb_strict = QRadioButton("Strict (Corporate/Managed)")
        self.rb_strict.setStyleSheet("QRadioButton { font-size: 13px; color: #000; }")
        self.rb_standard.setChecked(True)
        mode_layout.addWidget(self.rb_standard)
        mode_layout.addWidget(self.rb_strict)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Output format
        fmt_group = QGroupBox("Report Format")
        fmt_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; color: #333; }")
        fmt_layout = QHBoxLayout()
        self.rb_json = QRadioButton("JSON")
        self.rb_json.setStyleSheet("QRadioButton { font-size: 13px; color: #000; }")
        self.rb_html = QRadioButton("HTML")
        self.rb_html.setStyleSheet("QRadioButton { font-size: 13px; color: #000; }")
        self.rb_both = QRadioButton("Both")
        self.rb_both.setStyleSheet("QRadioButton { font-size: 13px; color: #000; }")
        self.rb_both.setChecked(True)
        fmt_layout.addWidget(self.rb_json)
        fmt_layout.addWidget(self.rb_html)
        fmt_layout.addWidget(self.rb_both)
        fmt_group.setLayout(fmt_layout)
        layout.addWidget(fmt_group)

        # Run Scan button
        btn_layout = QHBoxLayout()
        self.btn_run = QPushButton("Run Scan")
        self.btn_run.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d7a2d, stop:1 #4bb34b);
                color: white;
                border-radius: 6px;
                padding: 10px 40px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #236323, stop:1 #3a9a3a);
            }
            QPushButton:disabled {
                background: #b0b0b0;
                color: #eee;
            }
        """)
        self.btn_run.clicked.connect(self.run_scan)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        btn_layout.addWidget(self.btn_run)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 28px;
                font-size: 14px;
                border: 2px solid #b0b0b0;
                border-radius: 8px;
                background: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d7a2d, stop:1 #4bb34b);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress)

        # Status label
        self.status_label = QLabel("Ready to scan")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #2d7a2d; font-weight: bold; min-height: 40px;")
        layout.addWidget(self.status_label)

        # Open report button
        self.btn_open_report = QPushButton("Open Last HTML Report")
        self.btn_open_report.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
            QPushButton:disabled {
                background: #d0d0d0;
                color: #888;
            }
        """)
        self.btn_open_report.setEnabled(False)
        self.btn_open_report.clicked.connect(self.open_html_report)
        layout.addWidget(self.btn_open_report)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def run_scan(self):
        self.status_label.setText("Starting scan...")
        self.progress.setValue(0)
        self.btn_run.setEnabled(False)
        self.btn_open_report.setEnabled(False)
        self.last_error = None
        mode = "strict" if self.rb_strict.isChecked() else "standard"
        fmt = "json" if self.rb_json.isChecked() else ("html" if self.rb_html.isChecked() else "both")
        output_name = "gui_scan_report.json"
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", output_name)
        # Run scan in a worker thread to avoid blocking the UI
        self.worker = ScanWorker(output_path, fmt, mode == "strict", compare=False, generate_fix=False)
        self.worker.progress.connect(self._parse_progress)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()

    # Worker progress and callbacks
    def _on_worker_error(self, msg: str):
        self.status_label.setText(f"<span style='color:#b00;'>Error: {msg}</span>")


    def _parse_progress(self, text):
        # Simple progress feedback
        if "Checking" in text:
            import re
            m = re.search(r"\[(\d+)/(\d+)\] Checking (.+?)\.\.\. (.+)", text)
            if m:
                idx, total, ctrl, status = m.groups()
                percent = int(int(idx) / int(total) * 100)
                self.progress.setValue(percent)
                self.status_label.setText(f"{ctrl}: {status}")
            else:
                # Support split messages where status appears on a separate line
                m2 = re.search(r"\[(\d+)/(\d+)\] Checking (.+?)\.\.\.", text)
                if m2:
                    idx, total, ctrl = m2.groups()
                    percent = int(int(idx) / int(total) * 100)
                    self.progress.setValue(percent)
                    self.status_label.setText(f"{ctrl}: running...")
        if "Overall Status:" in text:
            self.progress.setValue(100)
            self.status_label.setText(text.strip())
        # Support 'Name => status' lines from programmatic runner
        import re
        m3 = re.search(r"(.+?)\s*=>\s*(pass|warn|fail|unknown)", text, flags=re.IGNORECASE)
        if m3:
            ctrl, st = m3.groups()
            self.status_label.setText(f"{ctrl}: {st.upper()}")
        if "HTML report saved to:" in text or "HTML saved to:" in text:
            self.btn_open_report.setEnabled(True)
            self.last_html_path = text.strip().split(":", 1)[-1].strip()
        if "JSON saved to:" in text or "JSON saved to" in text or "JSON saved to:" in text:
            # nothing to do here; used for confirmation in progress
            pass

    def _on_worker_finished(self, result: dict):
        self.btn_run.setEnabled(True)
        json_path = result.get("json_path")
        html_path = result.get("html_path")
        fmt = "html" if self.rb_html.isChecked() else ("json" if self.rb_json.isChecked() else "both")

        if fmt in ("both", "html") and html_path and os.path.exists(html_path):
            self.last_html_path = html_path
            self.btn_open_report.setEnabled(True)
            self.status_label.setText("<span style='color:#2d7a2d;'>Scan complete. Report saved.</span>")
        elif fmt == "json" and json_path and os.path.exists(json_path):
            self.status_label.setText("<span style='color:#2d7a2d;'>Scan complete. JSON report saved.</span>")
        else:
            self.status_label.setText("<span style='color:#b00;'>Scan complete but no report found.</span>")

    def open_html_report(self):
        if hasattr(self, "last_html_path") and os.path.exists(self.last_html_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.last_html_path))
        else:
            QMessageBox.warning(self, "Report Not Found", "No HTML report found to open.")

    def _main_stylesheet(self):
        return """
        QMainWindow {
            background: #f5f7fa;
        }
        """

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QProgressBar, QFileDialog, QMessageBox, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtCore import Qt, QProcess, QUrl

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
        args = [sys.executable, "-m", "scanner.main", "--no-admin", f"--output", output_path, f"--format", fmt]
        if mode == "strict":
            # Use the CLI flag supported by scanner: --strict-mode
            args.append("--strict-mode")
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._scan_finished)
        self.process.start(args[0], args[1:])

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self._parse_progress(data)

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='ignore')
        if not data:
            return

        # Filter out non-critical warnings and info noise (verbose messages)
        lowered = data.lower()
        # Show only serious issues (tracebacks, unrecognized args, exception, failed)
        show_keywords = ["traceback", "unrecognized arguments", "exception", "failed", "error:"]
        if any(k in lowered for k in show_keywords):
            # Display helpful, user-friendly extract of the error
            first_line = data.strip().splitlines()[0]
            self.status_label.setText(f"<span style='color:#b00;'>Error: {first_line}</span>")
            self.last_error = data
        else:
            # Ignore noisy stderr output (info/encoding messages coming from the scanner)
            pass

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
        if "Overall Status:" in text:
            self.progress.setValue(100)
            self.status_label.setText(text.strip())
        if "HTML report saved to:" in text:
            self.btn_open_report.setEnabled(True)
            self.last_html_path = text.strip().split(":", 1)[-1].strip()

    def _scan_finished(self, exit_code: int = 0, exit_status=None):
        # Called when the scanner process finishes
        self.btn_run.setEnabled(True)

        if exit_code != 0:
            # Show error (already potentially set in stderr handler)
            msg = getattr(self, "last_error", "The scanner exited with an error.")
            self.status_label.setText(f"<span style='color:#b00;'>Scan failed: {msg}</span>")
            return

        # On success, verify that expected report files exist
        # The scanner stores JSON in reports/json/ and HTML in reports/html/
        output_name = "gui_scan_report.json"
        root_reports = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        json_path = os.path.join(root_reports, "json", output_name)
        html_path = os.path.join(root_reports, "html", output_name.replace('.json', '.html'))

        # If output format includes HTML, enable open button if file exists
        fmt = "html" if self.rb_html.isChecked() else ("json" if self.rb_json.isChecked() else "both")
        if fmt in ("both", "html") and os.path.exists(html_path):
            self.last_html_path = html_path
            self.btn_open_report.setEnabled(True)
            self.status_label.setText("<span style='color:#2d7a2d;'>Scan complete. Report saved.</span>")
        elif fmt == "json" and os.path.exists(json_path):
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

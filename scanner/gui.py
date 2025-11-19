"""
PySide6 GUI for Cyber Essentials Scanner
Provides a user-friendly graphical interface for running security compliance scans.
"""
from __future__ import annotations

import sys
import json
import os
import threading
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QProgressBar, QGroupBox,
    QComboBox, QCheckBox, QLineEdit, QFileDialog, QTabWidget,
    QMessageBox, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView, QStatusBar
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QFont, QColor, QTextCursor

from scanner.runner import run_scan


class ScanWorker(QObject):
    """Worker thread for running scans without blocking the UI"""
    
    progress = Signal(str)  # Progress messages
    finished = Signal(dict)  # Scan results
    error = Signal(str)  # Error messages
    
    def __init__(self, output_path, output_format, strict_mode, compare, generate_fix):
        super().__init__()
        self.output_path = output_path
        self.output_format = output_format
        self.strict_mode = strict_mode
        self.compare = compare
        self.generate_fix = generate_fix
    
    def run(self):
        """Execute the scan"""
        try:
            result = run_scan(
                output_path=self.output_path,
                output_format=self.output_format,
                strict_mode=self.strict_mode,
                compare=self.compare,
                generate_fix=self.generate_fix,
                skip_admin=True,
                progress_callback=self.progress.emit
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class CyberEssentialsGUI(QMainWindow):
    """Main GUI window for Cyber Essentials Scanner"""
    
    def __init__(self):
        super().__init__()
        self.scan_thread = None
        self.scan_worker = None
        self.current_report = None
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Cyber Essentials Scanner v0.2.0")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("🛡️ Cyber Essentials System Scanner")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("UK Cyber Essentials v3.2 (2025) - Compliance Verification Tool")
        subtitle_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Configuration Group
        config_group = QGroupBox("Scan Configuration")
        config_layout = QVBoxLayout()
        
        # Compliance Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Compliance Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Standard (Personal/BYOD)", "Strict (Corporate/Managed)"])
        self.mode_combo.setToolTip(
            "Standard: For personal devices, BYOD (conditional checks as warnings)\n"
            "Strict: For corporate/managed devices (all checks mandatory)"
        )
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        config_layout.addLayout(mode_layout)
        
        # Output Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Both (JSON + HTML)", "JSON Only", "HTML Only"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        config_layout.addLayout(format_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.compare_checkbox = QCheckBox("Compare with previous scan")
        self.remediation_checkbox = QCheckBox("Generate remediation script (Windows only)")
        options_layout.addWidget(self.compare_checkbox)
        options_layout.addWidget(self.remediation_checkbox)
        options_layout.addStretch()
        config_layout.addLayout(options_layout)
        
        # Output Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Report Name:"))
        self.output_path_edit = QLineEdit("report.json")
        path_layout.addWidget(self.output_path_edit)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_path)
        path_layout.addWidget(self.browse_button)
        config_layout.addLayout(path_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # Scan Controls
        controls_layout = QHBoxLayout()
        self.scan_button = QPushButton("🔍 Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setMinimumHeight(40)
        controls_layout.addWidget(self.scan_button)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        self.stop_button.setMinimumHeight(40)
        controls_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("🗑 Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        self.clear_button.setMinimumHeight(40)
        controls_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(controls_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        main_layout.addWidget(self.progress_bar)
        
        # Create tabbed interface for results
        self.tabs = QTabWidget()
        
        # Progress/Log Tab
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(200)
        self.tabs.addTab(self.progress_text, "📝 Scan Progress")
        
        # Results Tab
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Overall Status
        self.overall_status_label = QLabel("Overall Status: Not scanned")
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.overall_status_label.setFont(status_font)
        self.overall_status_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.overall_status_label)
        
        # Controls Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Control", "Status", "Score", "Summary"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        
        self.tabs.addTab(results_widget, "📊 Results Summary")
        
        # Detailed Report Tab
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.tabs.addTab(self.report_text, "📄 Detailed Report")
        
        # Recommendations Tab
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.tabs.addTab(self.recommendations_text, "💡 Recommendations")
        
        main_layout.addWidget(self.tabs)
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready to scan")
        
        # Info label at bottom
        info_label = QLabel(
            "ℹ️ Note: Some checks require elevated privileges for complete results. "
            "Run with administrator/sudo for full detection."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #88b3d9; padding: 5px; background-color: #002649; border-radius: 3px;")
        main_layout.addWidget(info_label)
    
    def apply_styles(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #001b37;
            }
            QWidget {
                background-color: #001b37;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0a3d62;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #002649;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4a9eff;
            }
            QPushButton {
                background-color: #0a3d62;
                color: #ffffff;
                border: 1px solid #4a9eff;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d4d7d;
                border: 1px solid #6bb3ff;
            }
            QPushButton:pressed {
                background-color: #053154;
            }
            QPushButton:disabled {
                background-color: #003050;
                color: #666666;
                border: 1px solid #004060;
            }
            QProgressBar {
                border: 2px solid #0a3d62;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: #002649;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 3px;
            }
            QTableWidget {
                gridline-color: #0a3d62;
                background-color: #002649;
                color: #ffffff;
                border: 1px solid #0a3d62;
            }
            QTableWidget::item {
                padding: 5px;
                background-color: #002649;
                color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #0a3d62;
            }
            QHeaderView::section {
                background-color: #0a3d62;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #001b37;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #002649;
                border: 1px solid #0a3d62;
                border-radius: 3px;
                color: #ffffff;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #0a3d62;
                border-radius: 3px;
                background-color: #002649;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #0a3d62;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #ffffff;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #002649;
                color: #ffffff;
                selection-background-color: #0a3d62;
                border: 1px solid #0a3d62;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #0a3d62;
                border-radius: 3px;
                background-color: #002649;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border: 1px solid #4a9eff;
            }
            QLabel {
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #0a3d62;
                background-color: #001b37;
            }
            QTabBar::tab {
                background-color: #002649;
                color: #ffffff;
                border: 1px solid #0a3d62;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0a3d62;
                border-bottom: 2px solid #4a9eff;
            }
            QTabBar::tab:hover {
                background-color: #0d4d7d;
            }
            QStatusBar {
                background-color: #002649;
                color: #ffffff;
                border-top: 1px solid #0a3d62;
            }
        """)
    
    def browse_output_path(self):
        """Open file dialog to select output path"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            "reports/report.json",
            "JSON Files (*.json)"
        )
        if file_name:
            # Extract just the filename
            self.output_path_edit.setText(os.path.basename(file_name))
    
    def start_scan(self):
        """Start the security scan"""
        # Get configuration
        strict_mode = "Strict" in self.mode_combo.currentText()
        
        format_map = {
            "Both (JSON + HTML)": "both",
            "JSON Only": "json",
            "HTML Only": "html"
        }
        output_format = format_map[self.format_combo.currentText()]
        
        output_path = self.output_path_edit.text() or "report.json"
        compare = self.compare_checkbox.isChecked()
        generate_fix = self.remediation_checkbox.isChecked()
        
        # Update UI state
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Scanning...")
        self.progress_text.clear()
        self.statusBar.showMessage("Scanning in progress...")
        
        # Create worker thread
        self.scan_worker = ScanWorker(
            output_path, output_format, strict_mode, compare, generate_fix
        )
        self.scan_thread = QThread()
        self.scan_worker.moveToThread(self.scan_thread)
        
        # Connect signals
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_finished)
        self.scan_worker.error.connect(self.scan_error)
        self.scan_worker.finished.connect(self.scan_thread.quit)
        self.scan_worker.error.connect(self.scan_thread.quit)
        
        # Start scanning
        self.scan_thread.start()
    
    def stop_scan(self):
        """Stop the current scan"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.progress_text.append("\n⚠️ Scan stopped by user")
            self.statusBar.showMessage("Scan stopped")
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def update_progress(self, message):
        """Update progress display"""
        self.progress_text.append(message)
        
        # Auto-scroll to bottom
        cursor = self.progress_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.progress_text.setTextCursor(cursor)
        
        # Update progress bar based on check count
        if "Checking" in message:
            # Extract check number if present
            if "[" in message and "/" in message:
                try:
                    parts = message.split("[")[1].split("]")[0].split("/")
                    current = int(parts[0])
                    total = int(parts[1])
                    progress = int((current / total) * 100)
                    self.progress_bar.setValue(progress)
                except:
                    pass
    
    def scan_finished(self, result):
        """Handle scan completion"""
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Scan Complete")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Load and display results
        doc = result.get("doc", {})
        self.current_report = doc
        self.display_results(doc)
        
        # Update status bar
        json_path = result.get("json_path", "")
        self.statusBar.showMessage(f"Scan complete! Report saved to: {json_path}")
        
        # Show completion message
        overall = doc.get("overall", {})
        status = overall.get("status", "unknown").upper()
        score = overall.get("score", 0)
        
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Security scan completed!\n\n"
            f"Overall Status: {status}\n"
            f"Score: {score:.1f}/100\n\n"
            f"Report saved to:\n{json_path}"
        )
    
    def scan_error(self, error_msg):
        """Handle scan errors"""
        self.progress_bar.setFormat("Error")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_text.append(f"\n❌ Error: {error_msg}")
        self.statusBar.showMessage("Scan failed")
        
        QMessageBox.critical(
            self,
            "Scan Error",
            f"An error occurred during the scan:\n\n{error_msg}"
        )
    
    def display_results(self, doc):
        """Display scan results in the GUI"""
        if not doc:
            return
        
        # Overall Status
        overall = doc.get("overall", {})
        status = overall.get("status", "unknown").upper()
        score = overall.get("score", 0)
        
        status_colors = {
            "PASS": "#28a745",
            "WARN": "#ffc107",
            "FAIL": "#dc3545",
            "UNKNOWN": "#6c757d"
        }
        
        color = status_colors.get(status, "#6c757d")
        self.overall_status_label.setText(
            f"Overall Status: {status} | Score: {score:.1f}/100"
        )
        self.overall_status_label.setStyleSheet(f"color: {color};")
        
        # Populate results table
        controls = doc.get("controls", [])
        self.results_table.setRowCount(len(controls))
        
        for i, control in enumerate(controls):
            name = control.get("name", "").replace("_", " ").title()
            status = control.get("status", "unknown").upper()
            score = control.get("score", 0)
            findings = control.get("findings", [])
            summary = findings[0] if findings else "No issues found"
            
            # Name
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("", weight=QFont.Bold))
            self.results_table.setItem(i, 0, name_item)
            
            # Status
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_colors.get(status, "#6c757d")))
            status_item.setFont(QFont("", weight=QFont.Bold))
            self.results_table.setItem(i, 1, status_item)
            
            # Score
            score_item = QTableWidgetItem(f"{score:.1f}")
            self.results_table.setItem(i, 2, score_item)
            
            # Summary
            summary_item = QTableWidgetItem(summary)
            self.results_table.setItem(i, 3, summary_item)
        
        # Display detailed report
        self.report_text.clear()
        self.report_text.append("=" * 80)
        self.report_text.append("CYBER ESSENTIALS COMPLIANCE REPORT")
        self.report_text.append("=" * 80)
        self.report_text.append(f"\nScanner Version: {doc.get('scanner_version', 'N/A')}")
        self.report_text.append(f"Timestamp: {doc.get('timestamp_utc', 'N/A')}")
        self.report_text.append(f"Compliance Mode: {doc.get('compliance_mode', 'N/A').upper()}")
        
        os_info = doc.get("os", {})
        self.report_text.append(f"OS: {os_info.get('platform', 'N/A')} {os_info.get('version', 'N/A')}")
        self.report_text.append(f"\nOverall Status: {status}")
        self.report_text.append(f"Overall Score: {score:.1f}/100")
        self.report_text.append("\n" + "=" * 80)
        
        for control in controls:
            name = control.get("name", "").replace("_", " ").upper()
            status = control.get("status", "unknown").upper()
            score = control.get("score", 0)
            
            self.report_text.append(f"\n{name}")
            self.report_text.append("-" * 40)
            self.report_text.append(f"Status: {status} | Score: {score:.1f}")
            
            findings = control.get("findings", [])
            if findings:
                self.report_text.append("\nFindings:")
                for finding in findings:
                    self.report_text.append(f"  • {finding}")
            else:
                self.report_text.append("\n✓ No issues found")
        
        # Display recommendations
        self.recommendations_text.clear()
        self.recommendations_text.append("=" * 80)
        self.recommendations_text.append("RECOMMENDATIONS")
        self.recommendations_text.append("=" * 80 + "\n")
        
        has_recommendations = False
        for control in controls:
            recommendations = control.get("recommendations", [])
            if recommendations:
                has_recommendations = True
                name = control.get("name", "").replace("_", " ").title()
                self.recommendations_text.append(f"\n{name}:")
                self.recommendations_text.append("-" * 40)
                for rec in recommendations:
                    self.recommendations_text.append(f"  ➤ {rec}")
                self.recommendations_text.append("")
        
        if not has_recommendations:
            self.recommendations_text.append("✓ No recommendations - system is compliant!")
    
    def clear_results(self):
        """Clear all displayed results"""
        self.progress_text.clear()
        self.report_text.clear()
        self.recommendations_text.clear()
        self.results_table.setRowCount(0)
        self.overall_status_label.setText("Overall Status: Not scanned")
        self.overall_status_label.setStyleSheet("")
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")
        self.statusBar.showMessage("Ready to scan")
        self.current_report = None


def main():
    """Main entry point for the GUI application"""
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = CyberEssentialsGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

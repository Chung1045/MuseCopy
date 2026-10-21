import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QHBoxLayout, QMainWindow, QMessageBox, QMenu,
    QTableWidgetItem, QWidget,
)

from service.muse_process import DEFAULT_SCHEMA, SCHEMA_FIELDS, muse_process_direct
from views.muse_window import Ui_MuseCopy


class ProcessWorker(QThread):
    """Runs the copy/rename job off the UI thread so the window stays responsive."""
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    done = pyqtSignal(object)  # summary dict from the backend
    failed = pyqtSignal(str)

    def __init__(self, **job):
        super().__init__()
        self.job = job

    def run(self):
        try:
            result = muse_process_direct(**self.job, log=self.log.emit, progress=self.progress.emit)
            self.done.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class MuseCopyApp(QMainWindow, Ui_MuseCopy):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.worker = None

        # Schema placeholder menu
        menu = QMenu(self.schemaButton)
        for field in SCHEMA_FIELDS:
            menu.addAction(field.capitalize(), lambda checked=False, f=field: self.schemaEdit.insert(f"{{{f}}}"))
        self.schemaButton.setMenu(menu)
        self.schemaButton.setPopupMode(self.schemaButton.InstantPopup)
        self.schemaEdit.setText(DEFAULT_SCHEMA)

        # Signals
        self.outputBrowseButton.clicked.connect(self.browse_output_folder)
        self.addInputButton.clicked.connect(self.add_input_folder)
        self.removeInputButton.clicked.connect(self.remove_input_folder)
        self.startButton.clicked.connect(self.start_processing)
        self.logButton.toggled.connect(self.toggle_log)

    # --- folder handling ---
    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.outputEdit.setText(folder)

    def add_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Music Folder")
        if folder and folder not in self.input_folders():
            row = self.inputTable.rowCount()
            self.inputTable.insertRow(row)

            path_item = QTableWidgetItem(folder)
            path_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.inputTable.setItem(row, 0, path_item)

            self.inputTable.setCellWidget(row, 1, self.make_subfolder_checkbox())

    @staticmethod
    def make_subfolder_checkbox():
        """A centered checkbox for the 'Subfolders' column (checked = include subfolders)."""
        box = QCheckBox()
        box.setChecked(True)
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(box)
        return container

    def remove_input_folder(self):
        rows = sorted({index.row() for index in self.inputTable.selectedIndexes()}, reverse=True)
        for row in rows:  # remove bottom-up so row numbers stay valid
            self.inputTable.removeRow(row)

    def input_folders(self):
        """Returns {folder_path: include_subfolders}."""
        table = self.inputTable
        return {
            table.item(row, 0).text(): table.cellWidget(row, 1).findChild(QCheckBox).isChecked()
            for row in range(table.rowCount())
        }

    # --- log panel ---
    def toggle_log(self, visible):
        self.logView.setVisible(visible)
        self.logButton.setText("Hide Log" if visible else "Show Log")

    # --- processing ---
    def start_processing(self):
        output_folder = self.outputEdit.text().strip()
        input_folders = self.input_folders()

        if not output_folder:
            QMessageBox.warning(self, "Muse Copy", "Please select an output folder.")
            return
        if not input_folders:
            QMessageBox.warning(self, "Muse Copy", "Please add at least one input folder.")
            return

        fields_to_drop = [
            name for name, check in (
                ("comments", self.dropCommentsCheck),
                ("artwork", self.dropArtworkCheck),
                ("lyrics", self.dropLyricsCheck),
            ) if check.isChecked()
        ]

        self.logView.clear()
        self.logButton.setChecked(True)  # show the log while working
        self.progressBar.setRange(0, 0)  # busy animation until the file count is known
        self.progressBar.setFormat("%v / %m")
        self.set_running(True)

        self.worker = ProcessWorker(
            folder_configs=input_folders,
            target_copy_folder=output_folder,
            fields_to_drop=fields_to_drop,
            schema=self.schemaEdit.text().strip() or DEFAULT_SCHEMA,
        )
        self.worker.log.connect(self.logView.appendPlainText)
        self.worker.progress.connect(self.update_progress)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def update_progress(self, done, total):
        self.progressBar.setMaximum(max(total, 1))
        self.progressBar.setValue(done)

    def reset_progress(self):
        """Back to the idle look: empty bar that says 'Ready'."""
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.progressBar.setFormat("Ready")

    def on_done(self, result):
        self.set_running(False)
        total, copied, failed = result["total"], result["copied"], result["failed"]

        if total == 0:
            self.reset_progress()
            QMessageBox.information(self, "Muse Copy", "No audio files were found in the selected folders.")
        elif failed:
            self.logButton.setChecked(True)
            QMessageBox.warning(
                self, "Muse Copy",
                f"Copied {copied} of {total} file(s).\n{failed} failed - see the log for details.",
            )
        else:
            QMessageBox.information(self, "Muse Copy", f"Done! Copied {copied} file(s).")

    def on_failed(self, message):
        self.set_running(False)
        self.reset_progress()
        self.logView.appendPlainText(f"Error: {message}")
        QMessageBox.critical(self, "Muse Copy", f"Processing stopped:\n{message}")

    def set_running(self, running):
        self.startButton.setEnabled(not running)
        self.startButton.setText("Working…" if running else "Start")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "Muse Copy", "Still processing - please wait for it to finish.")
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MuseCopyApp()
    window.show()
    sys.exit(app.exec_())
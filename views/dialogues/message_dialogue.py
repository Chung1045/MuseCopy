from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QSpacerItem, QSizePolicy

from app_info import APP_NAME

TITLE = APP_NAME
DIALOGUE_MIN_WIDTH = 400

def _show(parent, icon, headline, detail="", buttons=QMessageBox.Ok, default=None, min_width=500):
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(TITLE)
    box.setText(headline)
    if detail:
        box.setInformativeText(detail)
    box.setStandardButtons(buttons)
    if default is not None:
        box.setDefaultButton(default)

    # QMessageBox ignores setMinimumWidth, so force the width with a spacer
    # in its grid layout instead.
    layout = box.layout()
    spacer = QSpacerItem(min_width, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())

    return box.exec_()

def show_info(parent, headline, detail="", min_width=DIALOGUE_MIN_WIDTH):
    _show(parent, QMessageBox.Information, headline, detail, min_width=min_width)

def show_warning(parent, headline, detail="", min_width=DIALOGUE_MIN_WIDTH):
    _show(parent, QMessageBox.Warning, headline, detail, min_width=min_width)

def show_error(parent, headline, detail="", min_width=DIALOGUE_MIN_WIDTH):
    _show(parent, QMessageBox.Critical, headline, detail, min_width=min_width)

def show_finished(parent, headline, detail, output_folder, warning=False, min_width=DIALOGUE_MIN_WIDTH):
    """Result dialog with an 'Open' button that reveals the output folder."""
    icon = QMessageBox.Warning if warning else QMessageBox.Information
    result = _show(
        parent, icon, headline, detail,
        buttons= QMessageBox.Ok | QMessageBox.Open,
        default=QMessageBox.Ok,
        min_width=min_width,
    )
    if result == QMessageBox.Open:
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_folder))
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app_info import APP_NAME, about_html, REPOSITORY_LINK


def nav_to_repository():
    """Opens the project repository in the system's default web browser."""
    url = QUrl(REPOSITORY_LINK)
    QDesktopServices.openUrl(url)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")

        self.resize(420, 260)
        self.setFixedSize(420, 260)  # Optional: prevent manual resizing

        # Layout setup
        layout = QVBoxLayout(self)

        # Content (Using your existing HTML generator)
        self.content_label = QLabel(about_html())
        self.content_label.setWordWrap(True)
        self.content_label.setOpenExternalLinks(True)  # Makes links clickable
        layout.addWidget(self.content_label)

        layout.addStretch()

        # 2. Adding multiple custom buttons
        # 2. Adding multiple custom buttons
        button_layout = QHBoxLayout()

        self.github_repo_button = QPushButton("View Github Repo")
        self.github_repo_button.setAutoDefault(False)  # Prevents it from taking the primary accent color
        self.github_repo_button.setDefault(False)
        self.github_repo_button.clicked.connect(nav_to_repository)
        button_layout.addWidget(self.github_repo_button)

        self.close_button = QPushButton("Close")
        self.close_button.setAutoDefault(False)  # Optional, good practice for secondary buttons
        self.close_button.setDefault(False)
        self.close_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)


def show_about_dialogue(parent=None):
    """Instantiates and opens the custom About dialog window."""
    dialog = AboutDialog(parent)
    dialog.exec_()
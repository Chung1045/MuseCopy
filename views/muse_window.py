from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QHeaderView,
    QTableWidget,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)


class Ui_MuseCopy(object):
    """Hand-written UI (layout-based, no absolute geometry)."""

    def setupUi(self, MuseCopy):
        MuseCopy.setWindowTitle("Muse Copy")
        MuseCopy.resize(640, 420)

        central = QWidget(MuseCopy)
        MuseCopy.setCentralWidget(central)
        root = QVBoxLayout(central)

        # --- Input folders ---
        self.addInputButton = QToolButton()
        self.addInputButton.setText("+")
        self.removeInputButton = QToolButton()
        self.removeInputButton.setText("−")

        row = QHBoxLayout()
        row.addWidget(QLabel("Input folders:"))
        row.addStretch(1)
        row.addWidget(self.addInputButton)
        row.addWidget(self.removeInputButton)
        root.addLayout(row)

        self.inputTable = QTableWidget(0, 2)
        self.inputTable.setHorizontalHeaderLabels(["Folder", "Include subfolders"])
        self.inputTable.verticalHeader().hide()
        self.inputTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inputTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.inputTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inputTable.setShowGrid(False)
        header = self.inputTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        root.addWidget(self.inputTable, 1)

        # --- Output folder ---
        self.outputEdit = QLineEdit()
        self.outputEdit.setPlaceholderText("Where processed files are copied to")
        self.outputBrowseButton = QToolButton()
        self.outputBrowseButton.setText("…")

        row = QHBoxLayout()
        row.addWidget(QLabel("Output folder:"))
        row.addWidget(self.outputEdit, 1)
        row.addWidget(self.outputBrowseButton)
        root.addLayout(row)

        # --- Rename schema ---
        self.schemaEdit = QLineEdit()
        self.schemaEdit.setPlaceholderText("{title} - {artist}")
        self.schemaButton = QToolButton()  # menu is attached in main.py
        self.schemaButton.setText("Insert")

        row = QHBoxLayout()
        row.addWidget(QLabel("Rename schema:"))
        row.addWidget(self.schemaEdit, 1)
        row.addWidget(self.schemaButton)
        root.addLayout(row)

        # --- Options ---
        self.dropCommentsCheck = QCheckBox("Comments")
        self.dropCommentsCheck.setChecked(True)
        self.dropArtworkCheck = QCheckBox("Artwork")
        self.dropLyricsCheck = QCheckBox("Lyrics")

        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(QLabel("Strip from copies:"))
        row.addWidget(self.dropCommentsCheck)
        row.addWidget(self.dropArtworkCheck)
        row.addWidget(self.dropLyricsCheck)
        root.addLayout(row)

        # --- Start / progress / log ---
        self.aboutButton = QPushButton("About")
        self.startButton = QPushButton("Start")
        self.logButton = QPushButton("Show Log")
        self.logButton.setCheckable(True)  # checked = log visible

        row = QHBoxLayout()
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.progressBar.setFormat("Ready")
        row.addWidget(self.aboutButton)
        row.addWidget(self.progressBar, 1)
        row.addWidget(self.logButton)
        row.addWidget(self.startButton)
        root.addLayout(row)

        self.logView = QPlainTextEdit()
        self.logView.setReadOnly(True)
        self.logView.setVisible(False)  # hidden until the user shows it
        root.addWidget(self.logView, 2)

        central.setStyleSheet("""
            QLineEdit, QPlainTextEdit {
                border: 1px solid #8a8a8a;
                border-radius: 4px;
                padding: 3px 6px;
            }
            QTableWidget {
                border: 1px solid #8a8a8a;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #8a8a8a;
                border-radius: 4px;
                text-align: center;
                min-height: 16px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
            QLineEdit:focus, QPlainTextEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
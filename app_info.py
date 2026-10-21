from datetime import date
from importlib import metadata

APP_NAME = "Muse Copy"
VERSION = "1.0"
AUTHOR = "Chung1045"
START_YEAR = 2026
REPOSITORY_LINK = "https://github.com/Chung1045/MuseCopy"

# (label shown in the dialog, pip distribution name)
DEPENDENCIES = [
    ("PyQt", "PyQt5"),
    ("TinyTag", "tinytag"),
    ("Mutagen", "mutagen"),
]


def copyright_years():
    current = date.today().year
    return str(START_YEAR) if current <= START_YEAR else f"{START_YEAR}–{current}"


def tech_stack():
    parts = []
    for label, dist in DEPENDENCIES:
        try:
            parts.append(f"{label} {metadata.version(dist)}")
        except metadata.PackageNotFoundError:
            parts.append(label)
    return ", ".join(parts)


def about_html():
    owner = f" {AUTHOR}" if AUTHOR else ""
    return (
        f"<h2>{APP_NAME} v{VERSION}</h2>"
        f"<hr>"
        f"<p> Dependencies:</p>"
        f"<p>{tech_stack()}</p>"
        f"<p style='color: gray;'>{owner} Copyright © {copyright_years()}</p>"
    )
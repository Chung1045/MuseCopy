# Muse Copy

A desktop music copier utility built with Python and PyQt5 that scans your music folders, copies the audio files into a single output folder, renames them from their metadata, and optionally strips unwanted tags, intended to work with various digital media player. Your original files are never modified.

---

## Features

* **Folder scanning:** Add any number of input folders and choose, per folder, whether to include its subfolders or scan only the top level.
* **Metadata reading:** Reads tags with **TinyTag** from `.mp3`, `.m4a`, `.mp4`, `.wav`, `.flac`, `.aac`, `.ogg` and `.wma` files.
* **Rename schema:** Name the copies with a pattern such as `{title} - {artist}`. Available placeholders: `{title}`, `{artist}`, `{album}`, `{track}`, `{year}`.
* **Metadata stripping:** Optionally remove comments, embedded artwork or lyrics from the copies using **Mutagen**.

---

## Requirements

* Python 3.8 or newer
* [PyQt5](https://pypi.org/project/PyQt5/)
* [TinyTag](https://pypi.org/project/tinytag/)
* [Mutagen](https://pypi.org/project/mutagen/)

---

## Installation

```bash
git clone https://github.com/Chung1045/MuseCopy
cd MuseCopy

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Run the app with this command
python main.py
```

---

### Rename schema notes

* The default schema is `{title} - {artist}`, you can create your own schema however you like.
* If a file is missing any tag the schema uses, it keeps its original filename.
* The file extension is always preserved.

---

## Limitations

* Metadata stripping works on **MP3** (ID3) and **M4A/MP4** files only. Other formats are still copied and renamed, but their tags are left untouched.
* An output folder inside an input folder is skipped during scanning, so files are not copied into themselves.

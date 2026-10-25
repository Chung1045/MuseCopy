import shutil
import time
from pathlib import Path
from string import Formatter

from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp4 import MP4

from service.metadata_fetcher import fetch_metadata

AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.mp4', '.wav', '.flac', '.aac', '.ogg', '.wma'}
DEFAULT_SCHEMA = "{title} - {artist}"
SCHEMA_TAGS = [
    {
        "displayName": "Title",
        "fieldName": "title",
    },
    {
        "displayName": "Artist",
        "fieldName": "artist",
    },
    {
        "displayName": "Album",
        "fieldName": "album",
    },
    {
        "displayName": "Track",
        "fieldName": "track",
    },
    {
        "displayName": "Year",
        "fieldName": "year",
    },
    {
        "displayName": "Bit Depth",
        "fieldName": "bitdepth",
    },
    {
        "displayName": "Bitrate",
        "fieldName": "bitrate",
    },
    {
        "displayName": "Sample Rate",
        "fieldName": "samplerate",
    },
]

SCHEMA_FIELDS = [item["fieldName"] for item in SCHEMA_TAGS]

def sanitize_filename(name):
    """Removes or replaces characters that are illegal in file paths."""
    if not name:
        return "Unknown"
    for char in '<>:"/\\|?*':
        name = name.replace(char, '_')
    return name.strip()


def build_filename(tag, schema, suffix, fallback_name):
    schema = (schema or DEFAULT_SCHEMA).strip()
    values = {field: getattr(tag, field, None) for field in SCHEMA_FIELDS}

    try:
        used = [name for _, name, _, _ in Formatter().parse(schema) if name]
        if not used:
            return fallback_name

        format_data = {}
        for name in used:
            val = values.get(name)
            format_data[name] = sanitize_filename(str(val)) if val is not None else ""

        text = schema.format(**format_data)
    except (KeyError, IndexError, ValueError):
        return fallback_name

    return f"{sanitize_filename(text)}{suffix}"


def strip_metadata(file_path, fields_to_drop, log=print):
    """Removes specific metadata fields from the copied audio file."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    drop = {f.lower() for f in fields_to_drop}

    try:
        if suffix == '.mp3':
            try:
                audio = ID3(file_path)
            except ID3NoHeaderError:
                return
            if drop & {'comment', 'comments'}:
                audio.delall('COMM')
            if drop & {'artwork', 'cover', 'apic'}:
                audio.delall('APIC')
            if drop & {'lyrics', 'uslt'}:
                audio.delall('USLT')
            audio.save()

        elif suffix in ('.m4a', '.mp4'):
            audio = MP4(file_path)
            if drop & {'comment', 'comments'}:
                audio.pop('©cmt', None)
            if drop & {'artwork', 'cover'}:
                audio.pop('covr', None)
            if drop & {'lyrics'}:
                audio.pop('©lyr', None)
            audio.save()

        else:
            return  # other formats aren't handled

        log(f"  Stripped {sorted(drop)} from {path.name}")
    except Exception as e:
        log(f"  Could not strip metadata from {path.name}: {e}")


def muse_copy_rename(file_path, tag, output_folder, fields_to_drop=None,
                     schema=DEFAULT_SCHEMA, rename_enabled=True, log=print):
    """Copies an audio file, renames it if enabled, and optionally drops metadata fields."""
    src_path = Path(file_path)
    dest_dir = Path(output_folder)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Use custom schema if batch renaming is enabled; otherwise retain original filename
    if rename_enabled:
        new_name = build_filename(tag, schema, src_path.suffix, src_path.name)
    else:
        new_name = src_path.name

    dest_file_path = dest_dir / new_name
    counter = 1
    while dest_file_path.exists():
        dest_file_path = dest_dir / f"{Path(new_name).stem}_{counter}{src_path.suffix}"
        counter += 1

    shutil.copy2(src_path, dest_file_path)
    log(f"Copied: {src_path.name} -> {dest_file_path.name}")

    if fields_to_drop:
        strip_metadata(dest_file_path, fields_to_drop, log)


def muse_process_direct(folder_configs, target_copy_folder, fields_to_drop=None,
                        default_include_subdirs=True, schema=DEFAULT_SCHEMA,
                        rename_enabled=True, log=print, progress=None):
    start_time = time.perf_counter()

    if isinstance(folder_configs, dict):
        configs = {Path(p): flag for p, flag in folder_configs.items()}
    else:
        configs = {Path(p): default_include_subdirs for p in folder_configs}

    target = Path(target_copy_folder).resolve()

    files = []
    for folder, include_subdirs in configs.items():
        if not folder.is_dir():
            log(f"Skipping (not a folder): {folder}")
            continue
        generator = folder.rglob('*') if include_subdirs else folder.glob('*')
        for f in generator:
            if not (f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS):
                continue
            resolved = f.resolve()
            if target in resolved.parents:
                continue
            files.append(resolved)

    total = len(files)
    log(f"Found {total} audio file(s).")
    if progress:
        progress(0, total)

    copied = failed = 0
    for i, resolved in enumerate(files, 1):
        try:
            tag = fetch_metadata(str(resolved))
            muse_copy_rename(
                resolved, tag, target, fields_to_drop,
                schema=schema, rename_enabled=rename_enabled, log=log
            )
            copied += 1
        except Exception as e:
            failed += 1
            log(f"Error processing {resolved.name}: {e}")
        if progress:
            progress(i, total)

    elapsed = time.perf_counter() - start_time
    log(f"Finished in {elapsed:.2f} seconds.")

    return {"total": total, "copied": copied, "failed": failed, "elapsed": elapsed}
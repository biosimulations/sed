# This file contains utility functions to deal with parsing input archives for relevant info
import os
import zipfile


def _extract_pbif_from_zip(archive_path: str, output_dir: str) -> str:
    archive_shortname = os.path.basename(archive_path).split(".")[0]
    extraction_destination = os.path.join(output_dir, archive_shortname)
    os.makedirs(extraction_destination, exist_ok=True)
    target_pbif = None
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            current_file = archive.extract(name, extraction_destination)
            if (not name.endswith(".pbif") and not name.endswith(".json")) or "/__MACOSX/._" in current_file:
                continue
            target_pbif = current_file  # Note: This scheme does not support multiple pbif!
            # TODO: Allow for multi-pbif files? May require omex enforcment...
    if target_pbif is None:
        raise ValueError(f"Could not locate Process Bigraph Intermediate Format file within archive: {archive_path}")
    return target_pbif


def _extract_pbif_from_omex(archive_path: str, output_dir: str) -> str:
    # At the moment, we're not doing anything complicated...
    return _extract_pbif_from_zip(archive_path, output_dir)


def extract_archive_returning_pbif_path(archive_path: str, output_dir: str) -> str:
    if archive_path.endswith(".omex"):
        return _extract_pbif_from_omex(archive_path, output_dir)
    elif archive_path.endswith(".zip"):
        return _extract_pbif_from_zip(archive_path, output_dir)
    else:
        raise Exception(f"Unsupported archive: {archive_path}")

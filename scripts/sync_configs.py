# -*- coding: utf-8 -*-

"""Synchronize configurations between source and destination.

This script checks if the source files are newer than the destination
files, and if so, it generates a diff and prompts the user to approve
the update. If the user confirms, it copies the source files to the
destination.

Requirements:
    - Python 3.x

Usage:
    python sync_configs.py [-y | --yes]

Arguments:
    -y, --yes: Automatically approve updates without user confirmation.
"""

# Standard Library
import argparse
import difflib
import logging
import os
import shutil


# List of file pairs (source, destination)
FILE_PAIRS = [
    (
        ".github/copilot/commit-message-instructions.md",
        "configs/.github/copilot/commit-message-instructions.md",
    ),
    (
        ".github/copilot/pull-request-description-instructions.md",
        "configs/.github/copilot/pull-request-description-instructions.md",
    ),
    (
        ".github/workflows/pages.yaml",
        "configs/.github/workflows/pages.yaml",
    ),
    (
        ".cspell.yaml",
        "configs/.cspell.yaml",
    ),
    (
        ".editorconfig",
        "configs/.editorconfig",
    ),
    (
        ".gitignore",
        "configs/.gitignore",
    ),
    (
        ".prettierrc.yaml",
        "configs/.prettierrc.yaml",
    ),
    (
        "centinum.code-workspace",
        "configs/code.code-workspace",
    ),
]


def file_is_newer(src: str, dst: str) -> bool:
    """Check if the source file is newer than the destination file.

    Checks if the source file exists and is newer than the destination
    file. If the destination file does not exist, it is considered
    outdated.

    Args:
        src (str):
            Path to the source file.
        dst (str):
            Path to the destination file.

    Returns:
        bool:
            True if the source file is newer or the destination file
            does not exist.
    """
    if not os.path.exists(src):
        logging.warning("[SKIP] Source file does not exist: %s", src)
        return False

    if not os.path.exists(dst):
        return True

    return os.path.getmtime(src) > os.path.getmtime(dst)


def file_diff(src: str, dst: str) -> str:
    """Generate a unified diff between the source and destination files.

    Reads both files and generates a unified diff if they differ. If the
    destination file does not exist, it returns the contents of the
    source file as a string. If there is an error reading either file,
    an error message is logged and an empty string is returned.

    Args:
        src (str):
            Path to the source file.
        dst (str):
            Path to the destination file.

    Returns:
        str:
            A string containing the unified diff, or an empty string if
            the files are identical.
    """
    try:
        with open(src, "r", encoding="utf-8") as f1:
            src_lines = f1.readlines()
    except (OSError, IOError) as e:
        logging.error("[ERROR] Could not read source file %s: %s", src, e)
        return ""

    if not os.path.exists(dst):
        return "".join(src_lines)

    try:
        with open(dst, "r", encoding="utf-8") as f2:
            dst_lines = f2.readlines()
    except (OSError, IOError) as e:
        logging.error("[ERROR] Could not read destination file %s: %s", dst, e)
        return ""

    diff = difflib.unified_diff(src_lines, dst_lines, fromfile=dst, tofile=src)
    return "".join(diff)


def sync_files(auto_approve: bool = False) -> None:
    """Synchronize files from source to destination if updated.

    Checks each file pair to see if the source file is newer than the
    destination file. If it is, generates a diff and prompts the user to
    approve the update. If the user confirms, copies the source file to
    the destination.

    Args:
        auto_approve (bool):
            If True, automatically approves updates without user
            confirmation. Defaults to False.
    """
    updated_files = []

    for src, dst in FILE_PAIRS:
        if file_is_newer(src, dst):
            diff = file_diff(src, dst)

            if diff:
                logging.info("[DIFF] %s -> %s", src, dst)
                logging.info(diff)
                updated_files.append((src, dst))
            else:
                logging.info("[OK] Up to date: %s", dst)
        else:
            logging.info("[OK] Up to date: %s", dst)

    if not updated_files:
        logging.info("[RESULT] All files are up to date.")
        return

    if auto_approve:
        confirm = "yes"
    else:
        confirm = (
            input("[INPUT] Update destination files? (y/N to confirm): ")
            .strip()
            .lower()
        )

    if confirm in ("y", "yes"):
        for src, dst in updated_files:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            logging.info("[UPDATED] %s", dst)
    else:
        logging.info("[RESULT] Update cancelled.")


def main() -> None:
    """Main function to parse arguments and execute the sync process.

    Parses command line arguments to determine if the user wants to
    auto-confirm updates. Calls the sync_files function with the
    appropriate argument based on user input.
    """
    parser = argparse.ArgumentParser(
        description="Sync files from source to destination if updated."
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Auto-confirm updates without prompt.",
    )
    args = parser.parse_args()

    sync_files(auto_approve=args.yes)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s",
    )
    main()

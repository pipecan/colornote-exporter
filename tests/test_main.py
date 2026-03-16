import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import main  # noqa: E402


EXAMPLES_DIR = PROJECT_ROOT / "examples"
PASSWORDS = dict(
    line.split(":", 1)
    for line in (EXAMPLES_DIR / "passwords").read_text().splitlines()
    if line.strip()
)
FIRST_BACKUP = EXAMPLES_DIR / "1773619940425-MANUAL.backup"
SECOND_BACKUP = EXAMPLES_DIR / "1773619997356-MANUAL.backup"


def test_decode_backup_reads_expected_notes_from_first_example():
    records = main.decode_backup(FIRST_BACKUP, PASSWORDS[FIRST_BACKUP.name])

    assert len(records) == 5
    assert [record["title"] for record in records] == [
        "Shopping List",
        "ColorNote",
        "(3/15/2026)",
        "IMDB top 100",
        "syncable_settings",
    ]
    assert records[0]["uuid"] == "6131df56-4cba-4461-8114-e5cfb9aa21e3"


def test_decode_backup_reads_expected_notes_from_second_example():
    records = main.decode_backup(SECOND_BACKUP, PASSWORDS[SECOND_BACKUP.name])

    assert len(records) == 6
    assert records[-1]["title"] == "Untitled - Notepad"
    assert records[-1]["uuid"] == "9620902c-cc4d-4ead-8ff3-b2b18f5db1c8"


def test_main_exports_json_for_one_backup(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "-p", PASSWORDS[FIRST_BACKUP.name], str(FIRST_BACKUP)],
    )

    exit_code = main.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    records = json.loads(captured.out)
    assert len(records) == 5
    assert [record["title"] for record in records] == [
        "Shopping List",
        "ColorNote",
        "(3/15/2026)",
        "IMDB top 100",
        "syncable_settings",
    ]


def test_main_rejects_directory_input(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "-p", PASSWORDS[FIRST_BACKUP.name], str(EXAMPLES_DIR)],
    )

    exit_code = main.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert f"error: {EXAMPLES_DIR} is not a file" in captured.err
    assert captured.out == ""

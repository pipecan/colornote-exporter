import json
from pathlib import Path

import main

EXAMPLES_DIR = Path("examples")
PASSWORD = (EXAMPLES_DIR / "password").read_text()
EXAMPLE_BACKUP = EXAMPLES_DIR / "1773619940425-MANUAL.backup"


def test_decode_json():
    records = main.decode_backup(EXAMPLE_BACKUP, PASSWORD)

    assert len(records) == 5
    assert [record["title"] for record in records] == [
        "Shopping List",
        "ColorNote",
        "(3/15/2026)",
        "IMDB top 100",
        "syncable_settings",
    ]
    assert records[0]["uuid"] == "6131df56-4cba-4461-8114-e5cfb9aa21e3"


def test_main_outputs_json(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "-p", PASSWORD, str(EXAMPLE_BACKUP)],
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
        ["main.py", "-p", PASSWORD, str(EXAMPLES_DIR)],
    )

    exit_code = main.main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert f"error: {EXAMPLES_DIR} is not a file" in captured.err
    assert captured.out == ""

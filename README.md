# ColorNote Exporter

Decrypt ColorNote backups and print the decoded records as JSON.

Decryption logic is adapted from [fcoiffie/decode-ColorNote](https://github.com/fcoiffie/decode-ColorNote).

## Run with uv

1. Create/sync the environment:
```
uv sync
```

2. Run the decoder on a single backup file:
```
uv run python main.py <filename>
```

3. Optional: pass a backup password (default: `0000`):
```
uv run python main.py -p <password> <filename>
```

## Example

Example input:

```bash
uv run python main.py -p hunter2 examples/1773619940425-MANUAL.backup
```

Example output:

```json
[
  {
    "_id": 1,
    "title": "Shopping List",
    "note": "[ ] Flour\n[V] Eggs\n[ ] Milk\n[V] Sugar\n",
    "uuid": "6131df56-4cba-4461-8114-e5cfb9aa21e3"
  },
  {
    "_id": 3,
    "title": "ColorNote",
    "note": "Makes it very difficult to export your data.",
    "uuid": "ec652792-3e31-4712-a30f-36edef2e6b1a"
  }
]
```

For the full output shape, see the generated JSON files in [`examples/`](./examples/).

## How It Works

The backup password is encoded as UTF-8 and combined with the fixed salt `ColorNote Fixed Salt` to derive the AES-128-CBC key and IV with MD5:

- `key = MD5(password || salt)`
- `iv = MD5(key || password || salt)`

The script skips the first 28 bytes of the backup file, decrypts the remaining bytes with AES-CBC, then skips the first 16 bytes of the decrypted payload. From there it reads a stream of records where each record starts with a 4-byte big-endian length followed by a UTF-8 JSON object. Parsing stops when the next 4 bytes are all the same value, which acts as the padding terminator.

```text
backup file
  |
  +-- [0x00..0x1b] 28-byte file header (ignored)
  |
  +-- [0x1c..end] encrypted payload
           |
           +-- AES-128-CBC decrypt
                 key = MD5(password || "ColorNote Fixed Salt")
                 iv  = MD5(key || password || "ColorNote Fixed Salt")
           |
           v
     decrypted payload
       |
       +-- [0x00..0x0f] 16-byte prelude (ignored)
       |
       +-- [0x10..end] record stream
                |
                +-- 4-byte big-endian length
                +-- N bytes of UTF-8 JSON
                +-- repeat until next 4 bytes are NN NN NN NN
```

## Roadmap

- [ ] Filters (--archived, --todos, --text, --color, --before, --after, --type)
- [ ] Formats (--markdown, --html, --jsonl, --txt)
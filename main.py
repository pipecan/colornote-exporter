import argparse
import json
import struct
import sys
from hashlib import md5
from pathlib import Path

from Crypto.Cipher import AES


DEFAULT_PASSWORD = "0000"
FIXED_SALT = b"ColorNote Fixed Salt"


def derive_key_iv(password_text: str) -> tuple[bytes, bytes]:
    password_bytes = password_text.encode("utf-8")
    key = md5(password_bytes + FIXED_SALT).digest()
    iv = md5(key + password_bytes + FIXED_SALT).digest()
    return (key, iv)


def decrypt_backup_bytes(file_bytes: bytes, password_text: str) -> bytes:
    if len(file_bytes) < 28:
        raise ValueError("backup is too short to contain the encrypted payload")

    key, iv = derive_key_iv(password_text)
    encrypted_payload = file_bytes[28:]

    if len(encrypted_payload) == 0 or len(encrypted_payload) % AES.block_size != 0:
        raise ValueError("encrypted payload length is invalid for AES-CBC")

    return AES.new(key, AES.MODE_CBC, iv).decrypt(encrypted_payload)


def parse_records(payload: bytes) -> list[dict]:
    if len(payload) < 16:
        raise ValueError("decrypted payload is too short to contain records")

    records: list[dict] = []
    index = 0x10

    while index + 4 <= len(payload):
        length_prefix = payload[index : index + 4]
        if len(length_prefix) < 4:
            break

        if length_prefix[0] == length_prefix[1] == length_prefix[2] == length_prefix[3]:
            break

        (chunk_length,) = struct.unpack(">L", length_prefix)
        chunk_start = index + 4
        chunk_end = chunk_start + chunk_length

        if chunk_end > len(payload):
            raise ValueError(
                "record length exceeds decrypted payload size (double check the password)"
            )

        chunk = payload[chunk_start:chunk_end]
        try:
            records.append(json.loads(chunk.decode("utf-8")))
        except UnicodeDecodeError as exc:
            raise ValueError("record is not valid UTF-8") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("record is not valid JSON") from exc

        index = chunk_end

    return records


def decode_backup(path: Path, password_text: str) -> list[dict]:
    return parse_records(decrypt_backup_bytes(path.read_bytes(), password_text))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decrypt ColorNote backup notes and print the decoded records as JSON."
    )
    parser.add_argument("path", type=Path, help="backup file to decode")
    parser.add_argument(
        "-p",
        "--password",
        default=DEFAULT_PASSWORD,
        help=f"backup password (default: {DEFAULT_PASSWORD})",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        if not args.path.exists():
            raise FileNotFoundError(f"{args.path} does not exist")
        if not args.path.is_file():
            raise ValueError(f"{args.path} is not a file")

        records = decode_backup(args.path, args.password)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    json.dump(records, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

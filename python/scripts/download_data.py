#!/usr/bin/env python3
import argparse
import json
import ssl
import sys
import urllib.request
import zipfile
from pathlib import Path


ENWIK9_URL = "https://mattmahoney.net/dc/enwik9.zip"
REDPAJAMA_C4_URLS_URL = "https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T/resolve/main/urls/c4.txt"
EXPECTED_EXTRACTED_BYTES = 1_000_000_000
DEFAULT_TARGET_BYTES = 1_000_000_000


def download(url: str, dest: Path, insecure: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    resume_at = tmp.stat().st_size if tmp.exists() else 0
    headers = {"User-Agent": "mini-attention-llm/1.0"}
    if resume_at:
        headers["Range"] = f"bytes={resume_at}-"
    request = urllib.request.Request(url, headers=headers)
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, context=context) as response:
        if resume_at and response.status != 206:
            tmp.unlink()
            resume_at = 0
        total_header = response.headers.get("Content-Length")
        total = int(total_header) + resume_at if total_header else None
        mode = "ab" if resume_at else "wb"
        downloaded = resume_at
        with tmp.open(mode) as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\rdownloaded {downloaded / 1024 / 1024:.1f} MiB / {total / 1024 / 1024:.1f} MiB ({pct:.1f}%)", end="")
                else:
                    print(f"\rdownloaded {downloaded / 1024 / 1024:.1f} MiB", end="")
                sys.stdout.flush()
    print()
    tmp.replace(dest)


def urlopen(url: str, insecure: bool = False):
    request = urllib.request.Request(url, headers={"User-Agent": "mini-attention-llm/1.0"})
    context = ssl._create_unverified_context() if insecure else None
    return urllib.request.urlopen(request, context=context)


def read_url_list(urls_url: str, insecure: bool = False) -> list[str]:
    with urlopen(urls_url, insecure=insecure) as response:
        body = response.read().decode("utf-8")
    return [line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")]


def write_jsonl_text_corpus(
    urls: list[str],
    target: Path,
    target_bytes: int = DEFAULT_TARGET_BYTES,
    insecure: bool = False,
) -> int:
    if target.exists():
        size = target.stat().st_size
        if size >= target_bytes:
            print(f"raw text already exists: {target} ({size:,} bytes)")
            return size
        raise RuntimeError(f"partial raw text exists at {target}; remove it or pass --force")

    target.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with target.open("wb") as output:
        for url in urls:
            print(f"streaming {url}")
            with urlopen(url, insecure=insecure) as response:
                for raw_line in response:
                    if written >= target_bytes:
                        break
                    try:
                        record = json.loads(raw_line)
                    except json.JSONDecodeError:
                        continue
                    text = record.get("text")
                    if not isinstance(text, str) or not text:
                        continue
                    payload = (text.strip() + "\n").encode("utf-8")
                    remaining = target_bytes - written
                    output.write(payload[:remaining])
                    written += min(len(payload), remaining)
                    if written % (16 * 1024 * 1024) < len(payload):
                        print(f"\rwrote {written / 1024 / 1024:.1f} MiB / {target_bytes / 1024 / 1024:.1f} MiB", end="")
                        sys.stdout.flush()
            if written >= target_bytes:
                break
    print()
    if written < target_bytes:
        raise RuntimeError(f"only wrote {written:,} bytes, expected {target_bytes:,}")
    print(f"wrote {target} ({written:,} bytes)")
    return written


def extract(zip_path: Path, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / "enwik9"
    if target.exists() and target.stat().st_size == EXPECTED_EXTRACTED_BYTES:
        print(f"raw text already exists: {target}")
        return target
    with zipfile.ZipFile(zip_path) as archive:
        member = archive.getinfo("enwik9")
        archive.extract(member, raw_dir)
    size = target.stat().st_size
    if size != EXPECTED_EXTRACTED_BYTES:
        raise RuntimeError(f"unexpected extracted size for {target}: {size}")
    print(f"extracted {target} ({size:,} bytes)")
    return target


def download_enwik9(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    raw_dir = Path(args.raw_dir)
    if archive.exists():
        if zipfile.is_zipfile(archive):
            print(f"archive already exists: {archive}")
        else:
            partial = archive.with_suffix(archive.suffix + ".part")
            archive.replace(partial)
            print(f"moved incomplete archive to {partial}")
            download(args.url, archive, insecure=args.insecure)
    else:
        download(args.url, archive, insecure=args.insecure)
    extract(archive, raw_dir)


def download_redpajama_c4(args: argparse.Namespace) -> None:
    target = Path(args.raw_dir) / "redpajama_c4_1gb.txt"
    if args.force and target.exists():
        target.unlink()
    urls = read_url_list(args.urls_url, insecure=args.insecure)
    write_jsonl_text_corpus(urls, target, target_bytes=args.target_bytes, insecure=args.insecure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download about 1 GB of public training text.")
    parser.add_argument("--dataset", choices=["redpajama-c4", "enwik9"], default="redpajama-c4")
    parser.add_argument("--url", default=ENWIK9_URL, help="enwik9 archive URL")
    parser.add_argument("--urls-url", default=REDPAJAMA_C4_URLS_URL, help="RedPajama C4 shard URL list")
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--archive", default="data/raw/enwik9.zip")
    parser.add_argument("--target-bytes", type=int, default=DEFAULT_TARGET_BYTES)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification for corporate proxy environments.")
    args = parser.parse_args()

    if args.dataset == "redpajama-c4":
        download_redpajama_c4(args)
    else:
        download_enwik9(args)


if __name__ == "__main__":
    main()

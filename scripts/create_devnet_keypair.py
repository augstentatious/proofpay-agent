#!/usr/bin/env python3
"""Create a Solana CLI-format devnet-only payer keypair."""

import argparse
import json
import os
from pathlib import Path

from solders.keypair import Keypair


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    path = args.out.resolve()
    if path.exists():
        raise SystemExit(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    keypair = Keypair()
    path.write_text(json.dumps(list(bytes(keypair))) + "\n")
    os.chmod(path, 0o600)
    print(keypair.pubkey())


if __name__ == "__main__":
    main()

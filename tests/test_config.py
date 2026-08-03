from decimal import Decimal
from pathlib import Path

from conftest import RECIPIENT, USDC_MINT
from proofpay.config import load_runtime


def write_config(path: Path, root: Path) -> None:
    path.write_text(
        f'''[proofpay]
artifact_root = "{root / 'artifacts'}"
encrypted_root = "{root / 'encrypted'}"
release_root = "{root / 'released'}"
state_db = "{root / 'proofpay.db'}"
recipient = "{RECIPIENT}"
token_mint = "{USDC_MINT}"
token_decimals = 6
max_amount = "250.00"
rpc_url = "https://api.mainnet-beta.solana.com"
'''
    )


def test_config_loads_locked_operator_policy(tmp_path: Path):
    config_path = tmp_path / "proofpay.toml"
    write_config(config_path, tmp_path)
    service, rpc = load_runtime(config_path)

    assert service.config.recipient == RECIPIENT
    assert service.config.token_mint == USDC_MINT
    assert service.config.max_amount == Decimal("250.00")
    assert rpc.url == "https://api.mainnet-beta.solana.com"

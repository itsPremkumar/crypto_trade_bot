import logging
from eth_account import Account
from eth_account.signers.local import LocalAccount
from bot.config import Config

logger = logging.getLogger(__name__)

class WalletManager:
    """Manages the non-custodial local wallet using a private key."""
    
    def __init__(self):
        self.account: LocalAccount = None
        self._load_wallet()

    def _load_wallet(self):
        """Loads and decrypts the wallet from the private key in config."""
        try:
            self.account = Account.from_key(Config.PRIVATE_KEY)
            logger.info("Wallet successfully loaded. Never log the private key.")
        except Exception as e:
            logger.warning("Invalid PRIVATE_KEY provided. Generating a temporary test wallet...")
            self.account = Account.create()
            logger.warning(f"Test Wallet Address: {self.account.address}")
            logger.warning("Do NOT send real funds to this test address. Update your .env to trade.")

    def get_address(self) -> str:
        """Returns the public address of the bot."""
        if not self.account:
            raise ValueError("Wallet not loaded")
        return self.account.address
    
    def sign_transaction(self, tx_dict: dict):
        """Signs a dictionary transaction meant to be sent via web3."""
        if not self.account:
            raise ValueError("Wallet not loaded")
        signed_tx = self.account.sign_transaction(tx_dict)
        return signed_tx

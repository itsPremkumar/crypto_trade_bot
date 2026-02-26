import logging
from web3 import Web3
from bot.dex.base_dex import BaseDex

logger = logging.getLogger(__name__)

# PCS V3 router shares structural similarity with Uni V3
PCS_V3_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                ],
                "internalType": "struct IV3SwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

class PancakeSwapV3(BaseDex):
    
    TOKEN_REGISTRY = {
        'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', # Binance-Peg USDC
        'BNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'  # WBNB
    }

    def __init__(self, w3: Web3):
        router = "0x1b81D678ffb9C0263b24A97847620C99d213e1Cb" # PCS V3 Router
        super().__init__(w3, router)
        self.contract = self.w3.eth.contract(address=self.router_address, abi=PCS_V3_ROUTER_ABI)

    def get_token_address(self, token_symbol: str) -> str:
        symbol = token_symbol.upper()
        if symbol not in self.TOKEN_REGISTRY:
            raise ValueError(f"Token {symbol} not supported on BSC")
        return self.w3.to_checksum_address(self.TOKEN_REGISTRY[symbol])

    async def build_swap_transaction(self, wallet_address: str, token_in: str, token_out: str, amount_in_wei: int, min_amount_out_wei: int, deadline: int) -> dict:
        token_in_addr = self.get_token_address(token_in)
        token_out_addr = self.get_token_address(token_out)
        
        fee = 500 # 0.05%
        
        params = (
            token_in_addr,
            token_out_addr,
            fee,
            self.w3.to_checksum_address(wallet_address),
            deadline,
            amount_in_wei,
            min_amount_out_wei,
            0
        )
        
        tx = self.contract.functions.exactInputSingle(params).build_transaction({
            'from': wallet_address,
            'nonce': self.w3.eth.get_transaction_count(wallet_address)
        })
        return tx

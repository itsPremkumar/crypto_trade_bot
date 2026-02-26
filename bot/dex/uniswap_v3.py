import logging
from web3 import Web3
from bot.dex.base_dex import BaseDex

logger = logging.getLogger(__name__)

# Minimal interface for exactInputSingle
UNISWAP_V3_ROUTER_ABI = [
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
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
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

class UniswapV3(BaseDex):
    
    # Using specific token addresses based on chain. In production, a robust token registry is needed.
    TOKEN_REGISTRY = {
        'polygon': {
            'USDC': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359', # USDCNative
            'MATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270' # WMATIC
        },
        'base': {
            'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'ETH': '0x4200000000000000000000000000000000000006' # WETH
        }
    }

    def __init__(self, w3: Web3, chain: str):
        # Quickswap V3 on Polygon or BaseSwap V3 on Base / Uniswap universal router
        router = "0xE592427A0AEce92De3Edee1F18E0157C05861564" # Uniswap V3 SwapRouter02 typically
        super().__init__(w3, router)
        self.chain = chain.lower()
        self.contract = self.w3.eth.contract(address=self.router_address, abi=UNISWAP_V3_ROUTER_ABI)

    def get_token_address(self, token_symbol: str) -> str:
        symbol = token_symbol.upper()
        tokens = self.TOKEN_REGISTRY.get(self.chain, {})
        if symbol not in tokens:
            raise ValueError(f"Token {symbol} not supported on {self.chain}")
        return self.w3.to_checksum_address(tokens[symbol])

    async def build_swap_transaction(self, wallet_address: str, token_in: str, token_out: str, amount_in_wei: int, min_amount_out_wei: int, deadline: int) -> dict:
        token_in_addr = self.get_token_address(token_in)
        token_out_addr = self.get_token_address(token_out)
        
        # Defaulting fee tier to 0.05% (500) or 0.3% (3000) depending on pool
        # In a real impl, we'd query Quoter to find the best pool fee tier. Using 500 as standard for stables/majors.
        fee = 500 

        params = (
            token_in_addr,
            token_out_addr,
            fee,
            self.w3.to_checksum_address(wallet_address),
            deadline,
            amount_in_wei,
            min_amount_out_wei,
            0 # sqrtPriceLimitX96
        )
        
        tx = self.contract.functions.exactInputSingle(params).build_transaction({
            'from': wallet_address,
            'nonce': self.w3.eth.get_transaction_count(wallet_address)
            # Gas parameters are injected by execution layer
        })
        return tx

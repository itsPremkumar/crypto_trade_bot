from web3 import Web3
import logging

logger = logging.getLogger(__name__)

class GasOptimizer:
    """Computes and injects correct gas parameters based on chain architecture (EIP-1559 vs Legacy)."""

    def __init__(self, w3_dict: dict):
        self.w3_dict = w3_dict

    def build_gas_params(self, chain: str) -> dict:
        """Fetch base fee and build gas cost dictionary."""
        w3 = self.w3_dict.get(chain)
        if not w3:
            raise ValueError(f"Web3 connection not found for {chain}")

        params = {}
        
        try:
            if chain in ['polygon', 'base']:
                # EIP-1559 support
                latest_block = w3.eth.get_block('latest')
                base_fee = latest_block.get('baseFeePerGas', 0)
                
                # Priority fee defaults: Base is cheap (~0.1-1 gwei), Polygon varies (30-50 gwei usually)
                max_priority = w3.to_wei(2, 'gwei') if chain == 'polygon' else w3.to_wei(0.1, 'gwei')
                
                max_fee = int(base_fee * 1.5) + max_priority
                
                params['maxFeePerGas'] = max_fee
                params['maxPriorityFeePerGas'] = max_priority
                params['type'] = 2
                
            elif chain == 'bsc':
                # Legacy gas
                gas_price = w3.eth.gas_price
                params['gasPrice'] = int(gas_price * 1.1) # Add 10% bumper
                params['type'] = 0
                
        except Exception as e:
            logger.error(f"Error building gas params on {chain}: {e}")
            # Fallback to extremely safe defaults
            params['gasPrice'] = w3.to_wei(50, 'gwei') if chain != 'base' else w3.to_wei(0.5, 'gwei')
            
        return params

    def get_estimated_gas_cost_usd(self, chain: str, gas_limit: int = 250000, native_token_price: float = 0.0) -> float:
        """Returns the estimated USD cost of a transaction for risk limits."""
        # Simple placeholder logic, assumes native_token_price is passed correctly from market analyzer
        w3 = self.w3_dict.get(chain)
        if not w3:
            return 0.0
            
        try:
            if chain in ['polygon', 'base']:
                base_fee = w3.eth.get_block('latest').get('baseFeePerGas', 0)
                cost_wei = (base_fee * 1.2) * gas_limit
            else:
                cost_wei = w3.eth.gas_price * gas_limit
                
            cost_native = w3.from_wei(cost_wei, 'ether')
            return float(cost_native) * native_token_price
        except Exception:
            return 999.9 # Unsafe fallback to prevent trading

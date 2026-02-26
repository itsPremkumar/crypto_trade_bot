import logging

logger = logging.getLogger(__name__)

class SlippageGuard:
    """Computes exact amountOutMinimum based on slippage tolerance config."""

    @staticmethod
    def calculate_min_out(expected_out_wei: int, slippage_tolerance: float) -> int:
        """
        Calculates the minimum acceptable output amount given the slippage tolerance.
        slippage_tolerance is a float where 0.015 = 1.5%
        """
        if expected_out_wei <= 0:
            return 0
            
        if slippage_tolerance < 0 or slippage_tolerance > 0.5:
            logger.warning(f"Unusual slippage tolerance specified: {slippage_tolerance}. Capping.")
            slippage_tolerance = min(max(slippage_tolerance, 0.001), 0.1) # Bound between 0.1% and 10%
            
        multiplier = 1.0 - slippage_tolerance
        min_out = int(expected_out_wei * multiplier)
        
        return min_out

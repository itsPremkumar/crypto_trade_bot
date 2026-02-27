import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import base58
from solders.keypair import Keypair

async def main():
    rpc_url = "https://api.devnet.solana.com"
    # Using the public address for a quick check
    address_str = "EtDQFNZzVFrTWCpDQ3gjJj8pt5fWUWFCauvf5Rho8Uhg"
    
    async with AsyncClient(rpc_url) as client:
        # Check by address
        pubkey = Pubkey.from_string(address_str)
        res = await client.get_balance(pubkey)
        print(f"Address: {address_str}")
        print(f"Balance: {res.value / 10**9} SOL")
        
        # Also check the private key in .env to see what address it derives
        priv_key = "5ATUQdt9gsh3uKZBru46H45ijSWPmfwVYdeL6sX3nhDd4S8SUpVLosfm8ZBeMPMP2UQqPB1dPmXYpDmCGUwXotD8"
        try:
            key_bytes = base58.b58decode(priv_key)
            kp = Keypair.from_bytes(key_bytes)
            print(f"Derived Address from Private Key: {kp.pubkey()}")
        except Exception as e:
            print(f"Failed to derive key: {e}")

if __name__ == "__main__":
    asyncio.run(main())

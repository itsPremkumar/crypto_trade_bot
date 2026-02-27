# ⚠️ PROTOTYPE: Decentralized Crypto Trading Bot ($10 Capital Focus)

> [!WARNING]
> **PROTOTYPE SOFTWARE - REQUIRES REAL FUNDS TO TEST NATIVE EXECUTION**
> This repository contains an experimental, fully decentralized trading bot. Real Decentralized Exchanges (DEXs like Jupiter or 1inch) do not execute Automated Market Maker (AMM) math on Testnets or Devnets. Therefore, **to test the complete end-to-end execution flow where token balances physically change, you MUST deploy this bot on Live Mainnet using real cryptocurrency.**
> 
> *Do not run this codebase unless you are prepared to connect a real wallet with at least $10 in real funds.*

A completely decentralized, low-capital ($10 USD equivalent) crypto trading bot operating autonomously on Solana, Polygon, BSC, and Base. Powered entirely by the Anthropic Claude API (with Ollama fallback) for decision-making and controlled securely via a Telegram interface.

## Core Features
- **Low Capital Focus**: Designed strictly to grow $10 capital while preserving funds.
- **Multi-LLM Engine**: Support for **Anthropic Claude** (Cloud) and **Ollama** (Local/Self-hosted) for all decisions.
- **Strict Risk Checks**: Hardcoded risk guardrails preventing severe losses and slippage.
- **Telegram Control Center**: 100% manageable through a comprehensive Telegram bot.
- **Non-Custodial**: Operates securely using the fast `eth_account` keystore locally.

## Supported Chains (Mainnet Only)
- **Solana (Primary - Jupiter Aggregator)**
- Polygon (Chain ID 137)
- BNB Chain (Chain ID 56)
- Base (Chain ID 8453)

## Quick Start (Live Mainnet Testing)
> **Crucial Requirement**: Because this prototype uses real, decentralized Liquidity Pools (Jupiter etc), it cannot simulate trades without native tokens. Before running the bot, your connected wallet keys must contain real native gas (e.g. SOL) and real base currency (e.g. USDC).

1. Clone the repository.
2. `cp .env.example .env` and carefully fill in your `ANTHROPIC_API_KEY` and `TELEGRAM_BOT_TOKEN`.
3. Set your `SOLANA_PRIVATE_KEY` with a wallet that holds your **$10 live capital ($2 SOL, $8 USDC)** on Mainnet.
4. Set a secure `TELEGRAM_PAIRING_CODE` in your `.env`.
5. Ensure `TRADING_MODE=live` is set in your `.env`.
6. Build and run using Docker Compose:
   ```bash
   docker compose up -d --build
   ```
   **OR** run manually:
   ```bash
   python -m bot.main
   ```
7. Open your bot in Telegram and send: `/pair <your_pairing_code>`.
8. You are now authorized! The engine will actively scan and attempt to execute real swaps on Mainnet with your $10.

## Contributing

We love contributions! Whether it's reporting a bug, suggesting an enhancement, or submitting a pull request, all contributions are welcome.

- **How to contribute?** Check out our [CONTRIBUTING.md](file:///c:/one/crypto_trade_bot/CONTRIBUTING.md) for guidelines.
- **Code of Conduct**: Please read our [CODE_OF_CONDUCT.md](file:///c:/one/crypto_trade_bot/CODE_OF_CONDUCT.md) before participating.

## License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/one/crypto_trade_bot/LICENSE) file for details.

## Disclaimer
Trading cryptocurrencies carries significant risk. This is experimental software. Never fund the bot with capital you are not prepared to lose.

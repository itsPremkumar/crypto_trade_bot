# Decentralized Crypto Trading Bot ($10 Capital Focus)

A completely decentralized, low-capital ($10 USD equivalent) crypto trading bot operating autonomously on Polygon, BSC, and Base. Powered entirely by the Anthropic Claude API for decision-making and controlled safely via a complete Telegram interface.

## Core Features
- **Low Capital Focus**: Designed strictly to grow $10 capital while preserving funds.
- **Multi-LLM Engine**: Support for **Anthropic Claude** (Cloud) and **Ollama** (Local/Self-hosted) for all decisions.
- **Strict Risk Checks**: Hardcoded risk guardrails preventing severe losses and slippage.
- **Telegram Control Center**: 100% manageable through a comprehensive Telegram bot.
- **Non-Custodial**: Operates securely using the fast `eth_account` keystore locally.

## Supported Chains
- Polygon (Chain ID 137)
- BNB Chain (Chain ID 56)
- Base (Chain ID 8453)

## Quick Start
1. Clone the repository.
2. `cp .env.example .env` and carefully fill in your `ANTHROPIC_API_KEY` and `TELEGRAM_BOT_TOKEN`.
3. Set a secure `TELEGRAM_PAIRING_CODE` in your `.env`.
4. Build and run using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
   **OR** run manually:
   ```bash
   python -m bot.main
   ```
5. Open your bot in Telegram and send: `/pair <your_pairing_code>`.
6. You are nowauthorized! You can use the menu or simply **chat with Claude** for market insights.

## Contributing

We love contributions! Whether it's reporting a bug, suggesting an enhancement, or submitting a pull request, all contributions are welcome.

- **How to contribute?** Check out our [CONTRIBUTING.md](file:///c:/one/crypto_trade_bot/CONTRIBUTING.md) for guidelines.
- **Code of Conduct**: Please read our [CODE_OF_CONDUCT.md](file:///c:/one/crypto_trade_bot/CODE_OF_CONDUCT.md) before participating.

## License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/one/crypto_trade_bot/LICENSE) file for details.

## Disclaimer
Trading cryptocurrencies carries significant risk. This is experimental software. Never fund the bot with capital you are not prepared to lose.

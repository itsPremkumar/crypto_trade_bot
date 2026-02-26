# Decentralized Crypto Trading Bot ($10 Capital Focus)

A completely decentralized, low-capital ($10 USD equivalent) crypto trading bot operating autonomously on Polygon, BSC, and Base. Powered entirely by the Anthropic Claude API for decision-making and controlled safely via a complete Telegram interface.

## Core Features
- **Low Capital Focus**: Designed strictly to grow $10 capital while preserving funds.
- **LLM Decision Engine**: Every BUY/SELL decision is analyzed and justified by Claude.
- **Strict Risk Checks**: Hardcoded risk guardrails preventing severe losses and slippage.
- **Telegram Control Center**: 100% manageable through a comprehensive Telegram bot.
- **Non-Custodial**: Operates securely using the fast `eth_account` keystore locally.

## Supported Chains
- Polygon (Chain ID 137)
- BNB Chain (Chain ID 56)
- Base (Chain ID 8453)

## Quick Start
1. Clone the repository.
2. `cp .env.example .env` and carefully fill in the required API keys and RPC endpoints.
3. Build and run using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
4. Access the bot safely via your Telegram app using `/start`.

## Contributing

We love contributions! Whether it's reporting a bug, suggesting an enhancement, or submitting a pull request, all contributions are welcome.

- **How to contribute?** Check out our [CONTRIBUTING.md](file:///c:/one/crypto_trade_bot/CONTRIBUTING.md) for guidelines.
- **Code of Conduct**: Please read our [CODE_OF_CONDUCT.md](file:///c:/one/crypto_trade_bot/CODE_OF_CONDUCT.md) before participating.

## License

This project is licensed under the MIT License - see the [LICENSE](file:///c:/one/crypto_trade_bot/LICENSE) file for details.

## Disclaimer
Trading cryptocurrencies carries significant risk. This is experimental software. Never fund the bot with capital you are not prepared to lose.

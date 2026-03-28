# Binance Futures Testnet Trading Bot (Python CLI)

A small Python CLI app that places **MARKET** and **LIMIT** orders on **Binance Futures Testnet (USDT-M)** with:

- structured project layout
- reusable API client layer
- CLI layer with validation
- file logging
- error handling for validation, API errors, and network failures

## Project Structure

```text
binance_trading_bot/
  bot/
    __init__.py
    client.py
    orders.py
    validators.py
    logging_config.py
  logs/
  cli.py
  .env.example
  README.md
  requirements.txt
```

## Features

- Place **BUY** and **SELL** orders
- Supports **MARKET** and **LIMIT**
- CLI input validation
- Logs API requests, API responses, and errors to `logs/trading_bot.log`
- Clean separation between CLI and Binance client logic

## Setup

### 1) Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Add your Binance Futures Testnet credentials

Copy `.env.example` to `.env` and fill in your values:

```bash
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_BASE_URL=https://testnet.binancefuture.com
```

## How to Run

### MARKET order example

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 1
```

### LIMIT order example

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 1 --price 70000
```

## Example Output

The CLI prints:

- order request summary
- response details including `orderId`, `status`, `executedQty`, and `avgPrice` when available
- clear success or failure message

## Assumptions

1. This implementation targets **USDT-M Futures Testnet**.
2. Symbols are expected in a USDT-M format such as `BTCUSDT`.
3. For `LIMIT` orders, `timeInForce=GTC` is applied.
4. `newOrderRespType=RESULT` is sent to get richer order responses.
5. Logging is stored in `logs/trading_bot.log`.
6. The hiring prompt specifies `https://testnet.binancefuture.com` as the testnet base URL, so that is the default in this project.
7. Binance documentation for USDⓈ-M futures currently shows a different testnet REST base URL in some official pages, so keeping the base URL configurable via `.env` and `--base-url` is safer.

## Validation Rules

- `symbol` must be non-empty, alphanumeric, and end with `USDT`
- `side` must be `BUY` or `SELL`
- `order-type` must be `MARKET` or `LIMIT`
- `quantity` must be a positive number
- `price` is required for `LIMIT` and must be positive

## Logging

All requests, responses, and errors are written to:

```text
logs/trading_bot.log
```

## Notes for Submission

The included source code is ready to run. To generate the required deliverable logs:

1. run one MARKET order
2. run one LIMIT order
3. submit the resulting files from `logs/`

## Binance API Notes

Binance USDⓈ-M futures order creation uses:

- `POST /fapi/v1/order` for new orders
- signed requests with API key header and HMAC SHA256 signature are required for trade endpoints

## Possible Improvements

- add symbol precision / lot size validation using `exchangeInfo`
- add a third order type such as `STOP`
- add richer CLI prompts using `Typer`
- add unit tests

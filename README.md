# Fidge Testnet Scripts 🚀

This collection of Python scripts empowers you to interact seamlessly with the Fidge Testnet, a blockchain test network for decentralized applications. The core script, `main.py`, offers automation and multi-account support for core testnet activities.

🔗 Register: [Fidge Testnet](https://www.fidge.app/join?ref=BIJ5L12Y)

## ✨ Features Overview

### General Features

- **Multi-Account Support**: Reads token from `accounts.txt` to perform actions across multiple accounts.
- **Colorful CLI**: Uses `colorama` for visually appealing output with colored text and borders.
- **Asynchronous Execution**: Built with `asyncio` for efficient blockchain interactions.
- **Error Handling**: Comprehensive error catching for blockchain transactions and RPC issues.
- **Bilingual Support**: Supports both English and Vietnamese output based on user selection.

### Included Scripts

✨ Register with Twitter OAuth

- ✅ Multi-Threading: Supports running multiple accounts simultaneously (CONFIG['THREADS']).
- ✅ Auto Spin & Sync: Automatically simulates spinner activity to earn points and energy naturally.
- ✅ Smart Convert: Automatically converts Points → Gems as soon as the set threshold is reached.
- ✅ Auto Wheel: Automatically performs lucky wheel spins when enough Gems are available.
- ✅ Auto Redeem: Automatically redeem code → Gems .
- ✅ Ad-Refill System: Simulates ad watching to refill Energy when empty, including a smart cooldown mechanism.
- ✅ Proxy Support: Supports HTTP/SOCKS proxies to avoid IP bans and protect your accounts.
- ✅ Bilingual UI: Professional command-line interface supporting both English and Vietnamese.

## 🛠️ Prerequisites

Before running the scripts, ensure you have the following installed:

- Python 3.8+
- `pip` (Python package manager)
- **Dependencies**: Install via `pip install -r requirements.txt` (ensure `web3.py`, `colorama`, `asyncio`, `eth-account`, `aiohttp_socks` and `inquirer` are included).
- **accounts.txt**: Add email and password (one per line) for wallet automation.
- **proxies.txt** (optional): Add proxy addresses for network requests, if needed.

## 📦 Installation

1. **Clone this repository:**
   ```sh
   git clone https://github.com/thog9/Fidge-testnet.git
   cd Fidge-testnet
   ```
2. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Prepare Input Files:**
   - Open the `accounts.txt`: Add email and password (one per line) in the root directory.
   ```sh
   nano accounts.txt 
   ```
   - Create `proxies.txt` for specific operations:
   ```sh
   nano proxies.txt
   ```
4. **Run:**
   ```sh
   python main.py
   ```
   - Choose a language (Vietnamese/English).
  
## 📨 Contact

Connect with us for support or updates:

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [CHANNEL](https://t.me/thogairdrops)
- **Group**: [GROUP CHAT](https://t.me/thogchats)
- **X**: [Thog](https://x.com/thog099) 

----

## ☕ Support Us

Love these scripts? Fuel our work with a coffee!

🔗 BUYMECAFE: [BUY ME CAFE](https://buymecafe.vercel.app/)

🔗 WEBSITE: [BUY SCRIPS](https://thogtoolhub.com/)

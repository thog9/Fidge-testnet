import os
import sys
import asyncio
import aiohttp
import random
from typing import List, Optional, Tuple
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style

init(autoreset=True)

BORDER_WIDTH = 80
BASE_URL     = "https://backend-production-app.up.railway.app"

CONFIG = {
    "THREADS":        5,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY":    5,
    "TIMEOUT":        60,
    "DELAY_BETWEEN":  2,
}

HEADERS_BASE = {
    "User-Agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept":             "application/json",
    "Accept-Language":    "vi-VN,vi;q=0.9,en-US;q=0.6,en;q=0.5",
    "Accept-Encoding":    "gzip, deflate, br",
    "Content-Type":       "application/json",
    "Origin":             "https://www.fidge.app",
    "Referer":            "https://www.fidge.app/",
    "Sec-Ch-Ua":          '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "Sec-Ch-Ua-Mobile":   "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest":     "empty",
    "Sec-Fetch-Mode":     "cors",
    "Sec-Fetch-Site":     "cross-site",
}

LANG = {
    'vi': {
        'title':              'FIDGE BOT - AUTO REDEEM COUPON',
        'enter_codes':        'Nhập mã coupon (cách nhau bằng dấu phẩy hoặc xuống dòng, Enter 2 lần để xong):',
        'found_accounts':     'Tìm thấy {count} tài khoản trong accounts.txt',
        'found_proxies':      'Tìm thấy {count} proxy',
        'no_proxies':         'Không có proxy, chạy trực tiếp',
        'found_codes':        'Tìm thấy {count} mã coupon',
        'processing':         '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'pausing':            'Tạm dừng',
        'completed':          '✅ HOÀN THÀNH: {ok}/{total} TÀI KHOẢN',
        'accounts_not_found': '❌ Không tìm thấy accounts.txt',
        'accounts_empty':     '❌ Không có tài khoản hợp lệ',
        'invalid_account':    'Dòng {i}: định dạng sai (cần email:password), bỏ qua',
        'no_codes':           '❌ Không có mã coupon nào được nhập',
        'no_proxy':           'Không có proxy',
        'unknown_ip':         'Không xác định',
        'proxy_line':         '🔄 Proxy: [{proxy}] | IP: [{ip}]',
        'account_label':      'Tài khoản',
        'retry':              'Retry {cur}/{max}...',
        'max_retry':          'Hết số lần thử',
        'login_req':          'Đang đăng nhập vào Fidge...',
        'login_ok':           'Đăng nhập thành công! User: {username}',
        'login_email':        '- Email:       {email}',
        'login_points':       '- Points:      {points:.2f}',
        'login_gems':         '- Gems:        {gems}',
        'login_fail':         'Đăng nhập thất bại',
        'redeem_req':         '🎫 Đang redeem mã: {code}...',
        'redeem_ok':          '✓ Thành công [{code}]! +{gems} 💎 Gems | Points: {points:.2f}',
        'redeem_fail':        '✖ Thất bại [{code}]: {msg}',
        'summary_header':     '📊 Tóm tắt:',
        'summary_email':      '- Email:       {v}',
        'summary_username':   '- Username:    {v}',
        'summary_gems':       '- Gems sau redeem: {v}',
        'summary_ok':         '- Mã thành công:   {v}/{total}',
        'success_line':       '✅ Thành công | {email} | {ok}/{total} mã | Gems: {gems}',
        'err_runtime':        'Lỗi: {e}',
    },
    'en': {
        'title':              'FIDGE BOT - AUTO REDEEM COUPON',
        'enter_codes':        'Enter coupon codes (comma or newline separated, press Enter twice to finish):',
        'found_accounts':     'Found {count} accounts in accounts.txt',
        'found_proxies':      'Found {count} proxies',
        'no_proxies':         'No proxies, running direct',
        'found_codes':        'Found {count} coupon code(s)',
        'processing':         '⚙ PROCESSING {count} ACCOUNTS',
        'pausing':            'Pausing',
        'completed':          '✅ COMPLETED: {ok}/{total} ACCOUNTS',
        'accounts_not_found': '❌ accounts.txt not found',
        'accounts_empty':     '❌ No valid accounts',
        'invalid_account':    'Line {i}: bad format (need email:password), skipped',
        'no_codes':           '❌ No coupon codes entered',
        'no_proxy':           'No proxy',
        'unknown_ip':         'Unknown',
        'proxy_line':         '🔄 Proxy: [{proxy}] | IP: [{ip}]',
        'account_label':      'Account',
        'retry':              'Retry {cur}/{max}...',
        'max_retry':          'Max retries reached',
        'login_req':          'Logging into Fidge...',
        'login_ok':           'Login successful! User: {username}',
        'login_email':        '- Email:       {email}',
        'login_points':       '- Points:      {points:.2f}',
        'login_gems':         '- Gems:        {gems}',
        'login_fail':         'Login failed',
        'redeem_req':         '🎫 Redeeming code: {code}...',
        'redeem_ok':          '✓ Success [{code}]! +{gems} 💎 Gems | Points: {points:.2f}',
        'redeem_fail':        '✖ Failed [{code}]: {msg}',
        'summary_header':     '📊 Summary:',
        'summary_email':      '- Email:       {v}',
        'summary_username':   '- Username:    {v}',
        'summary_gems':       '- Gems after redeem: {v}',
        'summary_ok':         '- Codes redeemed:    {v}/{total}',
        'success_line':       '✅ Done | {email} | {ok}/{total} codes | Gems: {gems}',
        'err_runtime':        'Error: {e}',
    },
}

def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def p(icon: str, text: str, color=Fore.CYAN):
    print(f"{color}  {icon} {text}{Style.RESET_ALL}")

def load_accounts() -> List[Tuple[int, str, str]]:
    fp = "accounts.txt"
    if not os.path.exists(fp):
        p("✖", LANG['accounts_not_found'], Fore.RED)
        with open(fp, 'w') as f:
            f.write("# Mỗi dòng một tài khoản theo định dạng: email:password\n")
            f.write("# Example: user@gmail.com:MyPassword123\n")
        sys.exit(1)
    accounts = []
    with open(fp) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(':', 1)
            if len(parts) != 2:
                p("⚠", LANG['invalid_account'].format(i=i), Fore.YELLOW)
                continue
            email, password = parts[0].strip(), parts[1].strip()
            if email and password:
                accounts.append((i, email, password))
            else:
                p("⚠", LANG['invalid_account'].format(i=i), Fore.YELLOW)
    if not accounts:
        p("✖", LANG['accounts_empty'], Fore.RED)
        sys.exit(1)
    return accounts

def load_proxies() -> List[str]:
    if not os.path.exists("proxies.txt"):
        return []
    return [l.strip() for l in open("proxies.txt") if l.strip() and not l.startswith('#')]

def parse_proxy(proxy: Optional[str]) -> Optional[str]:
    if not proxy:
        return None
    proxy = proxy.strip()
    if proxy.startswith(("http://", "https://", "socks4://", "socks5://")):
        return proxy
    parts = proxy.split(":")
    if len(parts) == 4:
        host, port, user, pwd = parts
        return f"http://{user}:{pwd}@{host}:{port}"
    if len(parts) == 2:
        return f"http://{parts[0]}:{parts[1]}"
    return f"http://{proxy}"

def make_connector(proxy_url: Optional[str]):
    if not proxy_url:
        return aiohttp.TCPConnector(ssl=False)
    if proxy_url.startswith("socks"):
        return ProxyConnector.from_url(proxy_url, ssl=False)
    return aiohttp.TCPConnector(ssl=False)

def proxy_kwargs(proxy_url: Optional[str]) -> dict:
    if not proxy_url or proxy_url.startswith("socks"):
        return {}
    return {"proxy": proxy_url}

async def get_proxy_ip(proxy_url: Optional[str]) -> str:
    try:
        connector = make_connector(proxy_url)
        kw        = proxy_kwargs(proxy_url)
        timeout   = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
            async with s.get("https://api.ipify.org?format=json", **kw) as r:
                data = await r.json()
                return data.get("ip", LANG['unknown_ip'])
    except Exception:
        return LANG['unknown_ip']

def input_coupon_codes() -> List[str]:
    """Prompt user to enter coupon codes interactively."""
    print()
    print(f"{Fore.CYAN}  📋 {LANG['enter_codes']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  {'─' * 50}{Style.RESET_ALL}")
    lines = []
    while True:
        try:
            line = input(f"{Fore.YELLOW}  > {Style.RESET_ALL}")
        except EOFError:
            break
        if line.strip() == "" and lines:
            break
        if line.strip():
            lines.append(line.strip())

    codes = []
    for line in lines:
        for code in line.split(','):
            code = code.strip().upper()
            if code:
                codes.append(code)

    seen = set()
    unique = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique

class FidgeClient:
    def __init__(self, session: aiohttp.ClientSession, proxy_url: Optional[str]):
        self.session = session
        self.kw      = proxy_kwargs(proxy_url)
        self.token   = None

    def _h(self) -> dict:
        h = dict(HEADERS_BASE)
        if self.token:
            h["x-auth-token"] = self.token
        return h

    async def login(self, email: str, password: str) -> Optional[dict]:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": email, "password": password},
                headers=self._h(),
                **self.kw
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    self.token = data.get("token")
                    return data
                return None
        except Exception:
            return None

    async def redeem_coupon(self, code: str) -> Tuple[bool, dict]:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/coupons/redeem",
                json={"code": code},
                headers=self._h(),
                **self.kw
            ) as r:
                data = await r.json()
                if r.status == 200:
                    return True, data
                return False, data
        except Exception as e:
            return False, {"message": str(e)}

async def process_account(
    index: int,
    email: str,
    password: str,
    proxy: Optional[str],
    codes: List[str],
) -> bool:
    proxy_url = parse_proxy(proxy)
    proxy_str = proxy or LANG['no_proxy']

    print_border(f"{LANG['account_label']} {index}: {email}", Fore.YELLOW)

    ip = await get_proxy_ip(proxy_url)
    print(f"{Fore.CYAN}  {LANG['proxy_line'].format(proxy=proxy_str, ip=ip)}{Style.RESET_ALL}")
    print()

    timeout = aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])

    try:
        connector = make_connector(proxy_url)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

            for attempt in range(CONFIG['RETRY_ATTEMPTS']):
                if attempt > 0:
                    p("ℹ", LANG['retry'].format(cur=attempt, max=CONFIG['RETRY_ATTEMPTS'] - 1), Fore.YELLOW)
                    await asyncio.sleep(CONFIG['RETRY_DELAY'])

                fidge = FidgeClient(session, proxy_url)

                p(">", LANG['login_req'], Fore.CYAN)
                login_data = await fidge.login(email, password)
                if not login_data or not fidge.token:
                    p("✖", LANG['login_fail'], Fore.RED)
                    continue

                user     = login_data.get('user', {})
                username = user.get('username', email)
                points   = float(user.get('points', 0))
                gems     = float(user.get('gems', 0))

                p("✓", LANG['login_ok'].format(username=username), Fore.GREEN)
                print(f"{Fore.WHITE}     {LANG['login_email'].format(email=email)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['login_points'].format(points=points)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['login_gems'].format(gems=gems)}{Style.RESET_ALL}")
                print()

                await asyncio.sleep(random.uniform(0.5, 1.2))

                label = "── AUTO REDEEM ──"
                print(f"{Fore.CYAN}┌─ {label} {'─' * (BORDER_WIDTH - len(label) - 4)}{Style.RESET_ALL}")

                ok_count   = 0
                fail_count = 0

                for code in codes:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                    p(">", LANG['redeem_req'].format(code=code), Fore.CYAN)

                    ok, data = await fidge.redeem_coupon(code)

                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                    if ok:
                        new_gems   = data.get('gems', gems)
                        new_points = float(data.get('points', points))
                        gained     = int(float(new_gems) - float(gems)) if ok else 0
                        gems       = float(new_gems)
                        points     = new_points
                        ok_count  += 1
                        p("✓", LANG['redeem_ok'].format(
                            code=code, gems=gained, points=points
                        ), Fore.GREEN)
                    else:
                        fail_count += 1
                        msg = data.get('message', data.get('error', 'Unknown error'))
                        p("✖", LANG['redeem_fail'].format(code=code, msg=msg), Fore.RED)

                    print(f"{Fore.CYAN}│{Style.RESET_ALL}")
                    await asyncio.sleep(random.uniform(0.8, 1.5))

                print(f"{Fore.CYAN}└{'─' * (BORDER_WIDTH - 2)}{Style.RESET_ALL}")
                print()

                print(f"{Fore.WHITE}  {'─' * 50}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}  {LANG['summary_header']}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_email'].format(v=email)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_username'].format(v=username)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_gems'].format(v=gems)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_ok'].format(v=ok_count, total=len(codes))}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}  {'─' * 50}{Style.RESET_ALL}")
                print()

                color = Fore.GREEN if ok_count > 0 else Fore.YELLOW
                print(f"{color}  {LANG['success_line'].format(email=email, ok=ok_count, total=len(codes), gems=gems)}{Style.RESET_ALL}")
                print()

                return True

            p("✖", LANG['max_retry'], Fore.RED)
            return False

    except Exception as e:
        import traceback
        p("✖", LANG['err_runtime'].format(e=e), Fore.RED)
        print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        return False

async def run_redeem(language: str = 'vi'):
    global LANG
    LANG = LANG[language]
    print()
    print_border(LANG['title'], Fore.CYAN)
    print()

    accounts = load_accounts()
    p("ℹ", LANG['found_accounts'].format(count=len(accounts)), Fore.YELLOW)

    proxies = load_proxies()
    if proxies:
        p("ℹ", LANG['found_proxies'].format(count=len(proxies)), Fore.YELLOW)
    else:
        p("ℹ", LANG['no_proxies'], Fore.YELLOW)

    codes = input_coupon_codes()
    if not codes:
        p("✖", LANG['no_codes'], Fore.RED)
        sys.exit(1)

    print()
    p("ℹ", LANG['found_codes'].format(count=len(codes)), Fore.GREEN)
    print(f"{Fore.WHITE}  Codes: {Fore.CYAN}{', '.join(codes)}{Style.RESET_ALL}")
    print()

    print_separator()
    print_border(LANG['processing'].format(count=len(accounts)), Fore.MAGENTA)
    print()

    total   = len(accounts)
    accs_ok = 0
    sema    = asyncio.Semaphore(CONFIG['THREADS'])

    async def run_one(i: int, idx: int, email: str, password: str):
        nonlocal accs_ok
        proxy = proxies[i % len(proxies)] if proxies else None
        async with sema:
            ok = await process_account(idx, email, password, proxy, codes)
            if ok:
                accs_ok += 1
            if i < total - 1:
                delay = CONFIG['DELAY_BETWEEN']
                p("ℹ", f"{LANG['pausing']} {delay}s...", Fore.YELLOW)
                await asyncio.sleep(delay)

    await asyncio.gather(
        *[run_one(i, idx, email, pwd) for i, (idx, email, pwd) in enumerate(accounts)],
        return_exceptions=True
    )

    print()
    print_border(LANG['completed'].format(ok=accs_ok, total=total), Fore.GREEN)
    print()


if __name__ == "__main__":
    asyncio.run(run_redeem('vi'))

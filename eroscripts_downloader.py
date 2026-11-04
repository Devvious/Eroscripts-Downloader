#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import html
import http.cookiejar
import importlib
import io
import json
import math
import os
import queue
import random
import re
import shutil
import socket
import ssl
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

VERSION = "1.5.2"
DEFAULT_SITE = "https://discuss.eroscripts.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# Settings

VIDEO_EXTS = {
    ".mp4", ".m4v", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".f4v",
    ".mpg", ".mpeg", ".m2ts", ".mts", ".ts", ".3gp", ".ogv", ".vob", ".divx",
    ".asf", ".rm", ".rmvb",
}
ARCHIVE_EXTS = {".zip", ".7z", ".rar"}
SCRIPT_EXT = ".funscript"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".avif", ".heic"}

AXIS_SUFFIXES = {
    "roll", "pitch", "twist", "surge", "sway", "suck", "valve", "vib", "vibe",
    "vibrate", "lube", "stroke",
    "l0", "l1", "l2", "l3", "r0", "r1", "r2", "v0", "v1", "v2", "a0", "a1", "a2",
}

HOSTS = [
    ("pixeldrain", "Pixeldrain", ("pixeldrain.com", "pixeldrain.net", "pixeldra.in")),
    ("mega", "Mega", ("mega.nz", "mega.co.nz", "mega.io")),
    ("gdrive", "Google Drive", ("drive.google.com", "docs.google.com", "drive.usercontent.google.com")),
    ("dropbox", "Dropbox", ("dropbox.com", "dropboxusercontent.com")),
    ("mediafire", "MediaFire", ("mediafire.com",)),
    ("gofile", "Gofile", ("gofile.io",)),
    ("kraken", "KrakenFiles", ("krakenfiles.com",)),
    ("buzz", "BuzzHeavier", ("buzzheavier.com",)),
    ("catbox", "Catbox", ("catbox.moe",)),
    ("viking", "VikingFile", ("vikingfile.com",)),
    ("e621", "e621", ("e621.net", "e926.net")),
    ("pmvhaven", "PMVHaven", ("pmvhaven.com",)),
]
VIKING_RE = re.compile(r"vik[i1]ng-?f[i1]le", re.I)
HOST_LABEL = {k: label for k, label, _ in HOSTS}
HOST_LABEL.update({"direct": "Direct link", "eroscripts": "EroScripts upload"})
HOST_PREF = {"pixeldrain": 0, "gdrive": 1, "mega": 2, "dropbox": 3, "mediafire": 4,
             "gofile": 5, "direct": 6, "catbox": 6, "e621": 6, "kraken": 7, "buzz": 7, "ytdlp": 8,
             "viking": 8, "pmvhaven": 6,
             "web": 9, "eroscripts": 11, "store": 12}

TUBE_HOSTS = (
    "pornhub.com", "pornhubpremium.com", "xvideos.com", "xvideos.red", "xnxx.com",
    "xhamster.com", "xhamster.desi", "xhamster2.com", "spankbang.com", "eporner.com",
    "redtube.com", "youporn.com", "tube8.com", "tnaflix.com", "motherless.com",
    "iwara.tv", "youtube.com", "youtu.be", "rule34video.com", "thisvid.com",
    "txxx.com", "hclips.com", "porntrex.com", "redgifs.com", "vimeo.com",
    "noodlemagazine.com", "hqporner.com", "sxyprn.com", "porn.com", "beeg.com",
)
STORE_HOSTS = (
    "sexlikereal.com", "vrporn.com", "czechvr.com", "czechvrfetish.com", "czechvrcasting.com",
    "badoinkvr.com", "vrbangers.com", "vrconk.com", "wankzvr.com", "naughtyamerica.com",
    "virtualrealporn.com", "realitylovers.com", "milfvr.com", "povr.com", "vrhush.com",
    "vrallure.com", "stripzvr.com", "sinsvr.com", "xsinsvr.com", "darkroomvr.com",
    "tmwvrnet.com", "vrcosplayx.com", "18vr.com", "baberoticavr.com", "lethalhardcorevr.com",
    "kinkvr.com", "vixen.com", "tushy.com", "blacked.com", "deeper.com", "brazzers.com",
    "realitykings.com", "bangbros.com", "mofos.com", "teamskeet.com", "mylf.com",
    "nubiles.net", "onlyfans.com", "fansly.com", "manyvids.com", "clips4sale.com",
    "iwantclips.com", "loyalfans.com", "fancentro.com", "pornpros.com", "evilangel.com",
    "julesjordan.com", "adulttime.com", "hentaivr.com", "vrlatina.com", "groobyvr.com",
    "slrporn.com", "deovr.com", "heresphere.com", "realjamvr.com", "vrspy.com",
    "dmm.co.jp", "fanza.com", "steampowered.com", "dlsite.com", "itch.io",
    "payhip.com", "fanbox.cc", "boosty.to",
)
IGNORE_HOSTS = (
    "twitter.com", "x.com", "reddit.com", "redd.it", "discord.gg", "discord.com",
    "discordapp.com", "instagram.com", "tiktok.com", "bsky.app", "t.me", "telegram.me",
    "linktr.ee", "github.com", "githubusercontent.com", "gitlab.com", "wikipedia.org",
    "imdb.com", "iafd.com", "data18.com", "freeones.com", "babepedia.com",
    "boobpedia.com", "indexxx.com", "theporndb.net", "stashdb.org", "ko-fi.com",
    "buymeacoffee.com", "paypal.com", "paypal.me", "patreon.com", "subscribestar.com",
    "subscribestar.adult", "gumroad.com", "imgur.com", "ibb.co", "imgbb.com", "gyazo.com",
    "postimg.cc", "postimages.org", "tenor.com", "giphy.com", "handyfeeling.com",
    "thehandy.com", "openfunscripter.org", "buttplug.io", "intiface.com", "xtoys.app",
    "eroscripts.com", "faptap.net", "airscripts.fun", "t.co",
    "imgsli.com", "slow.pics", "imgbox.com", "imgchest.com", "pixhost.to", "imagebam.com", "prnt.sc",
    "prntscr.com", "imagetwist.com", "freeimage.host", "vgy.me", "imgpile.com", "lervik.com",
)

ONLINE, BROWSER, PAGE, UNKNOWN, STORE, DEAD, CHECKING = (
    "online", "browser", "page", "unknown", "store", "dead", "checking")
STATUS_TEXT = {
    ONLINE: "✔ Online", BROWSER: "↗ Browser only", PAGE: "? Page is up",
    UNKNOWN: "? Couldn't check", STORE: "$ Store page", DEAD: "✖ Gone", CHECKING: "… checking",
}
STATUS_RANK = {ONLINE: 0, BROWSER: 1, PAGE: 2, UNKNOWN: 3, CHECKING: 4, STORE: 5, DEAD: 6}

DEAD_RE = re.compile(
    r"\b(file (?:was |has been )?(?:deleted|removed)|file not found|file (?:does not|doesn'?t) exist"
    r"|(?:video|file|page) (?:is )?no longer available|(?:video|file) (?:has been|was) "
    r"(?:deleted|removed|disabled|taken down)|this (?:video|file) (?:is )?(?:unavailable|not available)"
    r"|404 not found|link (?:has )?expired|invalid or deleted file)\b", re.I)

SETTINGS_FILE = "eroscripts_downloader_settings.json"
HISTORY_FILE = "eroscripts_downloader_history.jsonl"
ORGANIZER_SETTINGS = "funscript_organizer_settings.json"

DEFAULT_SETTINGS = {
    "dest": "",
    "cookie": "",
    "username": "",
    "site": DEFAULT_SITE,
    "user_agent": "",
    "replies": True,
    "max_posts": 400,
    "parallel_downloads": 2,
    "show_dead": False,
    "watch_clipboard": False,
    "allow_bad_certificates": True,
    "geometry": "",
    "show_context": False,
    "script_lengths": True,
    "prefer_versions": "",
}


# Helpers


class _Color:
    on = False


def setup_console():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if sys.stdout is not None and sys.stdout.isatty() and not os.environ.get("NO_COLOR"):
        if os.name == "nt":
            os.system("")
        _Color.on = True


def _c(text, code):
    return f"\033[{code}m{text}\033[0m" if _Color.on else str(text)


def bold(t): return _c(t, "1")
def dim(t): return _c(t, "2")
def red(t): return _c(t, "31")
def green(t): return _c(t, "32")
def yellow(t): return _c(t, "33")
def cyan(t): return _c(t, "36")


def fmt_size(n):
    if n is None:
        return ""
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit in ("B", "KB") else f"{n:.1f} {unit}"
        n /= 1024


def fmt_dur(seconds):
    if not seconds:
        return ""
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_size(text):
    if not text:
        return None
    t = text.strip()
    t = t.replace(",", "") if re.search(r",\d{3}\b", t) else t.replace(",", ".")
    m = re.match(r"^([\d.]+)\s*([KMGT]?)i?B?$", t, re.I)
    if not m:
        return None
    try:
        num = float(m.group(1))
    except ValueError:
        return None
    return int(num * {"": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}[m.group(2).upper()])


def ext_of(name):
    n = str(name).lower()
    if n.endswith(SCRIPT_EXT):
        return SCRIPT_EXT
    return os.path.splitext(n)[1]


def is_axis(stem):
    base, dot, suf = stem.rpartition(".")
    return bool(dot and base and suf.casefold() in AXIS_SUFFIXES)


def is_videoish(name):
    e = ext_of(os.path.basename(name))
    return e in VIDEO_EXTS or e in ARCHIVE_EXTS or e == ""


_WIN_BAD = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED = {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} | \
    {f"lpt{i}" for i in range(1, 10)}


def tidy_name(name):
    n = html.unescape(str(name)).replace("_", " ")
    return re.sub(r"\s+", " ", n).strip()


def safe_name(name, limit=150):
    n = tidy_name(name)
    n = re.sub(r"\s*:\s*", " - ", n)
    n = _WIN_BAD.sub(" ", n)
    n = re.sub(r"\s+", " ", n).strip().rstrip(" .")
    if len(n) > limit:
        n = n[:limit].rstrip(" .")
    if n.split(".")[0].casefold() in _RESERVED:
        n = n + " file"
    return n or "untitled"


def unique_path(path):
    path = Path(path)
    if not os.path.lexists(path):
        return path
    e = ext_of(path.name)
    stem = path.name[:-len(e)] if e else path.name
    n = 2
    while True:
        p = path.with_name(f"{stem} ({n}){e}")
        if not os.path.lexists(p):
            return p
        n += 1


def existing_video(folder, base):
    folder = Path(folder)
    if not folder.is_dir():
        return None
    for p in folder.iterdir():
        if p.is_file() and ext_of(p.name) in VIDEO_EXTS and \
                p.name[:-len(ext_of(p.name))].casefold() == base.casefold():
            return p
    return None


def host_of(url):
    try:
        h = (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def _match(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


def open_url(url):
    try:
        webbrowser.open(url, new=2)
    except Exception:
        pass


def open_path(path):
    try:
        if os.name == "nt":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def app_dir():
    for base in (Path(sys.argv[0]).resolve().parent, Path.home()):
        try:
            test = base / ".esd_write_test"
            test.write_text("ok")
            test.unlink()
            return base
        except OSError:
            continue
    return Path.cwd()


def _decode(body, headers=None):
    cs = None
    if headers is not None:
        m = re.search(r"charset=([\w-]+)", headers.get("Content-Type") or "", re.I)
        cs = m.group(1) if m else None
    try:
        return body.decode(cs or "utf-8", "replace")
    except LookupError:
        return body.decode("utf-8", "replace")


def cd_filename(cd):
    if not cd:
        return None
    m = re.search(r"filename\*\s*=\s*([^']*)'[^']*'([^;]+)", cd, re.I)
    if m:
        try:
            return urllib.parse.unquote(m.group(2).strip().strip('"'), encoding=m.group(1) or "utf-8")
        except LookupError:
            pass
    m = re.search(r'filename\s*=\s*"([^"]+)"', cd, re.I) or re.search(r"filename\s*=\s*([^;]+)", cd, re.I)
    if not m:
        return None
    name = m.group(1).strip()
    try:
        name = name.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return urllib.parse.unquote(name)


def _strip_tags(body):
    body = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", body)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))


def _title(body):
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
    return html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()[:150] if m else ""


def _og(body, prop):
    m = re.search(r'<meta[^>]+property="og:%s"[^>]+content="([^"]*)"' % prop, body, re.I) or \
        re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="og:%s"' % prop, body, re.I)
    return html.unescape(m.group(1)).strip() if m else ""


EXT_BY_CTYPE = {
    "video/mp4": ".mp4", "video/x-matroska": ".mkv", "video/webm": ".webm",
    "video/quicktime": ".mov", "video/x-msvideo": ".avi", "video/x-ms-wmv": ".wmv",
    "video/x-flv": ".flv", "video/mp2t": ".ts", "application/zip": ".zip",
    "application/x-zip-compressed": ".zip", "application/x-7z-compressed": ".7z",
    "application/vnd.rar": ".rar", "application/x-rar-compressed": ".rar",
}


class Cancelled(Exception):
    pass


class DownloadError(Exception):
    pass


class HttpError(Exception):
    def __init__(self, code, reason="", body=b"", headers=None, url=""):
        super().__init__(f"HTTP {code} {reason}".strip())
        self.code = code
        self.body = body or b""
        self.headers = headers or {}
        self.url = url

    def text(self):
        return self.body.decode("utf-8", "replace")

    def cloudflare(self):
        h = self.headers
        return self.code in (403, 429, 503) and (
            b"cf-chl" in self.body or b"Just a moment" in self.body or
            bool(h and h.get("cf-mitigated")))


class Pool:
    def __init__(self, n):
        self.q = queue.Queue()
        for _ in range(n):
            threading.Thread(target=self._run, daemon=True).start()

    def submit(self, fn, *args, done=None):
        self.q.put((fn, args, done))

    def _run(self):
        while True:
            fn, args, done = self.q.get()
            try:
                res, err = fn(*args), None
            except BaseException as e:
                res, err = None, e
            if done:
                try:
                    done(res, err)
                except Exception:
                    traceback.print_exc()


# HTTP


def set_cookie(jar, domain, name, value, path="/"):
    c = http.cookiejar.Cookie(
        0, name, value, None, False, domain, True, domain.startswith("."), path, True,
        False, None, False, None, None, {})
    jar.set_cookie(c)


def is_cert_error(e):
    reason = getattr(e, "reason", e)
    return isinstance(reason, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in str(e)


def safe_url(url):
    try:
        sp = urllib.parse.urlsplit(url)
        path = urllib.parse.quote(sp.path, safe="/%:@!$&'()*+,;=~")
        query = urllib.parse.quote(sp.query, safe="=&%:/?@!$'()*+,;~")
        return urllib.parse.urlunsplit((sp.scheme, sp.netloc, path, query, sp.fragment))
    except ValueError:
        return url


def _host_in(host, hosts):
    return any(host == h or host.endswith("." + h) for h in hosts if h)


def ssl_context():
    ctx = ssl.create_default_context()
    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except Exception:
        pass
    return ctx


class Http:
    def __init__(self, ua=None):
        self.ua = ua or UA
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar),
                                                  urllib.request.HTTPSHandler(context=ssl_context()))
        self.allow_insecure = True
        self.protected_hosts = set()
        self.insecure_hosts = set()
        self._insecure_opener = None
        self._lock = threading.Lock()

    def _insecure(self):
        with self._lock:
            if self._insecure_opener is None:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                protected = self.protected_hosts

                class _Redirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                        if _host_in(host_of(newurl), protected):
                            raise urllib.error.URLError("won't follow that redirect without a "
                                                        "valid certificate")
                        return super().redirect_request(req, fp, code, msg, hdrs, newurl)
                self._insecure_opener = urllib.request.build_opener(
                    urllib.request.HTTPCookieProcessor(self.jar),
                    urllib.request.HTTPSHandler(context=ctx), _Redirect())
            return self._insecure_opener

    def bad_cert(self, url):
        return host_of(url) in self.insecure_hosts

    def can_skip_cert(self, url):
        return self.allow_insecure and not _host_in(host_of(url), self.protected_hosts)

    def open(self, url, data=None, headers=None, method=None, timeout=30):
        h = {"User-Agent": self.ua, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
        if headers:
            h.update(headers)
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode()
            h.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        elif isinstance(data, str):
            data = data.encode()
        url = safe_url(url)
        host = host_of(url)
        insecure = host in self.insecure_hosts and self.can_skip_cert(url)
        for attempt in range(2):
            req = urllib.request.Request(url, data=data, headers=h, method=method)
            opener = self._insecure() if insecure else self.opener
            try:
                return opener.open(req, timeout=timeout)
            except urllib.error.HTTPError as e:
                try:
                    body = e.read(300_000)
                except Exception:
                    body = b""
                raise HttpError(e.code, e.reason or "", body, e.headers, url) from None
            except urllib.error.URLError as e:
                if attempt or insecure or not is_cert_error(e) or not self.can_skip_cert(url):
                    raise
                self.insecure_hosts.add(host)
                insecure = True

    def read(self, url, limit=20_000_000, **kw):
        with self.open(url, **kw) as r:
            body = r.read(limit + 1)
            if len(body) > limit:
                raise DownloadError("the answer was much bigger than expected")
            return body, r.geturl(), r.headers, r.status

    def text(self, url, limit=3_000_000, **kw):
        body, final, headers, _ = self.read(url, limit=limit, **kw)
        return _decode(body, headers), final, headers

    def json(self, url, **kw):
        h = {"Accept": "application/json, text/javascript, */*; q=0.01"}
        h.update(kw.pop("headers", None) or {})
        body, _, _, _ = self.read(url, headers=h, **kw)
        try:
            return json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            raise DownloadError(f"{host_of(url)} sent something that isn't JSON") from None

    def probe(self, url, headers=None, timeout=25):
        h = {"Range": "bytes=0-0"}
        h.update(headers or {})
        r = self.open(url, headers=h, timeout=timeout)
        try:
            info = {"status": r.status, "url": r.geturl(),
                    "ctype": (r.headers.get("Content-Type") or "").lower(),
                    "name": cd_filename(r.headers.get("Content-Disposition") or ""), "size": None}
            m = re.search(r"/(\d+)\s*$", r.headers.get("Content-Range") or "")
            if m:
                info["size"] = int(m.group(1))
            elif r.status == 200 and (r.headers.get("Content-Length") or "").isdigit():
                info["size"] = int(r.headers["Content-Length"])
            if "text/html" in info["ctype"]:
                info["body"] = _decode(r.read(300_000), r.headers)
            return info
        finally:
            r.close()


def _html_problem(snippet, host):
    low = snippet.lower()
    if "too many users" in low or ("quota" in low and "exceed" in low):
        return (f"{host}: the download limit for this file is used up for today. "
                "Try later, or open the link in your browser.")
    if "captcha" in low or "recaptcha" in low or "hcaptcha" in low:
        return f"{host} wants a captcha - open the link in your browser."
    if "sign in" in low or "log in" in low or "login" in low:
        return f"{host} wants you to sign in - open the link in your browser."
    return f"{host} sent a web page instead of the file - open the link in your browser."


def http_download(http_, url, folder, base, progress, cancel, headers=None, name_hint=None):
    folder = Path(folder)
    part = folder / f".{base[:60]}.{hashlib.md5(url.encode()).hexdigest()[:8]}.part"
    pos = part.stat().st_size if part.exists() else 0
    h = dict(headers or {})
    if pos:
        h["Range"] = f"bytes={pos}-"
    try:
        r = http_.open(url, headers=h, timeout=60)
    except HttpError as e:
        if e.code == 416 and pos:
            part.unlink()
            pos = 0
            r = http_.open(url, headers=dict(headers or {}), timeout=60)
        elif e.code == 509:
            raise DownloadError(f"{host_of(url)}: download limit reached - try again later.") from None
        elif e.cloudflare():
            raise DownloadError(f"{host_of(url)} is showing a 'checking your browser' page - "
                                "open the link in your browser.") from None
        else:
            raise DownloadError(f"{host_of(url)}: {e}") from None
    total = None
    done = pos
    try:
        with r:
            ctype = (r.headers.get("Content-Type") or "").lower()
            name = cd_filename(r.headers.get("Content-Disposition") or "") or name_hint or \
                urllib.parse.unquote(os.path.basename(urllib.parse.urlsplit(r.geturl()).path))
            if "text/html" in ctype:
                snippet = _decode(r.read(200_000), r.headers)
                raise DownloadError(_html_problem(snippet, host_of(r.geturl())))
            if pos and r.status != 206:
                pos = done = 0
            length = r.headers.get("Content-Length") or ""
            if length.isdigit():
                total = int(length) + pos
            m = re.search(r"/(\d+)\s*$", r.headers.get("Content-Range") or "")
            if m:
                total = int(m.group(1))
            with open(part, "ab" if pos else "wb") as fo:
                while True:
                    if cancel.is_set():
                        raise Cancelled()
                    buf = r.read(1 << 20)
                    if not buf:
                        break
                    fo.write(buf)
                    done += len(buf)
                    progress(done, total)
    except Cancelled:
        try:
            part.unlink()
        except OSError:
            pass
        raise
    except (socket.timeout, TimeoutError, ConnectionError, urllib.error.URLError) as e:
        raise DownloadError(f"connection dropped at {fmt_size(done)} ({e}) - press Retry to "
                            "continue where it stopped") from None
    if total and done < total:
        raise DownloadError(f"download stopped early ({fmt_size(done)} of {fmt_size(total)}) - "
                            "press Retry to continue where it stopped")
    ext = ext_of(name)
    if ext not in VIDEO_EXTS | ARCHIVE_EXTS | {SCRIPT_EXT}:
        ext = EXT_BY_CTYPE.get(ctype.split(";")[0].strip(), ".mp4")
    target = unique_path(folder / (base + ext))
    os.replace(part, target)
    return target


def dl_http(url=None, headers=None, name_hint=None, resolve=None):
    def dl(core, folder, base, progress, cancel):
        u, h = resolve(core) if resolve else (url, headers)
        return http_download(core.http, u, folder, base, progress, cancel, headers=h,
                             name_hint=name_hint)
    return dl


# Forum


class LoginError(Exception):
    def __init__(self, msg, need_2fa=False):
        super().__init__(msg)
        self.need_2fa = need_2fa


class ForumError(Exception):
    pass


class Attachment:
    def __init__(self, name, url, size_text, post, user, by_op, pos=0, span=None):
        self.name, self.url, self.size_text = name, url, size_text
        self.post, self.user, self.by_op = post, user, by_op
        self.pos = pos
        self.span = span


class LinkRef:
    def __init__(self, url, text, post, user, by_op, pos=0, before="", span=None):
        self.url, self.text, self.post, self.user, self.by_op = url, text, post, user, by_op
        self.pos = pos
        self.before = before
        self.span = span

    @property
    def where(self):
        if self.post == 0:
            return "added by you"
        return f"#{self.post} by {self.user}" + (" (OP)" if self.by_op else "")


class Topic:
    def __init__(self):
        self.id = 0
        self.slug = ""
        self.title = ""
        self.author = ""
        self.url = ""
        self.tags = []
        self.posts_count = 0
        self.scanned = 0
        self.truncated = False
        self.attachments = []
        self.links = []
        self.posts = {}

    def post_url(self, num):
        return f"{self.url}/{num}" if num and self.url else self.url


TOPIC_PATH_RE = re.compile(r"^/t/(?:([^/]+)/)?(\d+)(?:/\d+)?/?$")
TOPIC_IN_TEXT_RE = re.compile(r"(?:https?://)?[\w.-]*eroscripts?\.com/t/[^\s<>\"'\]\)]+", re.I)


def topic_id(url):
    url = url.strip()
    if url.isdigit():
        return int(url), ""
    if not re.match(r"https?://", url):
        url = "https://" + url
    path = urllib.parse.urlsplit(url).path.rstrip("/")
    m = TOPIC_PATH_RE.match(path)
    if not m:
        raise ForumError(f"That doesn't look like a topic link: {url}")
    return int(m.group(2)), m.group(1) or ""


def find_topic_urls(text, site_host=""):
    found, seen = [], set()
    pats = [TOPIC_IN_TEXT_RE]
    if site_host and "eroscript" not in site_host:
        pats.append(re.compile(r"(?:https?://)?" + re.escape(site_host) +
                               r"(?::\d+)?/t/[^\s<>\"'\]\)]+", re.I))
    for pat in pats:
        for m in pat.finditer(text or ""):
            u = m.group(0).rstrip(".,;:!?")
            try:
                tid, _ = topic_id(u)
            except ForumError:
                continue
            if tid not in seen:
                seen.add(tid)
                found.append(u if re.match(r"https?://", u) else "https://" + u)
    return found


class _Cooked(HTMLParser):
    URL_ATTRS = ("data-onebox-src", "data-video-src", "data-download-href", "data-orig-href")

    BLOCKS = {"p", "li", "br", "div", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "hr"}

    PARAS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "aside", "hr", "ul", "ol", "table",
             "details", "pre"}
    LINES = {"li", "div", "tr", "summary", "header", "article"}
    GREY = {"aside", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.extra = []
        self.text = []
        self.quotes = []
        self.pos = 0
        self._since = []
        self._a = None
        self._tail = None
        self._skip = 0
        self.disp = []
        self.dlen = 0
        self._dsp = False
        self._dnl = 2
        self._pre = 0
        self._hide = None
        self._grey = []
        self.grey = []
        self.dlinks = []

    def _ctx(self):
        lines = [x.strip() for x in "".join(self._since)[-400:].split("\n") if x.strip()]
        return lines[-1][-160:] if lines else ""

    def _emit(self, s):
        self.disp.append(s)
        self.dlen += len(s)
        nl = len(s) - len(s.rstrip("\n"))
        self._dnl = min(2, self._dnl + nl) if nl == len(s) else min(2, nl)

    def _break(self, n):
        self._dsp = False
        while self.dlen and self._dnl < n:
            self._emit("\n")

    def _words(self, data):
        if self._pre:
            if data:
                self._emit(data)
            return
        t = re.sub(r"\s+", " ", data)
        if not t.strip():
            if t and self.dlen and not self._dnl:
                self._dsp = True
            return
        if t[0] == " " and self.dlen and not self._dnl:
            self._dsp = True
        if self._dsp and self.dlen and not self._dnl:
            self._emit(" ")
        self._dsp = t[-1] == " "
        self._emit(t.strip())

    def _show_start(self, tag, cls):
        if self._hide is not None:
            if tag == self._hide[0]:
                self._hide[1] += 1
            return
        if tag in self.PARAS:
            self._break(2)
        elif tag in self.LINES:
            self._break(1)
        elif tag == "br" and self.dlen:
            self._dsp = False
            self._emit("\n")
        if tag == "div" and "lightbox-wrapper" in cls:
            self._words(" [image] ")
            self._hide = [tag, 1]
            return
        if tag == "li":
            self._words("• ")
        if tag in self.GREY:
            self._grey.append((tag, self.dlen))
        if tag == "pre":
            self._pre += 1

    def _show_end(self, tag):
        if self._hide is not None:
            if tag == self._hide[0]:
                self._hide[1] -= 1
                if self._hide[1] <= 0:
                    self._hide = None
                    self._break(1)
            return
        if tag == "pre" and self._pre:
            self._pre -= 1
        if tag in self.GREY:
            for i in range(len(self._grey) - 1, -1, -1):
                if self._grey[i][0] == tag:
                    start = self._grey.pop(i)[1]
                    if self.dlen > start:
                        self.grey.append((start, self.dlen))
                    break
        if tag in self.PARAS:
            self._break(2)
        elif tag in self.LINES:
            self._break(1)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        cls = a.get("class", "")
        if tag == "aside" and "quote" in cls and a.get("data-post", "").isdigit():
            self.quotes.append((int(a["data-post"]), a.get("data-topic", "")))
        self._show_start(tag, cls)
        for k in self.URL_ATTRS:
            if a.get(k):
                d0 = self.dlen
                if k == "data-video-src" and self._hide is None:
                    self._words(" [video] ")
                self.extra.append((a[k], self.pos, self._ctx(), (d0, self.dlen)))
        if tag == "a":
            self._tail = None
            self._a = {"href": a.get("href", ""), "cls": cls, "text": "", "tail": "",
                       "pos": self.pos, "before": self._ctx(), "d0": None}
            self.anchors.append(self._a)
            self._since = []
        elif tag in ("video", "source"):
            if tag == "video":
                d0 = self.dlen
                if self._hide is None:
                    self._words(" [video] ")
                self._vspan = (d0, self.dlen)
            if a.get("src"):
                span = getattr(self, "_vspan", None) or (self.dlen, self.dlen)
                self.extra.append((a["src"], self.pos, self._ctx(), span))
        elif tag in ("script", "style"):
            self._skip += 1
        elif tag in self.BLOCKS:
            self._since.append("\n")

    def handle_endtag(self, tag):
        if tag == "a" and self._a is not None:
            if self._a["d0"] is None:
                self._a["d0"] = self.dlen
            self._a["d1"] = self.dlen
            self.dlinks.append((self._a["d0"], self.dlen, self._a["href"]))
            self._tail = self._a
            self._a = None
        elif tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in self.BLOCKS:
            self._since.append("\n")
        if tag == "video":
            self._vspan = None
        self._show_end(tag)

    def handle_data(self, data):
        if self._skip:
            return
        if self._hide is None:
            self._words(data)
            if self._a is not None and self._a["d0"] is None and data.strip():
                self._a["d0"] = self.dlen - len(re.sub(r"\s+", " ", data).strip()) if not self._pre \
                    else self.dlen - len(data)
        if self._a is not None:
            self._a["text"] += data
        else:
            self._since.append(data)
            if self._tail is not None:
                self._tail["tail"] += data
                if len(self._tail["tail"]) > 40:
                    self._tail = None
        self.text.append(data)
        self.pos += len(data) + 1

    def readable(self):
        return "".join(self.disp).rstrip()


_TEXT_URL_RE = re.compile(r"https?://[^\s<>\"'`]+", re.I)
_BARE_HOST_RE = re.compile(
    r"(?<![\w./@-])((?:www\.)?(?:pixeldrain\.com|mega\.nz|gofile\.io|drive\.google\.com|"
    r"mediafire\.com|dropbox\.com|krakenfiles\.com|buzzheavier\.com)/[^\s<>\"'`]+)", re.I)


def _trim_url(u):
    u = u.strip()
    while u and u[-1] in ".,;:!?'\"]>*":
        u = u[:-1]
    while u.endswith(")") and u.count("(") < u.count(")"):
        u = u[:-1]
    return u


def link_key(url):
    s = urllib.parse.urlsplit(url)
    h = (s.hostname or "").lower()
    h = h[4:] if h.startswith("www.") else h
    h = "mega.nz" if h == "mega.co.nz" else h
    return f"{h}{s.path.rstrip('/')}?{s.query}#{s.fragment}"


def classify(url, site_host):
    h = host_of(url)
    if not h:
        return None
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(parts.path).lower()
    ext = ext_of(path)
    sh = site_host[4:] if site_host.startswith("www.") else site_host
    if h == sh or h.endswith("." + sh) or "eroscript" in h:
        return "eroscripts" if ("/uploads/" in path and ext in VIDEO_EXTS) else None
    if ext in IMAGE_EXTS:
        return None
    if _match(h, IGNORE_HOSTS):
        return None
    if VIKING_RE.search(h):
        return "viking"
    for kind, _, domains in HOSTS:
        if _match(h, domains):
            if kind == "gdrive" and not re.search(r"/file/d/|[?&]id=|/folders/|folderview", url):
                return None
            return kind
    if ext in VIDEO_EXTS or ext in ARCHIVE_EXTS or ext == SCRIPT_EXT:
        return "direct"
    if _match(h, STORE_HOSTS):
        return "store"
    return "web"


def parse_post(topic, post, site, site_host):
    cooked = post.get("cooked") or ""
    p = _Cooked()
    try:
        p.feed(cooked)
        p.close()
    except Exception:
        pass
    num = post.get("post_number") or 0
    user = post.get("username") or ""
    by_op = user.casefold() == (topic.author or "").casefold()
    quotes = {n for n, t in p.quotes if n != num and (not t or t == str(topic.id))}
    readable = p.readable()
    links = []
    for d0, d1, href in p.dlinks:
        href = (href or "").strip()
        if href and not href.startswith(("#", "javascript:")):
            links.append((d0, d1, urllib.parse.urljoin(site + "/", href)))
    reply_user = (post.get("reply_to_user") or {}).get("username") if isinstance(
        post.get("reply_to_user"), dict) else None
    topic.posts[num] = {"user": user, "reply_to": post.get("reply_to_post_number"), "quotes": quotes,
                        "reply_user": reply_user, "text": readable, "grey": p.grey, "links": links,
                        "date": (post.get("created_at") or "")[:10],
                        "edited": (post.get("version") or 1) > 1}
    text = "\n".join(p.text)

    def line_before(start):
        return text[text.rfind("\n", 0, start) + 1:start].strip()[-160:]

    def find_span(u):
        i = readable.find(u)
        return (i, i + len(u)) if i >= 0 else None
    cands = [(a["href"], a["text"], a["tail"], a["pos"], a["before"],
              (a["d0"], a["d1"]) if a.get("d1") is not None else None) for a in p.anchors]
    cands += [(u, "", "", pos, ctx, span) for u, pos, ctx, span in p.extra]
    cands += [(m.group(0), "", "", m.start(), line_before(m.start()), find_span(m.group(0)))
              for m in _TEXT_URL_RE.finditer(text)]
    cands += [("https://" + m.group(1), "", "", m.start(), line_before(m.start()), find_span(m.group(1)))
              for m in _BARE_HOST_RE.finditer(text)]
    seen_att = {a.url for a in topic.attachments}
    seen_link = {link_key(x.url) for x in topic.links}
    for href, label, tail, pos, before, span in cands:
        href = (href or "").strip()
        if not href or href.startswith(("mailto:", "#", "javascript:", "tel:")):
            continue
        url = _trim_url(urllib.parse.urljoin(site + "/", href))
        if not url.lower().startswith(("http://", "https://")):
            continue
        h = host_of(url)
        path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        sh = site_host[4:] if site_host.startswith("www.") else site_host
        internal = h == sh or h.endswith("." + sh)
        if internal and ("/uploads/" in path or "/secure-uploads/" in path):
            name = (label or "").strip()
            ext = ext_of(name) if ext_of(name) in ARCHIVE_EXTS | {SCRIPT_EXT} else ext_of(path)
            if ext in ARCHIVE_EXTS or ext == SCRIPT_EXT:
                if ext_of(name) != ext:
                    name = os.path.basename(path)
                if url not in seen_att:
                    seen_att.add(url)
                    m = re.search(r"\(\s*([\d.,]+\s*[KMGT]?i?B)\s*\)", tail or "", re.I)
                    topic.attachments.append(
                        Attachment(name, url, m.group(1) if m else "", num, user, by_op, pos, span))
                continue
        kind = classify(url, site_host)
        if kind is None:
            continue
        k = link_key(url)
        if k in seen_link:
            continue
        seen_link.add(k)
        topic.links.append(LinkRef(url, (label or "").strip(), num, user, by_op, pos, before, span))


class Forum:
    def __init__(self, http_, site=DEFAULT_SITE):
        self.http = http_
        self.set_site(site)

    def set_site(self, site):
        site = (site or DEFAULT_SITE).strip().rstrip("/")
        if not re.match(r"https?://", site):
            site = "https://" + site
        self.site = site
        self.host = (urllib.parse.urlsplit(site).hostname or "").lower()

    def url(self, path):
        return path if path.startswith("http") else self.site + path

    def _hdr(self):
        return {"Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest", "Referer": self.site + "/"}

    def get_json(self, path, tries=4):
        for n in range(tries):
            try:
                return self.http.json(self.url(path), headers=self._hdr(), timeout=30)
            except HttpError as e:
                if e.cloudflare():
                    raise ForumError("EroScripts is showing a 'checking your browser' page "
                                     "(Cloudflare). Open the site in your browser once, then try "
                                     "again - or paste your browser cookie in Account...") from None
                if e.code == 429 and n < tries - 1:
                    wait = 5.0
                    try:
                        wait = float(e.headers.get("Retry-After") or
                                     json.loads(e.text()).get("extras", {}).get("wait_seconds") or 5)
                    except Exception:
                        pass
                    time.sleep(min(max(wait, 1.0), 30.0))
                    continue
                raise

    def _forum_cookies(self):
        out = []
        for c in self.http.jar:
            d = c.domain.lstrip(".").lower()
            if self.host == d or self.host.endswith("." + d):
                out.append(c)
        return out

    def cookie_string(self):
        return "; ".join(f"{c.name}={c.value}" for c in self._forum_cookies())

    def clear_cookies(self):
        for c in self._forum_cookies():
            try:
                self.http.jar.clear(c.domain, c.path, c.name)
            except KeyError:
                pass

    def set_cookie_string(self, s):
        s = (s or "").strip()
        if s.lower().startswith("cookie:"):
            s = s[7:].strip()
        if not s:
            return
        if "=" not in s:
            pairs = [("_t", s)]
        else:
            pairs = [p.split("=", 1) for p in s.split(";") if "=" in p]
        self.clear_cookies()
        for name, value in pairs:
            if name.strip():
                set_cookie(self.http.jar, self.host, name.strip(), value.strip())

    def current_user(self):
        try:
            j = self.get_json("/session/current.json", tries=2)
        except HttpError as e:
            if e.code in (401, 403, 404):
                return None
            raise
        return ((j or {}).get("current_user") or {}).get("username")

    def login(self, user, password, otp=None):
        self.clear_cookies()
        try:
            csrf = (self.get_json("/session/csrf") or {}).get("csrf") or ""
        except HttpError as e:
            raise LoginError(f"Couldn't start the login ({e}).") from None
        data = {"login": user, "password": password, "second_factor_method": "1"}
        if otp:
            data["second_factor_token"] = otp.strip().replace(" ", "")
        h = self._hdr()
        h.update({"X-CSRF-Token": csrf, "Origin": self.site, "Referer": self.site + "/login"})
        try:
            body, _, _, _ = self.http.read(self.url("/session"), data=data, headers=h, timeout=30)
        except HttpError as e:
            if e.cloudflare():
                raise LoginError("Cloudflare blocked the login. Paste your browser cookie instead "
                                 "(see below).") from None
            body = e.body
            if not body:
                raise LoginError(f"Login failed ({e}).") from None
        try:
            j = json.loads(body.decode("utf-8", "replace"))
        except ValueError:
            raise LoginError("The site answered with something unexpected. Paste your browser "
                             "cookie instead (see below).") from None
        if j.get("error"):
            if j.get("reason") == "invalid_second_factor" or j.get("totp_enabled") or \
                    j.get("security_key_enabled") or j.get("second_factor_required"):
                if j.get("security_key_enabled") and not j.get("totp_enabled"):
                    raise LoginError("This account uses a security key for 2-factor login, which "
                                     "this program can't do. Paste your browser cookie instead.")
                raise LoginError(html.unescape(str(j["error"])) if otp else
                                 "Enter your 2-factor code, then press Log in again.", need_2fa=True)
            raise LoginError(html.unescape(re.sub(r"<[^>]+>", "", str(j["error"]))))
        name = (j.get("user") or {}).get("username") or self.current_user()
        if not name:
            raise LoginError("The site didn't confirm the login.")
        return name

    def download(self, url, cancel=None, limit=300_000_000):
        for n in range(4):
            if cancel is not None and cancel.is_set():
                raise Cancelled()
            try:
                body, final, headers, _ = self.http.read(url, limit=limit, timeout=60,
                                                         headers={"Referer": self.site + "/"})
                break
            except HttpError as e:
                if e.code == 429 and n < 3:
                    try:
                        wait = float(e.headers.get("Retry-After") or 5)
                    except (TypeError, ValueError):
                        wait = 5.0
                    time.sleep(min(max(wait, 1.0), 30.0))
                    continue
                if e.code in (401, 403, 404):
                    raise DownloadError(f"EroScripts refused the download (HTTP {e.code}) - "
                                        "log in with Account... first.") from None
                raise DownloadError(f"EroScripts: {e}") from None
        ctype = (headers.get("Content-Type") or "").lower()
        if "text/html" in ctype and not url.lower().endswith(".html"):
            raise DownloadError("EroScripts sent a web page instead of the file - "
                                "log in with Account... first.")
        return body

    def topic(self, url, max_posts=400, replies=True, on_progress=None):
        tid, slug = topic_id(url)
        j = self.get_json(f"/t/{tid}.json")
        ps = j.get("post_stream") or {}
        posts = {p["id"]: p for p in ps.get("posts") or [] if "id" in p}
        stream = ps.get("stream") or list(posts)
        t = Topic()
        t.id = tid
        t.slug = j.get("slug") or slug or "topic"
        t.title = html.unescape(j.get("title") or j.get("fancy_title") or f"Topic {tid}")
        t.url = f"{self.site}/t/{t.slug}/{tid}"
        t.posts_count = j.get("posts_count") or len(stream)
        tags = j.get("tags") or []
        t.tags = [x.get("name") if isinstance(x, dict) else str(x) for x in tags]
        t.author = (((j.get("details") or {}).get("created_by") or {}).get("username") or "")
        if replies:
            want = [pid for pid in stream[:max_posts] if pid not in posts]
            t.truncated = len(stream) > max_posts
            for i in range(0, len(want), 20):
                chunk = want[i:i + 20]
                q = urllib.parse.urlencode([("post_ids[]", pid) for pid in chunk])
                jj = self.get_json(f"/t/{tid}/posts.json?{q}")
                for p in (jj.get("post_stream") or {}).get("posts") or []:
                    if "id" in p:
                        posts[p["id"]] = p
                if on_progress:
                    on_progress(min(len(posts), max_posts), min(len(stream), max_posts))
                time.sleep(0.2)
        order = [posts[pid] for pid in stream if pid in posts] or \
            sorted(posts.values(), key=lambda p: p.get("post_number") or 0)
        if not replies:
            order = [p for p in order if p.get("post_number") == 1] or order[:1]
        if not t.author and order:
            t.author = order[0].get("username") or ""
        t.scanned = len(order)
        for p in order:
            parse_post(t, p, self.site, self.host)
        return t


# Link checking


class RemoteFile:
    def __init__(self, name, size=None, status=ONLINE, note="", dl=None, duration=None, url=""):
        self.name = name or "?"
        self.size = size if isinstance(size, int) or size is None else int(size)
        self.status = status
        self.note = note
        self.dl = dl
        self.duration = duration
        self.url = url
        self.media = ""
        self.probe = None
        self.deco = False

    @property
    def downloadable(self):
        return self.status == ONLINE and self.dl is not None

    @property
    def is_script(self):
        return self.name.lower().endswith(SCRIPT_EXT)


def _mvhd_seconds(buf):
    i = buf.find(b"mvhd")
    while i >= 4:
        b = buf[i + 4:i + 40]
        try:
            if b[0] == 1:
                ts, dur = struct.unpack(">IQ", b[20:32])
            else:
                ts, dur = struct.unpack(">II", b[12:20])
        except (struct.error, IndexError):
            return None
        if ts and 0 < dur / ts < 24 * 3600:
            return dur / ts
        i = buf.find(b"mvhd", i + 4)
    return None


def media_duration(http_, url, headers=None):
    ext = ext_of(urllib.parse.urlsplit(url).path)
    if ext and ext not in (".mp4", ".m4v", ".mov", ""):
        return None
    h = dict(headers or {})
    try:
        r = http_.open(url, headers=dict(h, Range="bytes=0-1048575"), timeout=20)
        with r:
            if "text/html" in (r.headers.get("Content-Type") or "").lower():
                return None
            head = r.read(1_048_576)
            total = None
            m = re.search(r"/(\d+)\s*$", r.headers.get("Content-Range") or "")
            if m:
                total = int(m.group(1))
        if head[4:8] not in (b"ftyp", b"moov", b"free", b"wide", b"mdat"):
            return None
        d = _mvhd_seconds(head)
        if d is not None or not total or total <= len(head):
            return d
        r = http_.open(url, headers=dict(h, Range=f"bytes={max(0, total - 4_194_304)}-"), timeout=25)
        with r:
            return _mvhd_seconds(r.read(4_194_304))
    except Exception:
        return None


class LinkResult:
    def __init__(self, ref, kind="web", host="", status=CHECKING, note=""):
        self.ref = ref
        self.kind = kind
        self.host = host or host_of(ref.url)
        self.status = status
        self.note = note
        self.files = []
        self.other_files = 0
        self.hints = []

    def video_files(self):
        vids = [f for f in self.files if not f.is_script]
        if len(vids) > 1:
            keep = [f for f in vids if is_videoish(f.name)]
            self.other_files = len(vids) - len(keep)
            vids = keep
        return vids

    def script_only(self):
        return bool(self.files) and all(f.is_script for f in self.files)

    def eff_status(self):
        vids = self.video_files()
        if vids:
            return min((f.status for f in vids), key=STATUS_RANK.get)
        return self.status


def res_sort_key(res):
    return (STATUS_RANK.get(res.eff_status(), 9), 0 if res.ref.by_op else 1,
            HOST_PREF.get(res.kind, 10), res.ref.post)


# Pixeldrain

PD_RE = re.compile(r"/(?:api/)?(u|l|file|list)/([A-Za-z0-9]+)")


def _pd_file(info):
    fid = info.get("id") or ""
    name = info.get("name") or fid
    rf = RemoteFile(name, info.get("size"), ONLINE, url=f"https://pixeldrain.com/u/{fid}",
                    dl=dl_http(f"https://pixeldrain.com/api/file/{fid}?download", name_hint=name))
    rf.probe = (f"https://pixeldrain.com/api/file/{fid}", None)
    av = (info.get("availability") or "").lower()
    if "captcha" in av or info.get("can_download") is False:
        rf.status, rf.dl = BROWSER, None
        rf.note = "Pixeldrain wants a captcha for this one - open it in the browser"
    elif av:
        rf.note = av.replace("_", " ")
    return rf


def _pd_fs_list(core, path, depth=0, limit=300):
    q = urllib.parse.quote(path.lstrip("/"))
    j = core.http.json(f"https://pixeldrain.com/api/filesystem/{q}?stat")
    nodes = j.get("path") or []
    base = j.get("base_index") or 0
    me = nodes[base] if 0 <= base < len(nodes) else (nodes[-1] if nodes else {})
    if me.get("type") == "file":
        return [me], me
    out = []
    for c in j.get("children") or []:
        if len(out) >= limit or (c.get("name") or "").startswith("."):
            continue
        if c.get("type") == "file":
            out.append(c)
        elif c.get("type") == "dir" and depth < 3:
            try:
                out += _pd_fs_list(core, c.get("path") or "", depth + 1, limit - len(out))[0]
            except Exception:
                continue
    return out, me


def h_pixeldrain_fs(core, res, path):
    try:
        files, top = _pd_fs_list(core, path)
    except HttpError as e:
        if e.code in (404, 410):
            res.status, res.note = DEAD, "deleted on Pixeldrain"
            return
        raise
    root = (top.get("path") or "") if top.get("type") == "dir" else os.path.dirname(top.get("path") or "")
    res.note = top.get("name") or ""
    if top.get("name"):
        res.hints.append(top["name"])
    if top.get("type") == "file":
        res.note = ""
    for f in files:
        fp = f.get("path") or ""
        name = f.get("name") or os.path.basename(fp) or "file"
        rel = fp[len(root):].lstrip("/") if top.get("type") == "dir" and root and fp.startswith(root + "/") \
            else name
        url = f"https://pixeldrain.com/api/filesystem/{urllib.parse.quote(fp.lstrip('/'))}?attach"
        rf = RemoteFile(rel or name, _int(f.get("file_size")), ONLINE, url=res.ref.url,
                        dl=dl_http(url, name_hint=name))
        rf.probe = (url, None)
        res.files.append(rf)
    if not res.files:
        res.status, res.note = DEAD, "the Pixeldrain folder is empty"


def h_pixeldrain(core, res):
    fs = re.match(r"/(?:d|api/filesystem)/(.+)", urllib.parse.unquote(urllib.parse.urlsplit(res.ref.url).path))
    if fs:
        h_pixeldrain_fs(core, res, "/" + fs.group(1).strip("/"))
        return
    m = PD_RE.search(urllib.parse.urlsplit(res.ref.url).path)
    if not m:
        res.status, res.note = PAGE, "not a Pixeldrain file link"
        return
    kind, pid = m.groups()
    api = "https://pixeldrain.com/api"
    if kind in ("l", "list"):
        j = core.http.json(f"{api}/list/{pid}")
        res.files = [_pd_file(f) for f in j.get("files") or []]
        res.note = j.get("title") or ""
        if not res.files:
            res.status, res.note = DEAD, "the list is empty"
    else:
        res.files = [_pd_file(core.http.json(f"{api}/file/{pid}/info"))]


# Mega

def _aes():
    for mod in ("Crypto.Cipher.AES", "Cryptodome.Cipher.AES"):
        try:
            return importlib.import_module(mod)
        except ImportError:
            continue
    return None


def _b64url(s):
    s = s.strip().replace("-", "+").replace("_", "/").replace(",", "")
    return base64.b64decode(s + "=" * (-len(s) % 4))


def _a32(b):
    return struct.unpack(">%dI" % (len(b) // 4), b[:len(b) // 4 * 4])


def _a32_bytes(a):
    return struct.pack(">%dI" % len(a), *a)


def mega_file_key(keyb):
    k = _a32(keyb)
    if len(k) < 8:
        raise ValueError("bad Mega key")
    aes_key = _a32_bytes((k[0] ^ k[4], k[1] ^ k[5], k[2] ^ k[6], k[3] ^ k[7]))
    return aes_key, _a32_bytes((k[4], k[5]))


def mega_attr(AES, at, key):
    try:
        data = _b64url(at)
        data += b"\0" * (-len(data) % 16)
        dec = AES.new(key, AES.MODE_CBC, iv=b"\0" * 16).decrypt(data)
        if not dec.startswith(b"MEGA"):
            return None
        raw = dec[4:].rstrip(b"\0")
        raw = raw[:raw.rfind(b"}") + 1]
        return json.loads(raw.decode("utf-8", "replace")).get("n")
    except Exception:
        return None


def parse_mega(url):
    u = url.replace("mega.co.nz", "mega.nz")
    m = re.search(r"mega\.nz/(?:file|embed)/([\w-]+)(?:#([\w-]+))?", u)
    if m:
        return "file", m.group(1), m.group(2) or "", None
    m = re.search(r"mega\.nz/(?:embed)?#!([\w-]+)(?:!([\w-]+))?", u)
    if m:
        return "file", m.group(1), m.group(2) or "", None
    m = re.search(r"mega\.nz/folder/([\w-]+)(?:#([\w-]+))?(?:/(?:file|folder)/([\w-]+))?", u)
    if m:
        return "folder", m.group(1), m.group(2) or "", m.group(3)
    m = re.search(r"mega\.nz/#F!([\w-]+)(?:!([\w-]+))?(?:!([\w-]+))?", u)
    if m:
        return "folder", m.group(1), m.group(2) or "", m.group(3)
    return None


MEGA_ERR = {-2: "invalid link", -3: "Mega is busy, try again", -4: "too many requests",
            -6: "too many requests", -9: "deleted / not found", -11: "access denied",
            -14: "wrong decryption key", -16: "taken down", -17: "over quota",
            -18: "temporarily unavailable"}
MEGA_DEAD = {-2, -9, -11, -16}


class MegaError(Exception):
    def __init__(self, code):
        super().__init__(f"Mega: {MEGA_ERR.get(code, code)}")
        self.code = code


def mega_api(http_, cmd, node=None):
    url = f"https://g.api.mega.co.nz/cs?id={random.randint(1, 2 ** 31)}" + \
        (f"&n={node}" if node else "")
    delay = 1.0
    for attempt in range(5):
        resp = http_.json(url, data=json.dumps([cmd]), timeout=30,
                          headers={"Content-Type": "application/json"})
        r = resp[0] if isinstance(resp, list) and resp else resp
        if isinstance(r, int):
            if r in (-3, -4, -6) and attempt < 4:
                time.sleep(delay)
                delay *= 2
                continue
            raise MegaError(r)
        if isinstance(r, dict) and isinstance(r.get("e"), int) and r["e"] < 0 and \
                not (r.get("g") or r.get("at") or r.get("f")):
            raise MegaError(r["e"])
        return r
    raise MegaError(-3)


def dl_mega(cmd, node, key, nonce, size, name=None):
    def dl(core, folder, base, progress, cancel):
        AES = _aes()
        if AES is None:
            raise DownloadError("Install the extras (pycryptodome) to download from Mega - "
                                "press Extras... in the window.")
        r = mega_api(core.http, cmd, node)
        g = r.get("g")
        if isinstance(g, list):
            g = g[0] if g else None
        if not g:
            raise DownloadError("Mega didn't hand out a download link.")
        fname = name or mega_attr(AES, r.get("at", ""), key) or "video.mp4"
        total = r.get("s") or size
        part = Path(folder) / f".{base[:60]}.mega.part"
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce, initial_value=0)
        try:
            resp = core.http.open(g, timeout=60)
        except HttpError as e:
            if e.code == 509:
                raise DownloadError("Mega's free download allowance (transfer quota) is used up "
                                    "for now. Try again in a few hours, or open the link in your "
                                    "browser.") from None
            raise DownloadError(f"Mega: {e}") from None
        done, carry = 0, b""
        try:
            with resp, open(part, "wb") as fo:
                while True:
                    if cancel.is_set():
                        raise Cancelled()
                    buf = resp.read(1 << 20)
                    if not buf:
                        break
                    done += len(buf)
                    buf = carry + buf
                    cut = len(buf) - len(buf) % 16
                    fo.write(cipher.decrypt(buf[:cut]))
                    carry = buf[cut:]
                    progress(done, total)
                if carry:
                    fo.write(cipher.decrypt(carry))
            if total and done != total:
                raise DownloadError(f"Mega download stopped early ({fmt_size(done)} of "
                                    f"{fmt_size(total)}) - press Retry")
        except BaseException:
            try:
                part.unlink()
            except OSError:
                pass
            raise
        ext = ext_of(fname)
        if ext not in VIDEO_EXTS | ARCHIVE_EXTS | {SCRIPT_EXT}:
            ext = ".mp4"
        target = unique_path(Path(folder) / (base + ext))
        os.replace(part, target)
        return target
    return dl


def h_mega(core, res):
    p = parse_mega(res.ref.url)
    if p is None:
        res.status, res.note = PAGE, "not a Mega file or folder link"
        return
    kind, handle, key, sub = p
    AES = _aes()
    try:
        if kind == "file":
            _mega_file(core, res, handle, key, AES)
        else:
            _mega_folder(core, res, handle, key, sub, AES)
    except MegaError as e:
        res.status = DEAD if e.code in MEGA_DEAD else UNKNOWN
        res.note = str(e)


def _mega_file(core, res, h, key, AES):
    r = mega_api(core.http, {"a": "g", "p": h})
    size = r.get("s")
    url = res.ref.url
    if not key:
        res.files = [RemoteFile(f"Mega file ({h})", size, BROWSER, url=url,
                                note="the link has no key (the part after #) - look for it in the post")]
        return
    if AES is None:
        res.files = [RemoteFile(f"Mega file ({h})", size, BROWSER, url=url,
                                note="install the extras (pycryptodome) to download Mega links here")]
        return
    try:
        k, nonce = mega_file_key(_b64url(key))
    except Exception:
        res.files = [RemoteFile(f"Mega file ({h})", size, BROWSER, url=url,
                                note="the key in this link looks broken")]
        return
    name = mega_attr(AES, r.get("at", ""), k)
    if not name:
        res.files = [RemoteFile(f"Mega file ({h})", size, BROWSER, url=url,
                                note="the key in this link doesn't fit (typo?)")]
        return
    res.files = [RemoteFile(name, size, ONLINE, url=url,
                            dl=dl_mega({"a": "g", "g": 1, "ssl": 2, "p": h}, None, k, nonce, size))]


def _mega_folder(core, res, h, key, sub, AES):
    r = mega_api(core.http, {"a": "f", "c": 1, "r": 1, "ca": 1}, node=h)
    nodes = r.get("f") or []
    files = [n for n in nodes if n.get("t") == 0]
    url = res.ref.url
    if AES is None or not key:
        res.status = BROWSER
        res.note = (f"Mega folder: {len(files)} file(s), {fmt_size(sum(n.get('s') or 0 for n in files))} - "
                    + ("install the extras (pycryptodome) to download it here" if key else
                       "the link has no key (the part after #)"))
        return
    try:
        master = _b64url(key)[:16]
        ecb = AES.new(master, AES.MODE_ECB)
    except Exception:
        res.status, res.note = BROWSER, "the key in this Mega link looks broken"
        return
    parents, names, keys = {}, {}, {}
    for n in nodes:
        nh = n.get("h")
        parents[nh] = n.get("p")
        enc = None
        for part in str(n.get("k") or "").split("/"):
            if ":" in part:
                enc = part.split(":", 1)[1]
                break
        if not enc:
            continue
        try:
            kb = _b64url(enc)
            dk = ecb.decrypt(kb[:len(kb) // 16 * 16])
        except Exception:
            continue
        if n.get("t") == 0 and len(dk) >= 32:
            fk, nonce = mega_file_key(dk[:32])
            keys[nh] = (fk, nonce)
            names[nh] = mega_attr(AES, n.get("a", ""), fk)
        elif n.get("t") == 1 and len(dk) >= 16:
            names[nh] = mega_attr(AES, n.get("a", ""), dk[:16])
    roots = {n.get("h") for n in nodes if n.get("p") not in parents}

    def under(nh, top):
        seen = 0
        while nh and seen < 64:
            if nh == top:
                return True
            nh = parents.get(nh)
            seen += 1
        return False

    def rel(nh):
        parts, cur, seen = [], nh, 0
        while cur and cur not in roots and seen < 64:
            parts.append(names.get(cur) or "?")
            cur = parents.get(cur)
            seen += 1
        return "/".join(reversed(parts)) or (names.get(nh) or "?")

    sel = [n for n in files if not sub or under(n.get("h"), sub)]
    out = []
    for n in sel:
        nh = n.get("h")
        nm = names.get(nh)
        if nh not in keys or not nm:
            continue
        fk, nonce = keys[nh]
        out.append(RemoteFile(rel(nh), n.get("s"), ONLINE, url=url,
                              dl=dl_mega({"a": "g", "g": 1, "ssl": 2, "n": nh}, h, fk, nonce,
                                         n.get("s"), name=nm)))
    res.files = out
    if not out:
        res.status = UNKNOWN if files else DEAD
        res.note = "couldn't read the Mega folder (wrong key?)" if files else "the folder is empty"


# Google Drive

GD_FILE_RES = [re.compile(r"/file/d/([\w-]{10,})"), re.compile(r"[?&]id=([\w-]{10,})")]
GD_FOLDER_RE = re.compile(r"/folders/([\w-]{10,})")


def _gd_id(url):
    for rx in GD_FILE_RES:
        m = rx.search(url)
        if m:
            return m.group(1)
    return None


def gd_lookup(http_, fid):
    u = f"https://drive.google.com/uc?export=download&id={fid}"
    out = {"status": UNKNOWN, "name": None, "size": None, "url": None, "note": ""}
    try:
        r = http_.open(u, timeout=30)
    except HttpError as e:
        if e.code in (404, 410):
            out.update(status=DEAD, note="deleted on Google Drive")
            return out
        if e.code in (401, 403):
            out.update(status=BROWSER, note="private - needs a Google sign-in or access")
            return out
        raise
    with r:
        final = r.geturl()
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "accounts.google.com" in final:
            out.update(status=BROWSER, note="private - needs a Google sign-in or access")
            return out
        if "text/html" not in ctype:
            length = r.headers.get("Content-Length") or ""
            out.update(status=ONLINE, url=u, name=cd_filename(r.headers.get("Content-Disposition") or ""),
                       size=int(length) if length.isdigit() else None)
            return out
        body = _decode(r.read(800_000), r.headers)
    m = re.search(r'<form[^>]*id="download-form"[^>]*>', body)
    if m:
        form = m.group(0)
        end = body.find("</form>", m.end())
        inner = body[m.end():end if end > 0 else None]
        am = re.search(r'action="([^"]+)"', form)
        params = []
        for tag in re.findall(r"<input[^>]*>", inner):
            if 'type="hidden"' not in tag:
                continue
            n = re.search(r'name="([^"]*)"', tag)
            v = re.search(r'value="([^"]*)"', tag)
            if n:
                params.append((n.group(1), html.unescape(v.group(1) if v else "")))
        if am:
            action = html.unescape(am.group(1))
            dl = action + ("&" if "?" in action else "?") + urllib.parse.urlencode(params)
            nm = re.search(r'class="uc-name-size"><a[^>]*>([^<]+)</a>\s*\(([^)]+)\)', body)
            out.update(status=ONLINE, url=dl,
                       name=html.unescape(nm.group(1)) if nm else None,
                       size=parse_size(nm.group(2)) if nm else None)
            return out
    low = body.lower()
    if "too many users" in low or ("quota" in low and "exceed" in low):
        out.update(status=BROWSER, note="Google's download limit for this file is used up today - "
                                        "try later")
    elif "does not exist" in low or "not found" in low or "file is in the owner's trash" in low:
        out.update(status=DEAD, note="deleted on Google Drive")
    elif "accounts.google.com" in low:
        out.update(status=BROWSER, note="private - needs a Google sign-in or access")
    else:
        out.update(note="Google Drive answered with a page this program doesn't understand")
    return out


def _gd_resolver(fid):
    def resolve(core):
        info = gd_lookup(core.http, fid)
        if info["status"] != ONLINE:
            raise DownloadError(f"Google Drive: {info['note'] or 'not available'}")
        return info["url"], None
    return resolve


def h_gdrive(core, res):
    url = res.ref.url
    fm = GD_FOLDER_RE.search(url)
    if fm or "folderview" in url:
        fid = fm.group(1) if fm else _gd_id(url)
        if fid:
            _gd_folder(core, res, fid)
            return
    fid = _gd_id(url)
    if not fid:
        res.status, res.note = PAGE, "a Google link that isn't a file"
        return
    info = gd_lookup(core.http, fid)
    rf = RemoteFile(info["name"] or f"Google Drive file ({fid})", info["size"], info["status"],
                    note=info["note"], url=url)
    if info["status"] == ONLINE:
        rf.dl = dl_http(resolve=_gd_resolver(fid), name_hint=info["name"])
    res.files = [rf]


def _gd_folder(core, res, fid):
    try:
        body, final, _ = core.http.text(f"https://drive.google.com/embeddedfolderview?id={fid}")
    except HttpError as e:
        if e.code in (404, 410):
            res.status, res.note = DEAD, "folder deleted on Google Drive"
            return
        raise
    if "accounts.google.com" in final:
        res.status, res.note = BROWSER, "private folder - needs a Google sign-in"
        return
    ids = [(m.start(), m.group(1)) for m in re.finditer(r'id="entry-([\w-]+)"', body)]
    out, subfolders = [], 0
    for n, (pos, eid) in enumerate(ids):
        seg = body[pos:ids[n + 1][0] if n + 1 < len(ids) else None]
        tm = re.search(r'class="flip-entry-title">([^<]*)<', seg)
        title = html.unescape(tm.group(1)).strip() if tm else eid
        if "/folders/" in seg:
            subfolders += 1
            continue
        if not (is_videoish(title) or title.lower().endswith(SCRIPT_EXT)):
            continue
        out.append(RemoteFile(title, None, ONLINE, url=f"https://drive.google.com/file/d/{eid}/view",
                              note="in a shared folder",
                              dl=dl_http(resolve=_gd_resolver(eid), name_hint=title)))
    res.files = out
    if subfolders:
        res.note = f"+{subfolders} subfolder(s) - open the link to see those"
    if not out:
        res.status = BROWSER if (ids or subfolders) else UNKNOWN
        res.note = res.note or "no video files listed - open the folder in your browser"


# Dropbox / MediaFire / Gofile / KrakenFiles / BuzzHeavier

def h_dropbox(core, res):
    url = res.ref.url
    s = urllib.parse.urlsplit(url)
    if "dropboxusercontent.com" in (s.hostname or ""):
        h_direct(core, res)
        return
    q = [(k, v) for k, v in urllib.parse.parse_qsl(s.query) if k not in ("dl", "raw")] + [("dl", "1")]
    u = urllib.parse.urlunsplit((s.scheme, s.netloc, s.path, urllib.parse.urlencode(q), ""))
    folder = "/scl/fo/" in s.path or "/sh/" in s.path
    info = core.http.probe(u)
    if "text/html" in info["ctype"]:
        body = info.get("body") or ""
        if re.search(r"(deleted|doesn.t exist|not found|no longer|isn.t available)", body, re.I):
            res.status, res.note = DEAD, "deleted on Dropbox"
        else:
            res.status, res.note = BROWSER, "Dropbox wouldn't hand out the file - open it in the browser"
        return
    name = info["name"] or urllib.parse.unquote(os.path.basename(s.path))
    res.files = [RemoteFile(name, info["size"], ONLINE, url=url,
                            note="a folder - downloads as a .zip" if folder else "",
                            dl=dl_http(u, name_hint=name))]


def _mf_lookup(http_, url):
    body, final, _ = http_.text(url)
    if "error.php" in final or re.search(
            r"(file (has been )?removed|invalid or deleted file|key you provided for file download "
            r"was invalid|file belongs to a user)", body, re.I):
        return DEAD, None, None, None
    m = re.search(r'href="(https?://download\d*\.mediafire\.com/[^"]+)"', body)
    link = html.unescape(m.group(1)) if m else None
    if not link:
        m = re.search(r'data-scrambled-url="([^"]+)"', body)
        if m:
            try:
                link = base64.b64decode(m.group(1)).decode("utf-8")
            except Exception:
                link = None
    nm = re.search(r'<div class="dl-btn-label"[^>]*title="([^"]+)"', body) or \
        re.search(r'<div class="filename">([^<]+)<', body)
    name = html.unescape(nm.group(1)).strip() if nm else \
        urllib.parse.unquote(os.path.basename(urllib.parse.urlsplit(link or url).path.rstrip("/file")))
    sm = re.search(r"Download\s*\(\s*([\d.,]+\s*[KMGT]?B)\s*\)", body, re.I)
    return (ONLINE if link else BROWSER), name, parse_size(sm.group(1)) if sm else None, link


def h_mediafire(core, res):
    url = res.ref.url
    if "/folder/" in url:
        res.status, res.note = BROWSER, "MediaFire folder - open it in the browser"
        return
    status, name, size, link = _mf_lookup(core.http, url)
    if status == DEAD:
        res.status, res.note = DEAD, "deleted on MediaFire"
        return

    def resolve(core_):
        st, _, _, lk = _mf_lookup(core_.http, url)
        if not lk:
            raise DownloadError("MediaFire didn't show a download button - open it in the browser.")
        return lk, {"Referer": url}
    res.files = [RemoteFile(name, size, status, url=url,
                            note="" if link else "page is up, but no download button found",
                            dl=dl_http(resolve=resolve, name_hint=name) if link else None)]


_GOFILE = {"token": None, "wt": None}
_GOFILE_LOCK = threading.Lock()


def _gofile_auth(http_):
    with _GOFILE_LOCK:
        if not _GOFILE["token"]:
            j = http_.json("https://api.gofile.io/accounts", data="{}",
                           headers={"Content-Type": "application/json"})
            _GOFILE["token"] = (j.get("data") or {}).get("token")
        if not _GOFILE["wt"]:
            wt = None
            for js in ("https://gofile.io/dist/js/global.js", "https://gofile.io/dist/js/config.js",
                       "https://gofile.io/dist/js/alljs.js"):
                try:
                    txt, _, _ = http_.text(js)
                except Exception:
                    continue
                m = re.search(r'\bwt\s*[:=]\s*["\']([A-Za-z0-9]{6,})["\']', txt) or \
                    re.search(r'websiteToken\s*[:=]\s*["\']([A-Za-z0-9]{6,})["\']', txt)
                if m:
                    wt = m.group(1)
                    break
            _GOFILE["wt"] = wt or "4fd6sg89d7s6"
        return _GOFILE["token"], _GOFILE["wt"]


def h_gofile(core, res):
    url = res.ref.url
    m = re.search(r"/d/([\w-]+)", url)
    if not m:
        res.status, res.note = PAGE, "not a Gofile download link"
        return
    try:
        token, wt = _gofile_auth(core.http)
    except Exception as e:
        res.status, res.note = BROWSER, f"Gofile wouldn't talk to this program ({e}) - open it in the browser"
        return
    if not token:
        res.status, res.note = BROWSER, "Gofile wouldn't give a guest pass - open it in the browser"
        return
    set_cookie(core.http.jar, ".gofile.io", "accountToken", token)
    try:
        j = core.http.json(f"https://api.gofile.io/contents/{m.group(1)}?wt={wt}&cache=true",
                           headers={"Authorization": f"Bearer {token}", "X-Website-Token": wt})
    except HttpError as e:
        try:
            j = json.loads(e.text())
        except ValueError:
            raise e from None
    st = str(j.get("status") or "")
    if st == "ok":
        data = j.get("data") or {}
        kids = data.get("children") or data.get("contents") or {}
        if data.get("type") == "file":
            kids = {"x": data}
        for c in kids.values():
            if c.get("type") != "file":
                continue
            link = c.get("link") or c.get("directLink")
            name = c.get("name") or "file"
            res.files.append(RemoteFile(name, c.get("size"), ONLINE if link else BROWSER, url=url,
                                        dl=dl_http(link, name_hint=name) if link else None))
        if not res.files:
            res.status, res.note = DEAD, "the Gofile folder is empty"
    elif "notfound" in st.lower():
        res.status, res.note = DEAD, "deleted on Gofile"
    elif "password" in st.lower():
        res.status, res.note = BROWSER, "password protected - open it in the browser"
    else:
        res.status, res.note = BROWSER, f"Gofile wouldn't list it here ({st or 'no answer'}) - open it in the browser"


def h_kraken(core, res):
    url = res.ref.url
    body, final, _ = core.http.text(url)
    if DEAD_RE.search(_title(body) + " " + _strip_tags(body)[:20000]):
        res.status, res.note = DEAD, "deleted on KrakenFiles"
        return
    name = _og(body, "title") or _title(body).replace(" - KrakenFiles.com", "") or "KrakenFiles file"
    sm = re.search(r"File size</div>\s*<div[^>]*>\s*([\d.,]+\s*[KMGT]?B)", body, re.I)

    def resolve(core_):
        b, fin, _ = core_.http.text(url)
        fm = re.search(r'<form[^>]*id="dl-form"[^>]*action="([^"]+)"', b)
        tk = re.search(r'name="token"[^>]*value="([^"]+)"', b) or \
            re.search(r'value="([^"]+)"[^>]*name="token"', b)
        if not (fm and tk):
            raise DownloadError("KrakenFiles changed its page - open the link in your browser.")
        j = core_.http.json(urllib.parse.urljoin(fin, html.unescape(fm.group(1))),
                            data={"token": tk.group(1)},
                            headers={"Referer": fin, "X-Requested-With": "XMLHttpRequest"})
        link = j.get("url")
        if not link:
            raise DownloadError("KrakenFiles didn't give a download link - open it in your browser.")
        return link, {"Referer": fin}
    ok = 'id="dl-form"' in body
    res.files = [RemoteFile(name, parse_size(sm.group(1)) if sm else None, ONLINE if ok else BROWSER,
                            url=url, note="" if ok else "open it in the browser",
                            dl=dl_http(resolve=resolve, name_hint=name) if ok else None)]


def h_buzz(core, res):
    url = res.ref.url.split("#")[0].rstrip("/")
    body, final, _ = core.http.text(url)
    if DEAD_RE.search(_title(body)):
        res.status, res.note = DEAD, "deleted on BuzzHeavier"
        return
    name = _og(body, "title") or _title(body) or "BuzzHeavier file"

    def resolve(core_):
        r = core_.http.open(url + "/download", timeout=30,
                            headers={"HX-Request": "true", "HX-Current-URL": url, "Referer": url})
        with r:
            loc = r.headers.get("HX-Redirect") or r.headers.get("hx-redirect")
            if not loc and "text/html" not in (r.headers.get("Content-Type") or "").lower():
                loc = r.geturl()
        if not loc:
            raise DownloadError("BuzzHeavier didn't give a download link - open it in your browser.")
        return urllib.parse.urljoin(url, loc), {"Referer": url}
    res.files = [RemoteFile(name, None, ONLINE, url=url, dl=dl_http(resolve=resolve, name_hint=name))]


# Direct links / yt-dlp / web pages

def h_direct(core, res, note=""):
    url = res.ref.url
    info = core.http.probe(url)
    if "text/html" in info["ctype"]:
        body = info.get("body") or ""
        if DEAD_RE.search(_title(body)):
            res.status, res.note = DEAD, "the page says the file is gone"
        else:
            _generic_page(core, res)
        return
    name = info["name"] or urllib.parse.unquote(os.path.basename(urllib.parse.urlsplit(info["url"]).path)) \
        or "video"
    res.files = [RemoteFile(name, info["size"], ONLINE, url=url, note=note,
                            dl=dl_http(url, name_hint=name))]
    res.files[0].probe = (url, None)


def h_eroscripts(core, res):
    h_direct(core, res, note="uploaded on EroScripts - often just a short preview")


def h_store(core, res):
    res.status, res.note = STORE, "shop / studio page - the video is sold there"


_YT = {"mod": None, "tried": False, "ies": None}
_YT_LOCK = threading.Lock()


def ytdlp_mod():
    with _YT_LOCK:
        if _YT["mod"] is None and not _YT["tried"]:
            _YT["tried"] = True
            try:
                import yt_dlp
                _YT["mod"] = yt_dlp
            except Exception:
                pass
        return _YT["mod"]


def extras_reset():
    importlib.invalidate_caches()
    with _YT_LOCK:
        _YT.update(mod=None, tried=False, ies=None)


def ytdlp_suitable(url):
    yd = ytdlp_mod()
    if yd is None:
        return False
    with _YT_LOCK:
        if _YT["ies"] is None:
            try:
                from yt_dlp.extractor import gen_extractor_classes
                _YT["ies"] = [ie for ie in gen_extractor_classes()
                              if ie.ie_key() not in ("Generic", "KnownPiracy", "KnownLiability")]
            except Exception:
                _YT["ies"] = []
        ies = _YT["ies"]
    for ie in ies:
        try:
            if ie.suitable(url):
                return True
        except Exception:
            continue
    return False


class _QuietLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def _yt_err(e):
    msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e))
    msg = re.sub(r"^(ERROR:\s*)?(\[[^\]]+\]\s*)?([\w-]+:\s*)?", "", msg.strip())
    return msg.split("\n")[0][:200]


YT_DEAD_RE = re.compile(r"(removed|deleted|not found|404|does not exist|no longer|disabled|"
                        r"private|unavailable|been blocked|terminated|copyright)", re.I)


def dl_ytdlp(url, insecure=False, referer=None):
    def dl(core, folder, base, progress, cancel):
        yd = ytdlp_mod()
        if yd is None:
            raise DownloadError("Install the extras (yt-dlp) first - press Extras... in the window.")
        ff = shutil.which("ffmpeg")

        def hook(d):
            if cancel.is_set():
                raise Cancelled()
            if d.get("status") == "downloading":
                progress(d.get("downloaded_bytes") or 0,
                         d.get("total_bytes") or d.get("total_bytes_estimate"))
        opts = {
            "format": "bv*+ba/b" if ff else "b/bv*",
            "outtmpl": {"default": os.path.join(str(folder), base.replace("%", "%%") + ".%(ext)s")},
            "noplaylist": True, "quiet": True, "no_warnings": True, "noprogress": True,
            "progress_hooks": [hook], "logger": _QuietLogger(), "overwrites": False,
            "continuedl": True, "retries": 5, "fragment_retries": 5,
            "concurrent_fragment_downloads": 4,
        }
        if insecure:
            opts["nocheckcertificate"] = True
        if referer:
            opts["http_headers"] = {"Referer": referer}
        if ff:
            opts["merge_output_format"] = "mp4"
        try:
            with yd.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info.get("_type") in ("playlist", "multi_video"):
                    info = next((x for x in info.get("entries") or [] if x), info)
                paths = [d.get("filepath") for d in info.get("requested_downloads") or []
                         if d.get("filepath")]
                path = paths[0] if paths else ydl.prepare_filename(info)
        except Cancelled:
            raise
        except Exception as e:
            if cancel.is_set():
                raise Cancelled() from None
            raise DownloadError("yt-dlp: " + _yt_err(e)) from None
        if not os.path.exists(path):
            alt = os.path.splitext(path)[0] + ".mp4"
            if os.path.exists(alt):
                path = alt
        return Path(path)
    return dl


def h_ytdlp(core, res):
    res.kind = "ytdlp"
    yd = ytdlp_mod()
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True,
            "socket_timeout": 20, "noprogress": True, "logger": _QuietLogger()}
    insecure = core.http.bad_cert(res.ref.url) and core.http.can_skip_cert(res.ref.url)
    info = None
    for attempt in range(2):
        if insecure:
            opts["nocheckcertificate"] = True
        try:
            with yd.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(res.ref.url, download=False)
            break
        except Exception as e:
            msg = _yt_err(e)
            if not attempt and not insecure and is_cert_error(e) and core.http.can_skip_cert(res.ref.url):
                core.http.insecure_hosts.add(host_of(res.ref.url))
                insecure = True
                continue
            res.status = DEAD if YT_DEAD_RE.search(msg) else UNKNOWN
            res.note = msg
            return
    if info.get("_type") in ("playlist", "multi_video"):
        entries = [x for x in info.get("entries") or [] if x]
        if entries:
            info = entries[0]
    title = info.get("title") or host_of(res.ref.url)
    res.hints.append(title)
    fmts = info.get("requested_formats") or [info]
    size = sum((f.get("filesize") or f.get("filesize_approx") or 0) for f in fmts) or None
    height = info.get("height")
    res.files = [RemoteFile(f"{title}.{info.get('ext') or 'mp4'}", size, ONLINE, url=res.ref.url,
                            note=f"{height}p" if height else "", duration=info.get("duration"),
                            dl=dl_ytdlp(res.ref.url, insecure))]


def h_web(core, res):
    url = res.ref.url
    yt_note = ""
    if ytdlp_suitable(url):
        h_ytdlp(core, res)
        if res.files or res.status == DEAD:
            return
        yt_note = res.note
        res.status, res.note, res.kind = CHECKING, "", "web"
    tube = _match(host_of(url), TUBE_HOSTS)
    try:
        _generic_page(core, res)
    except Exception:
        if not yt_note:
            raise
        res.status = UNKNOWN
    if res.files or res.status == DEAD:
        return
    if yt_note:
        res.kind = "ytdlp"
        res.note = f"yt-dlp: {yt_note}"
    elif tube and not ytdlp_mod():
        res.status, res.note = BROWSER, "install the extras (yt-dlp) to download from this site here"


AD_HOSTS = (
    "doubleclick.net", "googlesyndication.com", "googletagmanager.com", "google-analytics.com",
    "exoclick.com", "exosrv.com", "exdynsrv.com", "juicyads.com", "trafficjunky.net",
    "trafficjunky.com", "adsterra.com", "magsrv.com", "a-ads.com", "realsrv.com", "tsyndicate.com",
    "twinrdsrv.com", "disqus.com", "facebook.com", "recaptcha.net", "hcaptcha.com",
    "challenges.cloudflare.com", "chaturbate.com", "stripchat.com", "livejasmin.com",
)
_MEDIA_EXT = r"(?:mp4|m4v|webm|mov|mkv|m3u8|mpd)"
_MEDIA_IN_TEXT = re.compile(r"https?://[^\s\"'<>()\\\[\]{}]+?\." + _MEDIA_EXT +
                            r"(?:\?[^\s\"'<>()\\\[\]{}]*)?(?=[\s\"'<>()\\,;\]}]|$)", re.I)
_MEDIA_RELATIVE = re.compile(r"[\"'](/[^\"'\s<>]+?\.(?:mp4|m4v|webm|m3u8)(?:\?[^\"'\s<>]*)?)[\"']", re.I)
_PREVIEWISH = re.compile(r"(preview|thumb|teaser|trailer|sample|[_/-]small[_/.-]|blur|sprite|/loop|"
                         r"hover|banner|intro)", re.I)
_QUALITY = {"2160": 8, "1440": 7, "1080": 6, "720": 4, "480": 2, "360": 1, "240": 0}


def _unescape_js(body):
    return (body.replace("\\/", "/").replace("\\u002F", "/").replace("\\u002f", "/")
            .replace("\\u0026", "&").replace("&amp;", "&"))


def _is_stream(u):
    return ext_of(urllib.parse.urlsplit(u).path) in (".m3u8", ".mpd")


def find_media_urls(body, base):
    found = {}

    def add(u, w):
        u = html.unescape((u or "").strip())
        if not u or u.startswith(("blob:", "data:", "javascript:")):
            return
        u = urllib.parse.urljoin(base, u)
        if not u.lower().startswith(("http://", "https://")) or _match(host_of(u), AD_HOSTS):
            return
        if ext_of(urllib.parse.urlsplit(u).path) in IMAGE_EXTS:
            return
        found[u] = max(found.get(u, -99), w)

    for prop in ("og:video:secure_url", "og:video:url", "og:video", "twitter:player:stream"):
        for m in re.finditer(r"<meta[^>]+(?:property|name)=[\"']%s[\"'][^>]*>" % re.escape(prop), body, re.I):
            c = re.search(r"content=[\"']([^\"']+)", m.group(0))
            if c and re.search(r"\." + _MEDIA_EXT + r"(?:$|\?)", urllib.parse.urlsplit(c.group(1)).path + "?", re.I):
                add(c.group(1), 30)
    for m in re.finditer(r"<(?:video|source)\b[^>]*?\bsrc=[\"']([^\"']+)[\"']", body, re.I):
        add(m.group(1), 25)
    for m in re.finditer(r"\"contentUrl\"\s*:\s*\"([^\"]+)\"", body):
        add(m.group(1).replace("\\/", "/"), 20)
    text = _unescape_js(body)
    for m in _MEDIA_IN_TEXT.finditer(text):
        add(m.group(0), 10)
    for m in _MEDIA_RELATIVE.finditer(text):
        add(m.group(1), 8)

    def score(u):
        w = found[u]
        path = urllib.parse.unquote(urllib.parse.urlsplit(u).path)
        if _PREVIEWISH.search(path):
            w -= 25
        q = re.search(r"(2160|1440|1080|720|480|360|240)p?", path)
        if q:
            w += _QUALITY[q.group(1)]
        if re.search(r"(?<![a-z0-9])4k(?![a-z0-9])", path, re.I):
            w += 8
        return w
    return sorted(found, key=score, reverse=True)


def find_embeds(body, base):
    out = []
    pats = [r"<iframe\b[^>]*?\bsrc=[\"']([^\"']+)[\"']",
            r"<meta[^>]+(?:property|name)=[\"'](?:og:video(?::secure_url|:url)?|twitter:player)[\"'][^>]*"
            r"content=[\"']([^\"']+)[\"']"]
    for pat in pats:
        for m in re.finditer(pat, body, re.I):
            u = urllib.parse.urljoin(base, html.unescape(m.group(1).strip()))
            if not u.lower().startswith(("http://", "https://")) or u == base:
                continue
            if _match(host_of(u), AD_HOSTS) or _match(host_of(u), IGNORE_HOSTS) or u in out:
                continue
            if re.search(r"\." + _MEDIA_EXT + r"$", urllib.parse.urlsplit(u).path, re.I):
                continue
            out.append(u)
    return out[:4]


def _media_name(info, u, title):
    name = info.get("name") or urllib.parse.unquote(os.path.basename(urllib.parse.urlsplit(u).path))
    stem, ext = os.path.splitext(name)
    if title and (not stem or re.fullmatch(r"[0-9a-fA-F_-]{8,}|\d+|video|index|file|master", stem, re.I)):
        name = title + (ext or ".mp4")
    return name or "video.mp4"


def decorative_media(body, base):
    out = set()
    for m in re.finditer(r"<video\b([^>]*)>(.*?)</video>", body, re.I | re.S):
        attrs = m.group(1).lower()
        if not all(re.search(r"\b%s\b" % a, attrs) for a in ("autoplay", "loop", "muted")):
            continue
        if re.search(r"\bcontrols\b", attrs):
            continue
        for sm in re.finditer(r"\bsrc=[\"']([^\"']+)[\"']", m.group(0), re.I):
            out.add(urllib.parse.urljoin(base, html.unescape(sm.group(1).strip())))
    return out


def videos_on_page(core, page_url, body, title, referer=None, note="found on the page"):
    referer = referer or page_url
    cands = find_media_urls(body, page_url)
    more = []
    for u in cands:
        m = re.search(r"\.mov(\d{3,4})\.mp4", u)
        if m:
            for alt in (".mov.mp4", ".mov1080.mp4", ".mov720.mp4"):
                v = u[:m.start()] + alt + u[m.end():]
                if v not in cands and v not in more:
                    more.append(v)
    cands = more + cands
    deco = decorative_media(body, page_url)
    direct, streams = [], []
    for u in cands:
        if _is_stream(u):
            streams.append(u)
            continue
        if len(direct) >= 6 or len(direct) + len(streams) >= 10:
            break
        try:
            info = core.http.probe(u, headers={"Referer": referer}, timeout=20)
        except Exception:
            continue
        ct = info["ctype"]
        if "text/html" in ct or ct.startswith(("image/", "text/", "application/json")):
            continue
        if info["size"] is not None and info["size"] < 50_000:
            continue
        direct.append((u, info))
    big = [d for d in direct if (d[1]["size"] or 0) >= 300_000]
    direct = big or direct
    direct.sort(key=lambda d: (1 if d[0] in deco else 0, 1 if _PREVIEWISH.search(d[0]) else 0,
                               -(d[1]["size"] or 0)))
    insecure = core.http.bad_cert(page_url)
    files = []
    for u, info in direct[:5]:
        name = _media_name(info, u, title)
        warn = " - may only be a preview" if _PREVIEWISH.search(u) else ""
        if u in deco:
            warn = " - looks like the site's background / promo clip"
        rf = RemoteFile(name, info["size"], ONLINE, url=page_url, note=note + warn,
                        dl=dl_http(u, headers={"Referer": referer}, name_hint=name))
        rf.media, rf.deco = u, u in deco
        rf.probe = (u, {"Referer": referer})
        files.append(rf)
    if not files and streams:
        s = streams[0]
        name = (title or "video") + ".mp4"
        if ytdlp_mod() is not None:
            files.append(RemoteFile(name, None, ONLINE, url=page_url,
                                    note="streamed video - yt-dlp downloads it",
                                    dl=dl_ytdlp(s, insecure, referer=referer)))
        else:
            files.append(RemoteFile(name, None, BROWSER, url=page_url,
                                    note="the video is streamed - install the extras (yt-dlp) to "
                                         "download it here"))
    return files


def _ytdlp_any_page(core, url, ref):
    if ytdlp_mod() is None:
        return []
    sub = LinkResult(LinkRef(url, ref.text, ref.post, ref.user, ref.by_op), "ytdlp")
    try:
        h_ytdlp(core, sub)
    except Exception:
        return []
    for f in sub.files:
        f.url = ref.url
        f.note = "found by yt-dlp" + (f" - {f.note}" if f.note else "")
    return sub.files


def _from_embed(core, embed, page_url, ref):
    host = host_of(embed)
    sub = LinkResult(LinkRef(embed, "", ref.post, ref.user, ref.by_op))
    try:
        if ytdlp_suitable(embed):
            h_ytdlp(core, sub)
        else:
            kind = classify(embed, "")
            if kind in HANDLERS and kind not in ("web", "store", "eroscripts", "direct"):
                HANDLERS[kind](core, sub)
            else:
                body, final, headers = core.http.text(embed, headers={"Referer": page_url}, limit=2_000_000)
                sub.files = videos_on_page(core, final, body, _title(body), referer=embed,
                                           note=f"from the player embedded from {host}")
    except Exception:
        return []
    files = [f for f in sub.files if f.status == ONLINE]
    for f in files:
        f.url = ref.url
        if "embedded" not in f.note:
            f.note = f"from the player embedded from {host}" + (f" - {f.note}" if f.note else "")
    return files


def _generic_page(core, res, deep=True):
    url = res.ref.url
    try:
        r = core.http.open(url, timeout=25)
    except HttpError as e:
        if e.code in (404, 410):
            res.status, res.note = DEAD, f"page not found ({e.code})"
        elif e.cloudflare() or e.code in (401, 403, 429, 503):
            res.status, res.note = UNKNOWN, f"the site blocked the check (HTTP {e.code}) - open it in the browser"
            if deep:
                res.files = _ytdlp_any_page(core, url, res.ref)
        else:
            res.status, res.note = UNKNOWN, f"the site answered HTTP {e.code}"
        return
    with r:
        final = r.geturl()
        ctype = (r.headers.get("Content-Type") or "").lower()
        if "text/html" not in ctype and not ctype.startswith("text/"):
            name = cd_filename(r.headers.get("Content-Disposition") or "") or \
                urllib.parse.unquote(os.path.basename(urllib.parse.urlsplit(final).path)) or "file"
            length = r.headers.get("Content-Length") or ""
            res.files = [RemoteFile(name, int(length) if length.isdigit() else None, ONLINE, url=url,
                                    dl=dl_http(url, name_hint=name))]
            return
        body = _decode(r.read(2_000_000), r.headers)
    title = _og(body, "title") or _title(body)
    if title:
        res.hints.append(title)
    if deep:
        res.files = videos_on_page(core, final, body, title)
        if res.files:
            return
    m = DEAD_RE.search(_title(body) + " " + _strip_tags(body)[:60000])
    if m:
        res.status, res.note = DEAD, f'the page says "{m.group(0)}"'
        return
    if deep:
        res.files = _ytdlp_any_page(core, url, res.ref)
        if res.files:
            return
        for embed in find_embeds(body, final):
            res.files = _from_embed(core, embed, final, res.ref)
            if res.files:
                return
    res.status = PAGE
    res.note = ((title + " - ") if title else "") + ("couldn't find the video on this page. Open it, "
                                                     "right-click the video > Copy video address, then "
                                                     "press 'Add video link...'")


def h_pmvhaven(core, res):
    url = res.ref.url
    m = re.search(r"_([0-9a-fA-F]{24})(?:[/?#]|$)", url) or re.search(r"/([0-9a-fA-F]{24})(?:[/?#]|$)", url)
    if not m:
        h_web(core, res)
        return
    vid = m.group(1)
    try:
        j = core.http.json(f"https://pmvhaven.com/api/videos/{vid}/watch-page",
                           headers={"Referer": url, "Origin": "https://pmvhaven.com"})
    except HttpError as e:
        if e.code in (404, 410):
            res.status, res.note = DEAD, "deleted on PMVHaven"
            return
        j = None
    except (DownloadError, urllib.error.URLError, socket.timeout, TimeoutError):
        j = None
    v = _find_dict_with(j, "videoUrl")
    if not v:
        h_web(core, res)
        return
    title = str(v.get("title") or "PMVHaven video")
    creator = v.get("creator")
    creator = creator[0] if isinstance(creator, list) and creator else (creator or v.get("uploader") or "")
    if isinstance(creator, dict):
        creator = creator.get("name") or creator.get("username") or ""
    res.hints.append(f"{title} {creator}")
    vurl = v["videoUrl"]
    ext = ext_of(urllib.parse.urlsplit(vurl).path) or ".mp4"
    name = f"{title}{ext if ext in VIDEO_EXTS else '.mp4'}"
    size = _int(v.get("size") or v.get("fileSize") or v.get("filesize"))
    dur = v.get("duration") if isinstance(v.get("duration"), (int, float)) else None
    res.files = [RemoteFile(name, size, ONLINE, url=url, duration=dur,
                            note=f"by {creator}" if creator else "",
                            dl=dl_http(vurl, headers={"Referer": "https://pmvhaven.com/"}, name_hint=name))]


def _find_dict_with(obj, key, depth=0):
    if depth > 8:
        return None
    if isinstance(obj, dict):
        if obj.get(key):
            return obj
        obj = list(obj.values())
    if isinstance(obj, list):
        for x in obj:
            d = _find_dict_with(x, key, depth + 1)
            if d:
                return d
    return None


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def h_viking(core, res):
    url = res.ref.url
    m = re.search(r"/f/([A-Za-z0-9_-]+)", urllib.parse.urlsplit(url).path)
    if not m:
        _generic_page(core, res)
        return
    fid = m.group(1)
    main = f"https://vikingfile.com/f/{fid}"
    try:
        j = core.http.json("https://vikingfile.com/api/check-file", data={"hash": fid})
    except (HttpError, DownloadError, urllib.error.URLError, socket.timeout, TimeoutError):
        _generic_page(core, res)
        return
    info = j[0] if isinstance(j, list) and j else (j if isinstance(j, dict) else {})
    if not info.get("exist"):
        res.status, res.note = DEAD, "deleted on VikingFile"
        return
    name = info.get("name") or f"VikingFile {fid}"
    if has_webview():
        res.files = [RemoteFile(name, _int(info.get("size")), ONLINE, url=url,
                                note="downloads in the program's own window (VikingFile may ask you to "
                                     "tick 'I am human')",
                                dl=dl_window(url, autoclick=True, title="VikingFile"))]
    else:
        res.files = [RemoteFile(name, _int(info.get("size")), BROWSER, url=main,
                                note="VikingFile wants a quick 'are you human' check - install the extras "
                                     "(Extras...) to download it here in the program's own window")]


# Download window

BAD_DOWNLOAD_EXTS = {".exe", ".msi", ".apk", ".dmg", ".bat", ".cmd", ".scr", ".com", ".js", ".vbs",
                     ".jar", ".ps1", ".lnk", ".iso", ".pkg", ".deb", ".app"}
_WINDOW_LOCK = threading.Lock()


def has_webview():
    try:
        import importlib.util
        return importlib.util.find_spec("webview") is not None
    except Exception:
        return False


def _self_cmd():
    if getattr(sys, "frozen", False):
        return [sys.executable]
    exe = sys.executable
    if os.name == "nt":
        d, n = os.path.split(exe)
        if n.lower() == "python.exe" and os.path.exists(os.path.join(d, "pythonw.exe")):
            exe = os.path.join(d, "pythonw.exe")
    return [exe, os.path.abspath(__file__)]


def _read_events(path, pos):
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.seek(pos)
            data = f.read()
    except OSError:
        return [], pos
    cut = data.rfind("\n") + 1
    out = []
    for line in data[:cut].splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out, pos + len(data[:cut].encode("utf-8"))


def dl_window(url, autoclick=False, title=""):
    def dl(core, folder, base, progress, cancel):
        if not has_webview():
            raise DownloadError("This one needs the download window - press Extras... > Install, then Retry.")
        stage = getattr(progress, "stage", lambda text: None)
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        if not _WINDOW_LOCK.acquire(blocking=False):
            stage("waiting for the other download window to close")
            while not _WINDOW_LOCK.acquire(timeout=0.5):
                if cancel.is_set():
                    raise Cancelled()
        try:
            got = _run_window(core, url, folder, base, progress, cancel, stage, autoclick, title)
        finally:
            _WINDOW_LOCK.release()
        if isinstance(got, Path):
            return got
        sniff = got
        stage("downloading the video the window found")
        hdrs = {k: v for k, v in (sniff.get("headers") or {}).items()
                if k.lower() in ("referer", "cookie", "user-agent", "origin")}
        if not any(k.lower() == "referer" for k in hdrs):
            hdrs["Referer"] = sniff.get("page") or url
        if sniff.get("stream"):
            ref = next((v for k, v in hdrs.items() if k.lower() == "referer"), url)
            return dl_ytdlp(sniff["url"], core.http.can_skip_cert(url), referer=ref)(
                core, folder, base, progress, cancel)
        return http_download(core.http, sniff["url"], folder, base, progress, cancel, headers=hdrs)
    return dl


def _run_window(core, url, folder, base, progress, cancel, stage, autoclick, title):
    status = folder / f".{base[:40]}.window.jsonl"
    log = folder / f".{base[:40]}.window.log"
    for f in (status, log):
        try:
            f.unlink()
        except OSError:
            pass
    cmd = _self_cmd() + ["--grab", url, "--out", str(folder), "--base", base, "--status", str(status),
                         "--title", title or host_of(url)]
    if autoclick:
        cmd.append("--autoclick")
    if core.http.can_skip_cert(url):
        cmd.append("--insecure")
    if os.environ.get("ESD_GRAB_TIMEOUT"):
        cmd += ["--grab-timeout", os.environ["ESD_GRAB_TIMEOUT"]]
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    stage("waiting for you in the download window")
    with open(log, "w", encoding="utf-8", errors="replace") as logf:
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=logf, stderr=logf, **kw)
    pos, result, error = 0, None, None
    try:
        while True:
            if cancel.is_set():
                raise Cancelled()
            evs, pos = _read_events(status, pos)
            for ev in evs:
                kind = ev.get("event")
                if kind == "started":
                    stage(f"downloading in the window: {ev.get('name') or 'file'}")
                    progress(0, ev.get("total"))
                elif kind == "progress":
                    progress(ev.get("done") or 0, ev.get("total"))
                elif kind == "done":
                    result = Path(ev["path"])
                elif kind == "sniffed":
                    result = ev
                elif kind == "error":
                    error = ev.get("msg")
                elif kind == "note":
                    stage(ev.get("msg") or "")
            if result is not None:
                break
            if proc.poll() is not None:
                evs, pos = _read_events(status, pos)
                for ev in evs:
                    if ev.get("event") == "done":
                        result = Path(ev["path"])
                    elif ev.get("event") == "sniffed":
                        result = ev
                    elif ev.get("event") == "error":
                        error = ev.get("msg")
                break
            time.sleep(0.2)
    except BaseException:
        try:
            proc.terminate()
        except Exception:
            pass
        raise
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
    tail = ""
    try:
        tail = log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1:]
        tail = tail[0][:200] if tail else ""
    except OSError:
        pass
    for f in (status, log):
        try:
            f.unlink()
        except OSError:
            pass
    if result is not None:
        return result
    if error:
        raise DownloadError(error)
    if proc.returncode not in (0, None):
        raise DownloadError("the download window closed unexpectedly" + (f": {tail}" if tail else ""))
    raise DownloadError("The download window was closed before a download started.")


_AUTOCLICK_JS = r"""(function(){
  if (window.__esdClicked) return 'done';
  var els = Array.prototype.slice.call(document.querySelectorAll('a,button,input[type=button],input[type=submit]'));
  for (var i = 0; i < els.length; i++) {
    var el = els[i], t = (el.innerText || el.value || '').replace(/\s+/g, ' ').trim();
    if (!/^download\b/i.test(t) || t.length > 40 || el.disabled) continue;
    var r = el.getBoundingClientRect(), st = getComputedStyle(el);
    if (r.width < 20 || r.height < 10 || st.visibility == 'hidden' || st.display == 'none' || st.opacity == '0') continue;
    window.__esdClicked = true; el.click(); return 'clicked';
  }
  return 'none';
})()"""

_BANNER_JS = r"""(function(){
  if (document.getElementById('__esd_note') || !document.body) return;
  var d = document.createElement('div'); d.id = '__esd_note';
  d.textContent = MSG;
  d.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:2147483647;background:#1f6feb;color:#fff;' +
    'font:13px Segoe UI,Arial,sans-serif;padding:6px 10px;text-align:center;pointer-events:none;opacity:.93';
  document.body.appendChild(d);
})()"""


class GrabSession:
    def __init__(self, url, folder, base, status_path, autoclick=False, title=""):
        self.url, self.folder, self.base = url, Path(folder), base
        self.status_path = status_path
        self.autoclick = autoclick
        self.title = title or host_of(url)
        self.window = None
        self.popups = []
        self.started = False
        self.done = False
        self.closed = False
        self.ext = ".mp4"
        self.part = None
        self.sniffed = {}
        self._last = 0.0
        self._lock = threading.Lock()
        self._keep = []

    def emit(self, **ev):
        with self._lock:
            with open(self.status_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev) + "\n")

    def set_title(self, text):
        try:
            if self.window is not None:
                self.window.set_title(text)
        except Exception:
            pass

    def close(self):
        for w in [self.window] + self.popups:
            try:
                if w is not None:
                    w.destroy()
            except Exception:
                pass

    def start_download(self, suggested, total=None):
        name = os.path.basename(str(suggested or "")) or "video"
        ext = ext_of(name)
        if ext in BAD_DOWNLOAD_EXTS:
            self.emit(event="note", msg=f"refused {name} - that's not a video")
            return None
        if self.started and not self.done:
            return None
        self.started = True
        self.ext = ext if ext else ".mp4"
        self.folder.mkdir(parents=True, exist_ok=True)
        self.part = self.folder / f".{self.base[:60]}.window.part"
        try:
            self.part.unlink()
        except OSError:
            pass
        self.emit(event="started", name=name, total=total)
        self.set_title(f"Downloading {name} - you can leave this window alone")
        return str(self.part)

    def progress(self, done, total):
        now = time.monotonic()
        if now - self._last >= 0.3:
            self._last = now
            self.emit(event="progress", done=done, total=total)

    def completed(self):
        target = unique_path(self.folder / (self.base + self.ext))
        for _ in range(100):
            try:
                os.replace(self.part, target)
                break
            except OSError:
                time.sleep(0.1)
        else:
            self.emit(event="error", msg="couldn't move the finished download into the folder")
            self.close()
            return
        self.done = True
        self.emit(event="done", path=str(target))
        self.close()

    def failed(self, reason):
        self.started = False
        self.emit(event="note", msg=f"the download stopped ({reason}) - press Download again")
        self.set_title(f"{self.title}: the download stopped - press Download again, or close")

    @staticmethod
    def _media_kind(url, ctype=""):
        path = urllib.parse.urlsplit(url).path.lower()
        ctype = (ctype or "").lower()
        if "mpegurl" in ctype or path.endswith(".m3u8") or "dash+xml" in ctype or path.endswith(".mpd"):
            return "stream"
        if ctype.startswith("video/") or ext_of(path) in VIDEO_EXTS - {".ts"}:
            return "file"
        return None

    def saw_request(self, request):
        try:
            url = request.url
            kind = self._media_kind(url)
            if not kind or _match(host_of(url), AD_HOSTS):
                return
            with self._lock:
                e = self.sniffed.setdefault(url, {"size": None, "stream": kind == "stream", "headers": {}})
                e["headers"] = {k: v for k, v in (request.headers or {}).items()
                                if k.lower() in ("referer", "cookie", "user-agent", "origin")}
            self._announce()
        except Exception:
            pass

    def saw_response(self, response):
        try:
            url = response.url
            h = {str(k).lower(): str(v) for k, v in (response.headers or {}).items()}
            kind = self._media_kind(url, h.get("content-type", ""))
            if not kind or _match(host_of(url), AD_HOSTS) or response.status_code not in (200, 206):
                return
            size = None
            m = re.search(r"/(\d+)\s*$", h.get("content-range", ""))
            if m:
                size = int(m.group(1))
            elif response.status_code == 200 and h.get("content-length", "").isdigit():
                size = int(h["content-length"])
            with self._lock:
                e = self.sniffed.setdefault(url, {"size": None, "stream": kind == "stream", "headers": {}})
                if size:
                    e["size"] = max(size, e["size"] or 0)
            self._announce()
        except Exception:
            pass

    def best(self):
        with self._lock:
            items = list(self.sniffed.items())
        files = [(u, e) for u, e in items if not e["stream"] and (e["size"] is None or e["size"] >= 300_000)]
        if files:
            files.sort(key=lambda x: (1 if _PREVIEWISH.search(x[0]) else 0, -(x[1]["size"] or 0)))
            return files[0]
        streams = [(u, e) for u, e in items if e["stream"]]
        streams.sort(key=lambda x: (0 if "master" in x[0].lower() else 1))
        return streams[0] if streams else None

    def _announce(self):
        if self.started:
            return
        b = self.best()
        if b:
            u, e = b
            size = f" ({fmt_size(e['size'])})" if e["size"] else ""
            self.set_title(f"Found a video{size} - close this window to download it "
                           "(or press the site's Download button)")

    def on_loaded(self):
        msg = ("EroScripts Downloader: press the site's Download button (tick the 'I am human' box if it "
               "asks). The file goes straight into your library. No button? Play the video, then close "
               "this window.")
        try:
            self.window.evaluate_js(_BANNER_JS.replace("MSG", json.dumps(msg)))
        except Exception:
            pass

    def autoclick_loop(self):
        while not (self.started or self.closed):
            time.sleep(1.5)
            try:
                self.window.evaluate_js(_AUTOCLICK_JS)
            except Exception:
                pass

    def popup(self, uri):
        if not uri or _match(host_of(uri), AD_HOSTS) or not uri.lower().startswith(("http://", "https://")):
            return
        import webview

        def make():
            try:
                self.popups.append(webview.create_window(
                    "Pop-up from the page (close it if it's an ad)", uri, width=900, height=650))
            except Exception:
                pass
        threading.Thread(target=make, daemon=True).start()

    def on_closed(self):
        if self.closed:
            return
        self.closed = True
        if not self.done:
            if self.started:
                self.emit(event="error", msg="the download window was closed before the download finished")
            else:
                b = self.best()
                if b:
                    u, e = b
                    self.emit(event="sniffed", url=u, stream=e["stream"], size=e["size"], headers=e["headers"],
                              page=self.url)
                else:
                    self.emit(event="closed")
        for w in self.popups:
            try:
                w.destroy()
            except Exception:
                pass


def _net_int(v):
    try:
        return None if v is None else int(v)
    except (TypeError, ValueError):
        try:
            return int(str(v))
        except (TypeError, ValueError):
            return None


def _patch_webview_engines(sess):
    try:
        from webview.platforms import edgechromium as edge

        def on_download_starting(self, sender, args):
            try:
                op = args.DownloadOperation
                path = sess.start_download(str(args.ResultFilePath), _net_int(op.TotalBytesToReceive))
                if path is None:
                    args.Cancel = True
                    return
                args.ResultFilePath = path
                args.Handled = True

                def on_bytes(s, e):
                    sess.progress(_net_int(op.BytesReceived) or 0, _net_int(op.TotalBytesToReceive))

                def on_state(s, e):
                    st = str(op.State)
                    st = {"0": "InProgress", "1": "Interrupted", "2": "Completed"}.get(st, st)
                    if "Completed" in st:
                        threading.Thread(target=sess.completed, daemon=True).start()
                    elif "Interrupted" in st:
                        sess.failed(str(op.InterruptReason))
                op.BytesReceivedChanged += on_bytes
                op.StateChanged += on_state
                sess._keep += [op, on_bytes, on_state]
            except Exception as e:
                sess.emit(event="note", msg=f"couldn't take over the download ({e})")

        def on_new_window_request(self, sender, args):
            args.set_Handled(True)
            sess.popup(str(args.get_Uri()))
        edge.EdgeChrome.on_download_starting = on_download_starting
        edge.EdgeChrome.on_new_window_request = on_new_window_request
    except Exception:
        pass
    try:
        from webview.platforms import qt

        def on_download_requested(self, download):
            if hasattr(download, "downloadFileName"):
                name = download.downloadFileName()
            else:
                name = os.path.basename(download.url().path())
            total = download.totalBytes()
            path = sess.start_download(name, total if total and total > 0 else None)
            if path is None:
                download.cancel()
                return

            def changed(*_):
                t = download.totalBytes()
                sess.progress(download.receivedBytes(), t if t and t > 0 else None)

            def finished(*_):
                st = str(download.state())
                if "Completed" in st:
                    threading.Thread(target=sess.completed, daemon=True).start()
                elif "Interrupted" in st or "Cancelled" in st:
                    sess.failed(st.rsplit(".", 1)[-1])
            if hasattr(download, "setDownloadFileName"):
                download.setDownloadDirectory(os.path.dirname(path))
                download.setDownloadFileName(os.path.basename(path))
                download.receivedBytesChanged.connect(changed)
                download.isFinishedChanged.connect(lambda *a: finished() if download.isFinished() else None)
            else:
                download.setPath(path)
                download.downloadProgress.connect(changed)
                download.finished.connect(finished)
            sess._keep += [download, changed, finished]
            download.accept()
        qt.BrowserView.on_download_requested = on_download_requested
    except Exception:
        pass


def grab_main(a):
    status = a.status or os.devnull
    try:
        import webview
    except ImportError:
        with open(status, "a", encoding="utf-8") as f:
            f.write(json.dumps({"event": "error", "msg": "pywebview isn't installed - press Extras... > "
                                                        "Install"}) + "\n")
        return 2
    sess = GrabSession(a.grab, a.out or ".", safe_name(a.base or "video"), status, a.autoclick, a.title)
    for key, val in (("OPEN_EXTERNAL_LINKS_IN_BROWSER", False), ("ALLOW_DOWNLOADS", True),
                     ("IGNORE_SSL_ERRORS", bool(a.insecure))):
        try:
            webview.settings[key] = val
        except Exception:
            pass
    _patch_webview_engines(sess)
    win = webview.create_window(f"{sess.title} - press Download on the page", a.grab, width=1150, height=820)
    sess.window = win
    win.events.loaded += sess.on_loaded
    win.events.closed += sess.on_closed
    for name, fn in (("request_sent", sess.saw_request), ("response_received", sess.saw_response)):
        ev = getattr(win.events, name, None)
        if ev is not None:
            ev += fn
    if a.autoclick:
        threading.Thread(target=sess.autoclick_loop, daemon=True).start()
    if a.grab_timeout:
        threading.Timer(a.grab_timeout, sess.close).start()
    storage = app_dir() / "eroscripts_downloader_web"
    try:
        webview.start(private_mode=False, storage_path=str(storage))
    except TypeError:
        webview.start()
    sess.on_closed()
    return 0


E621_UA = f"EroScriptsDownloader/{VERSION} (+{DEFAULT_SITE})"


def h_e621(core, res):
    url = res.ref.url
    if ext_of(urllib.parse.urlsplit(url).path) in VIDEO_EXTS:
        h_direct(core, res)
        return
    m = re.search(r"/posts?/(?:show/)?(\d+)", urllib.parse.urlsplit(url).path)
    if not m:
        _generic_page(core, res)
        return
    pid = m.group(1)
    site = "e926.net" if host_of(url).endswith("e926.net") else "e621.net"
    hdr = {"User-Agent": E621_UA}
    post = (core.http.json(f"https://{site}/posts/{pid}.json", headers=hdr) or {}).get("post") or {}
    f = post.get("file") or {}
    tags = post.get("tags") or {}
    words = [t.replace("_", " ") for k in ("artist", "character", "copyright") for t in tags.get(k) or []
             if t not in ("conditional_dnp", "sound_warning", "third-party_edit")]
    if words:
        res.hints.append(" ".join(words))
    ext = (f.get("ext") or "").lower()
    name = f"{pid}.{ext or 'webm'}"
    if (post.get("flags") or {}).get("deleted"):
        res.status, res.note = DEAD, "deleted on e621"
    elif not f.get("url"):
        res.status, res.note = BROWSER, "e621 only shows this file to logged-in users - open it in the browser"
    elif "." + ext not in VIDEO_EXTS:
        res.status, res.note = PAGE, f"an image post ({ext}), not a video"
    else:
        dims = f"{f.get('width')}x{f.get('height')}" if f.get("width") else ""
        res.files = [RemoteFile(name, _int(f.get("size")), ONLINE, url=url, note=dims,
                                duration=post.get("duration"),
                                dl=dl_http(f["url"], headers=hdr, name_hint=name))]


HANDLERS = {
    "viking": h_viking, "e621": h_e621, "pmvhaven": h_pmvhaven,
    "pixeldrain": h_pixeldrain, "mega": h_mega, "gdrive": h_gdrive, "dropbox": h_dropbox,
    "mediafire": h_mediafire, "gofile": h_gofile, "kraken": h_kraken, "buzz": h_buzz,
    "catbox": h_direct, "direct": h_direct, "eroscripts": h_eroscripts, "store": h_store,
    "web": h_web,
}


# Core


class Core:
    def __init__(self, st):
        self.st = st
        self.http = Http(st.get("user_agent") or UA)
        self.forum = Forum(self.http, st.get("site") or DEFAULT_SITE)
        self.http.allow_insecure = bool(st.get("allow_bad_certificates", True))
        self.http.protected_hosts = {self.forum.host[4:] if self.forum.host.startswith("www.")
                                     else self.forum.host}
        set_preferred(st.get("prefer_versions") or "")
        if st.get("cookie"):
            self.forum.set_cookie_string(st["cookie"])

    @staticmethod
    def has_crypto():
        return _aes() is not None

    @staticmethod
    def has_ytdlp():
        return ytdlp_mod() is not None

    def check(self, ref):
        kind = classify(ref.url, self.forum.host) or "web"
        res = LinkResult(ref, kind, HOST_LABEL.get(kind) or host_of(ref.url))
        try:
            HANDLERS.get(kind, h_web)(self, res)
        except HttpError as e:
            if e.code in (404, 410):
                res.status, res.note = DEAD, f"not found ({e.code})"
            elif e.cloudflare():
                res.status, res.note = UNKNOWN, "the site blocked the check (Cloudflare) - open it in the browser"
            else:
                res.status, res.note = UNKNOWN, f"{res.host} answered {e}"
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
            reason = getattr(e, "reason", e)
            if isinstance(reason, socket.gaierror):
                res.status, res.note = UNKNOWN, "site not found - it's probably gone (or you're offline)"
            elif is_cert_error(e):
                res.status, res.note = UNKNOWN, ("the site's security certificate is broken or expired - "
                                                 "tick 'Connect to file hosts whose security certificate "
                                                 "has expired' in Extras... to check it anyway")
            else:
                res.status, res.note = UNKNOWN, f"couldn't connect ({reason})"
        except MegaError as e:
            res.status = DEAD if e.code in MEGA_DEAD else UNKNOWN
            res.note = str(e)
        except Exception as e:
            res.status, res.note = UNKNOWN, f"check failed: {str(e)[:160]}"
        if res.status == CHECKING:
            res.status = min((f.status for f in res.files), key=STATUS_RANK.get) if res.files else UNKNOWN
        for f in [f for f in res.files if not f.is_script and f.duration is None and f.probe
                  and f.status == ONLINE][:12]:
            f.duration = media_duration(self.http, *f.probe)
        if self.http.bad_cert(ref.url):
            warn = "⚠ the site's security certificate is expired/invalid - checked anyway"
            res.note = f"{warn}. {res.note}" if res.note else warn
            for f in res.files:
                f.note = f"{warn}. {f.note}" if f.note else warn
        return res


# Scripts


class ScriptItem:
    def __init__(self, name, size=None, size_text="", where="", by_op=False, post=0, url="", rf=None,
                 user="", pos=0, span=None):
        self.name = name
        self.size = size
        self.size_text = size_text or fmt_size(size)
        self.where = where
        self.by_op = by_op
        self.post = post
        self.url = url
        self.rf = rf
        self.user = user
        self.pos = pos
        self.span = span
        self.checked = False
        self.default = False
        self.length = None
        self.length_state = ""
        self.data = None

    @property
    def ext(self):
        return ext_of(self.name)

    def length_text(self):
        if self.length_state == "ok":
            if isinstance(self.length, tuple):
                return f"{fmt_dur(self.length[0])}–{fmt_dur(self.length[1])}"
            return fmt_dur(self.length) or "0:00"
        if self.length_state == "reading":
            return "…"
        if self.length_state in ("", "skipped"):
            return ""
        return "log in" if "log in" in self.length_state else "?"

    def read_length(self, core, cancel=None):
        if self.ext not in (SCRIPT_EXT, ".zip"):
            self.length_state = "skipped"
            return
        self.length_state = "reading"
        try:
            data = self.data if self.data is not None else self.fetch(core, cancel or threading.Event())
            lens = script_lengths(data, self.name)
        except Cancelled:
            self.length_state = ""
            return
        except Exception as e:
            self.length_state = str(e) or type(e).__name__
            return
        if not lens:
            self.length_state = "no funscript in it" if self.ext == ".zip" else "unreadable"
            return
        self.data = data
        lo, hi = min(lens), max(lens)
        self.length = hi if hi - lo < 1.5 else (lo, hi)
        self.length_state = "ok"

    def fetch(self, core, cancel):
        if self.data is not None:
            return self.data
        if self.rf is not None:
            tmp = Path(tempfile.mkdtemp(prefix="esd-"))
            try:
                p = self.rf.dl(core, tmp, "script", lambda d, t: None, cancel)
                return Path(p).read_bytes()
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        return core.forum.download(self.url, cancel)


def funscript_length(data):
    try:
        j = json.loads(data.decode("utf-8-sig") if isinstance(data, bytes) else data)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(j, dict):
        return None
    tracks = [j.get("actions")] + [a.get("actions") for a in j.get("axes") or [] if isinstance(a, dict)]
    last = 0.0
    for acts in tracks:
        for a in acts or []:
            if isinstance(a, dict) and isinstance(a.get("at"), (int, float)):
                last = max(last, float(a["at"]))
    last /= 1000.0
    meta = j.get("metadata") if isinstance(j.get("metadata"), dict) else {}
    dur = meta.get("duration")
    if isinstance(dur, (int, float)) and dur > 0:
        for d in (float(dur), float(dur) / 1000.0):
            if last - 1 <= d <= last * 1.5 + 60 or (not last and d < 6 * 3600):
                return d
    return last if last or "actions" in j else None


def script_lengths(data, name):
    if ext_of(name) == ".zip":
        out, axes = [], []
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for m in _zip_members(zf):
                if not m.filename.lower().endswith(SCRIPT_EXT) or m.file_size > 200_000_000:
                    continue
                n = funscript_length(zf.read(m))
                if n is None:
                    continue
                stem = os.path.basename(m.filename)[:-len(SCRIPT_EXT)]
                (axes if is_axis(stem) else out).append(n)
        return out or axes
    n = funscript_length(data)
    return [] if n is None else [n]


ZIP_LENGTH_LIMIT = 25 * 1024 * 1024


def wants_length(it):
    if it.ext == SCRIPT_EXT:
        return True
    return it.ext == ".zip" and (it.size or 0) <= ZIP_LENGTH_LIMIT


_SIZE_IN_TEXT = re.compile(r"\(\s*[\d.,]+\s*[KMGT]?i?B\s*\)", re.I)
_NOT_WORDS = re.compile(r"https?://\S+|\S+\.(?:funscript|zip|7z|rar|mp4|mkv|webm)\b|\[(?:image|video)\]", re.I)


def _says_something(line):
    rest = _NOT_WORDS.sub(" ", _SIZE_IN_TEXT.sub(" ", line))
    return len(re.findall(r"[^\W\d_]", rest)) >= 3


def _clip(line, limit, at=0):
    line = line.strip()
    if len(line) <= limit:
        return line
    start = max(0, min(at - (limit - 50), len(line) - limit))
    end = start + limit
    if start:
        sp = line.find(" ", start)
        start = sp + 1 if 0 <= sp < start + 25 else start
    if end < len(line):
        sp = line.rfind(" ", start, end)
        end = sp if sp > end - 25 else end
    return ("…" if start else "") + line[start:end].strip() + ("…" if end < len(line) else "")


def post_snippet(topic, post, span, limit=150):
    meta = (topic.posts if topic is not None else {}).get(post) or {}
    text = meta.get("text") or ""
    if not text:
        return ""
    if not span or span[0] is None:
        return _clip(next((x for x in text.split("\n") if _says_something(x)), ""), limit)
    a = max(0, min(span[0], len(text)))
    b = max(a, min(span[1], len(text)))
    ls = text.rfind("\n", 0, a) + 1
    le = text.find("\n", b)
    le = len(text) if le < 0 else le
    label = text[a:b]
    if re.match(r"\s*(https?://|www\.)", label, re.I):
        label = "‹link›"
    line = text[ls:a] + label + text[b:le]
    if _says_something(text[ls:a] + text[b:le]):
        return _clip(line, limit, a - ls)
    lines = text.split("\n")
    here = text.count("\n", 0, a)
    for i in list(range(here - 1, max(-1, here - 6), -1)) + list(range(here + 1, min(len(lines), here + 3))):
        if _says_something(lines[i]):
            return _clip(lines[i], limit)
    return _clip(line, limit, a - ls) if label != "‹link›" and _says_something(label) else ""


def build_script_items(topic):
    items = [ScriptItem(a.name, parse_size(a.size_text), a.size_text,
                        f"#{a.post} by {a.user}" + (" (OP)" if a.by_op else ""), a.by_op, a.post,
                        url=a.url, user=a.user, pos=a.pos, span=a.span) for a in topic.attachments]
    pool = [i for i in items if i.by_op] or items
    latest = {}
    for i in pool:
        latest[i.name.casefold()] = i
    for i in latest.values():
        i.checked = i.default = True
    return items


def main_scripts(scripts, all_items=False):
    out, seen = [], set()
    for i in scripts:
        if (all_items or i.checked) and i.ext == SCRIPT_EXT and not is_axis(i.name[:-len(SCRIPT_EXT)]):
            k = i.name[:-len(SCRIPT_EXT)].casefold()
            if k not in seen:
                seen.add(k)
                out.append(i)
    return out


PREFERRED_VERSIONS = []


def set_preferred(text):
    PREFERRED_VERSIONS[:] = [t for t in (name_tokens(x) for x in re.split(r"[,;\n]", text or "")) if t]


def preferred_rank(name):
    toks = name_tokens(name)
    for n, want in enumerate(PREFERRED_VERSIONS):
        if want <= toks:
            return n
    return len(PREFERRED_VERSIONS)


def pick_main(scripts, key=None, all_items=False):
    mains = main_scripts(scripts, all_items)
    if key:
        for i in reversed([x for x in scripts if (all_items or x.checked) and x.ext == SCRIPT_EXT]):
            if i.name[:-len(SCRIPT_EXT)].casefold() == key:
                return i
    if not mains:
        return None
    return min(mains, key=lambda i: (preferred_rank(i.name[:-len(SCRIPT_EXT)]),
                                     len(name_tokens(i.name[:-len(SCRIPT_EXT)]))))


VARIATION_TAG = " (+Variation)"


_BRACKETED = re.compile(r"[(\[{]([^)\]}]*)[)\]}]")


VERSION_WORDS = {
    "smooth", "smoothed", "maxinterval", "max", "interval", "min", "soft", "softer", "hard", "harder", "easy",
    "easier", "intense", "extreme", "simple", "simplified", "alt", "alternate", "alternative", "vib", "vibe",
    "vibes", "vibration", "vibrations", "vibrate", "no", "non", "without", "with", "less", "more", "handy",
    "pro", "overclocked", "oc", "edging", "edge", "beginner", "advanced", "slow", "slower", "fast", "faster",
    "half", "speed", "cropped", "uncut", "cut", "remastered", "remaster", "redux", "edit", "edited", "fixed",
    "fix", "updated", "lite", "light", "heavy", "denoised", "funscript", "osr", "sr6", "stroker", "rhythm",
    "rhythmic", "cock", "hero", "ch", "tease", "gentle", "rough", "teasing", "default", "normal", "standard",
}


def is_variant(a_name, b_name):
    a, b = name_tokens(a_name), name_tokens(b_name)
    if not a or not b or a == b:
        return False
    labels = name_tokens(" ".join(_BRACKETED.findall(a_name) + _BRACKETED.findall(b_name)))
    core = a & b
    if not any(len(t) >= 3 for t in core) or len(core) < 0.6 * min(len(a), len(b)):
        return False
    extras = [a - core, b - core]
    loose = [x - labels for x in extras]
    if any(len(x) > 2 or any(t.isdigit() for t in x) for x in loose):
        return False
    if len(core) < 2 and any(loose):
        return False
    if all(extras) and all(loose) and not all(x <= VERSION_WORDS for x in loose):
        return False
    return True


def has_variations(scripts, all_items=False):
    names = [i.name[:-len(SCRIPT_EXT)] for i in main_scripts(scripts, all_items)]
    return any(is_variant(a, b) for n, a in enumerate(names) for b in names[n + 1:])


PATH_LIMIT = 250


def shorten(text, n):
    text = text.strip()
    if len(text) <= n:
        return text
    head, sep, tail = text.rpartition(" - ")
    if sep and head and len(tail) <= min(40, n // 3) and not tail.endswith(VARIATION_TAG.strip()):
        return _shorten(head, n - len(tail) - 4) + "… - " + tail
    return _shorten(text, n)


def _shorten(text, n):
    text = text.strip()
    if len(text) <= n:
        return text
    cut = text[:n]
    sp = max(cut.rfind(" "), cut.rfind("_"))
    if sp >= n * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" -._,") or text[:n]


def fit_name(folder, name, room=6):
    ext = ext_of(name)
    stem = name[:-len(ext)] if ext else name
    allowed = PATH_LIMIT - len(str(folder)) - 1 - len(ext) - room
    if len(stem) <= allowed:
        return name
    return shorten(stem, max(20, allowed)) + ext


def job_names(dest, name, scripts, all_items=False):
    base = safe_name(name)
    fname = folder_name(name, scripts, all_items)
    budget = PATH_LIMIT - len(str(dest)) - 1
    if len(fname) + 1 + len(base) + 26 > budget:
        tag = VARIATION_TAG if fname.endswith(VARIATION_TAG.strip()) else ""
        keep = max(30, (budget - 28) // 2 - len(tag))
        base = shorten(base, keep)
        fname = base + tag
    return fname, base


def folder_name(name, scripts, all_items=False):
    base = safe_name(name)
    if has_variations(scripts, all_items) and not base.endswith(VARIATION_TAG.strip()):
        return safe_name(base + VARIATION_TAG)
    return base


_LEAD_TAG = re.compile(r"^\s*\[([^\]]+)\]\s*")
_TRAIL_PAREN = re.compile(r"(\s*\([^()]*\))+\s*$")


def tagged_name(stem, title):
    m = _LEAD_TAG.match(title or "")
    if not m or "[" in stem:
        return stem
    tag = m.group(1).strip()
    tag_toks = name_tokens(tag)
    clean = _TRAIL_PAREN.sub("", title).strip() or title.strip()
    core = name_tokens(_LEAD_TAG.sub("", clean)) - tag_toks
    stoks = name_tokens(stem)
    label = " ".join(f"({x})" for x in _BRACKETED.findall(stem))
    loose = stoks - core - tag_toks - name_tokens(label)
    if core and core <= stoks and all(t.isdigit() for t in loose):
        return clean + (f" {label}" if label and not name_tokens(label) <= name_tokens(clean) else "")
    lead = re.match(r"^\s*" + r"[\s_.-]*".join(re.escape(w) for w in re.split(r"[\s_.-]+", tag) if w) +
                    r"(?![^\W_])[\s_]*(-\s*)?", stem, re.I)
    if lead and stem[lead.end():].strip():
        rest = stem[lead.end():]
        return f"[{tag}] " + ("- " if lead.group(1) else "") + rest
    return stem


def _edit1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if a + "s" == b or b + "s" == a or a + "es" == b or b + "es" == a:
        return False
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        return len(diff) == 1 or (len(diff) == 2 and diff[1] == diff[0] + 1 and
                                  a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])
    if len(a) > len(b):
        a, b = b, a
    for i in range(len(b)):
        if a == b[:i] + b[i + 1:]:
            return True
    return False


def fix_typos(stem, title):
    words = {w.casefold(): w for w in re.findall(r"[^\W\d_]{3,}", title or "")}
    if not words:
        return stem

    def swap(m):
        w = m.group(0)
        if w.casefold() in words:
            return w
        hits = [t for k, t in words.items() if _edit1(w.casefold(), k) and k not in stem.casefold()]
        return hits[0] if len(hits) == 1 else w
    return re.sub(r"[^\W\d_]{3,}", swap, stem)


def default_name(scripts, title, main_key=None):
    stem = fix_typos(_default_name(scripts, title, main_key), title)
    if title and not re.search(r"[^\W\d_]{3}", tidy_name(stem)):
        stem = _TRAIL_PAREN.sub("", title).strip() or title
    return tidy_name(tagged_name(stem, title))


def script_length(ts, keys=None):
    if ts is None:
        return None
    pool = ts.scripts
    if keys:
        pool = [i for st in ts.sets if st.key in keys for i in st.items]
    elif any(i.checked for i in ts.scripts):
        pool = [i for i in ts.scripts if i.checked]
    m = pick_main(pool, ts.main_key, all_items=True)
    if m is not None and m.length_state == "ok" and not isinstance(m.length, tuple):
        return m.length
    return None


def _default_name(scripts, title, main_key=None):
    checked = [i for i in scripts if i.checked]
    m = pick_main(scripts, main_key)
    if m is not None:
        return m.name[:-len(SCRIPT_EXT)]
    for i in checked:
        if i.ext == SCRIPT_EXT and not is_axis(i.name[:-len(SCRIPT_EXT)]):
            return i.name[:-len(SCRIPT_EXT)]
    for i in checked:
        if i.ext in ARCHIVE_EXTS:
            return os.path.splitext(i.name)[0]
    for i in checked:
        if i.ext == SCRIPT_EXT:
            return i.name[:-len(SCRIPT_EXT)].rpartition(".")[0]
    return title


# Video / script matching

NAME_NOISE = {
    "the", "and", "an", "of", "for", "by", "with", "in", "on", "to", "my", "your", "is", "it", "vs",
    "mp4", "m4v", "mkv", "webm", "avi", "mov", "wmv", "funscript", "funscripts", "script", "scripts",
    "scripted", "video", "videos", "vid", "zip", "rar", "pack", "bundle", "multi", "axis", "multiaxis",
    "version", "ver", "final", "full", "hd", "uhd", "fhd", "sd", "vr", "pov", "sbs", "lr", "tb", "fisheye",
    "mkx", "hevc", "avc", "av1", "remux", "mirror", "mirrors", "link", "links", "here", "download",
    "dl", "source", "backup", "watch", "original", "https", "http", "www", "com", "net", "org", "site",
    "file", "files", "new", "updated", "update", "pixeldrain", "mega", "gofile", "google", "drive",
    "dropbox", "mediafire", "vikingfile", "krakenfiles", "catbox", "buzzheavier", "iwara", "pornhub",
    "xhamster", "xvideos", "spankbang", "youtube", "e621", "e926", "pd", "gd",
}
_NOISE_TOKEN = re.compile(r"^(\d{3,4}p|\d+k|\d+fps|v\d+|x26[45]|h26[45]|\d+x\d+|\d+bit|\d{3,4}x)$")


def name_tokens(text):
    t = urllib.parse.unquote(str(text or ""))
    t = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", t).lower()
    t = re.sub(r"\.(funscript|mp4|m4v|mkv|webm|avi|mov|wmv|zip|7z|rar)\b", " ", t)
    out = set()
    for tok in re.split(r"[\W_]+", t):
        if not tok or _NOISE_TOKEN.match(tok):
            continue
        for run in re.findall(r"\d+|[^\W\d_]+", tok):
            if run.isdigit():
                run = run.lstrip("0") or "0"
            elif len(run) < 2:
                continue
            if run not in NAME_NOISE:
                out.add(run)
    return out


def name_sim(a, b):
    if not a or not b:
        return 0.0
    shared = a & b
    if not any(len(x) >= 3 for x in shared):
        return 0.0
    return 0.7 * len(shared) / min(len(a), len(b)) + 0.3 * len(shared) / len(a | b)


class ScriptSet:
    def __init__(self, key, label, tokens, first):
        self.key, self.label, self.tokens = key, label, tokens
        self.items = [first]
        self.post, self.pos, self.user, self.by_op = first.post, first.pos, first.user, first.by_op

    def default_items(self):
        d = [i for i in self.items if i.default]
        if d:
            return d
        latest = {}
        for i in self.items:
            latest[i.name.casefold()] = i
        return list(latest.values())


def _script_stem(it):
    if it.ext == SCRIPT_EXT:
        stem = it.name[:-len(SCRIPT_EXT)]
        return stem.rpartition(".")[0] if is_axis(stem) else stem
    return os.path.splitext(it.name)[0]


def script_sets(scripts):
    sets = []
    order = sorted(scripts, key=lambda i: (i.post, i.pos))
    for it in order:
        if it.ext != SCRIPT_EXT:
            continue
        stem = _script_stem(it)
        toks = name_tokens(stem)
        key = " ".join(sorted(toks)) or stem.casefold()
        st = next((x for x in sets if x.key == key), None)
        if st is None:
            sets.append(ScriptSet(key, stem, toks, it))
        else:
            st.items.append(it)
    for it in order:
        if it.ext == SCRIPT_EXT:
            continue
        stem = _script_stem(it)
        toks = name_tokens(stem)
        key = " ".join(sorted(toks)) or stem.casefold()
        st = next((x for x in sets if x.key == key), None)
        if st is None and sets:
            scored = sorted(((name_sim(toks, x.tokens), n) for n, x in enumerate(sets)), reverse=True)
            if scored[0][0] >= 0.6 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.05):
                st = sets[scored[0][1]]
            else:
                mine = [x for x in sets if x.user == it.user and x.key != key and
                        any(i.ext == SCRIPT_EXT for i in x.items)]
                if len(mine) == 1 and len([x for x in sets if any(i.ext == SCRIPT_EXT for i in x.items)]) == 1:
                    st = mine[0]
        if st is None:
            sets.append(ScriptSet(key, stem, toks, it))
        else:
            st.items.append(it)
    sets.sort(key=lambda x: (x.post, x.pos))
    return sets


def _token_weight(sets):
    n = len(sets)
    df = {}
    for st in sets:
        for t in st.tokens:
            df[t] = df.get(t, 0) + 1
    return (lambda t: math.log((n + 1) / df[t]) if t in df else 0.0), math.log(n + 1)


def _fit(ev, sets, w, full):
    out = []
    for st in sets:
        shared = ev & st.tokens
        s = sum(w(t) for t in shared)
        tot = sum(w(t) for t in st.tokens)
        if s <= 0 or tot <= 0 or not any(len(x) >= 3 for x in shared):
            out.append(0.0)
            continue
        out.append((s / tot) * min(1.0, s / full))
    return out


def _unit_scores(res, rf, sets, link_level):
    names, hints, ctx = [], [], set()
    if rf is not None:
        names.append(rf.name)
    if link_level:
        t = res.ref.text
        if t and not re.match(r"https?://", t, re.I):
            names.append(t)
        for seg in urllib.parse.urlsplit(res.ref.url).path.split("/"):
            if ext_of(urllib.parse.unquote(seg)) in VIDEO_EXTS | ARCHIVE_EXTS:
                names.append(seg)
        hints = res.hints
        ctx = name_tokens(res.ref.before)
    w, full = _token_weight(sets)
    out = [0.0] * len(sets)
    for toks, factor in [(name_tokens(n), 1.0) for n in names] + [(name_tokens(h), 0.9) for h in hints] + \
            [(ctx, 0.85)]:
        if toks:
            out = [max(a, factor * b) for a, b in zip(out, _fit(toks, sets, w, full))]
    return out


def _pick(scores, floor=0.4, ratio=0.85):
    best = max(scores) if scores else 0
    if best < floor:
        return None
    chosen = [n for n, sc in enumerate(scores) if sc >= best * ratio]
    return chosen if len(chosen) < len(scores) else None


def _order_map(lis, sids, results):
    n = len(sids)
    if n < 2 or not lis:
        return None
    om = _order_map1(lis, sids, results)
    if om is None:
        live = [li for li in lis if results[li].eff_status() != DEAD]
        if live and len(live) < len(lis):
            om = _order_map1(live, sids, results)
    return om


def _order_map1(lis, sids, results):
    n = len(sids)
    if len(lis) == n:
        return {li: [sids[i]] for i, li in enumerate(lis)}
    groups = {}
    for li in lis:
        groups.setdefault(results[li].kind + results[li].host, []).append(li)
    if len(groups) > 1 and all(len(g) == n for g in groups.values()):
        return {li: [sids[i]] for g in groups.values() for i, li in enumerate(g)}
    if len(lis) % n == 0:
        k = len(lis) // n
        return {li: [sids[i // k]] for i, li in enumerate(lis)}
    return None


def _structure(ts, sets, atts, post, lis):
    results = ts.results
    out = {}
    a = sorted(atts.get(post, []))
    if a:
        sids = list(dict.fromkeys(si for _, si in a))
        if len(sids) == 1:
            return {li: ([sids[0]], "posted with this script") for li in lis}
        events = sorted([(pos, 0, si) for pos, si in a] + [(results[li].ref.pos, 1, li) for li in lis])
        clusters, cur, waiting = [], None, []
        before, after = {}, {}
        for _, kind, x in events:
            if kind == 0:
                if cur is None:
                    cur = []
                    clusters.append(cur)
                    for li in waiting:
                        after[li] = len(clusters) - 1
                    waiting = []
                if x not in cur:
                    cur.append(x)
            else:
                if clusters:
                    before[x] = len(clusters) - 1
                cur = None
                waiting.append(x)
        if len(clusters) == 1:
            cl = clusters[0]
            om = _order_map(lis, cl, results) if len(cl) > 1 else None
            if om:
                return {li: (v, "same order as the scripts in the post") for li, v in om.items()}
            return {li: (cl, "posted with these scripts") for li in lis}
        scripts_first = events[0][1] == 0
        for li in lis:
            ci = (before.get(li, after.get(li)) if scripts_first else after.get(li, before.get(li)))
            if ci is not None:
                out[li] = (clusters[ci], "posted next to this script")
        return out
    meta = (ts.topic.posts if ts.topic else {}).get(post) or {}
    targets = ([meta["reply_to"]] if meta.get("reply_to") else []) + sorted(meta.get("quotes") or ())
    for t in targets:
        ta = sorted(atts.get(t, []))
        if not ta:
            continue
        tsids = list(dict.fromkeys(si for _, si in ta))
        if len(tsids) == 1:
            return {li: ([tsids[0]], f"a reply to post #{t}") for li in lis}
        om = _order_map(lis, tsids, results)
        if om:
            return {li: (v, f"same order as the scripts in post #{t}") for li, v in om.items()}
        return {}
    user = (meta.get("user") or results[lis[0]].ref.user).casefold()
    pool = [n for n, st in enumerate(sets) if (st.user or "").casefold() == user and
            any(i.rf is None for i in st.items)]
    if len(pool) == 1:
        return {li: ([pool[0]], "posted by the script's author") for li in lis}
    pool = pool or [n for n, st in enumerate(sets) if any(i.rf is None for i in st.items)]
    om = _order_map(lis, pool, results)
    if om:
        return {li: (v, "same order as the scripts") for li, v in om.items()}
    return {}


def script_variants(sets):
    out = {}
    for i, a in enumerate(sets):
        for j, b in enumerate(sets):
            if i == j or not a.tokens or not b.tokens:
                continue
            if (a.user or "").casefold() != (b.user or "").casefold():
                continue
            if is_variant(a.label, b.label):
                out.setdefault(i, set()).add(j)
    return out


def match_videos(ts):
    sets = script_sets(ts.scripts)
    ts.sets = sets
    out = {}
    if not sets:
        return out
    units = []
    for li, res in ts.results.items():
        if res.script_only():
            continue
        vids = res.video_files()
        if len(vids) <= 1:
            units.append((f"L{li}", li, res, vids[0] if vids else None, True))
        else:
            units.append((f"L{li}", li, res, None, True))
            units += [(f"L{li}_{fi}", li, res, rf, False) for fi, rf in enumerate(vids)]
    if len(sets) == 1:
        return {u[0]: ([0], "the only script in the topic") for u in units}
    scores = {}
    for rid, li, res, rf, link_level in units:
        if res.status == CHECKING and rf is None and not res.ref.text and not res.ref.before:
            continue
        scores[rid] = _unit_scores(res, rf, sets, link_level)
        m = _pick(scores[rid])
        if m:
            out[rid] = (m, "the names match")
    atts = {}
    for si, st in enumerate(sets):
        for it in st.items:
            if it.rf is None:
                atts.setdefault(it.post, []).append((it.pos, si))
    by_post = {}
    for li, res in ts.results.items():
        if not res.script_only():
            by_post.setdefault(res.ref.post, []).append(li)
    struct = {}
    for post, lis in by_post.items():
        lis.sort(key=lambda li: ts.results[li].ref.pos)
        struct.update(_structure(ts, sets, atts, post, lis))
    claimed = {}
    for rid, li, res, rf, link_level in units:
        if rid in out:
            claimed.setdefault(res.ref.post, {})[rid] = set(out[rid][0])
    for rid, li, res, rf, link_level in units:
        if rid in out:
            continue
        m = (out.get(f"L{li}") if not link_level else None) or struct.get(li)
        if m and len(m[0]) > 1 and rid in scores:
            sub = [scores[rid][i] for i in m[0]]
            narrowed = _pick(sub, floor=0.15, ratio=0.7)
            if narrowed and len(narrowed) < len(m[0]):
                m = ([m[0][i] for i in narrowed], m[1] + "; the names fit best")
            else:
                taken = set().union(*[v for k, v in claimed.get(res.ref.post, {}).items()
                                      if not k.startswith(f"L{li}")] or [set()])
                left = [i for i in m[0] if i not in taken]
                if left and len(left) < len(m[0]):
                    pick = _pick([scores[rid][i] for i in left], floor=0.03, ratio=0.5)
                    if pick and len(pick) == 1:
                        m = ([left[pick[0]]], "the script left over in that post that fits")
        if m:
            out[rid] = m
    exact, own = {}, set()
    for rid, li, res, rf, link_level in units:
        if rf is None:
            continue
        toks = frozenset(name_tokens(os.path.splitext(os.path.basename(rf.name))[0]))
        hit = [i for i, st in enumerate(sets) if toks and frozenset(st.tokens) == toks]
        if len(hit) == 1:
            exact[rid] = hit[0]
            own.add(hit[0])
    for rid, i in exact.items():
        if rid not in out or i in out[rid][0]:
            out[rid] = ([i], "same name as the script")
    var = script_variants(sets)
    for rid, (idxs, why) in list(out.items()):
        more = sorted(set(idxs).union(*[var.get(i, set()) - own for i in idxs]))
        if len(more) > len(idxs):
            out[rid] = (more, why + "; versions of the same script")
    for rid, keys in (getattr(ts, "manual", None) or {}).items():
        idxs = [i for i, st in enumerate(sets) if st.key in keys]
        if idxs:
            out[rid] = (idxs, "you chose this")
    return out


def match_label(ts, m):
    if not m:
        return ""
    idxs = m[0]
    if len(idxs) > 2 and len(idxs) == len(ts.sets):
        return "all scripts"
    return " + ".join(ts.sets[i].label for i in idxs if i < len(ts.sets))


def apply_match(ts, idxs):
    chosen = {id(it) for i in idxs if i < len(ts.sets) for it in ts.sets[i].default_items()}
    for it in ts.scripts:
        it.checked = id(it) in chosen
    ts.active_keys = frozenset(ts.sets[i].key for i in idxs if i < len(ts.sets))


def ticked_sets(ts):
    return [n for n, st in enumerate(ts.sets) if any(i.checked for i in st.items)]


class TopicState:
    _n = 0

    def __init__(self, url):
        TopicState._n += 1
        self.key = f"t{TopicState._n}"
        self.url = url
        try:
            self.tid = topic_id(url)[0]
        except ForumError:
            self.tid = None
        self.topic = None
        self.error = None
        self.state = "waiting"
        self.scripts = []
        self.sets = []
        self.matches = {}
        self.results = {}
        self.gen = 0
        self.name = ""
        self.name_edited = False
        self.local_video = None
        self.local_move = True
        self.jobs = []
        self.removed = False
        self.user_pick = None
        self.touched = False
        self.active_keys = frozenset()
        self.queued_keys = set()
        self.manual = {}
        self.main_key = None
        self._remote = set()

    @property
    def job(self):
        return self.jobs[-1] if self.jobs else None

    def set_topic(self, topic):
        self.topic = topic
        self.scripts = build_script_items(topic)
        self._remote = set()
        self.sets, self.matches = script_sets(self.scripts), {}
        self.user_pick, self.touched, self.active_keys = None, False, frozenset()
        self.main_key = None
        if not self.name_edited:
            self.name = default_name(self.scripts, topic.title, self.main_key)

    def add_remote_scripts(self, res):
        added = False
        has_attach = any(i.rf is None for i in self.scripts)
        for rf in res.files:
            if not (rf.is_script and rf.downloadable):
                continue
            k = (link_key(res.ref.url), rf.name)
            if k in self._remote:
                continue
            self._remote.add(k)
            it = ScriptItem(os.path.basename(rf.name), rf.size, "", f"{res.host} link in {res.ref.where}",
                            res.ref.by_op, res.ref.post, rf=rf, user=res.ref.user, pos=res.ref.pos,
                            span=res.ref.span)
            it.checked = it.default = not has_attach and res.ref.by_op
            self.scripts.append(it)
            added = True
        if added and not self.name_edited:
            self.name = default_name(self.scripts, self.topic.title if self.topic else "", self.main_key)
        return added

    def pending(self):
        return sum(1 for r in self.results.values() if r.status == CHECKING)

    def online(self):
        return sum(1 for r in self.results.values()
                   if not r.script_only() and any(f.downloadable for f in r.video_files()))


def window_file(res, rf=None):
    page = rf.url if rf is not None and rf.url else res.ref.url
    name = (rf.name if rf is not None else "") or res.ref.text or host_of(page)
    return RemoteFile(name, rf.size if rf is not None else None, ONLINE, url=page,
                      note="through the download window", dl=dl_window(page, title=res.host))


def drop_site_videos(ts):
    pages = {}
    for res in ts.results.values():
        for f in res.files:
            if f.media:
                pages.setdefault(f.media, set()).add(link_key(res.ref.url))
    shared = {m for m, pg in pages.items() if len(pg) > 1}
    if not shared:
        return False
    groups = {}
    for m in shared:
        groups.setdefault(frozenset(pages[m]), set()).add(m)
    furniture = set()
    for g in groups.values():
        names = {frozenset(name_tokens(os.path.basename(urllib.parse.urlsplit(m).path))) for m in g}
        if len(names) >= 2:
            furniture |= g
    if not furniture:
        return False
    changed = False
    for res in ts.results.values():
        keep = [f for f in res.files if f.media not in furniture]
        if len(keep) != len(res.files):
            changed = True
            res.files = keep
            if not keep:
                res.status = PAGE
                res.note = ("only the site's own clips (ads / promos) on this page - "
                            "not a video for this topic")
    return changed


def add_link(ts, url, user="you"):
    url = url.strip()
    if any(link_key(x.url) == link_key(url) for x in ts.topic.links):
        return None
    ref = LinkRef(url, "", 0, user, False, 0, "")
    ts.topic.links.append(ref)
    li = len(ts.topic.links) - 1
    kind = classify(url, "") or "web"
    ts.results[li] = LinkResult(ref, kind, HOST_LABEL.get(kind) or host_of(url))
    return li


def video_rows(ts, show_dead=False):
    rows, hidden = [], 0
    for li, res in sorted(ts.results.items(), key=lambda kv: res_sort_key(kv[1])):
        if res.script_only():
            continue
        if res.eff_status() == DEAD and not show_dead:
            hidden += 1
            continue
        vids = res.video_files()
        if len(vids) <= 1:
            rows.append((f"L{li}", res, vids[0] if vids else None, 0))
            continue
        rows.append((f"L{li}", res, None, 0))
        order = sorted(range(len(vids)), key=lambda fi: (STATUS_RANK.get(vids[fi].status, 9),
                                                          -(vids[fi].size or 0)))
        for fi in order:
            if vids[fi].status == DEAD and not show_dead:
                continue
            rows.append((f"L{li}_{fi}", res, vids[fi], 1))
    return rows, hidden


def best_row(rows, matches=None, keys=None, sets=None, want=None):
    if want:
        fits = [r for r in rows if r[2] is not None and r[2].duration and abs(r[2].duration - want) <= 5]
        if fits:
            got = best_row(fits, matches, keys, sets)
            if got:
                return got
    for rid, res, rf, _ in rows:
        if rf is None or not rf.downloadable or res.kind == "eroscripts":
            continue
        if keys is not None:
            m = (matches or {}).get(rid)
            if not m or not keys & {sets[i].key for i in m[0] if i < len(sets)}:
                continue
        return rid
    return None


# Saving to the library


def check_funscript(data, name):
    try:
        j = json.loads(data.decode("utf-8-sig"))
        if isinstance(j, dict):
            return
    except (ValueError, UnicodeDecodeError):
        pass
    if data.lstrip()[:1] == b"<":
        raise DownloadError(f"{name}: got a web page instead of the script - log in with Account... first.")
    raise DownloadError(f"{name} isn't a valid funscript.")


def write_unique(folder, name, data):
    target = Path(folder) / fit_name(folder, name)
    if target.exists():
        try:
            if target.read_bytes() == data:
                return target
        except OSError:
            pass
        target = unique_path(target)
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, target)
    return target


def _zip_members(zf):
    for m in zf.infolist():
        if m.is_dir() or m.filename.startswith("__MACOSX") or os.path.basename(m.filename).startswith("._"):
            continue
        yield m


def extract_scripts(zf, folder):
    out = []
    for m in _zip_members(zf):
        if m.filename.lower().endswith(SCRIPT_EXT) and m.file_size < 200_000_000:
            out.append(write_unique(folder, safe_name(os.path.basename(m.filename)), zf.read(m)))
    return out


def unpack_video_zip(path, folder, base):
    out = []
    with zipfile.ZipFile(path) as zf:
        out += extract_scripts(zf, folder)
        vids = sorted((m for m in _zip_members(zf) if ext_of(m.filename) in VIDEO_EXTS),
                      key=lambda m: -m.file_size)
        for n, m in enumerate(vids):
            name = base + ext_of(m.filename) if n == 0 else fit_name(folder, safe_name(os.path.basename(m.filename)))
            target = unique_path(Path(folder) / name)
            tmp = target.with_name(target.name + ".tmp")
            with zf.open(m) as fi, open(tmp, "wb") as fo:
                shutil.copyfileobj(fi, fo, 8 << 20)
            os.replace(tmp, target)
            out.append(target)
    if any(ext_of(p.name) in VIDEO_EXTS for p in out):
        try:
            os.remove(path)
        except OSError:
            pass
    else:
        out.append(Path(path))
    return out


def write_shortcut(folder, title, url):
    target = Path(folder) / fit_name(folder, safe_name(f"EroScripts - {title}.url", limit=120), room=2)
    if not target.name.lower().endswith(".url"):
        target = target.with_name(target.name.rstrip(".") + ".url")
    data = f"[InternetShortcut]\r\nURL={url}\r\n".encode("utf-8")
    try:
        if target.exists() and target.read_bytes() == data:
            return target
        target.write_bytes(data)
    except OSError:
        return None
    return target


def normalize_main(folder, base):
    folder = Path(folder)
    files = [p for p in folder.iterdir() if p.is_file() and p.name.lower().endswith(SCRIPT_EXT)]
    if any(p.name.casefold() == (base + SCRIPT_EXT).casefold() for p in files):
        return
    mains = [p for p in files if not is_axis(p.name[:-len(SCRIPT_EXT)])]
    if len(mains) != 1:
        return
    old = mains[0].name[:-len(SCRIPT_EXT)]
    for p in files:
        stem = p.name[:-len(SCRIPT_EXT)]
        if stem == old:
            new = base
        elif is_axis(stem) and stem.rpartition(".")[0] == old:
            new = f"{base}.{stem.rpartition('.')[2]}"
        else:
            continue
        t = folder / (new + SCRIPT_EXT)
        if not t.exists():
            p.rename(t)


def copy_progress(src, dst, progress, cancel):
    total = os.path.getsize(src)
    tmp = Path(str(dst) + ".part")
    done = 0
    try:
        with open(src, "rb") as fi, open(tmp, "wb") as fo:
            while True:
                if cancel.is_set():
                    raise Cancelled()
                buf = fi.read(8 << 20)
                if not buf:
                    break
                fo.write(buf)
                done += len(buf)
                progress(done, total)
        shutil.copystat(src, tmp)
        os.replace(tmp, dst)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


class Job:
    def __init__(self, ts, scripts, video, local, local_move, name, dest, main_key=None):
        self.ts = ts
        self.main_key = main_key
        self.title = ts.topic.title if ts and ts.topic else name
        self.url = ts.topic.url if ts and ts.topic else ""
        self.topic_id = ts.topic.id if ts and ts.topic else None
        self.scripts = list(scripts)
        self.video = video
        self.local = local
        self.local_move = local_move
        self.name = name
        self.dest = dest
        self.status = "queued"
        self.stage = ""
        self.done = 0
        self.total = None
        self.speed = 0.0
        self.error = None
        self.folder = None
        self.saved = []
        self.cancel = threading.Event()
        self.iid = None

    def clone(self):
        j = Job(self.ts, self.scripts, self.video, self.local, self.local_move, self.name, self.dest,
                self.main_key)
        j.title, j.url, j.topic_id = self.title, self.url, self.topic_id
        return j


def _progress_fn(job, report):
    st = {"t": None, "d": 0, "last": 0.0}

    def cb(done, total):
        if job.cancel.is_set():
            raise Cancelled()
        now = time.monotonic()
        job.done, job.total = done, total
        if st["t"] is None:
            st["t"], st["d"] = now, done
        elif now - st["t"] >= 0.5:
            inst = (done - st["d"]) / (now - st["t"])
            job.speed = inst if not job.speed else 0.7 * job.speed + 0.3 * inst
            st["t"], st["d"] = now, done
        if now - st["last"] > 0.25:
            st["last"] = now
            report()

    def stage(text):
        job.stage = text
        report()
    cb.stage = stage
    return cb


def run_job(core, job, report=lambda: None):
    dest = Path(job.dest)
    fname, base = job_names(dest, job.name, job.scripts, all_items=True)
    folder = dest / fname
    folder.mkdir(parents=True, exist_ok=True)
    job.folder = folder
    saved = job.saved

    main = pick_main(job.scripts, job.main_key, all_items=True)
    main_stem = main.name[:-len(SCRIPT_EXT)] if main else None
    for n, it in enumerate(job.scripts, 1):
        if job.cancel.is_set():
            raise Cancelled()
        job.stage = f"script {n}/{len(job.scripts)}"
        job.done, job.total = 0, None
        report()
        data = it.fetch(core, job.cancel)
        if it.ext == SCRIPT_EXT:
            check_funscript(data, it.name)
            stem = it.name[:-len(SCRIPT_EXT)]
            if it is main:
                target = base + SCRIPT_EXT
            elif main_stem and is_axis(stem) and stem.rpartition(".")[0].casefold() == main_stem.casefold():
                target = f"{base}.{stem.rpartition('.')[2]}{SCRIPT_EXT}"
            else:
                target = safe_name(it.name)
            saved.append(write_unique(folder, target, data))
        elif it.ext == ".zip":
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    got = extract_scripts(zf, folder)
            except zipfile.BadZipFile:
                if data.lstrip()[:1] == b"<":
                    raise DownloadError(f"{it.name}: got a web page instead of the file - log in "
                                        "with Account... first.") from None
                raise DownloadError(f"{it.name} isn't a valid zip file.") from None
            if not got:
                got = [write_unique(folder, safe_name(it.name), data)]
            saved += got
        else:
            saved.append(write_unique(folder, safe_name(it.name), data))
    normalize_main(folder, base)
    if job.url:
        link = write_shortcut(folder, job.title or base, job.url)
        if link is not None:
            saved.append(link)

    vbase = base
    if job.video is not None or job.local:
        n = 2
        while existing_video(folder, vbase):
            vbase = f"{base} ({n})"
            n += 1
    progress = _progress_fn(job, report)
    if job.video is not None:
        job.stage = "video"
        job.done, job.total, job.speed = 0, job.video.size, 0.0
        report()
        path = Path(job.video.dl(core, folder, vbase, progress, job.cancel))
        if ext_of(path.name) == ".zip":
            job.stage = "unpacking"
            report()
            saved += unpack_video_zip(path, folder, vbase)
            normalize_main(folder, base)
        else:
            saved.append(path)
    elif job.local:
        src = Path(job.local)
        target = unique_path(folder / (vbase + ext_of(src.name)))
        job.stage = "moving your video" if job.local_move else "copying your video"
        report()
        moved = False
        if job.local_move:
            try:
                os.rename(src, target)
                moved = True
            except OSError:
                pass
        if not moved:
            copy_progress(src, target, progress, job.cancel)
            if job.local_move:
                try:
                    os.remove(src)
                except OSError:
                    pass
        saved.append(target)
    add_history({"time": datetime.now().isoformat(timespec="seconds"), "topic_id": job.topic_id,
                 "url": job.url, "title": job.title, "folder": str(folder),
                 "video": (job.video.url or job.video.name) if job.video else
                 (str(job.local) if job.local else None),
                 "files": [p.name for p in saved]})
    return folder


# Saved settings and history


def load_settings():
    st = dict(DEFAULT_SETTINGS)
    try:
        with open(app_dir() / SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        for k in st:
            if k in saved and type(saved[k]) is type(st[k]):
                st[k] = saved[k]
    except Exception:
        pass
    if "eroscript.com" in (st.get("site") or "").lower():
        st["site"] = DEFAULT_SITE
    if not st["dest"]:
        try:
            with open(app_dir() / ORGANIZER_SETTINGS, "r", encoding="utf-8") as f:
                st["dest"] = json.load(f).get("dest") or ""
        except Exception:
            pass
    return st


def save_settings(st):
    try:
        with open(app_dir() / SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
    except Exception:
        pass


_HIST_LOCK = threading.Lock()


def add_history(entry):
    with _HIST_LOCK:
        try:
            with open(app_dir() / HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass


def load_history():
    out = {}
    try:
        with open(app_dir() / HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("topic_id") is not None:
                    out[e["topic_id"]] = e
    except OSError:
        pass
    return out


def friendly_error(e, logged_in=True):
    if isinstance(e, HttpError):
        if e.code in (401, 403, 404) and not logged_in:
            return (f"Couldn't open the topic (HTTP {e.code}). Log in first with Account... - "
                    "some sections are for members only.")
        if e.code == 404:
            return "Topic not found - it was deleted, or the link is wrong."
        if e.code in (401, 403):
            try:
                msg = " ".join(json.loads(e.text()).get("errors") or [])
            except Exception:
                msg = ""
            return "You don't have access to this topic." + (f" ({msg})" if msg else "")
        return f"EroScripts answered {e}."
    if isinstance(e, urllib.error.URLError):
        if isinstance(e.reason, socket.gaierror):
            return ("Couldn't find the EroScripts website. Check your internet connection, and that "
                    "a VPN, firewall or DNS blocker isn't blocking discuss.eroscripts.com.")
        return f"Couldn't reach EroScripts ({e.reason})."
    if isinstance(e, (socket.timeout, TimeoutError)):
        return "EroScripts took too long to answer - try again."
    return str(e) or type(e).__name__


# GUI


class App:
    def __init__(self):
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        self.tk, self.ttk, self.fd, self.mb = tk, ttk, filedialog, messagebox
        self.q = queue.Queue()
        self.st = load_settings()
        self.core = Core(self.st)
        self.topics = []
        self.cur = None
        self.jobs = []
        self.job_q = queue.Queue()
        self.checks = Pool(6)
        self.lengths = Pool(2)
        self.loader_q = queue.Queue()
        self.user = None
        self.history = load_history()
        self._filling = False
        self._last_clip = None
        self.vrows = {}
        self.srows = {}

        self.root = tk.Tk()
        self.root.title(f"EroScripts Downloader {VERSION}")
        self.root.geometry(self.st.get("geometry") or "1280x900")
        self.root.minsize(980, 680)
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Head.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Good.TLabel", foreground="#1a7f37")
        style.configure("Warn.TLabel", foreground="#b35900")
        style.configure("Big.TButton", padding=(14, 6))

        self._build()
        threading.Thread(target=self._loader, daemon=True).start()
        for _ in range(max(1, min(4, int(self.st.get("parallel_downloads") or 2)))):
            threading.Thread(target=self._worker, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(80, self._poll)
        self.root.after(200, self._startup)

    def run(self):
        self.root.mainloop()

    def post(self, fn, *a):
        self.q.put((fn, a))

    def _poll(self):
        try:
            while True:
                fn, a = self.q.get_nowait()
                try:
                    fn(*a)
                except Exception:
                    traceback.print_exc()
        except queue.Empty:
            pass
        self.root.after(80, self._poll)

    def _save(self):
        self.st["dest"] = self.dest_var.get().strip().strip('"')
        self.st["watch_clipboard"] = bool(self.watch_var.get())
        self.st["show_dead"] = bool(self.dead_var.get())
        self.st["show_context"] = bool(self.ctx_var.get())
        ck = self.core.forum.cookie_string()
        if ck or not self.user:
            self.st["cookie"] = ck
        try:
            if self.root.state() == "normal":
                self.st["geometry"] = self.root.geometry()
        except Exception:
            pass
        save_settings(self.st)

    # Layout
    def _build(self):
        tk, ttk = self.tk, self.ttk
        c = ttk.Frame(self.root, padding=10)
        c.pack(fill="both", expand=True)

        r1 = ttk.Frame(c)
        r1.pack(fill="x")
        ttk.Label(r1, text="EroScripts link(s):").pack(side="left")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(r1, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=6)
        self.url_entry.bind("<Return>", lambda e: self._add_from_entry())
        ttk.Button(r1, text="Paste", command=self._paste).pack(side="left")
        ttk.Button(r1, text="Add", command=self._add_from_entry).pack(side="left", padx=(6, 0))
        self.watch_var = tk.BooleanVar(value=self.st["watch_clipboard"])
        ttk.Checkbutton(r1, text="Watch clipboard", variable=self.watch_var,
                        command=self._toggle_watch).pack(side="left", padx=(12, 0))

        r2 = ttk.Frame(c)
        r2.pack(fill="x", pady=(6, 0))
        ttk.Label(r2, text="Library folder:").pack(side="left")
        self.dest_var = tk.StringVar(value=self.st["dest"])
        self.dest_var.trace_add("write", lambda *_: self._update_banner())
        ttk.Entry(r2, textvariable=self.dest_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(r2, text="Browse...", command=self._pick_dest).pack(side="left")
        ttk.Button(r2, text="Extras...", command=self._extras_dialog).pack(side="right")
        ttk.Button(r2, text="Account...", command=self._account_dialog).pack(side="right", padx=6)
        self.login_var = tk.StringVar(value="Checking login...")
        ttk.Label(r2, textvariable=self.login_var).pack(side="right", padx=(16, 0))

        vp = ttk.PanedWindow(c, orient="vertical")
        vp.pack(fill="both", expand=True, pady=(10, 0))
        hp = ttk.PanedWindow(vp, orient="horizontal")
        vp.add(hp, weight=5)

        left = ttk.Frame(hp)
        hp.add(left, weight=1)
        ttk.Label(left, text="Topics", style="Head.TLabel").pack(anchor="w")
        tf = ttk.Frame(left)
        tf.pack(fill="both", expand=True)
        self.ttree = ttk.Treeview(tf, columns=("state",), selectmode="browse")
        self.ttree.heading("#0", text="Topic")
        self.ttree.heading("state", text="Status")
        self.ttree.column("#0", width=210, stretch=True)
        self.ttree.column("state", width=120, stretch=False)
        tsb = ttk.Scrollbar(tf, orient="vertical", command=self.ttree.yview)
        self.ttree.configure(yscrollcommand=tsb.set)
        self.ttree.pack(side="left", fill="both", expand=True)
        tsb.pack(side="left", fill="y")
        self.ttree.tag_configure("done", foreground="#1a7f37")
        self.ttree.tag_configure("error", foreground="#b42318")
        self.ttree.tag_configure("busy", foreground="#3a5a8c")
        self.ttree.bind("<<TreeviewSelect>>", lambda e: self._on_topic_select())
        self.ttree.bind("<Delete>", lambda e: self._remove_topic())
        bl = ttk.Frame(left)
        bl.pack(fill="x", pady=(6, 0))
        ttk.Button(bl, text="Remove", command=self._remove_topic).pack(side="left")
        ttk.Button(bl, text="Clear finished", command=self._clear_finished).pack(side="left", padx=6)

        right = ttk.Frame(hp, padding=(10, 0, 0, 0))
        hp.add(right, weight=4)
        hdr = ttk.Frame(right)
        hdr.pack(fill="x")
        self.title_var = tk.StringVar(value="Paste an EroScripts topic link above to start.")
        ttk.Label(hdr, textvariable=self.title_var, style="Head.TLabel", wraplength=720).pack(
            side="left", anchor="w")
        ttk.Button(hdr, text="Open topic in browser", command=self._open_topic).pack(side="right")
        self.meta_var = tk.StringVar()
        ttk.Label(right, textvariable=self.meta_var, foreground="#555555", wraplength=860).pack(anchor="w")
        self.banner_var = tk.StringVar()
        ttk.Label(right, textvariable=self.banner_var, style="Warn.TLabel", wraplength=860).pack(
            anchor="w", pady=(2, 0))

        self.rpane = ttk.PanedWindow(right, orient="vertical")
        sf = ttk.LabelFrame(self.rpane, text="Scripts  (click a row to tick / untick it - right-click for more)",
                            padding=6)
        self.rpane.add(sf, weight=1)
        sfi = ttk.Frame(sf)
        sfi.pack(fill="both", expand=True)
        self.scols = ("chk", "file", "size", "length", "where", "context")
        self.stree = ttk.Treeview(sfi, columns=self.scols, show="headings", height=5, selectmode="browse")
        for col, text, w, anchor, stretch in (("chk", "Use", 40, "center", False),
                                              ("file", "File", 300, "w", True),
                                              ("size", "Size", 75, "e", False),
                                              ("length", "Length", 90, "e", False),
                                              ("where", "Posted in", 190, "w", False),
                                              ("context", "Post says", 280, "w", True)):
            self.stree.heading(col, text=text)
            self.stree.column(col, width=w, anchor=anchor, stretch=stretch)
        ssb = ttk.Scrollbar(sfi, orient="vertical", command=self.stree.yview)
        self.stree.configure(yscrollcommand=ssb.set)
        self.stree.pack(side="left", fill="both", expand=True)
        ssb.pack(side="left", fill="y")
        self.stree.tag_configure("off", foreground="#888888")
        self.stree.bind("<ButtonRelease-1>", self._on_script_click)
        self.stree.bind("<space>", lambda e: self._toggle_script(self.stree.focus()))
        for seq in ("<KeyRelease-Up>", "<KeyRelease-Down>"):
            self.stree.bind(seq, lambda e: self._show_context("script"))
        self._bind_menu(self.stree, self._script_menu)

        vf = ttk.LabelFrame(self.rpane, text="Videos linked in the topic  (right-click a video for more)",
                            padding=6)
        self.rpane.add(vf, weight=3)
        vfi = ttk.Frame(vf)
        self.vcols = ("status", "host", "file", "script", "size", "length", "where", "context", "info")
        self.vtree = ttk.Treeview(vfi, columns=self.vcols, selectmode="browse")
        self.vtree.heading("#0", text="")
        self.vtree.column("#0", width=26, stretch=False)
        for col, text, w, anchor, stretch in (
                ("status", "Status", 105, "w", False), ("host", "Host", 100, "w", False),
                ("file", "File", 240, "w", True), ("script", "Goes with script", 160, "w", False),
                ("size", "Size", 75, "e", False),
                ("length", "Length", 60, "e", False), ("where", "Posted in", 140, "w", False),
                ("context", "Post says", 240, "w", True),
                ("info", "Note / link", 200, "w", True)):
            self.vtree.heading(col, text=text)
            self.vtree.column(col, width=w, anchor=anchor, stretch=stretch)
        vsb = ttk.Scrollbar(vfi, orient="vertical", command=self.vtree.yview)
        self.vtree.configure(yscrollcommand=vsb.set)
        self.vtree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")
        for st, color in ((ONLINE, "#1a7f37"), (BROWSER, "#b35900"), (PAGE, "#3a5a8c"),
                          (UNKNOWN, "#666666"), (STORE, "#7a3fa8"), (DEAD, "#b42318"),
                          (CHECKING, "#888888")):
            self.vtree.tag_configure(st, foreground=color)
        self.vtree.tag_configure("group", font=("Segoe UI", 9, "bold"))
        self.vtree.bind("<<TreeviewSelect>>", lambda e: self._on_video_select())
        for seq in ("<ButtonRelease-1>", "<KeyRelease-Up>", "<KeyRelease-Down>"):
            self.vtree.bind(seq, lambda e: self._remember_pick(user=True))
        self.vtree.bind("<Double-1>", lambda e: self._open_link())
        self._bind_menu(self.vtree, self._video_menu)
        self.vtree.bind("<Return>", lambda e: self._download())
        vb = ttk.Frame(vf)
        self.vinfo_var = tk.StringVar()
        vi = ttk.Label(vf, textvariable=self.vinfo_var, foreground="#555555", anchor="w")
        vi.pack(side="bottom", fill="x", pady=(4, 0))
        vb.pack(side="bottom", fill="x", pady=(6, 0))
        vfi.pack(fill="both", expand=True)
        vf.bind("<Configure>", lambda e: vi.configure(wraplength=max(200, e.width - 20)))
        ttk.Button(vb, text="I already have the video...", command=self._pick_local).pack(side="right")
        ttk.Button(vb, text="Add video link...", command=self._add_video_link).pack(side="right", padx=(6, 0))
        ttk.Button(vb, text="Recheck", command=self._recheck).pack(side="right", padx=6)
        ttk.Button(vb, text="Open link in browser", command=self._open_link).pack(side="right")
        self.dead_var = tk.BooleanVar(value=self.st["show_dead"])
        ttk.Checkbutton(vb, text="Show dead links", variable=self.dead_var,
                        command=self._fill_videos).pack(side="right", padx=10)

        self.pf = ttk.LabelFrame(self.rpane, text="Post text", padding=6)
        ph = ttk.Frame(self.pf)
        ph.pack(fill="x")
        self.post_head_var = tk.StringVar()
        ttk.Label(ph, textvariable=self.post_head_var, font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Button(ph, text="Open post in browser", command=self._open_post).pack(side="right")
        pti = ttk.Frame(self.pf)
        pti.pack(fill="both", expand=True, pady=(4, 0))
        self.ptext = tk.Text(pti, height=8, wrap="word", font=("Segoe UI", 9), relief="flat",
                             padx=8, pady=6, background="#fbfbfb", cursor="arrow", takefocus=0)
        psb = ttk.Scrollbar(pti, orient="vertical", command=self.ptext.yview)
        self.ptext.configure(yscrollcommand=psb.set)
        self.ptext.pack(side="left", fill="both", expand=True)
        psb.pack(side="left", fill="y")
        self.ptext.tag_configure("sub", foreground="#666666")
        self.ptext.tag_configure("grey", foreground="#6e6e6e", lmargin1=14, lmargin2=14)
        self.ptext.tag_configure("url", foreground="#0b5cad", underline=True)
        self.ptext.tag_configure("hl", background="#ffe58a")
        self.ptext.tag_bind("url", "<Enter>", lambda e: self.ptext.configure(cursor="hand2"))
        self.ptext.tag_bind("url", "<Leave>", lambda e: self.ptext.configure(cursor="arrow"))
        self.ptext.configure(state="disabled")
        self.ctx_var = tk.BooleanVar(value=bool(self.st.get("show_context")))
        ttk.Checkbutton(hdr, text="Show post text", variable=self.ctx_var,
                        command=self._toggle_context).pack(side="right", padx=10)
        self._ctx_src = "video"
        self._ctx_shown = None
        self._stretch = {str(self.stree): {"file": 3, "context": 3},
                         str(self.vtree): {"file": 3, "context": 3, "info": 2}}
        self._fit_w = {}
        for tree in (self.stree, self.vtree):
            tree.bind("<Configure>", lambda e, t=tree: self._fit_columns(t, e.width), add="+")
        self._apply_context_option()

        sv = ttk.Frame(right)
        ttk.Label(sv, text="Save as folder:").pack(side="left")
        self.name_var = tk.StringVar()
        self.name_var.trace_add("write", lambda *_: self._on_name_edit())
        ttk.Entry(sv, textvariable=self.name_var).pack(side="left", fill="x", expand=True, padx=6)
        mv = ttk.Frame(right)
        self.main_row = mv
        ttk.Label(mv, text="Main script:").pack(side="left")
        self.main_var = tk.StringVar()
        self.main_box = ttk.Combobox(mv, textvariable=self.main_var, state="readonly", width=34)
        self.main_box.pack(side="left", padx=6)
        self.main_box.bind("<<ComboboxSelected>>", lambda e: self._pick_main(self.main_box.current()))
        ttk.Label(mv, text="★ = gets the folder name and the video; the rest keep their names",
                  foreground="#555555").pack(side="left")
        self._main_items = []
        lv = ttk.Frame(right)
        self.local_var = tk.StringVar()
        ttk.Label(lv, textvariable=self.local_var, style="Good.TLabel").pack(side="left")
        self.forget_btn = ttk.Button(lv, text="Don't use it", command=self._forget_local)
        bb = ttk.Frame(right)
        ttk.Button(bb, text="⬇  Download scripts + selected video", style="Big.TButton",
                   command=self._download).pack(side="left")
        ttk.Button(bb, text="Scripts only", command=lambda: self._download(scripts_only=True)).pack(
            side="left", padx=6)
        self.path_var = tk.StringVar()
        ttk.Label(bb, textvariable=self.path_var, foreground="#555555").pack(side="left", padx=8)
        bb.pack(side="bottom", fill="x", pady=(6, 0))
        lv.pack(side="bottom", fill="x")
        self._main_anchor = lv
        sv.pack(side="bottom", fill="x", pady=(8, 0))
        self.rpane.pack(fill="both", expand=True, pady=(8, 0))

        df = ttk.LabelFrame(vp, text="Downloads", padding=6)
        vp.add(df, weight=1)
        dfi = ttk.Frame(df)
        dfi.pack(fill="both", expand=True)
        self.jtree = ttk.Treeview(dfi, columns=("status", "progress", "speed"), height=4,
                                  selectmode="browse")
        self.jtree.heading("#0", text="Folder")
        self.jtree.heading("status", text="Status")
        self.jtree.heading("progress", text="Progress")
        self.jtree.heading("speed", text="Speed")
        self.jtree.column("#0", width=320, stretch=True)
        self.jtree.column("status", width=320, stretch=True)
        self.jtree.column("progress", width=200, stretch=False)
        self.jtree.column("speed", width=170, stretch=False)
        jsb = ttk.Scrollbar(dfi, orient="vertical", command=self.jtree.yview)
        self.jtree.configure(yscrollcommand=jsb.set)
        self.jtree.pack(side="left", fill="both", expand=True)
        jsb.pack(side="left", fill="y")
        self.jtree.tag_configure("done", foreground="#1a7f37")
        self.jtree.tag_configure("failed", foreground="#b42318")
        self.jtree.tag_configure("cancelled", foreground="#888888")
        self.jtree.bind("<Double-1>", lambda e: self._open_job_folder())
        jb = ttk.Frame(df)
        jb.pack(fill="x", pady=(6, 0))
        ttk.Button(jb, text="Open folder", command=self._open_job_folder).pack(side="left")
        ttk.Button(jb, text="Cancel", command=self._cancel_job).pack(side="left", padx=6)
        ttk.Button(jb, text="Retry", command=self._retry_job).pack(side="left")
        ttk.Button(jb, text="Clear finished", command=self._clear_jobs).pack(side="left", padx=6)
        self.jobs_var = tk.StringVar()
        ttk.Label(jb, textvariable=self.jobs_var).pack(side="right")

    # Login
    def _startup(self):
        if self.watch_var.get():
            self._toggle_watch()
        if not self.core.forum.cookie_string():
            self.login_var.set("Not logged in")
            return

        def work():
            try:
                u = self.core.forum.current_user()
            except Exception:
                u = None
            self.post(self._set_user, u)
            if u:
                self.post(self._reload_topics, True)
        threading.Thread(target=work, daemon=True).start()

    def _reload_topics(self, only_failed=False):
        n = 0
        for ts in self.topics:
            if ts.removed or ts.jobs or (only_failed and ts.topic is not None):
                continue
            ts.error = None
            ts.gen += 1
            self._topic_state(ts, "waiting")
            self.loader_q.put(ts)
            n += 1
        if n and self.cur is not None and self.cur.topic is None:
            self._render()
        return n

    def _set_user(self, u):
        self.user = u
        self.login_var.set(f"Logged in as {u}" if u else "Not logged in")
        if u:
            self.st["username"] = u
            self._save()

    def _account_dialog(self):
        tk, ttk = self.tk, self.ttk
        dlg = tk.Toplevel(self.root)
        dlg.title("EroScripts account")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        f = ttk.Frame(dlg, padding=14)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Log in to EroScripts", style="Head.TLabel").grid(row=0, column=0, columnspan=3,
                                                                          sticky="w")
        ttk.Label(f, text="Needed to download the script attachments. Your password isn't saved - "
                          "only the login session.", wraplength=460).grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 10))
        uv = tk.StringVar(value=self.st.get("username") or "")
        pv = tk.StringVar()
        ov = tk.StringVar()
        for r, (lbl, var, show) in enumerate((("Username or email", uv, ""), ("Password", pv, "•"),
                                             ("2-factor code (if you use it)", ov, "")), start=2):
            ttk.Label(f, text=lbl).grid(row=r, column=0, sticky="w", pady=2)
            e = ttk.Entry(f, textvariable=var, show=show, width=34)
            e.grid(row=r, column=1, columnspan=2, sticky="ew", pady=2)
            if r == 2:
                first = e
        status = tk.StringVar(value=f"Logged in as {self.user}" if self.user else "Not logged in")
        sl = ttk.Label(f, textvariable=status, wraplength=460)
        sl.grid(row=5, column=0, columnspan=3, sticky="w", pady=(8, 0))
        btns = ttk.Frame(f)
        btns.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        def done_login(name, err):
            if err is None:
                self._set_user(name)
                n = self._reload_topics()
                status.set(f"Logged in as {name}." + (f" Refreshing {n} topic(s)..." if n else ""))
                self._save()
                dlg.after(900, dlg.destroy)
            else:
                status.set(str(err) if isinstance(err, LoginError) else friendly_error(err))
                sl.configure(style="Warn.TLabel")

        def do_login():
            if not uv.get().strip() or not pv.get():
                status.set("Type your username and password.")
                return
            status.set("Logging in...")

            def work():
                try:
                    name = self.core.forum.login(uv.get().strip(), pv.get(), ov.get().strip() or None)
                    self.post(done_login, name, None)
                except Exception as e:
                    self.post(done_login, None, e)
            threading.Thread(target=work, daemon=True).start()

        def do_logout():
            self.core.forum.clear_cookies()
            self.st["cookie"] = ""
            self._set_user(None)
            save_settings(self.st)
            status.set("Logged out.")

        ttk.Button(btns, text="Log in", style="Big.TButton", command=do_login).pack(side="left")
        ttk.Button(btns, text="Log out", command=do_logout).pack(side="left", padx=6)
        ttk.Button(btns, text="Close", command=dlg.destroy).pack(side="right")
        ttk.Separator(f).grid(row=7, column=0, columnspan=3, sticky="ew", pady=12)
        ttk.Label(f, text="Login blocked (Cloudflare, security key)? Copy the _t cookie from your "
                          "browser (F12 > Application/Storage > Cookies > discuss.eroscripts.com) "
                          "and paste it here. Username + password is more reliable - a copied "
                          "cookie can stop working when the site refreshes it.",
                  wraplength=460, foreground="#555555").grid(row=8, column=0, columnspan=3, sticky="w")
        cv = tk.StringVar()
        ttk.Entry(f, textvariable=cv, width=40).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        def use_cookie():
            if not cv.get().strip():
                return
            self.core.forum.set_cookie_string(cv.get())
            status.set("Checking the cookie...")

            def work():
                try:
                    u = self.core.forum.current_user()
                    self.post(done_login, u, None if u else Exception("That cookie didn't log you in."))
                except Exception as e:
                    self.post(done_login, None, e)
            threading.Thread(target=work, daemon=True).start()
        ttk.Button(f, text="Use cookie", command=use_cookie).grid(row=9, column=2, sticky="e", pady=(6, 0))
        dlg.bind("<Return>", lambda e: do_login())
        dlg.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dlg.winfo_width()) // 2
        dlg.geometry(f"+{max(0, x)}+{self.root.winfo_rooty() + 80}")
        dlg.grab_set()
        first.focus_set()

    def _extras_dialog(self):
        tk, ttk = self.tk, self.ttk
        dlg = tk.Toplevel(self.root)
        dlg.title("Extras")
        dlg.transient(self.root)
        f = ttk.Frame(dlg, padding=14)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Optional extras", style="Head.TLabel").pack(anchor="w")
        state = tk.StringVar()

        def refresh():
            extras_reset()
            state.set(
                f"yt-dlp (tube sites: PornHub, xHamster, Iwara...):  "
                f"{'installed' if self.core.has_ytdlp() else 'not installed'}\n"
                f"pycryptodome (Mega links):  {'installed' if self.core.has_crypto() else 'not installed'}\n"
                f"pywebview (download window for VikingFile and other 'browser only' sites):  "
                f"{'installed' if has_webview() else 'not installed'}\n"
                f"FFmpeg (best quality from tube sites):  "
                f"{'found' if shutil.which('ffmpeg') else 'not found - install it from ffmpeg.org'}")
        refresh()
        ttk.Label(f, textvariable=state, justify="left").pack(anchor="w", pady=(6, 8))
        cert_var = tk.BooleanVar(value=bool(self.st.get("allow_bad_certificates", True)))

        def cert_changed():
            self.st["allow_bad_certificates"] = bool(cert_var.get())
            self.core.http.allow_insecure = bool(cert_var.get())
            if not cert_var.get():
                self.core.http.insecure_hosts.clear()
            self._save()
        ttk.Checkbutton(f, text="Connect to file hosts whose security certificate has expired or is "
                                "invalid (never used for EroScripts itself)",
                        variable=cert_var, command=cert_changed).pack(anchor="w", pady=(0, 4))
        len_var = tk.BooleanVar(value=bool(self.st.get("script_lengths", True)))

        def len_changed():
            self.st["script_lengths"] = bool(len_var.get())
            self._save()
            if len_var.get() and self.cur is not None and self.cur.topic is not None:
                self._read_lengths(self.cur)
        ttk.Checkbutton(f, text="Show how long each script runs (reads the scripts when a topic loads - "
                                "they're kept, so downloading them later costs nothing extra)",
                        variable=len_var, command=len_changed).pack(anchor="w", pady=(0, 8))
        pv = ttk.Frame(f)
        pv.pack(fill="x", pady=(0, 8))
        ttk.Label(pv, text="When a script comes in several versions, make this one the main script "
                           "(several: separate with commas, first wins):").pack(anchor="w")
        pref_var = tk.StringVar(value=self.st.get("prefer_versions") or "")
        pe = ttk.Entry(pv, textvariable=pref_var)
        pe.pack(fill="x", pady=(2, 0))
        ttk.Label(pv, text="e.g.  Handy 2 Pro Overclocked, Less Vibrations", foreground="#555555").pack(anchor="w")

        def pref_changed(*_):
            self.st["prefer_versions"] = pref_var.get().strip()
            set_preferred(self.st["prefer_versions"])
            self._save()
            for t in self.topics:
                if t.topic is not None and not t.name_edited and not t.main_key:
                    t.name = default_name(t.scripts, t.topic.title, t.main_key)
            if self.cur is not None and self.cur.topic is not None:
                self._render()
        pref_var.trace_add("write", pref_changed)
        out = tk.Text(f, height=10, width=80, font=("Consolas", 9))
        out.pack(fill="both", expand=True)
        bar = ttk.Frame(f)
        bar.pack(fill="x", pady=(8, 0))

        def finished(rc, text):
            out.insert("end", text + ("\nDone.\n" if rc == 0 else f"\npip stopped with code {rc}\n"))
            out.see("end")
            refresh()
            if self.cur:
                self._recheck()

        def install():
            out.insert("end", "Installing yt-dlp, pycryptodome, pywebview and certifi...\n")
            exe = sys.executable
            if exe.lower().endswith("pythonw.exe"):
                alt = exe[:-len("pythonw.exe")] + "python.exe"
                exe = alt if os.path.exists(alt) else exe

            def work():
                kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
                try:
                    r = subprocess.run([exe, "-m", "pip", "install", "--upgrade", "yt-dlp", "pycryptodome",
                                        "pywebview", "certifi"],
                                       capture_output=True, text=True, errors="replace", **kw)
                    self.post(finished, r.returncode, (r.stdout or "")[-3000:] + (r.stderr or "")[-2000:])
                except Exception as e:
                    self.post(finished, 1, str(e))
            threading.Thread(target=work, daemon=True).start()
        ttk.Button(bar, text="Install / update extras", style="Big.TButton", command=install).pack(side="left")
        ttk.Button(bar, text="Close", command=dlg.destroy).pack(side="right")

    # Adding topics
    def _paste(self):
        try:
            txt = self.root.clipboard_get()
        except Exception:
            txt = ""
        if not self._add_text(txt):
            self.url_var.set(txt.strip())
            self.mb.showinfo("Paste", "There's no EroScripts topic link in the clipboard.", parent=self.root)

    def _add_from_entry(self):
        txt = self.url_var.get()
        if self._add_text(txt):
            self.url_var.set("")
        elif txt.strip():
            self.mb.showwarning("Add", "That doesn't look like an EroScripts topic link.\n"
                                "It should look like https://discuss.eroscripts.com/t/some-title/12345",
                                parent=self.root)

    def _add_text(self, txt):
        urls = find_topic_urls(txt, self.core.forum.host)
        if not urls and txt.strip().isdigit():
            urls = [txt.strip()]
        if not urls:
            return False
        have = {t.tid for t in self.topics if not t.removed}
        first = None
        for u in urls:
            ts = TopicState(u)
            if ts.tid is None or ts.tid in have:
                continue
            have.add(ts.tid)
            self.topics.append(ts)
            self.ttree.insert("", "end", iid=ts.key, text=u, values=("waiting",), tags=("busy",))
            self.loader_q.put(ts)
            first = first or ts
        if first and (self.cur is None or self.cur.job is not None):
            self._select(first)
        return True

    def _toggle_watch(self):
        if self.watch_var.get():
            try:
                self._last_clip = self.root.clipboard_get()
            except Exception:
                self._last_clip = ""
            self.root.after(1000, self._watch_tick)
        self._save()

    def _watch_tick(self):
        if not self.watch_var.get():
            return
        try:
            txt = self.root.clipboard_get()
        except Exception:
            txt = ""
        if txt and txt != self._last_clip:
            self._last_clip = txt
            self._add_text(txt)
        self.root.after(1000, self._watch_tick)

    def _loader(self):
        while True:
            ts = self.loader_q.get()
            if ts.removed:
                continue
            self.post(self._topic_state, ts, "loading...")
            try:
                topic = self.core.forum.topic(
                    ts.url, max_posts=int(self.st.get("max_posts") or 400),
                    replies=bool(self.st.get("replies", True)),
                    on_progress=lambda n, t, ts=ts: self.post(self._topic_state, ts, f"loading {n}/{t}"))
                ts.set_topic(topic)
                self.post(self._topic_loaded, ts)
            except Exception as e:
                ts.error = friendly_error(e, bool(self.user))
                self.post(self._topic_failed, ts)
            self.post(self._save)

    def _topic_state(self, ts, text, tag="busy"):
        ts.state = text
        if self.ttree.exists(ts.key):
            self.ttree.set(ts.key, "state", text)
            self.ttree.item(ts.key, tags=(tag,))

    def _topic_failed(self, ts):
        self._topic_state(ts, "error", "error")
        if ts is self.cur:
            self._render()

    def _topic_loaded(self, ts):
        if self.ttree.exists(ts.key):
            self.ttree.item(ts.key, text=ts.topic.title)
        self._start_checks(ts)
        self._read_lengths(ts)
        if ts is self.cur:
            self._render()

    def _start_checks(self, ts):
        ts.results = {}
        ts.gen += 1
        gen = ts.gen
        for li, ref in enumerate(ts.topic.links):
            kind = classify(ref.url, self.core.forum.host) or "web"
            ts.results[li] = LinkResult(ref, kind, HOST_LABEL.get(kind) or host_of(ref.url))
            self.checks.submit(self.core.check, ref, done=lambda res, err, ts=ts, li=li, gen=gen:
                               self.post(self._link_done, ts, li, res, err, gen))
        self._refresh_topic_row(ts)

    def _link_done(self, ts, li, res, err, gen=None):
        if ts.removed or li not in ts.results or (gen is not None and gen != ts.gen):
            return
        if err is not None or res is None:
            res = ts.results[li]
            res.status, res.note = UNKNOWN, f"check failed: {err}"
        ts.results[li] = res
        drop_site_videos(ts)
        before = len(ts.scripts)
        added = ts.add_remote_scripts(res)
        if added:
            self._read_lengths(ts, ts.scripts[before:])
        self._refresh_topic_row(ts)
        if ts is self.cur:
            if added:
                self._fill_scripts()
                if not ts.name_edited:
                    self._set_name(ts.name)
            self._fill_videos()

    def _refresh_topic_row(self, ts):
        if ts.job is not None:
            return
        if ts.topic is None:
            return
        n = ts.pending()
        if n:
            self._topic_state(ts, f"checking ({n} left)")
        else:
            k = ts.online()
            self._topic_state(ts, f"{k} online" if k else "no video online", "busy" if k else "error")

    # Topic view
    def _select(self, ts):
        if self.ttree.exists(ts.key):
            self.ttree.selection_set(ts.key)
            self.ttree.see(ts.key)
        self.cur = ts
        self._render()

    def _on_topic_select(self):
        sel = self.ttree.selection()
        ts = next((t for t in self.topics if sel and t.key == sel[0]), None)
        if ts is not None and ts is not self.cur:
            self.cur = ts
            self._hint = ""
            self._render()

    def _render(self):
        ts = self.cur
        self._filling = True
        try:
            if ts is None:
                self.title_var.set("Paste an EroScripts topic link above to start.")
                self.meta_var.set("")
                self.name_var.set("")
            elif ts.topic is None:
                self.title_var.set(ts.url)
                self.meta_var.set(ts.error or "Loading...")
                self.name_var.set("")
            else:
                t = ts.topic
                self.title_var.set(t.title)
                bits = [f"by {t.author}", f"{t.posts_count} post(s)",
                        f"{len(t.attachments)} script file(s)", f"{len(t.links)} link(s)"]
                if t.tags:
                    bits.append("tags: " + ", ".join(t.tags[:8]))
                if t.truncated:
                    bits.append(f"only the first {t.scanned} posts were read")
                self.meta_var.set("   ·   ".join(bits))
                self.name_var.set(ts.name)
            self._ctx_src, self._ctx_shown = "video", None
            self._fill_scripts()
            self._fill_videos()
            self._show_local()
        finally:
            self._filling = False
        self._update_banner()
        self._show_context()

    def _script_values(self, it):
        ts = self.cur
        chk = "✔" if it.checked else ""
        if it.checked and ts is not None and len(main_scripts(ts.scripts)) > 1 and \
                pick_main(ts.scripts, ts.main_key) is not None and \
                it.name.casefold() == pick_main(ts.scripts, ts.main_key).name.casefold():
            chk = "★"
        return (chk, it.name, it.size_text, it.length_text(), it.where,
                post_snippet(ts.topic if ts else None, it.post, it.span))

    def _fill_scripts(self):
        sel = self.stree.selection()
        keep = self.srows.get(sel[0]) if sel else None
        self.stree.delete(*self.stree.get_children())
        self.srows = {}
        ts = self.cur
        if ts is None or ts.topic is None:
            return
        for n, it in enumerate(ts.scripts):
            iid = f"s{n}"
            self.srows[iid] = it
            self.stree.insert("", "end", iid=iid, tags=() if it.checked else ("off",),
                              values=self._script_values(it))
            if it is keep:
                self.stree.selection_set(iid)
                self.stree.focus(iid)
        if not ts.scripts:
            self.stree.insert("", "end", iid="none", values=(
                "", "No script attachments found in the topic.", "", "", "", ""), tags=("off",))
        self._refresh_main()

    def _refresh_main(self):
        ts = self.cur
        mains = main_scripts(ts.scripts) if ts is not None and ts.topic is not None else []
        self._main_items = mains
        if len(mains) < 2:
            self.main_row.pack_forget()
            return
        cur = pick_main(ts.scripts, ts.main_key)
        self.main_box.configure(values=[m.name for m in mains])
        idx = next((n for n, m in enumerate(mains) if cur is not None and
                    m.name.casefold() == cur.name.casefold()), 0)
        self.main_box.current(idx)
        if not self.main_row.winfo_ismapped():
            self.main_row.pack(side="bottom", fill="x", pady=(4, 0), before=self._main_anchor)

    def _pick_main(self, idx):
        ts = self.cur
        if ts is None or not 0 <= idx < len(self._main_items):
            return
        it = self._main_items[idx]
        ts.main_key = it.name[:-len(SCRIPT_EXT)].casefold()
        ts.name_edited = False
        ts.name = default_name(ts.scripts, ts.topic.title, ts.main_key)
        self._set_name(ts.name)
        for iid, x in self.srows.items():
            self.stree.set(iid, "chk", self._script_values(x)[0])
        self._refresh_main()

    def _script_iid(self, it):
        return next((iid for iid, x in self.srows.items() if x is it), None)

    def _read_lengths(self, ts, items=None, force=False):
        if not (force or self.st.get("script_lengths", True)):
            return
        for it in (ts.scripts if items is None else items):
            if it.length_state in ("ok", "reading") or not (force or wants_length(it)):
                continue
            if it.ext not in (SCRIPT_EXT, ".zip"):
                continue
            it.length_state = "reading"
            self.lengths.submit(it.read_length, self.core,
                                done=lambda r, err, ts=ts, it=it: self.post(self._length_done, ts, it, err))
        if ts is self.cur:
            for it in (ts.scripts if items is None else items):
                iid = self._script_iid(it)
                if iid and self.stree.exists(iid):
                    self.stree.set(iid, "length", it.length_text())

    def _length_done(self, ts, it, err=None):
        if err is not None:
            it.length_state = str(err) or "failed"
        if ts is not self.cur or ts.removed:
            return
        iid = self._script_iid(it)
        if iid and self.stree.exists(iid):
            self.stree.set(iid, "length", it.length_text())
        self._on_video_select()

    def _on_script_click(self, e):
        iid = self.stree.identify_row(e.y)
        if iid and self.stree.identify("region", e.x, e.y) == "cell":
            self._toggle_script(iid)
        if iid in self.srows:
            self._show_context("script")

    def _toggle_script(self, iid):
        it = self.srows.get(iid)
        if it is None:
            return
        it.checked = not it.checked
        self.stree.set(iid, "chk", "✔" if it.checked else "")
        self.stree.item(iid, tags=() if it.checked else ("off",))
        self._ticks_changed()

    def _only_script(self, iid):
        it = self.srows.get(iid)
        ts = self.cur
        if it is None or ts is None:
            return
        for x in ts.scripts:
            x.checked = x is it
        for i, x in self.srows.items():
            self.stree.set(i, "chk", "✔" if x.checked else "")
            self.stree.item(i, tags=() if x.checked else ("off",))
        self._ticks_changed()

    def _ticks_changed(self):
        ts = self.cur
        if ts is None:
            return
        ts.touched = True
        if ts.main_key and pick_main(ts.scripts, ts.main_key) is not None and \
                pick_main(ts.scripts, ts.main_key).name[:-len(SCRIPT_EXT)].casefold() != ts.main_key:
            ts.main_key = None
        for iid, x in self.srows.items():
            self.stree.set(iid, "chk", self._script_values(x)[0])
        self._refresh_main()
        if not ts.name_edited:
            ts.name = default_name(ts.scripts, ts.topic.title, ts.main_key)
            self._set_name(ts.name)
        ticked = ticked_sets(ts) if len(ts.sets) > 1 else []
        if len(ticked) == 1:
            key = ts.sets[ticked[0]].key
            ts.active_keys = frozenset([key])
            sel = self.vtree.selection()
            m = ts.matches.get(sel[0]) if sel else None
            if not m or key not in {ts.sets[i].key for i in m[0] if i < len(ts.sets)}:
                rows, _ = video_rows(ts, bool(self.dead_var.get()))
                rid = best_row(rows, ts.matches, {key}, ts.sets, want=script_length(ts, {key}))
                if rid:
                    ts.user_pick = rid
                    self.vtree.selection_set(rid)
                    self.vtree.see(rid)

    def _set_name(self, name):
        self._filling = True
        try:
            self.name_var.set(name)
        finally:
            self._filling = False
        self._update_banner()

    def _on_name_edit(self):
        if self._filling or self.cur is None:
            self._update_banner()
            return
        self.cur.name = self.name_var.get()
        self.cur.name_edited = True
        self._update_banner()

    def _update_banner(self):
        ts = self.cur
        dest = self.dest_var.get().strip().strip('"')
        name = self.name_var.get().strip()
        if ts is None or ts.topic is None:
            self.banner_var.set(ts.error if ts is not None and ts.error else "")
            self.path_var.set("")
            return
        base = safe_name(name) if name else ""
        fname = folder_name(name, ts.scripts) if name else ""
        self.path_var.set(f"→  {os.path.join(dest, fname)}{os.sep}" if dest and base else "")
        msgs = []
        h = self.history.get(ts.topic.id)
        if h:
            msgs.append(f"You downloaded this topic on {h.get('time', '?')[:10]} into {h.get('folder')}.")
        if dest and base:
            folder = Path(dest) / fname
            v = existing_video(folder, base)
            if v is not None:
                msgs.append(f"Already in your library: {folder} (has {v.name}).")
            elif folder.is_dir():
                msgs.append(f"The folder {folder} already exists - files will be added to it.")
        self.banner_var.set("   ".join(msgs))

    def _remember_pick(self, user=False):
        sel = self.vtree.selection()
        ts = self.cur
        if ts is not None and sel and sel[0] in self.vrows:
            if ts.user_pick != sel[0]:
                self._hint = ""
                ts.user_pick = sel[0]
                ts.touched = True
                self._follow_match(sel[0])
        if user:
            self._show_context("video")

    # Right-click menus
    def _bind_menu(self, tree, fn):
        buttons = ["<Button-3>"] + (["<Button-2>"] if sys.platform == "darwin" else [])
        for seq in buttons:
            tree.bind(seq, lambda e: fn(tree.identify_row(e.y), e.x_root, e.y_root))

        def key(e):
            iid = tree.focus() or next(iter(tree.selection()), "")
            if not iid:
                return "break"
            bb = tree.bbox(iid) or (0, 0, 0, 0)
            fn(iid, tree.winfo_rootx() + bb[0] + 60, tree.winfo_rooty() + bb[1] + bb[3])
            return "break"
        for seq in ("<Shift-F10>", "<App>", "<Menu>"):
            try:
                tree.bind(seq, key)
            except self.tk.TclError:
                pass

    def _popup(self, menu, x, y):
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _copy(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def _video_menu(self, rid, x, y):
        ts = self.cur
        if ts is None or ts.topic is None or not rid or rid not in self.vrows:
            return
        if self.vtree.selection() != (rid,):
            self.vtree.selection_set(rid)
        self.vtree.focus(rid)
        self._remember_pick(user=True)
        res, rf = self.vrows[rid]
        li = int(rid[1:].split("_")[0])
        obj = rf if rf is not None else res
        group = rf is None and len(res.video_files()) > 1
        url = rf.url if rf is not None and rf.url else res.ref.url
        tk = self.tk
        menu = tk.Menu(self.root, tearoff=0)
        if group:
            menu.add_command(label="Download: pick one of the videos under it", state="disabled")
        else:
            menu.add_command(label="Download the ticked scripts + this video", command=self._download,
                             state="disabled" if obj.status in (DEAD, CHECKING) else "normal")
        menu.add_separator()
        menu.add_command(label="Open link in browser", command=self._open_link)
        menu.add_command(label="Copy link", command=lambda: self._copy(url))
        if rf is not None and rf.media:
            menu.add_command(label="Copy the video file's own address", command=lambda: self._copy(rf.media))
        menu.add_command(label="Check this link again", command=lambda: self._recheck_link(li))
        menu.add_separator()
        if res.ref.post:
            menu.add_command(label=f"Show the post it's in (#{res.ref.post} by {res.ref.user})",
                             command=lambda: self._show_post_for("video"))
            menu.add_command(label="Open that post in browser",
                             command=lambda: open_url(ts.topic.post_url(res.ref.post)))
        else:
            menu.add_command(label="You added this link yourself", state="disabled")
        if len(ts.sets) > 1:
            menu.add_separator()
            sub = tk.Menu(menu, tearoff=0)
            cur = ts.matches.get(rid)
            cur_idx = set(cur[0]) if cur else set()
            menu._vars = []
            for i, st in enumerate(ts.sets):
                v = tk.BooleanVar(value=i in cur_idx)
                menu._vars.append(v)
                sub.add_checkbutton(label=st.label, variable=v,
                                    command=lambda i=i, rid=rid: self._set_manual(rid, [i]))
            sub.add_separator()
            sub.add_command(label="All of them", command=lambda rid=rid: self._set_manual(
                rid, list(range(len(ts.sets)))))
            if rid in ts.manual:
                sub.add_command(label="Let the program guess again", command=lambda: self._set_manual(rid, None))
            now = match_label(ts, cur) if cur else "not sure"
            menu.add_cascade(label=f"Goes with script:  {now[:48] + ('…' if len(now) > 48 else '')}", menu=sub)
        self._popup(menu, x, y)

    def _script_menu(self, iid, x, y):
        ts = self.cur
        it = self.srows.get(iid)
        if ts is None or it is None:
            return
        self.stree.selection_set(iid)
        self.stree.focus(iid)
        self._show_context("script")
        menu = self.tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Don't use this script" if it.checked else "Use this script",
                         command=lambda: self._toggle_script(iid))
        if len(ts.scripts) > 1:
            menu.add_command(label="Use only this script", command=lambda: self._only_script(iid))
        mains = main_scripts(ts.scripts)
        if it.checked and len(mains) > 1 and it.ext == SCRIPT_EXT and not is_axis(it.name[:-len(SCRIPT_EXT)]):
            idx = next((n for n, m in enumerate(mains) if m.name.casefold() == it.name.casefold()), None)
            if idx is not None:
                menu.add_command(label="Make this the main script (gets the folder name)",
                                 command=lambda: self._pick_main(idx))
        if it.ext in (SCRIPT_EXT, ".zip") and it.length_state not in ("ok", "reading"):
            why = it.length_state if it.length_state not in ("", "skipped") else ""
            menu.add_command(label="Read its length" + (f"  (last time: {why[:60]})" if why else ""),
                             command=lambda: self._read_lengths(ts, [it], force=True))
        menu.add_separator()
        link = it.url or (it.rf.url if it.rf is not None else "")
        if link:
            menu.add_command(label="Copy link", command=lambda: self._copy(link))
        if it.post:
            menu.add_command(label=f"Show the post it's in (#{it.post} by {it.user})",
                             command=lambda: self._show_post_for("script"))
            menu.add_command(label="Open that post in browser",
                             command=lambda: open_url(ts.topic.post_url(it.post)))
        self._popup(menu, x, y)

    def _recheck_link(self, li):
        ts = self.cur
        if ts is None or ts.topic is None or not 0 <= li < len(ts.topic.links):
            return
        ref = ts.topic.links[li]
        kind = classify(ref.url, self.core.forum.host) or "web"
        ts.results[li] = LinkResult(ref, kind, HOST_LABEL.get(kind) or host_of(ref.url))
        gen = ts.gen
        extras_reset()
        self.checks.submit(self.core.check, ref, done=lambda res, err, ts=ts, li=li, gen=gen:
                           self.post(self._link_done, ts, li, res, err, gen))
        self._refresh_topic_row(ts)
        self._fill_videos()

    # Post text
    def _set_columns(self):
        on = bool(self.ctx_var.get())
        multi = self.cur is not None and len(self.cur.sets) > 1
        for tree, cols in ((self.stree, [c for c in self.scols if on or c != "context"]),
                           (self.vtree, [c for c in self.vcols if (on or c != "context") and
                                         (multi or c != "script")])):
            if list(tree.cget("displaycolumns")) != cols:
                tree.configure(displaycolumns=cols)
                self._fit_columns(tree, force=True)

    def _fit_columns(self, tree, width=None, force=False):
        width = width or tree.winfo_width()
        if width < 100 or (not force and self._fit_w.get(str(tree)) == width):
            return
        self._fit_w[str(tree)] = width
        weights = self._stretch.get(str(tree), {})
        shown = list(tree.cget("displaycolumns"))
        if shown in (["#all"], []):
            shown = list(tree.cget("columns"))
        fixed = sum(int(tree.column(c, "width")) for c in shown if c not in weights)
        if "tree" in str(tree.cget("show")):
            fixed += int(tree.column("#0", "width"))
        grow = {c: w for c, w in weights.items() if c in shown}
        avail = width - fixed - 6
        total = sum(grow.values()) or 1
        for c, w in grow.items():
            tree.column(c, width=max(110, int(avail * w / total)))

    def _apply_context_option(self):
        on = bool(self.ctx_var.get())
        self._set_columns()
        shown = str(self.pf) in [str(x) for x in self.rpane.panes()]
        if on and not shown:
            self.rpane.add(self.pf, weight=2)
            self.root.after(150, self._place_post_sash)
        elif not on and shown:
            self.rpane.forget(self.pf)
        self._ctx_shown = None
        self._show_context()

    def _place_post_sash(self, tries=10):
        try:
            if len(self.rpane.panes()) < 3:
                return
            h = self.rpane.winfo_height()
            if h < 200:
                if tries:
                    self.root.after(200, lambda: self._place_post_sash(tries - 1))
                return
            s0 = min(max(self.rpane.sashpos(0), min(160, int(h * 0.26))), 220)
            self.rpane.sashpos(0, s0)
            rest = h - s0
            videos = min(max(230, int(rest * 0.55)), rest - 110)
            self.rpane.sashpos(1, s0 + max(120, videos))
        except Exception:
            pass

    def _toggle_context(self):
        self._apply_context_option()
        self._save()

    def _show_post_for(self, src):
        if not self.ctx_var.get():
            self.ctx_var.set(True)
            self._toggle_context()
        self._show_context(src)

    def _context_target(self):
        ts = self.cur
        if ts is None or ts.topic is None:
            return None
        if self._ctx_src == "script":
            iid = self.stree.focus() or next(iter(self.stree.selection()), "")
            it = self.srows.get(iid)
            if it is not None:
                return it.post, it.span, it.name
        res, rf = self._selected_video()
        if res is not None:
            return res.ref.post, res.ref.span, res.ref.url
        return None

    def _show_context(self, src=None):
        if src:
            self._ctx_src = src
        if not self.ctx_var.get():
            return
        target = self._context_target()
        key = (id(self.cur), target[:2] if target else None)
        if key == self._ctx_shown:
            return
        self._ctx_shown = key
        self._render_post(*(target or (None, None, None)))

    def _render_post(self, post, span, what):
        t = self.ptext
        ts = self.cur
        topic = ts.topic if ts is not None else None
        self._post_num = post
        t.configure(state="normal")
        t.delete("1.0", "end")
        for tag in t.tag_names():
            if re.fullmatch(r"u\d+", tag):
                t.tag_delete(tag)

        def put(text, tags=()):
            try:
                t.insert("end", text, tags)
            except self.tk.TclError:
                t.insert("end", "".join(c if ord(c) < 0x10000 else "\ufffd" for c in text), tags)
        try:
            if topic is None or post is None:
                self.post_head_var.set("")
                put("Click a script or video to see the post it was posted in.", ("sub",))
                return
            if post == 0:
                self.post_head_var.set("A link you added")
                put("You added this link yourself with \"Add video link...\" - it isn't in a post.", ("sub",))
                return
            meta = topic.posts.get(post)
            if not meta:
                self.post_head_var.set(f"Post #{post}")
                put("This post wasn't read (only the first posts of very long topics are read).", ("sub",))
                return
            head = f"Post #{post} by {meta['user']}"
            if meta["user"].casefold() == (topic.author or "").casefold():
                head += " (OP)"
            if meta.get("date"):
                head += f"   ·   {meta['date']}"
            if meta.get("edited"):
                head += "   ·   edited"
            self.post_head_var.set(head)
            rt = meta.get("reply_to")
            if rt:
                other = topic.posts.get(rt) or {}
                who = meta.get("reply_user") or other.get("user") or ""
                said = post_snippet(topic, rt, None, 200) if other else ""
                put(f"In reply to #{rt}" + (f" by {who}" if who else "") + (f":  {said}" if said else "") + "\n\n",
                    ("sub",))
            text = meta.get("text") or ""
            if not text:
                put("(this post has no text)", ("sub",))
                return
            grey = meta.get("grey") or []
            links = meta.get("links") or []
            hl = None
            if span and span[0] is not None:
                a = max(0, min(span[0], len(text)))
                b = max(a, min(span[1], len(text)))
                if a == b:
                    b = text.find("\n", a)
                    b = len(text) if b < 0 else b
                hl = (a, b) if b > a else None
            cuts = {0, len(text)}
            for g0, g1 in grey:
                cuts |= {g0, g1}
            for l0, l1, _ in links:
                cuts |= {l0, l1}
            if hl:
                cuts |= set(hl)
            cuts = sorted(c for c in cuts if 0 <= c <= len(text))
            marked = False
            for a, b in zip(cuts, cuts[1:]):
                tags = []
                if any(g0 <= a and b <= g1 for g0, g1 in grey):
                    tags.append("grey")
                for n, (l0, l1, href) in enumerate(links):
                    if l0 <= a and b <= l1 and l0 < l1:
                        tag = f"u{n}"
                        if tag not in t.tag_names():
                            t.tag_bind(tag, "<Button-1>", lambda e, h=href: open_url(h))
                        tags += ["url", tag]
                        break
                if hl and hl[0] <= a and b <= hl[1]:
                    tags.append("hl")
                    if not marked:
                        t.mark_set("hl", "end-1c")
                        t.mark_gravity("hl", "left")
                        marked = True
                put(text[a:b], tuple(tags))
            t.yview_moveto(0)
            if marked:
                self._post_gen = gen = getattr(self, "_post_gen", 0) + 1

                def scroll():
                    if gen == self._post_gen and "hl" in t.mark_names():
                        t.yview(t.index("hl linestart - 2 lines"))
                        t.see("hl")
                t.see("hl")
                t.after(60, scroll)
                t.after(400, scroll)
        finally:
            t.configure(state="disabled")

    def _open_post(self):
        ts = self.cur
        if ts is not None and ts.topic is not None:
            open_url(ts.topic.post_url(getattr(self, "_post_num", None) or 0))

    def _set_manual(self, rid, idxs):
        ts = self.cur
        if ts is None:
            return
        if idxs is None:
            ts.manual.pop(rid, None)
        else:
            ts.manual[rid] = {ts.sets[i].key for i in idxs}
        ts.user_pick = rid
        ts.touched = True
        self._fill_videos()
        m = ts.matches.get(rid)
        if m:
            ts.active_keys = frozenset()
            self._follow_match(rid)
        self._on_video_select()

    def _follow_match(self, rid):
        ts = self.cur
        if ts is None or len(ts.sets) < 2:
            return False
        m = ts.matches.get(rid)
        if not m:
            return False
        keys = frozenset(ts.sets[i].key for i in m[0] if i < len(ts.sets))
        if keys == ts.active_keys and set(ticked_sets(ts)) == set(m[0]):
            return False
        apply_match(ts, m[0])
        ts.main_key = None
        ts.name_edited = False
        ts.name = default_name(ts.scripts, ts.topic.title, ts.main_key)
        self._fill_scripts()
        self._set_name(ts.name)
        return True

    def _fill_videos(self):
        keep = self.cur.user_pick if self.cur is not None else None
        self.vtree.delete(*self.vtree.get_children())
        self.vrows = {}
        ts = self.cur
        if ts is None or ts.topic is None:
            self.vinfo_var.set("")
            return
        ts.matches = match_videos(ts)
        self._set_columns()
        rows, hidden = video_rows(ts, bool(self.dead_var.get()))
        for rid, res, rf, depth in rows:
            parent = rid.split("_")[0] if depth else ""
            mlabel = match_label(ts, ts.matches.get(rid)) if len(ts.sets) > 1 else ""
            if depth == 0 and rf is None and len(res.video_files()) > 1:
                vids = res.video_files()
                total = sum(f.size or 0 for f in vids)
                extra = f", +{res.other_files} other file(s)" if res.other_files else ""
                vals = (STATUS_TEXT.get(res.eff_status(), ""), res.host, f"{len(vids)} videos in this link{extra}",
                        mlabel, fmt_size(total) if total else "", "", res.ref.where,
                        post_snippet(ts.topic, res.ref.post, res.ref.span), res.note or res.ref.url)
                self.vtree.insert("", "end", iid=rid, open=True, values=vals,
                                  tags=(res.eff_status(), "group"))
            else:
                obj = rf if rf is not None else res
                name = rf.name if rf is not None else (res.ref.text if res.ref.text and
                                                       res.ref.text != res.ref.url else "")
                note = (rf.note if rf is not None and rf.note else res.note) or res.ref.url
                if not name:
                    name, note = note, res.ref.url
                vals = (STATUS_TEXT.get(obj.status, ""), res.host if depth == 0 else "", name, mlabel,
                        fmt_size(rf.size) if rf is not None else "",
                        fmt_dur(rf.duration) if rf is not None else "",
                        res.ref.where if depth == 0 else "",
                        post_snippet(ts.topic, res.ref.post, res.ref.span) if depth == 0 else "", note)
                self.vtree.insert(parent, "end", iid=rid, values=vals, tags=(obj.status,))
            self.vrows[rid] = (res, rf)
        if not rows:
            msg = "No video links found in the topic." if not ts.results else \
                "None of the video links work any more."
            if hidden:
                msg += f"  ({hidden} dead link(s) hidden - tick 'Show dead links')"
            self.vtree.insert("", "end", iid="none", values=("", "", msg, "", "", "", "", "", ""))
        target = keep if keep in self.vrows else None
        if target is None and ts.active_keys and len(ts.sets) > 1:
            target = best_row(rows, ts.matches, ts.active_keys, ts.sets,
                              want=script_length(ts, ts.active_keys))
        target = target or best_row(rows, want=script_length(ts) if len(ts.sets) <= 1 else None)
        if target:
            self.vtree.selection_set(target)
            self.vtree.see(target)
            if not ts.touched and not ts.queued_keys:
                self._follow_match(target)
        n = ts.pending()
        bits = []
        if n:
            bits.append(f"Checking {n} link(s)...")
        if hidden:
            bits.append(f"{hidden} dead link(s) hidden")
        self._vinfo_base = "   ".join(bits)
        self._on_video_select()

    def _selected_video(self):
        sel = self.vtree.selection()
        return self.vrows.get(sel[0], (None, None)) if sel else (None, None)

    def _on_video_select(self):
        self._show_context()
        res, rf = self._selected_video()
        base = getattr(self, "_vinfo_base", "")
        hint = getattr(self, "_hint", "")
        if hint:
            self.vinfo_var.set(hint)
            return
        if res is None:
            self.vinfo_var.set(base)
            return
        url = rf.url if rf is not None and rf.url else res.ref.url
        sel = self.vtree.selection()
        m = self.cur.matches.get(sel[0]) if self.cur is not None and sel else None
        goes = ""
        if m and self.cur is not None and len(self.cur.sets) > 1:
            goes = f"For: {match_label(self.cur, m)} ({m[1]})   "
        self.vinfo_var.set((base + "   " if base else "") + goes + self._length_compare(rf) + url)

    def _length_compare(self, rf):
        ts = self.cur
        if ts is None or rf is None or not rf.duration:
            return ""
        lens = [i.length for i in ts.scripts if i.checked and i.length_state == "ok" and
                i.ext in (SCRIPT_EXT, ".zip") and not is_axis(i.name[:-len(SCRIPT_EXT)])]
        lens = [x for x in lens if not isinstance(x, tuple)]
        if not lens:
            return ""
        sl = max(lens)
        diff = rf.duration - sl
        if abs(diff) < 3:
            return f"Video {fmt_dur(rf.duration)} = script length.   "
        how = f"{fmt_dur(abs(diff))} {'longer' if diff > 0 else 'shorter'}"
        return f"⚠ Video {fmt_dur(rf.duration)}, script {fmt_dur(sl)} (video is {how}).   "

    def _open_topic(self):
        ts = self.cur
        if ts:
            open_url(ts.topic.url if ts.topic else ts.url)

    def _open_link(self):
        res, rf = self._selected_video()
        if res is not None:
            open_url(rf.url if rf is not None and rf.url else res.ref.url)

    def _recheck(self):
        ts = self.cur
        if ts is None or ts.topic is None:
            return
        extras_reset()
        self._start_checks(ts)
        self._fill_videos()

    def _add_video_link(self):
        ts = self.cur
        if ts is None or ts.topic is None:
            return
        from tkinter import simpledialog
        try:
            clip = self.root.clipboard_get().strip()
        except Exception:
            clip = ""
        url = simpledialog.askstring(
            "Add a video link",
            "Paste the link of the video - its page on any site, or the video file itself.\n\n"
            "Tip: if the program can't find the video on a page, play it in your browser,\n"
            "right-click the video > Copy video address, and paste that here.",
            initialvalue=clip if re.match(r"https?://", clip) else "", parent=self.root)
        url = (url or "").strip()
        if not url:
            return
        if not re.match(r"https?://", url, re.I):
            self.mb.showwarning("Add a video link", "That isn't a web link (it should start with http).",
                                parent=self.root)
            return
        li = add_link(ts, url, self.user or "you")
        if li is None:
            self.mb.showinfo("Add a video link", "That link is already in the list.", parent=self.root)
            return
        gen = ts.gen
        self.checks.submit(self.core.check, ts.topic.links[li], done=lambda res, err, ts=ts, li=li, gen=gen:
                           self.post(self._link_done, ts, li, res, err, gen))
        ts.user_pick = f"L{li}"
        self._hint = ""
        self._refresh_topic_row(ts)
        self._fill_videos()

    def _pick_local(self):
        ts = self.cur
        if ts is None or ts.topic is None:
            return
        exts = " ".join(f"*{e}" for e in sorted(VIDEO_EXTS))
        p = self.fd.askopenfilename(parent=self.root, title="Pick the video for this topic",
                                    filetypes=[("Videos", exts), ("All files", "*.*")])
        if not p:
            return
        ans = self.mb.askyesnocancel(
            "Move or copy?", f"{os.path.basename(p)}\n\nYes = MOVE it into the folder\n"
            "No = COPY it (the original stays where it is)", parent=self.root)
        if ans is None:
            return
        ts.local_video = os.path.normpath(p)
        ts.local_move = bool(ans)
        self._show_local()

    def _forget_local(self):
        if self.cur:
            self.cur.local_video = None
            self._show_local()

    def _show_local(self):
        ts = self.cur
        if ts is not None and ts.local_video:
            how = "moved" if ts.local_move else "copied"
            self.local_var.set(f"Using your video: {os.path.basename(ts.local_video)}  (will be {how} "
                               "into the folder instead of downloading one)")
            self.forget_btn.pack(side="left", padx=8)
        else:
            self.local_var.set("")
            self.forget_btn.pack_forget()

    def _remove_topic(self):
        ts = self.cur
        if ts is None:
            return
        ts.removed = True
        idx = self.topics.index(ts)
        self.topics.remove(ts)
        if self.ttree.exists(ts.key):
            self.ttree.delete(ts.key)
        self.cur = None
        nxt = self.topics[min(idx, len(self.topics) - 1)] if self.topics else None
        if nxt:
            self._select(nxt)
        else:
            self._render()

    def _clear_finished(self):
        for ts in list(self.topics):
            if ts.jobs and all(j.status == "done" for j in ts.jobs):
                ts.removed = True
                self.topics.remove(ts)
                if self.ttree.exists(ts.key):
                    self.ttree.delete(ts.key)
                if ts is self.cur:
                    self.cur = None
        if self.cur is None and self.topics:
            self._select(self.topics[0])
        else:
            self._render()

    def _pick_dest(self):
        d = self.fd.askdirectory(parent=self.root, title="Library folder")
        if d:
            self.dest_var.set(os.path.normpath(d))
            self._save()

    # Downloads
    def _download(self, scripts_only=False):
        ts = self.cur
        if ts is None or ts.topic is None:
            return
        dest = self.dest_var.get().strip().strip('"')
        if not dest:
            self.mb.showwarning("Library folder", "Choose your library folder first.", parent=self.root)
            return
        if os.path.exists(dest) and not os.path.isdir(dest):
            self.mb.showwarning("Library folder", "The library folder is a file, not a folder.",
                                parent=self.root)
            return
        name = self.name_var.get().strip()
        if not name:
            self.mb.showwarning("Folder name", "Type a name for the folder.", parent=self.root)
            return
        scripts = [i for i in ts.scripts if i.checked]
        video, local = None, None
        if not scripts_only:
            if ts.local_video:
                local = ts.local_video
            else:
                res, rf = self._selected_video()
                if res is None:
                    if not self.mb.askyesno("No video selected", "No video is selected.\n\n"
                                            "Download only the scripts?", parent=self.root):
                        return
                elif rf is None and len(res.video_files()) > 1:
                    self.mb.showinfo("Pick a file", "This link has several videos - select the one "
                                     "you want under it.", parent=self.root)
                    return
                elif rf is not None and rf.downloadable:
                    video = rf
                else:
                    obj = rf if rf is not None else res
                    url = rf.url if rf is not None and rf.url else res.ref.url
                    if obj.status in (BROWSER, PAGE, UNKNOWN) and has_webview():
                        video = window_file(res, rf)
                    elif obj.status == CHECKING:
                        self.mb.showinfo("Still checking", "That link is still being checked - give it "
                                         "a second.", parent=self.root)
                        return
                    if video is None and obj.status == DEAD:
                        self.mb.showinfo("Link is gone", "That link doesn't work any more - pick "
                                         "another one.", parent=self.root)
                        return
                    if video is None:
                        note = (rf.note if rf is not None else "") or res.note
                        if self.mb.askyesno(
                                "Open in your browser?",
                                "This one can't be downloaded from here" + (f" ({note})" if note else "") +
                                ".\n\nTip: press Extras... > Install to get the download window, which "
                                "handles sites like this inside the program.\n\nOpen it in your browser "
                                "instead? When the video has downloaded, press \"I already have the "
                                "video...\" to sort it into the folder.", parent=self.root):
                            open_url(url)
                        return
        if not scripts and video is None and not local:
            self.mb.showinfo("Nothing to download", "Tick a script or select a video first.",
                             parent=self.root)
            return
        base = safe_name(name)
        folder = Path(dest) / folder_name(name, scripts, all_items=True)
        have = existing_video(folder, base)
        if (video is not None or local) and have is not None:
            if not self.mb.askyesno("Already in your library",
                                    f"{folder}\nalready has a video: {have.name}\n\nDownload another "
                                    f"one anyway? It's saved next to it as \"{base} (2)\".",
                                    parent=self.root):
                return
        sl = script_length(ts)
        if video is not None and video.duration and sl and video.duration < sl - 10:
            if not self.mb.askyesno(
                    "Video shorter than the script",
                    f"The video is {fmt_dur(video.duration)} long, but the script runs {fmt_dur(sl)}.\n\n"
                    "It's probably a preview or a cut version. Download it anyway?", parent=self.root):
                return
        if video is not None and video.size:
            probe_dir = Path(dest)
            while not probe_dir.exists() and probe_dir.parent != probe_dir:
                probe_dir = probe_dir.parent
            try:
                free = shutil.disk_usage(probe_dir).free
                if free < video.size + 200 * 1024 * 1024 and not self.mb.askyesno(
                        "Low disk space", f"The video is {fmt_size(video.size)} but only "
                        f"{fmt_size(free)} is free there.\n\nTry anyway?", parent=self.root):
                    return
            except OSError:
                pass
        self.st["dest"] = dest
        self._save()
        job = Job(ts, scripts, video, local, ts.local_move, name, dest, ts.main_key)
        self._queue_job(job)
        ts.jobs.append(job)
        self._topic_state(ts, "queued")
        if len(ts.sets) > 1 and self._next_set(ts, scripts):
            return
        nxt = next((t for t in self.topics[self.topics.index(ts) + 1:] if not t.jobs and not t.removed),
                   None) or next((t for t in self.topics if not t.jobs and not t.removed), None)
        if nxt is not None:
            self._select(nxt)

    def _next_set(self, ts, just_queued):
        ids = {id(i) for i in just_queued}
        ts.queued_keys |= {st.key for st in ts.sets if any(id(i) in ids for i in st.items)}
        pool = [n for n, st in enumerate(ts.sets) if st.by_op] or list(range(len(ts.sets)))
        left = [n for n in pool if ts.sets[n].key not in ts.queued_keys]
        if not left:
            return False
        nxt = left[0]
        apply_match(ts, [nxt])
        ts.local_video = None
        ts.main_key = None
        ts.name_edited = False
        ts.name = default_name(ts.scripts, ts.topic.title, ts.main_key)
        rows, _ = video_rows(ts, bool(self.dead_var.get()))
        ts.user_pick = best_row(rows, ts.matches, {ts.sets[nxt].key}, ts.sets,
                                want=script_length(ts, {ts.sets[nxt].key}))
        self._render()
        if ts.user_pick is None:
            self.vtree.selection_set(())
        self._hint = (f"Queued. Next script in this topic: {ts.sets[nxt].label} ({len(left)} left) - "
                      "check its video and download, or move on to another topic.")
        self._on_video_select()
        return True

    def _queue_job(self, job):
        self.jobs.append(job)
        job.iid = f"j{len(self.jobs)}"
        self.jtree.insert("", 0, iid=job.iid, text=safe_name(job.name), values=("queued", "", ""))
        self._update_jobs_label()
        self.job_q.put(job)

    def _worker(self):
        while True:
            job = self.job_q.get()
            if job.cancel.is_set():
                job.status = "cancelled"
                self.post(self._job_update, job)
                continue
            job.status = "downloading"
            self.post(self._job_update, job)
            try:
                run_job(self.core, job, report=lambda job=job: self.post(self._job_update, job))
                job.status = "done"
            except Cancelled:
                job.status = "cancelled"
            except Exception as e:
                job.status = "failed"
                job.error = str(e) or type(e).__name__
                if not isinstance(e, (DownloadError, HttpError, MegaError)):
                    traceback.print_exc()
            self.post(self._job_update, job)
            self.post(self._save)

    def _job_update(self, job):
        if not job.iid or not self.jtree.exists(job.iid):
            return
        if job.status == "downloading":
            status = f"downloading - {job.stage}" if job.stage else "starting..."
            if job.total:
                pct = int(job.done * 100 / max(1, job.total))
                prog = f"{pct}%  ({fmt_size(job.done)} / {fmt_size(job.total)})"
            else:
                prog = fmt_size(job.done) if job.done else ""
            speed = ""
            if job.speed > 1:
                speed = f"{fmt_size(job.speed)}/s"
                if job.total and job.done < job.total:
                    speed += f"  ·  {fmt_dur((job.total - job.done) / job.speed) or '0:01'} left"
            self.jtree.item(job.iid, values=(status, prog, speed), tags=())
        elif job.status == "done":
            n = len(job.saved)
            self.jtree.item(job.iid, values=(f"done ✔  ({n} file(s))", "100%", ""), tags=("done",))
            if job.topic_id is not None:
                self.history = load_history()
        elif job.status == "failed":
            self.jtree.item(job.iid, values=(f"failed: {job.error}", "", ""), tags=("failed",))
        elif job.status == "cancelled":
            self.jtree.item(job.iid, values=("cancelled", "", ""), tags=("cancelled",))
        else:
            self.jtree.item(job.iid, values=(job.status, "", ""))
        if job.ts:
            self._topic_jobs_state(job.ts)
        self._update_jobs_label()

    def _topic_jobs_state(self, ts):
        jobs = ts.jobs
        if not jobs:
            return
        many = f" ({sum(1 for j in jobs if j.status == 'done')}/{len(jobs)})" if len(jobs) > 1 else ""
        run = next((j for j in jobs if j.status == "downloading"), None)
        if run is not None:
            pct = f" {int(run.done * 100 / run.total)}%" if run.total and run.stage == "video" else ""
            self._topic_state(ts, f"downloading{pct}{many}")
        elif any(j.status == "queued" for j in jobs):
            self._topic_state(ts, f"queued{many}")
        elif any(j.status == "failed" for j in jobs):
            self._topic_state(ts, f"failed{many}", "error")
        elif all(j.status == "done" for j in jobs):
            self._topic_state(ts, f"done ✔{many}", "done")
        else:
            self._topic_state(ts, f"cancelled{many}", "error")

    def _update_jobs_label(self):
        active = sum(1 for j in self.jobs if j.status in ("queued", "downloading"))
        self.jobs_var.set(f"{active} active" if active else "")

    def _selected_job(self):
        sel = self.jtree.selection()
        return next((j for j in self.jobs if sel and j.iid == sel[0]), None)

    def _open_job_folder(self):
        j = self._selected_job()
        if j is not None:
            p = j.folder or Path(j.dest) / folder_name(j.name, j.scripts, all_items=True)
            open_path(p if Path(p).exists() else j.dest)

    def _cancel_job(self):
        j = self._selected_job()
        if j is not None and j.status in ("queued", "downloading"):
            j.cancel.set()
            if j.status == "queued":
                j.status = "cancelled"
                self._job_update(j)

    def _retry_job(self):
        j = self._selected_job()
        if j is None or j.status not in ("failed", "cancelled"):
            return
        nj = j.clone()
        if j.ts:
            j.ts.jobs = [nj if x is j else x for x in j.ts.jobs]
            self._topic_state(j.ts, "queued")
        self._queue_job(nj)

    def _clear_jobs(self):
        for j in list(self.jobs):
            if j.status in ("done", "cancelled", "failed") and self.jtree.exists(j.iid):
                self.jtree.delete(j.iid)
                self.jobs.remove(j)
        self._update_jobs_label()

    def _on_close(self):
        active = [j for j in self.jobs if j.status in ("queued", "downloading")]
        if active and not self.mb.askyesno(
                "Quit?", f"{len(active)} download(s) are still running or waiting.\n\nQuit anyway? "
                "(Unfinished downloads continue where they stopped when you retry them.)",
                parent=self.root):
            return
        self._save()
        self.root.destroy()


def gui_main():
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    try:
        import tkinter
    except ImportError:
        return None
    App().run()
    return 0


# Console


def ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        raise KeyboardInterrupt() from None


def _console_report(job):
    last = {"t": 0.0}

    def report():
        now = time.monotonic()
        if now - last["t"] < 0.3:
            return
        last["t"] = now
        bits = [f"  {job.stage}"]
        if job.total:
            bits.append(f"{int(job.done * 100 / max(1, job.total)):3d}%  {fmt_size(job.done)} / {fmt_size(job.total)}")
        elif job.done:
            bits.append(fmt_size(job.done))
        if job.speed > 1:
            bits.append(f"{fmt_size(job.speed)}/s")
        line = "   ".join(bits)
        sys.stdout.write("\r" + line[:110].ljust(110))
        sys.stdout.flush()
    return report


def _print_rows(rows, ts=None):
    for n, (rid, res, rf, depth) in enumerate(rows, 1):
        obj = rf if rf is not None else res
        st = STATUS_TEXT.get(obj.status, "")
        color = green if obj.status == ONLINE else (red if obj.status == DEAD else yellow)
        if rf is None and len(res.video_files()) > 1:
            print(f"      {color(st):<16} {res.host}: {len(res.video_files())} videos  {dim(res.ref.where)}")
            continue
        name = rf.name if rf is not None else (res.ref.text or res.ref.url)
        size = fmt_size(rf.size) if rf is not None and rf.size else ""
        dur = fmt_dur(rf.duration) if rf is not None else ""
        indent = "    " if depth else ""
        goes = ""
        if ts is not None and len(ts.sets) > 1 and ts.matches.get(rid):
            goes = cyan(f"  -> {match_label(ts, ts.matches[rid])}")
        print(f"  {n:>2}) {indent}{color(st):<16} {res.host if not depth else '':<14} {name}  "
              f"{dim(' '.join(x for x in (size, dur) if x))}{goes}")
        note = (rf.note if rf is not None and rf.note else res.note)
        print(dim(f"          {indent}{(res.ref.where + ' | ') if not depth else ''}"
                  f"{(note + ' | ') if note else ''}{rf.url if rf is not None and rf.url else res.ref.url}"))
        says = post_snippet(ts.topic, res.ref.post, res.ref.span, 110) if ts is not None and not depth else ""
        if says:
            print(f"          {cyan('post says:')} {says}")


def print_post(topic, post, span=None):
    meta = topic.posts.get(post) if topic is not None else None
    if not post:
        print(dim("  You added that link yourself - it isn't in a post."))
        return
    if not meta:
        print(dim(f"  Post #{post} wasn't read."))
        return
    head = f"Post #{post} by {meta['user']}" + (f"  ·  {meta['date']}" if meta.get("date") else "")
    print("\n" + bold(head) + dim(f"   {topic.post_url(post)}"))
    if meta.get("reply_to"):
        said = post_snippet(topic, meta["reply_to"], None, 150)
        print(dim(f"  In reply to #{meta['reply_to']}" + (f": {said}" if said else "")))
    text = meta.get("text") or "(no text)"
    if span and span[0] is not None and _Color.on:
        a, b = max(0, span[0]), max(span[0], span[1])
        text = text[:a] + _c(text[a:b], "1;33") + text[b:]
    for line in text.split("\n"):
        print("  " + line)
    print()


def cli_topic(core, url, dest, args):
    print()
    print(bold(f"Loading {url} ..."))
    topic = core.forum.topic(url, max_posts=args.max_posts, replies=not args.no_replies)
    ts = TopicState(url)
    ts.set_topic(topic)
    print(bold(cyan(topic.title)) + dim(f"  by {topic.author}, {topic.posts_count} post(s)"))
    links = topic.links
    reads = [it for it in ts.scripts if wants_length(it)] \
        if core.st.get("script_lengths", True) and not args.no_lengths else []
    print(f"Checking {len(links)} link(s)" + (f" and reading {len(reads)} script(s)..." if reads else "..."))
    pool = Pool(6)
    done_ev = threading.Event()
    lock = threading.Lock()
    left = {"n": len(links) + len(reads)}

    def read_done(res, err):
        with lock:
            left["n"] -= 1
            if left["n"] <= 0:
                done_ev.set()
    for it in reads:
        pool.submit(it.read_length, core, done=read_done)
    for li, ref in enumerate(links):
        def done(res, err, li=li, ref=ref):
            with lock:
                if res is None:
                    res = LinkResult(ref, status=UNKNOWN, note=str(err))
                ts.results[li] = res
                left["n"] -= 1
                if left["n"] <= 0:
                    done_ev.set()
        pool.submit(core.check, ref, done=done)
    if not links and not reads:
        done_ev.set()
    total = len(links) + len(reads)
    while not done_ev.wait(0.3):
        sys.stdout.write(f"\r  {total - left['n']}/{total} done")
        sys.stdout.flush()
    sys.stdout.write("\r" + " " * 40 + "\r")
    drop_site_videos(ts)
    before = len(ts.scripts)
    for res in ts.results.values():
        ts.add_remote_scripts(res)
    if reads or (core.st.get("script_lengths", True) and not args.no_lengths):
        for it in ts.scripts[before:]:
            it.read_length(core)
    ts.matches = match_videos(ts)

    def show_scripts():
        print(bold("\nScripts:"))
        if not ts.scripts:
            print(dim("  (no script attachments in the topic)"))
        for n, it in enumerate(ts.scripts, 1):
            mark = green("[x]") if it.checked else "[ ]"
            length = it.length_text()
            print(f"  {n:>2}) {mark} {it.name}  {dim(it.size_text)}  {cyan(length) if length else ''}  "
                  f"{dim(it.where)}")
            says = post_snippet(ts.topic, it.post, it.span, 110)
            if says:
                print(f"          {cyan('post says:')} {says}")
    if len(ts.sets) > 1:
        print(dim(f"\nThis topic has {len(ts.sets)} different scripts: "
                  + ", ".join(st.label for st in ts.sets) + ". The script each video goes with is "
                  "shown after it (->)."))
    else:
        show_scripts()

    show_dead = False
    video, local, vrid = None, None, None
    while True:
        rows, hidden = video_rows(ts, show_dead)
        pickable = [(rid, res, rf) for rid, res, rf, d in rows]
        print(bold("\nVideos:"))
        if not rows:
            print(dim("  No working video links."))
        _print_rows(rows, ts)
        if hidden:
            print(dim(f"  ({hidden} dead link(s) hidden - type d to show them)"))
        best = best_row(rows)
        best_n = next((n for n, (rid, *_x) in enumerate(pickable, 1) if rid == best), None)
        if args.auto:
            if best_n:
                vrid, _, video = pickable[best_n - 1]
            break
        a = ask(f"Video to download [Enter = {best_n or 'none'}, 0 = none, o# = open in browser, "
                f"p# = show its post, a = add a video link, f = a file you already have"
                f"{', d = show dead' if hidden else ''}]: ").strip().lower()
        if a == "" and best_n:
            vrid, _, video = pickable[best_n - 1]
            break
        if a in ("", "0"):
            break
        if a == "d":
            show_dead = True
            continue
        if a == "a":
            u = ask("Video link (its page on any site, or the file itself): ").strip()
            if re.match(r"https?://", u, re.I):
                li = add_link(ts, u)
                if li is None:
                    print(yellow("  Already in the list."))
                else:
                    print("  Checking...")
                    ts.results[li] = core.check(ts.topic.links[li])
                    ts.matches = match_videos(ts)
            continue
        if a == "f":
            p = ask("Path of your video: ").strip().strip('"')
            if os.path.isfile(p):
                local = p
                break
            print(red("  Can't find that file."))
            continue
        m = re.fullmatch(r"p\s*(\d+)", a)
        if m:
            n = int(m.group(1))
            if 1 <= n <= len(pickable):
                _, res, rf = pickable[n - 1]
                print_post(ts.topic, res.ref.post, res.ref.span)
            continue
        m = re.fullmatch(r"o\s*(\d+)", a)
        if m:
            n = int(m.group(1))
            if 1 <= n <= len(pickable):
                _, res, rf = pickable[n - 1]
                open_url(rf.url if rf is not None and rf.url else res.ref.url)
            continue
        if a.isdigit() and 1 <= int(a) <= len(pickable):
            rid, res, rf = pickable[int(a) - 1]
            if rf is not None and rf.downloadable:
                vrid, video = rid, rf
                break
            if has_webview() and (rf or res).status in (BROWSER, PAGE, UNKNOWN):
                print(dim("  That one opens in the download window."))
                vrid, video = rid, window_file(res, rf)
                break
            print(yellow("  That one can't be downloaded from here - type o" + a +
                         " to open it in your browser, then use f to point to the file."))
            continue
        print(red("  Didn't catch that."))

    if len(ts.sets) > 1:
        m = ts.matches.get(vrid) if vrid else None
        if m:
            apply_match(ts, m[0])
            print(dim(f"Ticked the script(s) for that video: {match_label(ts, m)} ({m[1]})"))
        show_scripts()
    if ts.scripts and not args.auto:
        a = ask("Which scripts? [Enter = the ticked ones, e.g. 1,3 / 0 = none]: ").strip()
        if a == "0":
            for it in ts.scripts:
                it.checked = False
        elif a:
            want = {int(x) for x in re.findall(r"\d+", a)}
            for n, it in enumerate(ts.scripts, 1):
                it.checked = n in want
    mains = main_scripts(ts.scripts)
    if len(mains) > 1 and not args.auto:
        print(bold("\nMain script (gets the folder name, with the video - the others keep their names):"))
        for n, it in enumerate(mains, 1):
            print(f"  {n:>2}) {it.name}")
        a = ask("Which one? [Enter = 1]: ").strip()
        if a.isdigit() and 1 <= int(a) <= len(mains):
            ts.main_key = mains[int(a) - 1].name[:-len(SCRIPT_EXT)].casefold()
    name = default_name(ts.scripts, topic.title, ts.main_key)

    scripts = [i for i in ts.scripts if i.checked]
    if not scripts and video is None and not local:
        print("Nothing to download.")
        return 0
    if not args.auto:
        n = ask(f"Folder name [{safe_name(name)}]: ").strip()
        name = n or name
    folder = Path(dest) / folder_name(name, scripts, all_items=True)
    print(f"Saving to {folder}")
    if args.dry_run:
        print(yellow("Dry run - nothing downloaded."))
        return 0
    move = True
    if local and not args.auto:
        move = not ask("Move it (M) or copy it (c)? ").strip().lower().startswith("c")
    job = Job(ts, scripts, video, local, move, name, dest, ts.main_key)
    try:
        run_job(core, job, _console_report(job))
    except Cancelled:
        print(yellow("\nCancelled."))
        return 1
    except Exception as e:
        print(red(f"\nFailed: {e}"))
        return 1
    sys.stdout.write("\r" + " " * 110 + "\r")
    print(green(f"Done: {len(job.saved)} file(s) in {folder}"))
    for p in job.saved:
        print(dim(f"   {p.name}"))
    return 0


def cli_main(args):
    st = load_settings()
    if args.site:
        st["site"] = args.site
    core = Core(st)
    if args.cookie:
        core.forum.set_cookie_string(args.cookie)
    print(bold(f"\n=== EroScripts Downloader {VERSION} ==="))
    user = None
    if args.login:
        pw = getpass.getpass(f"Password for {args.login}: ")
        try:
            user = core.forum.login(args.login, pw)
        except LoginError as e:
            if not e.need_2fa:
                print(red(f"Login failed: {e}"))
                return 1
            otp = ask("2-factor code: ").strip()
            try:
                user = core.forum.login(args.login, pw, otp)
            except LoginError as e2:
                print(red(f"Login failed: {e2}"))
                return 1
        st["username"] = user
    else:
        try:
            user = core.forum.current_user() if core.forum.cookie_string() else None
        except Exception:
            user = None
    print(f"Logged in as {user}" if user else yellow("Not logged in - script downloads need an account "
                                                     "(use --login USERNAME)."))
    st["cookie"] = core.forum.cookie_string() or st["cookie"]
    save_settings(st)
    if not core.has_ytdlp():
        print(dim("Tip: pip install yt-dlp  -> downloads from tube sites too."))
    if not core.has_crypto():
        print(dim("Tip: pip install pycryptodome  -> downloads from Mega too."))
    urls = list(args.urls)
    if not urls and args.login and not args.cli:
        return 0
    dest = args.dest or st["dest"]
    while not dest:
        dest = ask("Library folder (where the folders go): ").strip().strip('"')
    st["dest"] = dest
    if not urls:
        urls = find_topic_urls(ask("Topic link(s): "), core.forum.host)
    rc = 0
    for u in urls:
        try:
            rc |= cli_topic(core, u, dest, args)
        except KeyboardInterrupt:
            print(yellow("\nStopped."))
            rc = 1
            break
        except Exception as e:
            print(red(friendly_error(e, bool(user))))
            rc = 1
        st["cookie"] = core.forum.cookie_string() or st["cookie"]
        save_settings(st)
    return rc


def build_parser():
    p = argparse.ArgumentParser(description="Download scripts + videos from EroScripts topics "
                                            "into their own folders.")
    p.add_argument("urls", nargs="*", help="topic link(s)")
    p.add_argument("--cli", action="store_true", help="use the console instead of the window")
    p.add_argument("--dest", metavar="DIR", help="library folder the topic folders go into")
    p.add_argument("--login", metavar="USERNAME", help="log in (asks for the password)")
    p.add_argument("--cookie", metavar="COOKIE", help="use this browser cookie (_t value or Cookie header)")
    p.add_argument("--site", metavar="URL", help=f"forum address (default {DEFAULT_SITE})")
    p.add_argument("--auto", action="store_true",
                   help="no questions: ticked scripts + the best online video")
    p.add_argument("--no-replies", action="store_true", help="only read the first post")
    p.add_argument("--max-posts", type=int, default=400, help="read at most this many posts (default 400)")
    p.add_argument("--dry-run", action="store_true", help="show what would be downloaded, then stop")
    p.add_argument("--no-lengths", action="store_true",
                   help="don't download the scripts up front to show how long they run")
    p.add_argument("--grab", metavar="URL", help=argparse.SUPPRESS)
    p.add_argument("--out", help=argparse.SUPPRESS)
    p.add_argument("--base", help=argparse.SUPPRESS)
    p.add_argument("--status", help=argparse.SUPPRESS)
    p.add_argument("--title", default="", help=argparse.SUPPRESS)
    p.add_argument("--autoclick", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--insecure", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--grab-timeout", type=float, default=0, help=argparse.SUPPRESS)
    return p


def main(argv=None):
    setup_console()
    args = build_parser().parse_args(argv)
    if args.grab:
        return grab_main(args)
    if not (args.cli or args.urls or args.login):
        rc = gui_main()
        if rc is not None:
            return rc
        print(yellow("The window couldn't open (tkinter is missing) - using the console instead."))
    try:
        return cli_main(args)
    except KeyboardInterrupt:
        print("\n" + yellow("Cancelled."))
        return 1


if __name__ == "__main__":
    sys.exit(main())

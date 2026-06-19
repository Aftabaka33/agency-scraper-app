"""
Home Services Lead Scraper Pro — Streamlit Web App
===================================================
Production-ready cloud-hostable web application with proxy rotation
and anti-blocking technology for Yellow Pages scraping.

Author: Blue Ocean Digital Products
License: Commercial - See LICENSE.txt for details
"""

import csv
import io
import json
import os
import re
import sys
import time
import random
import threading
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent

# ---------------------------------------------------------------------------
# Streamlit imports
# ---------------------------------------------------------------------------
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Home Services Lead Scraper PRO",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for professional look
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    :root {
        --primary: #1a73e8;
        --primary-dark: #1557b0;
        --bg: #f8f9fa;
        --card-bg: #ffffff;
        --text: #202124;
        --text-secondary: #5f6368;
        --success: #0f9d58;
        --warning: #f29900;
        --error: #d93025;
        --border: #dadce0;
    }

    * { box-sizing: border-box; }

    html, body {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem;
        background: linear-gradient(135deg, #1a73e8 0%, #4285f4 50%, #0f9d58 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(26,115,232,0.25);
    }

    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .main-header p {
        font-size: 1.1rem;
        opacity: 0.92;
        margin-top: 0.5rem;
    }

    .badge-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .badge {
        background: rgba(255,255,255,0.2);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
    }

    .card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .card h3 {
        margin-top: 0;
        font-size: 1.15rem;
        color: var(--text);
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .stat-box {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }

    .stat-box .value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }

    .stat-box .label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }

    .stDownloadButton>button {
        background: var(--success) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }

    .stDownloadButton>button:hover {
        background: #0b8043 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(15,157,88,0.3);
    }

    .log-box {
        background: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.85rem;
        padding: 1rem;
        border-radius: 8px;
        max-height: 320px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .log-info { color: #4fc3f7; }
    .log-success { color: #81c784; }
    .log-warning { color: #ffb74d; }
    .log-error { color: #e57373; }

    footer {
        text-align: center;
        padding: 2rem 1rem;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "scrape_running": False,
        "scrape_done": False,
        "businesses": [],
        "logs": [],
        "progress": 0.0,
        "status_text": "Idle",
        "csv_bytes": None,
        "csv_filename": "",
        "proxy_mode": "Direct",
        "premium_api_key": "",
        "premium_api_url": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session_state()


# ---------------------------------------------------------------------------
# Proxy Manager
# ---------------------------------------------------------------------------
class ProxyManager:
    """
    Modular 3-tier proxy system:
      1. Direct (no proxy) — default, works on localhost.
      2. Free public proxies — fetched from public APIs, auto-rotated on failure.
      3. Premium scraping APIs — ScraperAPI, ScrapingBee, etc. Drop-in configurable.

    Usage:
        pm = ProxyManager(mode="Direct")          # no proxy
        pm = ProxyManager(mode="Free Proxies")    # auto-rotate free proxies
        pm = ProxyManager(
            mode="Premium API",
            premium_api_url="http://api.scraperapi.com?key=...",
            premium_api_key="YOUR_KEY"
        )
    """

    FREE_PROXY_SOURCES = [
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_https.txt",
    ]

    def __init__(self, mode="Direct", premium_api_url="", premium_api_key=""):
        self.mode = mode
        self.premium_api_url = premium_api_url
        self.premium_api_key = premium_api_key
        self.free_proxies = []
        self.free_proxy_index = 0
        self.current_proxy = None
        self.failure_counts = {}

    # ------------------------------------------------------------------
    # Fetch free proxies
    # ------------------------------------------------------------------
    def fetch_free_proxies(self, max_proxies=30):
        """Try multiple sources to fetch a list of working HTTPS proxies."""
        proxies = set()
        headers = {"User-Agent": UserAgent().random}

        for source in self.FREE_PROXY_SOURCES:
            try:
                resp = requests.get(source, headers=headers, timeout=10)
                if resp.status_code == 200:
                    for line in resp.text.strip().split("\n"):
                        line = line.strip()
                        if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", line):
                            proxies.add(f"http://{line}")
                if len(proxies) >= max_proxies:
                    break
            except Exception:
                continue

        self.free_proxies = list(proxies)
        return self.free_proxies

    # ------------------------------------------------------------------
    # Get next proxy dict for requests
    # ------------------------------------------------------------------
    def get_proxy_dict(self):
        if self.mode == "Direct":
            return None

        if self.mode == "Premium API":
            return self._build_premium_proxy()

        if self.mode == "Free Proxies":
            return self._get_next_free_proxy()

        return None

    def _build_premium_proxy(self):
        """Build proxy dict for premium scraping APIs."""
        if not self.premium_api_url:
            return None
        return {"http": self.premium_api_url, "https": self.premium_api_url}

    def _get_next_free_proxy(self):
        """Round-robin through free proxies, skipping known-bad ones."""
        if not self.free_proxies:
            self.fetch_free_proxies()

        if not self.free_proxies:
            return None

        for _ in range(len(self.free_proxies)):
            proxy = self.free_proxies[self.free_proxy_index]
            self.free_proxy_index = (self.free_proxy_index + 1) % len(self.free_proxies)
            if self.failure_counts.get(proxy, 0) < 3:
                return {"http": proxy, "https": proxy}

        # All proxies exhausted
        self.free_proxies = []
        self.free_proxy_index = 0
        return None

    # ------------------------------------------------------------------
    # Mark proxy as failed / success
    # ------------------------------------------------------------------
    def mark_success(self, proxy):
        if proxy:
            self.failure_counts.pop(proxy, None)

    def mark_failure(self, proxy):
        if proxy:
            self.failure_counts[proxy] = self.failure_counts.get(proxy, 0) + 1


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------
def add_log(message, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")
    if len(st.session_state.logs) > 200:
        st.session_state.logs = st.session_state.logs[-200:]


# ---------------------------------------------------------------------------
# Scraping helpers (refactored from agency_scraper.py)
# ---------------------------------------------------------------------------
def get_random_headers():
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Referer": "https://www.yellowpages.com/",
    }


def random_delay(min_delay=2, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))


def extract_phone(text):
    if not text:
        return ""
    patterns = [
        r"\(?\d{3}\)?[-.\\s]\\d{3}[-.\\s]\\d{4}",
        r"\\+?1[-.\\s]?\\(?\\d{3}\\)?[-.\\s]\\d{3}[-.\\s]\\d{4}",
        r"\\d{3}[-.\\s]\\d{3}[-.\\s]\\d{4}",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return ""


def extract_email_from_url(url, session, headers, proxy_manager):
    if not url or not url.startswith("http"):
        return ""
    try:
        random_delay()
        proxy = proxy_manager.get_proxy_dict()
        resp = session.get(
            url, headers=headers, timeout=15, allow_redirects=True, proxies=proxy
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}", text)
        junk = {
            "example@example.com", "email@example.com", "your@email.com",
            "name@domain.com", "user@example.com", "info@example.com",
            "support@example.com", "admin@example.com", "webmaster@example.com",
        }
        valid = [
            e for e in emails
            if e.lower() not in junk
            and not e.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js", ".json", ".xml"))
            and "noreply" not in e.lower()
        ]
        if valid:
            return valid[0]
        mailto_links = soup.find_all("a", href=re.compile(r"^mailto:", re.I))
        if mailto_links:
            href = mailto_links[0].get("href", "")
            m = re.search(r"mailto:([^?]+)", href)
            if m and m.group(1) not in junk:
                return m.group(1)
        return ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Yellow Pages parsing
# ---------------------------------------------------------------------------
def build_yellowpages_url(service, city, page=1):
    query = f"{service} {city}"
    encoded = quote_plus(query)
    base = "https://www.yellowpages.com/search"
    if page == 1:
        return f"{base}?search_terms={encoded}"
    return f"{base}?search_terms={encoded}&page={page}"


def parse_yellowpages_listing(container, service, city):
    try:
        name = ""
        for selector in [
            ("a", re.compile("business-name", re.I)),
            ("h2", None),
            ("span", re.compile("business-name", re.I)),
        ]:
            tag, cls = selector
            el = container.find(tag, class_=cls) if cls else container.find(tag)
            if el:
                name = el.get_text(strip=True)
                if name:
                    break

        if not name or len(name) < 2:
            return None

        phone = ""
        phone_el = container.find("div", class_=re.compile("phones|phone", re.I))
        if phone_el:
            phone = phone_el.get_text(strip=True)
        if not phone:
            phone = extract_phone(container.get_text())

        website = ""
        link_el = container.find("a", class_=re.compile("track-visit-website|website-link", re.I))
        if link_el:
            website = link_el.get("href", "")
        if not website:
            for a in container.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "yellowpages.com" not in href:
                    website = href
                    break

        address = ""
        addr_el = container.find("div", class_=re.compile("street-address|adr", re.I))
        if addr_el:
            address = addr_el.get_text(strip=True)

        return {
            "Business Name": name,
            "Phone Number": phone,
            "Website URL": website,
            "Email Address": "",
            "Service Type": service,
            "City Searched": city,
            "Address": address,
            "Date Scraped": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main scraping function (used inside a thread to keep UI responsive)
# ---------------------------------------------------------------------------
def run_scrape(service, city, max_pages, proxy_mode, premium_api_url, premium_api_key, progress_callback=None):
    """
    Runs the scrape in a background thread. Updates st.session_state.
    progress_callback(current_page, total_pages, message) -> None
    """
    proxy_manager = ProxyManager(
        mode=proxy_mode,
        premium_api_url=premium_api_url,
        premium_api_key=premium_api_key,
    )

    if proxy_mode == "Free Proxies":
        add_log("Fetching free proxies...", "info")
        proxies = proxy_manager.fetch_free_proxies()
        add_log(f"Loaded {len(proxies)} free proxies.", "info")

    businesses = []
    session = requests.Session()
    headers = get_random_headers()

    add_log(f"Target: {service} in {city}", "info")
    add_log(f"Proxy mode: {proxy_mode}", "info")

    for page in range(1, max_pages + 1):
        if not st.session_state.scrape_running:
            add_log("Scrape stopped by user.", "warning")
            break

        url = build_yellowpages_url(service, city, page)
        if progress_callback:
            progress_callback(page, max_pages, f"Page {page}/{max_pages} — fetching...")

        try:
            random_delay()
            proxy = proxy_manager.get_proxy_dict()
            resp = session.get(url, headers=headers, timeout=20, proxies=proxy)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            page_businesses = []

            # Primary parser
            results = soup.find_all("div", class_=re.compile("result|listing|v-card", re.I))
            for result in results:
                biz = parse_yellowpages_listing(result, service, city)
                if biz:
                    page_businesses.append(biz)

            # Fallback 1
            if not page_businesses:
                results = soup.find_all("div", class_=re.compile("srp-listing|search-result", re.I))
                for result in results:
                    biz = parse_yellowpages_listing(result, service, city)
                    if biz:
                        page_businesses.append(biz)

            # Fallback 2: broad div scan
            if not page_businesses:
                for div in soup.find_all("div"):
                    text = div.get_text()
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    if len(lines) < 2:
                        continue
                    potential_name = lines[0]
                    if len(potential_name) < 3 or len(potential_name) > 80:
                        continue
                    phone_found = extract_phone(text)
                    if phone_found:
                        links = div.find_all("a", href=True)
                        website = ""
                        for a in links:
                            href = a["href"]
                            if href.startswith("http") and "yellowpages.com" not in href:
                                website = href
                                break
                        page_businesses.append({
                            "Business Name": potential_name,
                            "Phone Number": phone_found,
                            "Website URL": website,
                            "Email Address": "",
                            "Service Type": service,
                            "City Searched": city,
                            "Address": "",
                            "Date Scraped": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                        if len(page_businesses) >= 20:
                            break

            businesses.extend(page_businesses)
            if progress_callback:
                progress_callback(page, max_pages, f"Page {page}/{max_pages} — found {len(page_businesses)} leads")

            if proxy:
                proxy_manager.mark_success(proxy)

            if not page_businesses and page > 1:
                add_log("Very few results. Stopping early.", "warning")
                break

        except Exception as e:
            add_log(f"Error on page {page}: {e}", "error")
            if proxy:
                proxy_manager.mark_failure(proxy)
            continue

    # Email enrichment pass
    add_log(f"Enriching {len(businesses)} leads with emails...", "info")
    for i, biz in enumerate(businesses):
        if not st.session_state.scrape_running:
            break
        website = biz.get("Website URL", "")
        if website and website.startswith("http"):
            biz["Email Address"] = extract_email_from_url(website, session, headers, proxy_manager)
        if (i + 1) % 10 == 0:
            if progress_callback:
                progress_callback(max_pages, max_pages, f"Enriching emails... {i+1}/{len(businesses)}")

    # Deduplicate
    seen = set()
    unique = []
    for biz in businesses:
        key = (biz["Business Name"], biz.get("Phone Number", ""))
        if key not in seen:
            seen.add(key)
            unique.append(biz)

    st.session_state.businesses = unique
    st.session_state.scrape_done = True
    st.session_state.scrape_running = False

    # Build CSV in memory
    if unique:
        df = pd.DataFrame(unique)
        column_order = ["Business Name", "Phone Number", "Website URL", "Email Address",
                        "Service Type", "City Searched", "Address", "Date Scraped"]
        cols = [c for c in column_order if c in df.columns]
        df = df[cols]
        df = df.drop_duplicates(subset=["Business Name", "Phone Number"]).reset_index(drop=True)
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.session_state.csv_bytes = csv_buf.getvalue().encode("utf-8-sig")
        st.session_state.csv_filename = f"leads_{service}_{city}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    add_log(f"Scrape complete! {len(unique)} leads found.", "success")
    if progress_callback:
        progress_callback(max_pages, max_pages, "Done!")


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Settings")

        st.subheader("Proxy / Anti-Blocking")
        proxy_mode = st.selectbox(
            "Proxy Mode",
            ["Direct", "Free Proxies", "Premium API"],
            index=0,
            help="Choose how requests are routed to avoid IP blocks.",
        )

        premium_api_url = ""
        premium_api_key = ""
        if proxy_mode == "Premium API":
            st.info(
                "Enter your premium scraping API endpoint.\n\n"
                "Examples:\n"
                "- ScraperAPI: `http://api.scraperapi.com?api_key=YOUR_KEY&autoparse=true&url=`\n"
                "- ScrapingBee: `https://app.scrapingbee.com/api/v1?api_key=YOUR_KEY&url=`"
            )
            premium_api_url = st.text_input(
                "Premium API Base URL",
                placeholder="http://api.scraperapi.com?api_key=...",
            )
            premium_api_key = st.text_input(
                "API Key (optional, if not in URL)",
                type="password",
            )

        st.subheader("Scrape Limits")
        max_pages = st.slider("Pages to scrape", 1, 10, 5)
        min_delay = st.slider("Min delay (sec)", 1, 5, 2)
        max_delay = st.slider("Max delay (sec)", 2, 10, 5)

        st.subheader("About")
        st.markdown(
            """
            **Home Services Lead Scraper PRO**

            Scrapes Yellow Pages for local home service business leads.

            Built with Streamlit + BeautifulSoup.
            """
        )

    return proxy_mode, premium_api_url, premium_api_key, max_pages, min_delay, max_delay


def render_main(proxy_mode, premium_api_url, premium_api_key, max_pages, min_delay, max_delay):
    # Banner
    st.markdown(
        """
    <div class="main-header">
        <h1>🏠 Home Services Lead Scraper PRO</h1>
        <p>Generate unlimited web design & SEO client leads in minutes</p>
        <div class="badge-row">
            <span class="badge">⚡ Anti-Blocking</span>
            <span class="badge">📊 CSV Export</span>
            <span class="badge">🎯 Targeted Leads</span>
            <span class="badge">🌐 Cloud-Ready</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Main input card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Define Your Target")
    col1, col2 = st.columns(2)
    with col1:
        service = st.text_input(
            "Service Type",
            placeholder="e.g., roofer, plumber, electrician, HVAC",
            label_visibility="visible",
        )
    with col2:
        city = st.text_input(
            "City / Area",
            placeholder="e.g., Dallas TX, London UK, Chicago IL",
            label_visibility="visible",
        )

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
    with col_btn1:
        start_btn = st.button(
            "🚀 Generate Leads",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.scrape_running,
        )
    with col_btn2:
        stop_btn = st.button(
            "⏹️ Stop",
            type="secondary",
            use_container_width=True,
            disabled=not st.session_state.scrape_running,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Handle start/stop
    if start_btn:
        if not service.strip() or not city.strip():
            st.warning("Please enter both a Service Type and a City.")
        else:
            st.session_state.scrape_running = True
            st.session_state.scrape_done = False
            st.session_state.businesses = []
            st.session_state.csv_bytes = None
            st.session_state.logs = []
            st.session_state.progress = 0.0
            st.session_state.status_text = "Starting..."

            # Persist runtime params into session so thread can read them
            st.session_state.proxy_mode = proxy_mode
            st.session_state.premium_api_url = premium_api_url
            st.session_state.premium_api_key = premium_api_key
            st.session_state.max_pages = max_pages
            st.session_state.min_delay = min_delay
            st.session_state.max_delay = max_delay

            thread = threading.Thread(
                target=_scrape_thread_target,
                args=(service.strip(), city.strip()),
                daemon=True,
            )
            thread.start()
            st.rerun()

    if stop_btn:
        st.session_state.scrape_running = False
        add_log("Stop requested by user.", "warning")
        st.rerun()

    # Status + Progress
    if st.session_state.scrape_running or st.session_state.scrape_done:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Live Status")

        # Progress bar
        progress = st.progress(
            st.session_state.progress,
            text=st.session_state.status_text,
        )

        # Stats
        if st.session_state.businesses:
            biz = st.session_state.businesses
            with_phone = sum(1 for b in biz if b.get("Phone Number"))
            with_email = sum(1 for b in biz if b.get("Email Address"))
            with_website = sum(1 for b in biz if b.get("Website URL"))

            st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="stat-box"><div class="value">{len(biz)}</div><div class="label">Total Leads</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="stat-box"><div class="value">{with_phone}</div><div class="label">With Phone</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="stat-box"><div class="value">{with_email}</div><div class="label">With Email</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="stat-box"><div class="value">{with_website}</div><div class="label">With Website</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Logs
        st.markdown("#### 📋 Activity Log")
        log_html = '<div class="log-box">'
        for entry in st.session_state.logs[-30:]:
            level = "log-info"
            if "error" in entry.lower():
                level = "log-error"
            elif "warning" in entry.lower():
                level = "log-warning"
            elif "success" in entry.lower() or "complete" in entry.lower():
                level = "log-success"
            log_html += f'<span class="{level}">{entry}</span>\n'
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Results + Download
    if st.session_state.scrape_done and st.session_state.csv_bytes:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Download Your Leads")
        st.success(
            f"✅ Scrape complete! Found {len(st.session_state.businesses)} unique leads."
        )
        st.download_button(
            label="📥 Download CSV File",
            data=st.session_state.csv_bytes,
            file_name=st.session_state.csv_filename,
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Data preview
        with st.expander("👁️ Preview first 20 leads"):
            df = pd.read_csv(io.StringIO(st.session_state.csv_bytes.decode("utf-8-sig")))
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Thread target wrapper (reads runtime params from session state)
# ---------------------------------------------------------------------------
def _scrape_thread_target(service, city):
    run_scrape(
        service=service,
        city=city,
        max_pages=st.session_state.get("max_pages", 5),
        proxy_mode=st.session_state.get("proxy_mode", "Direct"),
        premium_api_url=st.session_state.get("premium_api_url", ""),
        premium_api_key=st.session_state.get("premium_api_key", ""),
        progress_callback=_progress_callback,
    )


def _progress_callback(current, total, message):
    st.session_state.progress = current / total if total > 0 else 0
    st.session_state.status_text = message
    add_log(message, "info")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    proxy_mode, premium_api_url, premium_api_key, max_pages, min_delay, max_delay = render_sidebar()
    render_main(proxy_mode, premium_api_url, premium_api_key, max_pages, min_delay, max_delay)

    # Footer
    st.markdown(
        """
    <footer>
        Home Services Lead Scraper PRO · Your Unfair Advantage in Client Acquisition
    </footer>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
"""
Home Services Lead Scraper Pro — Streamlit Web App (Cloud Stable)
=================================================================
Production-ready cloud-hostable web application.
Synchronous execution (no threading) with Standard Mode scraping.

Author: Blue Ocean Digital Products
License: Commercial - See LICENSE.txt for details
"""

import io
import re
import time
import random
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Lead Scraper PRO | ToolPilot Design",
    page_icon="🏠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Backend configuration
# ---------------------------------------------------------------------------
GLOBAL_SCRAPE_STOPS = {}


def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UserAgent().random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Referer": "https://www.yellowpages.com/",
    })
    return s


def random_delay(min_delay=2, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))


def extract_phone(text):
    if not text:
        return ""
    patterns = [
        r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}",
        r"\+?1[-.\s]?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}",
        r"\d{3}[-.\s]\d{3}[-.\s]\d{4}",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return ""


def extract_email_from_url(url, session):
    if not url or not url.startswith("http"):
        return ""
    try:
        random_delay()
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
        junk = {"example@example.com", "email@example.com", "your@email.com", "name@domain.com", "user@example.com", "info@example.com", "support@example.com", "admin@example.com", "webmaster@example.com"}
        valid = [e for e in emails if e.lower() not in junk and "noreply" not in e.lower() and not e.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js", ".json", ".xml"))]
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


def get_target_directory(city_input):
    city_lower = city_input.strip().lower()
    uk_markers = ["uk", "london", "england", "manchester", "birmingham", "scotland", "wales"]
    for marker in uk_markers:
        if marker in city_lower:
            return "UK"
    return "US"


def build_yellowpages_url(service, city, page=1, country="US"):
    encoded_service = quote_plus(service.strip())
    encoded_city = quote_plus(city.strip())
    if country == "UK":
        return f"https://www.yell.com/ucs/UcsSearchAction.do?keywords={encoded_service}&location={encoded_city}&pageNum={page}"
    else:
        base = "https://www.yellowpages.com/search"
        if page == 1:
            return f"{base}?search_terms={encoded_service}&geo_location_terms={encoded_city}"
        return f"{base}?search_terms={encoded_service}&geo_location_terms={encoded_city}&page={page}"


def parse_listing(container, service, city, country="US"):
    try:
        name = ""
        website = ""
        address = ""
        if country == "US":
            for tag, cls in [("a", re.compile("business-name", re.I)), ("h2", None), ("span", re.compile("business-name", re.I))]:
                el = container.find(tag, class_=cls) if cls else container.find(tag)
                if el:
                    name = el.get_text(strip=True)
                    if name:
                        break
            phone_el = container.find("div", class_=re.compile("phones|phone", re.I))
            phone = phone_el.get_text(strip=True) if phone_el else ""
            if not phone:
                phone = extract_phone(container.get_text())
            link_el = container.find("a", class_=re.compile("track-visit-website|website-link", re.I))
            if link_el:
                website = link_el.get("href", "")
            if not website:
                for a in container.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http") and "yellowpages.com" not in href:
                        website = href
                        break
            addr_el = container.find("div", class_=re.compile("street-address|adr", re.I))
            if addr_el:
                address = addr_el.get_text(strip=True)
        else:
            for tag in ["h2", "h3", "h1"]:
                el = container.find(tag)
                if el:
                    name = el.get_text(strip=True)
                    if name and 2 <= len(name) <= 80:
                        break
            phone = extract_phone(container.get_text())
            for a in container.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "yellowpages.com" not in href and "yell.com" not in href:
                    website = href
                    break
        if not name or len(name) < 2:
            return None
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


def scrape(service, city, max_pages=5, progress_callback=None):
    country = get_target_directory(city)
    GLOBAL_SCRAPE_STOPS["active_run"] = False
    businesses = []
    session = get_session()
    log_lines = []

    def log(msg):
        log_lines.append(msg)

    log(f"Target: {service} in {city} ({country})")
    log(f"Pages: {max_pages} | Connection: Standard Mode (Direct)")

    for page in range(1, max_pages + 1):
        if GLOBAL_SCRAPE_STOPS.get("active_run", False):
            log("Scrape stopped by user via global interruption signal.")
            break
        if progress_callback:
            progress_callback(page, max_pages, f"Page {page}/{max_pages} -- fetching...")
        url = build_yellowpages_url(service, city, page, country=country)
        try:
            random_delay()
            ua = UserAgent()
            stealth_headers = {
                "User-Agent": ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US;en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            resp = session.get(url, headers=stealth_headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            page_businesses = []
            results = soup.find_all("div", class_=re.compile("result|listing|v-card", re.I))
            for r in results:
                biz = parse_listing(r, service, city, country=country)
                if biz:
                    page_businesses.append(biz)
            if not page_businesses:
                results = soup.find_all("div", class_=re.compile("srp-listing|search-result", re.I))
                for r in results:
                    biz = parse_listing(r, service, city, country=country)
                    if biz:
                        page_businesses.append(biz)
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
            log(f"Page {page}: found {len(page_businesses)} leads")
            if not page_businesses and page > 1:
                log("Very few results. Stopping early.")
                break
        except Exception as e:
            log(f"Error on page {page}: {e}")
            continue

    log(f"Enriching {len(businesses)} leads with emails...")
    for i, biz in enumerate(businesses):
        website = biz.get("Website URL", "")
        if website and website.startswith("http"):
            biz["Email Address"] = extract_email_from_url(website, session)
        if (i + 1) % 10 == 0 and progress_callback:
            progress_callback(max_pages, max_pages, f"Enriching emails... {i+1}/{len(businesses)}")

    seen = set()
    unique = []
    for biz in businesses:
        key = (biz["Business Name"], biz.get("Phone Number", ""))
        if key not in seen:
            seen.add(key)
            unique.append(biz)

    log(f"Scrape complete! {len(unique)} unique leads found.")
    return unique, log_lines


# ---------------------------------------------------------------------------
# CSS Design System — Premium Light Edition
# ---------------------------------------------------------------------------
def inject_css():
    css_block = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    * { font-family: 'Inter', -apple-system, sans-serif; }

    :root {
      --bg-base: #FFFFFF;
      --bg-surface: #F8F9FA;
      --bg-elevated: #F4F5F7;
      --bg-glass: rgba(255, 255, 255, 0.85);
      --brand: #2563EB;
      --brand-dark: #1D4ED8;
      --brand-dim: rgba(37, 99, 235, 0.10);
      --brand-glow: rgba(37, 99, 235, 0.22);
      --volt: #10B981;
      --volt-dim: rgba(16, 185, 129, 0.10);
      --ember: #F59E0B;
      --ember-dim: rgba(245, 158, 11, 0.10);
      --rose: #EF4444;
      --rose-dim: rgba(239, 68, 68, 0.10);
      --text-primary: #1A1D20;
      --text-secondary: #5A6472;
      --text-muted: #8D96A3;
      --border-subtle: rgba(0, 0, 0, 0.08);
      --border-glow: rgba(37, 99, 235, 0.25);
      --border-active: rgba(37, 99, 235, 0.45);
      --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.05);
      --shadow-float: 0 8px 32px rgba(0, 0, 0, 0.08);
      --shadow-glow: 0 4px 20px rgba(37, 99, 235, 0.12);
      --r-sm: 8px;
      --r-md: 14px;
      --r-lg: 20px;
      --r-xl: 28px;
    }

    body { background: var(--bg-base) !important; color: var(--text-primary) !important; }

    .stApp, .main, [data-testid="stAppViewContainer"] {
      background: var(--bg-base) !important;
      color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"],
    [data-testid="block-container"],
    .block-container {
      background: transparent !important;
      padding-top: 1.5rem !important;
      max-width: 95% !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: var(--border-glow); border-radius: 3px; }

    @keyframes pulse-glow {
      0%, 100% { opacity: 0.08; transform: scale(1); }
      50% { opacity: 0.18; transform: scale(1.06); }
    }
    @keyframes dot-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }
    @keyframes shimmer {
      0% { background-position: -200% center; }
      100% { background-position: 200% center; }
    }

    .hero-header {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-xl);
      padding: 2.5rem 2rem 2rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-float);
      position: relative;
      overflow: hidden;
      text-align: center;
    }
    .hero-glow {
      position: absolute;
      top: -40%;
      left: 50%;
      transform: translateX(-50%);
      width: 420px;
      height: 420px;
      background: radial-gradient(circle, var(--brand) 0%, transparent 70%);
      opacity: 0.10;
      animation: pulse-glow 6s ease-in-out infinite;
      pointer-events: none;
    }
    .hero-title {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 800;
      font-size: 2.4rem;
      color: var(--brand);
      margin: 0;
      letter-spacing: -0.6px;
      position: relative;
    }
    .hero-tagline {
      color: var(--text-secondary);
      font-size: 1.05rem;
      margin-top: 0.6rem;
      position: relative;
    }
    .badge-row {
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
      margin-top: 1.4rem;
      position: relative;
    }
    .badge-pill {
      background: var(--bg-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 6px 16px;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-secondary);
      letter-spacing: 0.2px;
    }
    .mode-indicator {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 1rem;
      padding: 6px 18px;
      background: var(--volt-dim);
      border: 1px solid rgba(16,185,129,0.22);
      border-radius: 20px;
      font-size: 0.82rem;
      font-weight: 600;
      color: #047857;
      position: relative;
    }
    .dot-live {
      width: 8px;
      height: 8px;
      background: var(--volt);
      border-radius: 50%;
      animation: dot-pulse 2s ease-in-out infinite;
      box-shadow: 0 0 8px var(--volt);
    }

    .hero-separator {
      border: none;
      border-top: 1px solid var(--border-subtle);
      margin: 1.5rem 0 0;
    }

    .glass-card {
      background: var(--bg-glass);
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-lg);
      padding: 1.75rem 2rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow-card);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .glass-card:hover {
      border-color: var(--border-glow);
      box-shadow: var(--shadow-card), var(--shadow-glow);
    }
    .glass-card h3 {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 1.1rem;
      color: var(--text-primary);
      margin: 0 0 1.25rem;
      letter-spacing: -0.2px;
    }

    .stat-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 1.25rem 0;
    }
    .stat-card {
      background: var(--bg-glass);
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-md);
      padding: 1.1rem 1rem;
      text-align: center;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
      backdrop-filter: blur(8px);
    }
    .stat-card:hover {
      transform: translateY(-3px);
      border-color: var(--border-glow);
      box-shadow: 0 8px 20px var(--brand-glow);
    }
    .stat-card .val {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.2rem;
      font-weight: 800;
      color: var(--brand);
      line-height: 1.1;
      letter-spacing: -1px;
    }
    .stat-card .lbl {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.7px;
      font-weight: 600;
      margin-top: 4px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
      background: var(--bg-surface) !important;
      border-radius: var(--r-md) var(--r-md) 0 0 !important;
      border-bottom: 1px solid var(--border-subtle) !important;
      gap: 4px !important;
      padding: 6px 8px 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
      background: transparent !important;
      color: var(--text-secondary) !important;
      border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
      font-family: 'Space Grotesk', sans-serif !important;
      font-weight: 600 !important;
      font-size: 0.88rem !important;
      padding: 0.5rem 1.2rem !important;
      border: none !important;
      transition: color 0.2s, background 0.2s !important;
    }
    .stTabs [aria-selected="true"] {
      background: var(--brand-dim) !important;
      color: var(--brand) !important;
      border-bottom: 2px solid var(--brand) !important;
    }
    .stTabs [data-testid="stTabContent"] {
      background: var(--bg-surface) !important;
      border: 1px solid var(--border-subtle) !important;
      border-top: none !important;
      border-radius: 0 0 var(--r-md) var(--r-md) !important;
      padding: 1.5rem !important;
    }

    /* Inputs */
    .stTextInput > div > div > input {
      background: #FFFFFF !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: var(--r-sm) !important;
      color: var(--text-primary) !important;
      font-family: 'Inter', sans-serif !important;
      font-size: 0.95rem !important;
      padding: 0.65rem 1rem !important;
      transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus {
      border-color: var(--border-active) !important;
      box-shadow: 0 0 0 3px var(--brand-dim) !important;
      outline: none !important;
    }
    .stTextInput > div > div > input::placeholder {
      color: var(--text-muted) !important;
    }
    .stTextInput label {
      color: var(--text-secondary) !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.7px !important;
      font-family: 'Space Grotesk', sans-serif !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
      background: var(--brand) !important;
      color: #FFFFFF !important;
      font-family: 'Space Grotesk', sans-serif !important;
      font-weight: 700 !important;
      font-size: 1rem !important;
      letter-spacing: 0.2px !important;
      border: none !important;
      border-radius: var(--r-md) !important;
      padding: 0.75rem 2rem !important;
      box-shadow: 0 4px 16px var(--brand-glow) !important;
      transition: transform 0.15s ease, box-shadow 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 24px var(--brand-glow) !important;
      background: var(--brand-dark) !important;
    }
    .stButton > button[kind="primary"]:active {
      transform: translateY(0px) scale(0.98) !important;
    }
    .stButton > button[kind="secondary"] {
      background: #FFFFFF !important;
      color: var(--text-secondary) !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: var(--r-md) !important;
      font-family: 'Inter', sans-serif !important;
      font-weight: 500 !important;
      transition: all 0.18s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
      border-color: var(--rose) !important;
      color: var(--rose) !important;
      background: var(--rose-dim) !important;
    }

    .stDownloadButton > button {
      background: var(--brand) !important;
      color: #FFFFFF !important;
      font-family: 'Space Grotesk', sans-serif !important;
      font-weight: 700 !important;
      font-size: 1.05rem !important;
      border: none !important;
      border-radius: var(--r-md) !important;
      width: 100% !important;
      padding: 0.85rem 2rem !important;
      box-shadow: 0 4px 16px var(--brand-glow) !important;
      transition: transform 0.15s ease, box-shadow 0.2s ease !important;
      letter-spacing: 0.2px !important;
    }
    .stDownloadButton > button:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 24px rgba(37, 99, 235, 0.28) !important;
      background: var(--brand-dark) !important;
    }

    /* Progress */
    .stProgress > div > div > div {
      background: linear-gradient(90deg, var(--brand) 0%, #3B82F6 50%, var(--brand) 100%) !important;
      background-size: 200% auto !important;
      animation: shimmer 2s linear infinite !important;
      border-radius: 10px !important;
    }
    .stProgress > div > div {
      background: var(--bg-elevated) !important;
      border-radius: 10px !important;
      height: 6px !important;
    }

    /* Log box */
    .log-terminal {
      background: #F4F5F7;
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-md);
      padding: 1rem 1.25rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      line-height: 1.7;
      max-height: 280px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
      color: #1A1D20;
    }
    .log-terminal .log-ok { color: #047857; }
    .log-terminal .log-err { color: #DC2626; }
    .log-terminal .log-dim { color: var(--text-muted); }
    .log-terminal .log-hi { color: var(--brand); }

    /* Badges */
    .badge-ok { background: var(--volt-dim); color: #047857; border: 1px solid rgba(16,185,129,0.25); border-radius: 20px; padding: 4px 12px; font-size: 0.82rem; font-weight: 600; }
    .badge-partial { background: var(--ember-dim); color: #B45309; border: 1px solid rgba(245,158,11,0.25); border-radius: 20px; padding: 4px 12px; font-size: 0.82rem; font-weight: 600; }
    .badge-no { background: var(--rose-dim); color: #DC2626; border: 1px solid rgba(239,68,68,0.25); border-radius: 20px; padding: 4px 12px; font-size: 0.82rem; font-weight: 600; }

    .service-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 10px;
      margin-top: 0.5rem;
    }
    .service-item {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-sm);
      padding: 0.8rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .service-item:hover { border-color: var(--border-glow); box-shadow: var(--shadow-glow); }
    .service-name {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-primary);
    }
    .bar-dot { font-size: 0.85rem; }
    .bar-dot.filled.high { color: var(--brand); }
    .bar-dot.filled.good { color: var(--volt); }
    .bar-dot.filled.mid { color: var(--ember); }
    .bar-dot.filled.low { color: var(--text-muted); }
    .bar-dot.empty { color: var(--text-muted); opacity: 0.3; }

    .tip-card {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-md);
      padding: 1.25rem;
      height: 100%;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .tip-card:hover {
      border-color: var(--border-glow);
      box-shadow: var(--shadow-glow);
    }
    .tip-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
    .tip-title {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }
    .tip-body {
      font-size: 0.83rem;
      color: var(--text-secondary);
      line-height: 1.6;
    }

    .legend-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .legend-table th {
      color: var(--text-muted);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.7px;
      padding: 0 0 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
      text-align: left;
    }
    .legend-table td {
      padding: 0.7rem 0;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      vertical-align: middle;
    }
    .legend-table tr:last-child td { border-bottom: none; }
    .legend-table td:first-child { color: var(--text-primary); font-weight: 500; padding-right: 1rem; }
    .auto-detect-note {
      margin-top: 1rem;
      padding: 0.65rem 1rem;
      background: var(--brand-dim);
      border: 1px solid var(--border-glow);
      border-radius: var(--r-sm);
      font-size: 0.83rem;
      color: var(--brand);
      font-weight: 500;
    }

    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.75rem; }
    .chip {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: 20px;
      padding: 5px 14px;
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.18s ease;
      font-family: 'Inter', sans-serif;
    }
    .chip:hover {
      border-color: var(--brand);
      color: var(--brand);
      background: var(--brand-dim);
    }

    .unlock-wrapper {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 60vh;
      padding: 2rem;
    }
    .unlock-card {
      background: #FFFFFF;
      border: 1px solid var(--border-subtle);
      border-radius: var(--r-xl);
      padding: 3rem 2.5rem;
      max-width: 420px;
      width: 100%;
      text-align: center;
      box-shadow: var(--shadow-float);
    }
    .unlock-icon { font-size: 3rem; margin-bottom: 1rem; }
    .unlock-title {
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      font-size: 1.5rem;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }
    .unlock-sub {
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-bottom: 1.5rem;
    }

    .app-footer {
      text-align: center;
      padding: 2.5rem 1rem 2rem;
      color: var(--text-muted);
      font-size: 0.78rem;
      border-top: 1px solid var(--border-subtle);
      margin-top: 2rem;
      font-family: 'Inter', sans-serif;
      letter-spacing: 0.3px;
    }
    .app-footer a {
      color: var(--brand);
      text-decoration: none;
      opacity: 0.85;
      transition: opacity 0.2s;
    }
    .app-footer a:hover { opacity: 1; }

    .stAlert {
      border-radius: var(--r-sm) !important;
      font-size: 0.88rem !important;
      font-family: 'Inter', sans-serif !important;
    }
    [data-baseweb="notification"][kind="info"] {
      background: var(--brand-dim) !important;
      border-color: var(--border-glow) !important;
      color: var(--brand) !important;
    }
    [data-baseweb="notification"][kind="warning"] {
      background: var(--ember-dim) !important;
      border-color: rgba(245,158,11,0.30) !important;
      color: var(--ember) !important;
    }
    [data-baseweb="notification"][kind="error"] {
      background: var(--rose-dim) !important;
      border-color: rgba(239,68,68,0.30) !important;
      color: var(--rose) !important;
    }
    [data-baseweb="notification"][kind="positive"] {
      background: var(--volt-dim) !important;
      border-color: rgba(16,185,129,0.30) !important;
      color: var(--volt) !important;
    }

    .streamlit-expanderHeader {
      background: #FFFFFF !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: var(--r-sm) !important;
      color: var(--text-primary) !important;
      font-family: 'Space Grotesk', sans-serif !important;
      font-weight: 600 !important;
      font-size: 0.9rem !important;
      padding: 0.65rem 1rem !important;
    }
    .streamlit-expanderHeader:hover {
      border-color: var(--border-glow) !important;
    }
    .stSpinner > div { border-color: var(--brand) !important; }
    </style>
    """
    st.markdown(css_block, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Access Gate
# ---------------------------------------------------------------------------
def access_gate():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown('<div class="unlock-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="unlock-card">', unsafe_allow_html=True)
        st.markdown('<div class="unlock-icon">🔐</div>', unsafe_allow_html=True)
        st.markdown('<div class="unlock-title">Access Required</div>', unsafe_allow_html=True)
        st.markdown('<div class="unlock-sub">Enter your access code to unlock the tool.</div>', unsafe_allow_html=True)

        access_code = st.text_input("Access Code", type="password", key="access_code_v2")
        if st.button("Unlock Tool →", type="primary", use_container_width=True, key="unlock_btn_v2"):
            if access_code == "LEAD2026":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid access code. Please try again.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()


# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
def render_header():
    st.markdown(
        """
    <div class="hero-header">
      <div class="hero-glow"></div>
      <h1 class="hero-title">🏠 Home Services Lead Scraper PRO</h1>
      <p class="hero-tagline">Generate unlimited web design & SEO client leads — US, UK & Europe Standard Mode</p>
      <div class="badge-row">
        <span class="badge-pill" style="border-color: var(--volt);">🟢 Live Data</span>
        <span class="badge-pill" style="border-color: var(--brand);">📍 US, UK & Europe</span>
        <span class="badge-pill" style="border-color: var(--brand);">📥 CSV Export</span>
        <span class="badge-pill" style="border-color: var(--ember);">🛡️ Anti-Block Engine</span>
      </div>
      <div class="mode-indicator">
        <span class="dot-live"></span>
        ⚡ Standard Mode Active
      </div>
      <hr class="hero-separator">
    </div>
    """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Target Input Card
# ---------------------------------------------------------------------------
def render_target_card():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Define Your Target")

    col1, col2 = st.columns(2)
    with col1:
        service_default = st.session_state.get("service_prefill", "")
        service = st.text_input("Service Type", placeholder="e.g., roofer, plumber, electrician, HVAC", value=service_default, key="service_input_v2")
        st.session_state["service_prefill"] = ""
    with col2:
        city = st.text_input("City / Area", placeholder="e.g., Dallas TX, London UK, Chicago IL", key="city_input_v2")

    st.markdown('<div class="chip-row">', unsafe_allow_html=True)
    chips = ["Roofer", "Plumber", "Electrician", "HVAC", "Painter", "Landscaper", "Pest Control", "Cleaner"]
    cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with cols[i]:
            if st.button(chip, key=f"chip_{chip}_v2"):
                st.session_state["service_prefill"] = chip
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return service, city


# ---------------------------------------------------------------------------
# Pro Tips
# ---------------------------------------------------------------------------
def render_legend():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌍 Region & Service Coverage")

    st.markdown("""
    <table class="legend-table">
      <thead>
        <tr>
          <th>Service Type</th>
          <th>United States</th>
          <th>United Kingdom</th>
          <th>Europe</th>
          <th>Canada</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>HVAC / Air Conditioning</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Plumber / Plumbing</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Roofer / Roofing</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Electrician / Electrical</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Pest Control</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>House Cleaning / Maid Service</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Landscaper / Lawn Care</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Painter / Painting</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Tree Service</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Flooring</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Pool Service</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Remodeling / Contractor</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Pressure Washing</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Appliance Repair</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Carpet Cleaning</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Locksmith</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Junk Removal</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
        <tr>
          <td>Solar / Radon / Niche</td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-ok">✅ Fully Supported</span></td>
          <td><span class="badge-partial">⚠️ Partial</span></td>
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Pro Tips")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="tip-card">
          <div class="tip-icon">🏙️</div>
          <div class="tip-title">Best Cities to Target</div>
          <div class="tip-body">Aim for mid-size metros (pop. 300K–2M) for the best results. Large cities like NYC or LA return 200+ leads but are highly competitive. Try Austin TX, Nashville TN, Charlotte NC, or Tampa FL for high-quality, less-saturated lists.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="tip-card">
          <div class="tip-icon">📋</div>
          <div class="tip-title">Using Your Leads</div>
          <div class="tip-body">Open the CSV in Google Sheets or Excel. Filter for rows with both a phone number AND a website — these are your highest-quality prospects. Prioritise businesses with older-looking websites or missing emails, as they're most likely to need your services.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="tip-card">
          <div class="tip-icon">⚡</div>
          <div class="tip-title">Getting Better Results</div>
          <div class="tip-body">Run the scraper at different times (morning 9–11 AM works best). If you get 0 results, try a broader service term — use "plumber" instead of "emergency plumber". Wait 10–15 minutes between runs on the same city to avoid temporary blocks.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Generate Controls
# ---------------------------------------------------------------------------
def render_generate_controls():
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_clicked = st.button("🚀 Generate Leads", type="primary", use_container_width=True, key="generate_btn_v2")
    with col2:
        stop_clicked = st.button("🛑 Stop", use_container_width=True, key="stop_btn_v2")
    return generate_clicked, stop_clicked


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def render_footer():
    st.markdown(
        """
    <div class="app-footer">
      © 2026 <strong>ToolPilot Design</strong> · Home Services Lead Scraper PRO v2.0 · Standard Mode
    </div>
    """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    inject_css()
    access_gate()
    render_header()
    service, city = render_target_card()
    render_legend()
    generate_clicked, stop_clicked = render_generate_controls()

    if stop_clicked:
        GLOBAL_SCRAPE_STOPS["active_run"] = True
        st.warning("Stop signal sent. Halting safely...")

    if generate_clicked:
        GLOBAL_SCRAPE_STOPS["active_run"] = False

        if not service.strip() or not city.strip():
            st.warning("Please enter both a Service Type and a City.")
            st.stop()

        detected_country = get_target_directory(city)
        if detected_country == "UK":
            st.info("Detected UK directory. Routing to Yell.com for best results...")

        progress_bar = st.progress(0.0, text="Starting...")
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        def progress_callback(current, total, message):
            progress_bar.progress(current / total if total else 0, text=message)
            status_placeholder.info(message)

        with st.spinner("Scraping in progress... Please wait 1-2 minutes while we gather your leads."):
            try:
                results, logs = scrape(service.strip(), city.strip(), max_pages=5, progress_callback=progress_callback)
            except Exception as e:
                st.error(f"Fatal error: {e}")
                st.stop()

        log_html = '<div class="log-terminal">'
        for entry in logs:
            if "Error" in entry or "error" in entry.lower():
                level = "log-err"
            elif "complete" in entry.lower() or "found" in entry.lower():
                level = "log-ok"
            elif "Enriching" in entry:
                level = "log-dim"
            else:
                level = "log-hi"
            log_html += f'<span class="{level}">{entry}</span>\n'
        log_html += "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

        if not results:
            st.warning("No results found. Try a different service type, or try again in a few minutes.")
            st.stop()

        with_phone = sum(1 for b in results if b.get("Phone Number"))
        with_email = sum(1 for b in results if b.get("Email Address"))
        with_website = sum(1 for b in results if b.get("Website URL"))

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Results")
        st.markdown('<div class="stat-row">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="val">{len(results)}</div><div class="lbl">Total Leads</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="val">{with_phone}</div><div class="lbl">With Phone</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="val">{with_email}</div><div class="lbl">With Email</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-card"><div class="val">{with_website}</div><div class="lbl">With Website</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        df = pd.DataFrame(results)
        column_order = ["Business Name", "Phone Number", "Website URL", "Email Address", "Service Type", "City Searched", "Address", "Date Scraped"]
        cols = [c for c in column_order if c in df.columns]
        df = df[cols].drop_duplicates(subset=["Business Name", "Phone Number"]).reset_index(drop=True)
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        csv_bytes = csv_buf.getvalue().encode("utf-8-sig")
        filename = f"leads_{service}_{city}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        st.success("Scrape complete! Download your CSV below.")
        st.download_button(label="📥 Download CSV File", data=csv_bytes, file_name=filename, mime="text/csv", use_container_width=True, key="download_btn_v2")

        with st.expander("👁️ Preview first 20 leads"):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


if __name__ == "__main__":
    main()
"""
Home Services Lead Scraper Pro — Streamlit Web App (Cloud Stable)
=================================================================
Production-ready cloud-hostable web application.
Synchronous execution (no threading) with dual-mode scraping:
Standard Mode (direct connection) and Turbo Mode (premium proxy API).

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
    page_title="Home Services Lead Scraper PRO",
    page_icon="🏠",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium, modern, professional
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    :root {
        --primary: #0a2540; --primary-light: #1a3a5c; --accent: #00b4d8; --accent-hover: #0096c7;
        --success: #06d6a0; --warning: #ff9f1c; --danger: #ef476f;
        --bg: #f0f2f5; --card: #ffffff; --text: #1a1a2e; --text-secondary: #6b7280; --border: #e5e7eb;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.08); --shadow-lg: 0 10px 40px rgba(0,0,0,0.12);
        --radius: 16px; --radius-sm: 10px;
    }
    body { background: var(--bg); color: var(--text); }
    .main-header { text-align: center; padding: 2.5rem 2rem 2rem; background: linear-gradient(135deg, #0a2540 0%, #1a3a5c 40%, #00b4d8 100%); color: white; border-radius: var(--radius); margin-bottom: 2rem; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; }
    .main-header::before { content: ''; position: absolute; top: -50%; right: -20%; width: 300px; height: 300px; background: rgba(255,255,255,0.03); border-radius: 50%; }
    .main-header::after { content: ''; position: absolute; bottom: -30%; left: -10%; width: 200px; height: 200px; background: rgba(255,255,255,0.02); border-radius: 50%; }
    .main-header h1 { font-size: 2.2rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; position: relative; }
    .main-header p { font-size: 1.05rem; opacity: 0.9; margin-top: 0.5rem; font-weight: 400; position: relative; }
    .badge-row { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 1.2rem; position: relative; }
    .badge { background: rgba(255,255,255,0.12); backdrop-filter: blur(4px); padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.3px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.75rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); transition: box-shadow 0.2s ease; }
    .card:hover { box-shadow: var(--shadow-md); }
    .card h3 { margin: 0 0 1rem; font-size: 1.1rem; font-weight: 700; color: var(--primary); }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .stat-box { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 1.2rem 1rem; text-align: center; transition: transform 0.15s ease, box-shadow 0.2s ease; }
    .stat-box:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    .stat-box .value { font-size: 2rem; font-weight: 800; color: var(--accent); line-height: 1.2; }
    .stat-box .label { font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.3rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .stButton>button { border-radius: var(--radius-sm) !important; font-weight: 600 !important; font-size: 1rem !important; padding: 0.65rem 1.5rem !important; transition: all 0.2s ease !important; box-shadow: var(--shadow-sm) !important; }
    .stButton>button[kind="primary"] { background: linear-gradient(135deg, var(--accent), var(--accent-hover)) !important; color: white !important; border: none !important; }
    .stButton>button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(0, 180, 216, 0.35) !important; }
    .stButton>button[kind="secondary"] { background: #f3f4f6 !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    .stButton>button[kind="secondary"]:hover { background: #e5e7eb !important; }
    .stDownloadButton>button { background: linear-gradient(135deg, var(--success), #05b588) !important; color: white !important; border: none !important; border-radius: var(--radius-sm) !important; padding: 0.75rem 2rem !important; font-size: 1.05rem !important; font-weight: 700 !important; width: 100% !important; transition: all 0.2s ease !important; box-shadow: 0 4px 15px rgba(6, 214, 160, 0.25) !important; }
    .stDownloadButton>button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(6, 214, 160, 0.35) !important; }
    .log-box { background: #0d1117; color: #e6edf3; font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace; font-size: 0.8rem; padding: 1rem 1.2rem; border-radius: var(--radius-sm); max-height: 350px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; line-height: 1.6; border: 1px solid #30363d; }
    .log-info { color: #58a6ff; } .log-success { color: #3fb950; } .log-warning { color: #d29922; } .log-error { color: #f85149; }
    .stTextInput>div>div>input { border-radius: var(--radius-sm) !important; border: 1px solid var(--border) !important; padding: 0.6rem 0.9rem !important; font-size: 0.95rem !important; transition: border-color 0.2s ease, box-shadow 0.2s ease !important; }
    .stTextInput>div>div>input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(0, 180, 216, 0.15) !important; }
    .stTextInput>div>div>input::placeholder { color: #9ca3af; }
    .stRadio>div { gap: 0.5rem; }
    .stRadio label { background: #f3f4f6; border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.6rem 1.2rem; font-weight: 500; font-size: 0.9rem; transition: all 0.2s ease; cursor: pointer; }
    .stRadio label:hover { border-color: var(--accent); background: rgba(0, 180, 216, 0.05); }
    .streamlit-expanderHeader { font-weight: 600 !important; font-size: 0.95rem !important; color: var(--primary) !important; background: #f9fafb !important; border-radius: var(--radius-sm) !important; padding: 0.6rem 1rem !important; border: 1px solid var(--border) !important; }
    .streamlit-expanderHeader:hover { background: #f3f4f6 !important; }
    .stProgress > div > div > div { background: linear-gradient(90deg, var(--accent), var(--success)) !important; border-radius: 10px !important; }
    footer { text-align: center; padding: 2rem 1rem; color: var(--text-secondary); font-size: 0.82rem; font-weight: 400; }
    .stSpinner > div { border-color: var(--accent) !important; }
    .stAlert { border-radius: var(--radius-sm) !important; font-size: 0.9rem !important; }
    .stInfo { background: rgba(0, 180, 216, 0.08) !important; border: 1px solid rgba(0, 180, 216, 0.2) !important; }
    .stWarning { background: rgba(255, 159, 28, 0.08) !important; border: 1px solid rgba(255, 159, 28, 0.2) !important; }
    .stError { background: rgba(239, 71, 111, 0.08) !important; border: 1px solid rgba(239, 71, 111, 0.2) !important; }
    .stSuccess { background: rgba(6, 214, 160, 0.08) !important; border: 1px solid rgba(6, 214, 160, 0.2) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Backend configuration
# ---------------------------------------------------------------------------
PREMIUM_SCRAPER_URL = "http://api.scraperapi.com?api_key={api_key}&autoparse=true&url={target_url}"
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


def extract_email_from_url(url, session, use_premium=False, api_key=None):
    if not url or not url.startswith("http"):
        return ""
    try:
        random_delay()
        target = url
        if use_premium and api_key:
            request_url = f"http://api.scraperapi.com/?api_key={api_key.strip()}&autoparse=true&url={quote_plus(target)}"
            resp = session.get(request_url, timeout=30)
        else:
            resp = session.get(target, timeout=10)
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


def scrape(service, city, max_pages=5, progress_callback=None, use_premium=False, api_key=None):
    country = get_target_directory(city)
    GLOBAL_SCRAPE_STOPS["active_run"] = False
    businesses = []
    session = get_session()
    log_lines = []

    def log(msg):
        log_lines.append(msg)

    mode_label = "Turbo Mode (Premium API)" if use_premium else "Standard Mode (Direct)"
    log(f"Target: {service} in {city} ({country})")
    log(f"Pages: {max_pages} | Connection: {mode_label}")

    for page in range(1, max_pages + 1):
        if GLOBAL_SCRAPE_STOPS.get("active_run", False):
            log("Scrape stopped by user via global interruption signal.")
            break
        if progress_callback:
            progress_callback(page, max_pages, f"Page {page}/{max_pages} -- fetching...")
        url = build_yellowpages_url(service, city, page, country=country)
        try:
            random_delay()
            if use_premium and api_key:
                request_url = f"http://api.scraperapi.com/?api_key={api_key.strip()}&autoparse=true&url={quote_plus(url)}"
                resp = session.get(request_url, timeout=30)
            else:
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
            biz["Email Address"] = extract_email_from_url(website, session, use_premium=use_premium, api_key=api_key)
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


def main():
    # ── Access Gate ─────────────────────────────────────────────────
    access_code = st.text_input("🔑 Enter Access Code", type="password", key="access_code_input")
    if access_code != "LEAD2026":
        st.warning("Please enter a valid access code to proceed.")
        st.stop()

    # ── Header ──────────────────────────────────────────────────────
    st.markdown(
        """
    <div class="main-header">
        <h1>🏠 Home Services Lead Scraper PRO</h1>
        <p>Generate unlimited web design & SEO client leads in minutes</p>
        <div class="badge-row">
            <span class="badge">⚡ Anti-Blocking Engine</span>
            <span class="badge">📊 CSV Export</span>
            <span class="badge">🌍 Multi-Region Support</span>
            <span class="badge">🔀 Dual Mode</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Target Input ────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Define Your Target")

    col1, col2 = st.columns(2)
    with col1:
        service = st.text_input("Service Type", placeholder="e.g., roofer, plumber, electrician, HVAC")
    with col2:
        city = st.text_input("City / Area", placeholder="e.g., Dallas TX, London UK, Chicago IL")

    st.markdown("### ⚙️ Scrape Mode")
    scrape_mode = st.radio(
        "Choose your connection method:",
        options=["Turbo Mode (High-Success Premium API)", "Standard Mode (Free Direct Connection)"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    api_key = ""
    if "Turbo" in scrape_mode:
        st.info("**How to use Turbo Mode for free:** Sign up at ScraperAPI.com, copy your free API key, and paste it below.")
        api_key = st.text_input("Enter your ScraperAPI Key", type="password")
    else:
        st.warning("Standard Mode: Direct connection. May encounter blocks on some pages. Use Turbo Mode if results fail.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Buttons ─────────────────────────────────────────────────────
    use_premium = "Turbo" in scrape_mode
    GLOBAL_SCRAPE_STOPS["active_run"] = False

    col1, col2 = st.columns([3, 1])
    with col1:
        generate_clicked = st.button("🚀 Generate Leads", type="primary", use_container_width=True, key="btn_gen_v1")
    with col2:
        stop_clicked = st.button("🛑 Stop", use_container_width=True, key="btn_stop_v1")

    if stop_clicked:
        GLOBAL_SCRAPE_STOPS["active_run"] = True
        st.warning("Stop signal sent. Halting background worker safely...")

    # ── Execution ───────────────────────────────────────────────────
    if generate_clicked:
        if "Turbo" in scrape_mode and not api_key.strip():
            st.error("You must enter a valid API Key to use Turbo Mode. Please enter your key or switch to Standard Mode.")
            st.stop()

        if not service.strip() or not city.strip():
            st.warning("Please enter both a Service Type and a City.")
            st.stop()

        detected_country = get_target_directory(city)
        if detected_country == "UK":
            st.info("Detected UK directory. Routing to Yell.com for best results...")

        GLOBAL_SCRAPE_STOPS["active_run"] = False
        progress_bar = st.progress(0.0, text="Starting...")
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        def progress_callback(current, total, message):
            progress_bar.progress(current / total if total else 0, text=message)
            status_placeholder.info(message)

        with st.spinner("Scraping in progress... Please wait 1-2 minutes while we gather your leads."):
            try:
                results, logs = scrape(service.strip(), city.strip(), max_pages=5, progress_callback=progress_callback, use_premium=use_premium, api_key=api_key.strip() if api_key else None)
            except Exception as e:
                st.error(f"Fatal error: {e}")
                st.stop()

        log_html = '<div class="log-box">'
        for entry in logs:
            level = "log-info"
            if "Error" in entry or "error" in entry.lower():
                level = "log-error"
            log_html += f'<span class="{level}">{entry}</span>\n'
        log_html += "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

        if not results:
            st.warning("No results found. Try a different service type, switch Scrape Mode, or try again in a few minutes.")
            st.stop()

        with_phone = sum(1 for b in results if b.get("Phone Number"))
        with_email = sum(1 for b in results if b.get("Email Address"))
        with_website = sum(1 for b in results if b.get("Website URL"))
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Results")
        st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="value">{len(results)}</div><div class="label">Total Leads</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="value">{with_phone}</div><div class="label">With Phone</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="value">{with_email}</div><div class="label">With Email</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-box"><div class="value">{with_website}</div><div class="label">With Website</div></div>', unsafe_allow_html=True)
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
        st.download_button(label="📥 Download CSV File", data=csv_bytes, file_name=filename, mime="text/csv", use_container_width=True)

        with st.expander("👁️ Preview first 20 leads"):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<footer>Home Services Lead Scraper PRO &mdash; Your Unfair Advantage in Client Acquisition</footer>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
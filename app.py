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
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
    :root {
        --primary: #1a73e8;
        --success: #0f9d58;
        --turbo: #f9ab00;
        --bg: #f8f9fa;
        --card: #ffffff;
        --text: #202124;
        --border: #dadce0;
    }
    html, body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    .main-header { text-align: center; padding: 2rem 1rem 1rem; background: linear-gradient(135deg, #1a73e8 0%, #4285f4 50%, #0f9d58 100%); color: white; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(26,115,232,0.25); }
    .main-header h1 { font-size: 2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
    .main-header p { font-size: 1.05rem; opacity: 0.92; margin-top: 0.5rem; }
    .badge-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 1rem; }
    .badge { background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .card h3 { margin-top: 0; font-size: 1.1rem; }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem; }
    .stat-box { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-box .value { font-size: 1.8rem; font-weight: 700; color: var(--primary); }
    .stat-box .label { font-size: 0.8rem; color: #5f6368; margin-top: 0.25rem; }
    .stDownloadButton>button { background: var(--success) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; font-size: 1.1rem !important; font-weight: 600 !important; width: 100% !important; }
    .log-box { background: #1e1e1e; color: #d4d4d4; font-family: Consolas, 'Courier New', monospace; font-size: 0.82rem; padding: 1rem; border-radius: 8px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; }
    .log-info { color: #4fc3f7; } .log-success { color: #81c784; } .log-warning { color: #ffb74d; } .log-error { color: #e57373; }
    footer { text-align: center; padding: 2rem 1rem; color: #5f6368; font-size: 0.82rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Backend configuration
# ---------------------------------------------------------------------------
# Replace the placeholder with your actual ScraperAPI / ScrapingBee key.
# Turbo Mode routes all requests through this endpoint to bypass Cloudflare.
PREMIUM_SCRAPER_URL = "http://api.scraperapi.com?api_key=YOUR_API_KEY_HERE&autoparse=true&url={target_url}"


def get_session():
    """Requests session with rotating headers."""
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


def extract_email_from_url(url, session, use_premium=False):
    if not url or not url.startswith("http"):
        return ""
    try:
        random_delay()
        target = url
        if use_premium:
            api_url = PREMIUM_SCRAPER_URL.format(target_url=quote_plus(target))
            resp = session.get(api_url, timeout=30)
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


def build_yellowpages_url(service, city, page=1):
    query = f"{service} {city}"
    encoded = quote_plus(query)
    base = "https://www.yellowpages.com/search"
    if page == 1:
        return f"{base}?search_terms={encoded}"
    return f"{base}?search_terms={encoded}&page={page}"


def parse_listing(container, service, city):
    try:
        name = ""
        for tag, cls in [("a", re.compile("business-name", re.I)), ("h2", None), ("span", re.compile("business-name", re.I))]:
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


def scrape(service, city, max_pages=5, progress_callback=None, use_premium=False):
    """Synchronous scrape — safe to call from main Streamlit thread."""
    businesses = []
    session = get_session()
    log_lines = []

    def log(msg):
        log_lines.append(msg)

    mode_label = "⚡ Turbo Mode (Premium API)" if use_premium else "🚀 Standard Mode (Direct)"
    log(f"🎯 Target: {service} in {city}")
    log(f"⚙️ Pages: {max_pages} | Connection: {mode_label}")

    for page in range(1, max_pages + 1):
        if progress_callback:
            progress_callback(page, max_pages, f"Page {page}/{max_pages} — fetching...")
        url = build_yellowpages_url(service, city, page)
        try:
            random_delay()
            if use_premium:
                api_url = PREMIUM_SCRAPER_URL.format(target_url=quote_plus(url))
                resp = session.get(api_url, timeout=30)
            else:
                resp = session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            page_businesses = []
            results = soup.find_all("div", class_=re.compile("result|listing|v-card", re.I))
            for r in results:
                biz = parse_listing(r, service, city)
                if biz:
                    page_businesses.append(biz)
            if not page_businesses:
                results = soup.find_all("div", class_=re.compile("srp-listing|search-result", re.I))
                for r in results:
                    biz = parse_listing(r, service, city)
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
            log(f"✅ Page {page}: found {len(page_businesses)} leads")
            if not page_businesses and page > 1:
                log("⚠️ Very few results. Stopping early.")
                break
        except Exception as e:
            log(f"❌ Error on page {page}: {e}")
            continue

    # Email enrichment
    log(f"🔍 Enriching {len(businesses)} leads with emails...")
    for i, biz in enumerate(businesses):
        website = biz.get("Website URL", "")
        if website and website.startswith("http"):
            biz["Email Address"] = extract_email_from_url(website, session, use_premium=use_premium)
        if (i + 1) % 10 == 0 and progress_callback:
            progress_callback(max_pages, max_pages, f"Enriching emails... {i+1}/{len(businesses)}")

    # Deduplicate
    seen = set()
    unique = []
    for biz in businesses:
        key = (biz["Business Name"], biz.get("Phone Number", ""))
        if key not in seen:
            seen.add(key)
            unique.append(biz)

    log(f"🎉 Scrape complete! {len(unique)} unique leads found.")
    return unique, log_lines


# ---------------------------------------------------------------------------
# Streamlit UI — clean, modern, no sidebar
# ---------------------------------------------------------------------------
def main():
    st.markdown(
        """
    <div class="main-header">
        <h1>🏠 Home Services Lead Scraper PRO</h1>
        <p>Generate unlimited web design & SEO client leads in minutes</p>
        <div class="badge-row">
            <span class="badge">⚡ Anti-Blocking</span>
            <span class="badge">📊 CSV Export</span>
            <span class="badge">🎯 Targeted Leads</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
    use_premium = scrape_mode.startswith("Turbo")

    if use_premium:
        st.info("⚡ Turbo Mode: All requests routed through premium proxy for maximum success rate. Recommended for best results.")
    else:
        st.warning("🚀 Standard Mode: Direct connection. May encounter blocks on some pages. Use Turbo Mode if results fail.")

    generate_btn = st.button("🚀 Generate Leads", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_btn:
        if not service.strip() or not city.strip():
            st.warning("Please enter both a Service Type and a City.")
            st.stop()

        progress_bar = st.progress(0.0, text="Starting...")
        status_placeholder = st.empty()
        log_placeholder = st.empty()

        def progress_callback(current, total, message):
            progress_bar.progress(current / total if total else 0, text=message)
            status_placeholder.info(message)

        with st.spinner("Scraping in progress... Please wait 1-2 minutes while we gather your leads."):
            try:
                results, logs = scrape(service.strip(), city.strip(), max_pages=5, progress_callback=progress_callback, use_premium=use_premium)
            except Exception as e:
                st.error(f"Fatal error: {e}")
                st.stop()

        log_html = '<div class="log-box">'
        for entry in logs:
            level = "log-info"
            if "❌" in entry or "error" in entry.lower():
                level = "log-error"
            elif "⚠️" in entry or "warning" in entry.lower():
                level = "log-warning"
            elif "🎉" in entry or "complete" in entry.lower():
                level = "log-success"
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

        st.success("✅ Scrape complete! Download your CSV below.")
        st.download_button(label="📥 Download CSV File", data=csv_bytes, file_name=filename, mime="text/csv", use_container_width=True)

        with st.expander("👁️ Preview first 20 leads"):
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<footer>Home Services Lead Scraper PRO · Your Unfair Advantage in Client Acquisition</footer>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
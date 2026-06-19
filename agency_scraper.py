"""
Home Services Lead Scraper Pro
===============================
Scrapes local home service business leads from Yellow Pages search results.
Designed for Web Design & SEO agencies to generate client leads.

Usage:
    python agency_scraper.py

Author: Blue Ocean Digital Products
License: Commercial - See LICENSE.txt for details
"""

import csv
import json
import os
import re
import sys
import time
import random
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel

# Initialize Rich Console for beautiful terminal output
console = Console()

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_CSV = "agency_leads.csv"
MIN_DELAY = 2   # Minimum seconds between requests
MAX_DELAY = 5   # Maximum seconds between requests
MAX_PAGES = 5   # Max pages to scrape per search (safety limit)

# Common business service keywords
SERVICE_KEYWORDS = [
    "roofer", "plumber", "electrician", "HVAC", "painter", "landscaper",
    "contractor", "builder", "remodeler", "flooring", "roofing", "plumbing",
    "electrical", "heating", "cooling", "paving", "concrete", "masonry",
    "carpenter", "handyman", "gutter", "window", "door", "siding",
    "insulation", "drywall", "painting", "lawn care", "tree service",
    "fencing", "deck", "patio", "pool", "cleaning service", "maid service",
    "pest control", "radon", "water heater", "septic", "foundation repair",
    "chimney", "fireplace", "solar", "roof cleaning", "pressure washing"
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_random_headers():
    """Generate random headers with rotating User-Agent to avoid blocks."""
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


def random_delay():
    """Sleep for a random duration to simulate human browsing."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)


def extract_phone(text):
    """Extract phone number from text using regex."""
    if not text:
        return ""
    patterns = [
        r"\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}",
        r"\+?1[-.\s]?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}",
        r"\d{3}[-.\s]\d{3}[-.\s]\d{4}",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return ""


def extract_email_from_url(url, session, headers):
    """Visit a business website homepage and try to find an email address."""
    if not url or url.startswith("http") is False:
        return ""

    try:
        random_delay()
        resp = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()

        # Find all email-like patterns
        email_pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, text)

        # Filter out common junk / asset emails
        junk = {"example@example.com", "email@example.com", "your@email.com",
                "name@domain.com", "user@example.com", "info@example.com",
                "support@example.com", "admin@example.com", "webmaster@example.com"}
        valid_emails = [
            e for e in emails
            if e.lower() not in junk
            and not e.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js", ".json", ".xml"))
            and "noreply" not in e.lower()
            and "no-reply" not in e.lower()
        ]

        if valid_emails:
            return valid_emails[0]

        # Also check mailto links
        mailto_links = soup.find_all("a", href=re.compile(r"^mailto:", re.I))
        if mailto_links:
            href = mailto_links[0].get("href", "")
            email_match = re.search(r"mailto:([^?]+)", href)
            if email_match:
                candidate = email_match.group(1)
                if candidate not in junk:
                    return candidate

        return ""

    except Exception:
        return ""


def build_yellowpages_url(service, city, page=1):
    """Build a Yellow Pages search URL."""
    query = f"{service} {city}"
    encoded = quote_plus(query)
    base = "https://www.yellowpages.com/search"
    if page == 1:
        return f"{base}?search_terms={encoded}"
    return f"{base}?search_terms={encoded}&page={page}"


def parse_yellowpages_listing(container, service, city):
    """Parse a single Yellow Pages business listing card."""
    try:
        # Business Name
        name = ""
        name_el = container.find("a", class_=re.compile("business-name", re.I))
        if name_el:
            name = name_el.get_text(strip=True)
        if not name:
            name_el = container.find("h2")
            if name_el:
                name = name_el.get_text(strip=True)
        if not name:
            name_el = container.find("span", class_=re.compile("business-name", re.I))
            if name_el:
                name = name_el.get_text(strip=True)

        if not name or len(name) < 2:
            return None

        # Phone Number
        phone = ""
        phone_el = container.find("div", class_=re.compile("phones|phone", re.I))
        if phone_el:
            phone = phone_el.get_text(strip=True)
        if not phone:
            phone = extract_phone(container.get_text())

        # Website URL
        website = ""
        link_el = container.find("a", class_=re.compile("track-visit-website|website-link", re.I))
        if link_el:
            website = link_el.get("href", "")
        if not website:
            # Try any external link that isn't yp itself
            for a in container.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "yellowpages.com" not in href:
                    website = href
                    break

        # Address (bonus)
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


def scrape_yellowpages(service, city, max_pages=MAX_PAGES):
    """Scrape Yellow Pages search results for a service + city."""
    businesses = []
    session = requests.Session()

    console.print(f"\n[bold cyan]Target:[/bold cyan] {service} in {city}")
    console.print(f"[bold yellow]Pages to scrape:[/bold yellow] {max_pages}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]Scraping pages...", total=max_pages)

        for page in range(1, max_pages + 1):
            url = build_yellowpages_url(service, city, page)
            headers = get_random_headers()
            progress.update(task, description=f"[cyan]Page {page}/{max_pages} - Fetching results...")

            try:
                random_delay()
                resp = session.get(url, headers=headers, timeout=20)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                page_businesses = []

                # Main listing containers on Yellow Pages
                results = soup.find_all("div", class_=re.compile("result|listing|v-card", re.I))

                for result in results:
                    biz = parse_yellowpages_listing(result, service, city)
                    if biz:
                        page_businesses.append(biz)

                # Fallback: if structured classes failed, try a broader scrape
                if not page_businesses:
                    # Look for search results in standard YP layout
                    results = soup.find_all("div", class_=re.compile("srp-listing|search-result", re.I))
                    for result in results:
                        biz = parse_yellowpages_listing(result, service, city)
                        if biz:
                            page_businesses.append(biz)

                # Second fallback: look for any div that contains a business-like name + phone pattern
                if not page_businesses:
                    all_divs = soup.find_all("div")
                    for div in all_divs:
                        text = div.get_text()
                        # Check if this div has both a reasonable name length and a phone pattern
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        if len(lines) < 2:
                            continue
                        potential_name = lines[0]
                        if len(potential_name) < 3 or len(potential_name) > 80:
                            continue
                        phone_found = extract_phone(text)
                        if phone_found:
                            # Try to find a link inside
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
                progress.update(task, advance=1)

                if not page_businesses:
                    console.print("[yellow]⚠ No results on this page. Checking next page or stopping...[/yellow]")
                # Stop early if page returned very few results
                if len(page_businesses) < 3 and page > 1:
                    console.print("[yellow]⚠ Very few results. Stopping early to avoid wasted requests.[/yellow]")
                    break

            except requests.exceptions.RequestException as e:
                console.print(f"[red]✗ Error on page {page}: {e}[/red]")
                random_delay()
                continue
            except Exception as e:
                console.print(f"[red]✗ Unexpected error on page {page}: {e}[/red]")
                continue

    return businesses


def enrich_with_emails(businesses):
    """Second pass: visit each business website to find email addresses."""
    console.print(f"\n[bold cyan]🔍 Enriching {len(businesses)} leads with email addresses...[/bold cyan]")

    session = requests.Session()
    enriched = []

    for i, biz in enumerate(businesses):
        website = biz.get("Website URL", "")
        if website and website.startswith("http"):
            email = extract_email_from_url(website, session, get_random_headers())
            biz["Email Address"] = email
        enriched.append(biz)

        # Progress every 10
        if (i + 1) % 10 == 0:
            console.print(f"[dim]  Processed {i + 1}/{len(businesses)}...[/dim]")

    return enriched


def save_to_csv(businesses, filename=OUTPUT_CSV):
    """Save results to a clean, formatted CSV file."""
    if not businesses:
        console.print("[red]✗ No businesses found to save.[/red]")
        return False

    df = pd.DataFrame(businesses)

    # Reorder columns for clarity
    column_order = ["Business Name", "Phone Number", "Website URL", "Email Address",
                    "Service Type", "City Searched", "Address", "Date Scraped"]
    cols = [c for c in column_order if c in df.columns]
    df = df[cols]

    # Clean up data
    df = df.drop_duplicates(subset=["Business Name", "Phone Number"])
    df = df.reset_index(drop=True)

    df.to_csv(filename, index=False, encoding="utf-8-sig")
    console.print(f"\n[bold green]✓ Saved {len(df)} leads to [cyan]{filename}[/cyan][/bold green]")
    return True


# =============================================================================
# BANNER & MAIN
# =============================================================================

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🏠  Home Services Lead Scraper PRO  🏠                    ║
║                                                              ║
║   Generate unlimited web design & SEO client leads          ║
║   for your agency in minutes.                               ║
║                                                              ║
║   ⚡ Anti-Blocking Technology  📊 CSV Export  🎯 Targeted   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


def main():
    console.print(Panel.fit(BANNER, border_style="blue"))

    # --- Service Type Input ---
    console.print("\n[bold]What type of home service business do you want to target?[/bold]")
    console.print("[dim]Examples: roofer, plumber, electrician, HVAC, painter, landscaper, contractor[/dim]")

    service = input("\n  ➤ Enter Service Type: ").strip()

    if not service:
        console.print("[red]✗ Service type cannot be empty. Exiting.[/red]")
        sys.exit(1)

    # --- City Input ---
    console.print(f"\n[bold]Which city/area do you want to search in?[/bold]")
    console.print("[dim]Examples: Dallas TX, London UK, Chicago IL, Miami FL[/dim]")

    city = input("\n  ➤ Enter City: ").strip()

    if not city:
        console.print("[red]✗ City cannot be empty. Exiting.[/red]")
        sys.exit(1)

    # --- Confirmation ---
    console.print(f"\n[bold yellow]Ready to scrape:[/bold yellow] [cyan]{service}[/cyan] in [cyan]{city}[/cyan]")
    confirm = input("  ➤ Start scraping? (y/n): ").strip().lower()

    if confirm not in ["y", "yes"]:
        console.print("[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    # --- Run Scraper ---
    start_time = time.time()
    console.print(f"\n[bold green]🚀 Starting scrape at {datetime.now().strftime('%H:%M:%S')}[/bold green]")

    try:
        # Main scrape
        businesses = scrape_yellowpages(service, city)

        if not businesses:
            console.print("\n[bold red]⚠ No results found.[/bold red]")
            console.print("[yellow]Possible reasons:[/yellow]")
            console.print("  • Yellow Pages may be blocking automated requests")
            console.print("  • Try a different service type or city")
            console.print("  • Check your internet connection")
            console.print("\n[dim]Tip: Wait a few minutes and try again.[/dim]")
            sys.exit(0)

        # Enrich with emails
        businesses = enrich_with_emails(businesses)

        # Remove duplicates
        seen = set()
        unique_businesses = []
        for biz in businesses:
            key = (biz["Business Name"], biz.get("Phone Number", ""))
            if key not in seen:
                seen.add(key)
                unique_businesses.append(biz)

        # Save to CSV
        saved = save_to_csv(unique_businesses)

        if saved:
            elapsed = time.time() - start_time
            mins, secs = divmod(int(elapsed), 60)

            console.print(f"\n[bold green]✅ SCRAPE COMPLETE![/bold green]")
            console.print(f"   • Total leads found: [cyan]{len(unique_businesses)}[/cyan]")
            console.print(f"   • With emails: [cyan]{sum(1 for b in unique_businesses if b.get('Email Address'))}[/cyan]")
            console.print(f"   • With phone numbers: [cyan]{sum(1 for b in unique_businesses if b.get('Phone Number'))}[/cyan]")
            console.print(f"   • Time elapsed: [cyan]{mins}m {secs}s[/cyan]")
            console.print(f"   • Output file: [cyan]{OUTPUT_CSV}[/cyan]")
            console.print(f"\n[bold]📋 Open the CSV file to see your leads![/bold]")
            console.print("[dim]You can now import this into your CRM, send cold emails, or make calls.[/dim]\n")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Scrape interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]✗ Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
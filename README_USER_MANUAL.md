# Home Services Lead Scraper Pro
## User Manual — For Non-Technical Agency Owners

---

## Table of Contents
1. [What Is This Tool?](#what-is-this-tool)
2. [What You'll Get](#what-youll-get)
3. [Requirements](#requirements)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [How to Run the Scraper](#how-to-run-the-scraper)
6. [Understanding the Output](#understanding-the-output)
7. [What to Do With Your Leads](#what-to-do-with-your-leads)
8. [Troubleshooting](#troubleshooting)
9. [Pro Tips](#pro-tips)

---

## What Is This Tool?

**Home Services Lead Scraper Pro** is a simple Python tool that automatically finds local home service businesses (like roofers, plumbers, electricians) in ANY city you choose and gives you their:

- ✅ Business Name
- ✅ Phone Number
- ✅ Website URL
- ✅ Email Address (when available)
- ✅ Address

All in a clean, organized **CSV file** (opens in Excel or Google Sheets).

**Think of it as your personal lead generation assistant** — instead of spending hours on Yellow Pages copy-pasting business info, you get hundreds of leads in minutes.

---

## What You'll Get

After installing, you'll have:

| File | Description |
|------|-------------|
| `app.py` | The modern web app (Streamlit) with dual-mode scraping |
| `agency_scraper.py` | The original command-line script for power users |
| `requirements.txt` | List of required software libraries |
| `README_USER_MANUAL.md` | This file |
| `GUMROAD_LISTING.txt` | Product info |
| `LICENSE.txt` | License terms |

**Output file created when you run the scraper:**
| File | Description |
|------|-------------|
| `agency_leads.csv` | YOUR RESULTS — the leads you scraped (web app) |

---

## Requirements

### What You Need on Your Computer

1. **Python 3.8 or newer** — A free programming language that runs the script
2. **Internet connection** — The tool needs to search Yellow Pages
3. **Windows, Mac, or Chromebook** — Works on all major operating systems

### Do You Already Have Python?

- **Windows:** Open Command Prompt (press `Win + R`, type `cmd`, press Enter) and type:
  ```
  python --version
  ```
  If you see something like `Python 3.10.5`, you're good. If you see "Python was not found" or "Microsoft Store" pops up, you need to install it (see Step 1 below).

- **Mac:** Open Terminal (`Cmd + Space`, type "Terminal") and type:
  ```
  python3 --version
  ```

---

## Step-by-Step Setup

### STEP 1: Install Python (if you don't have it)

**For Windows:**
1. Go to: **https://www.python.org/downloads/**
2. Click the big yellow **"Download Python"** button
3. Run the installer
4. **IMPORTANT:** At the bottom of the installer, check the box that says **"Add Python to PATH"**
5. Click **"Install Now"**
6. Wait for it to finish, then close the installer

**For Mac:**
1. Go to: **https://www.python.org/downloads/**
2. Download the latest Mac installer
3. Double-click the downloaded file and follow the instructions
4. Open Terminal and type `python3 --version` to confirm it worked

**Verify Installation:**
Close and reopen your Command Prompt/Terminal, then type:
```
python --version
```
(On Mac, type `python3 --version`)

You should see a version number like `Python 3.10.5`. If you do — **you're ready for Step 2!**

---

### STEP 2: Install the Required Packages

The tool needs some extra tools (called "libraries") to work. Here's how to install them:

1. **Open Command Prompt (Windows) or Terminal (Mac):**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Mac: Press `Cmd + Space`, type "Terminal", press Enter

2. **Navigate to the folder where you unzipped this product.**
   For example, if you extracted it to your Desktop:
   ```
   cd Desktop\Agency_Lead_Scraper_Tool
   ```
   (On Mac, replace backslashes `\` with forward slashes `/`):
   ```
   cd Desktop/Agency_Lead_Scraper_Tool
   ```

3. **Run this command to install everything at once:**
   ```
   pip install -r requirements.txt
   ```

   You should see it downloading and installing several packages. This is normal.

   **If you get an error on Mac, try:**
   ```
   pip3 install -r requirements.txt
   ```

   **If you get a permissions error, try adding `--user`:**
   ```
   pip install --user -r requirements.txt
   ```

---

### STEP 3 (OPTIONAL but Recommended): Create a Virtual Environment

A "virtual environment" keeps this tool's libraries separate from other Python programs on your computer. It's like having a private workspace.

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Mac:**
```
python3 -m venv venv
source venv/bin/activate
```

After activating, your command prompt should show `(venv)` at the beginning. To deactivate when done:
```
deactivate
```

*Note: If you don't want to use a virtual environment, that's fine. Skip this step and go straight to running the scraper.*

---

## How to Run the Scraper

This product includes **TWO** ways to run the scraper:

- **Option A: Web App (Recommended)** — A modern, browser-based interface with dual-mode scraping
- **Option B: Command Line** — The original terminal-based script for advanced users

---

### Option A: Web App (Streamlit) — RECOMMENDED

The web app gives you a clean, modern interface directly in your browser. No need to type commands — just click and go.

#### Running the Web App Locally

1. **Make sure you're in the right folder** in your Command Prompt/Terminal:
   ```
   cd Desktop\Agency_Lead_Scraper_Tool
   ```

2. **Launch the app:**
   ```
   streamlit run app.py
   ```

3. **Your browser will open automatically** showing the Home Services Lead Scraper PRO interface.

4. **Enter your target:**
   - Service Type: e.g., "roofer", "plumber", "electrician"
   - City / Area: e.g., "Dallas TX", "London UK", "Chicago IL"

5. **Choose your Scrape Mode:**
   - **Turbo Mode (Premium API)** — Routes requests through a premium proxy. Best for cloud hosting or if you're getting blocked. Requires a premium API key (ScraperAPI, ScrapingBee, etc.).
   - **Standard Mode (Free Direct)** — Direct connection to Yellow Pages. Great for local use on your own machine. No API key needed.

6. **Click "Generate Leads"** and watch the magic happen.

7. **Download your CSV** when the scrape finishes.

---

#### Deploying to the Cloud (Free Hosting)

Want to access your scraper from anywhere, even on your phone? Deploy it for free on Streamlit Cloud:

1. **Get a premium scraping API key** (needed for cloud use):
   - Sign up at [ScraperAPI.com](https://www.scraperapi.com) or [ScrapingBee.com](https://www.scrapingbee.com)
   - Copy your API key

2. **Push the code to GitHub:**
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

3. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Select your repository and the `app.py` file
   - Click "Deploy"

4. **Add your API key:**
   - In the Streamlit Cloud dashboard, go to Settings → Secrets
   - Add your API key (you'll need to update `app.py` to read from `st.secrets` instead of the hardcoded URL — contact support if you need help)

---

### Option B: Command Line (Original Script)

If you prefer the terminal or want more control:

1. **Make sure you're in the right folder** in your Command Prompt/Terminal:
   ```
   cd Desktop\Agency_Lead_Scraper_Tool
   ```

2. **Run the script:**
   ```
   python agency_scraper.py
   ```
   (On Mac: `python3 agency_scraper.py`)

3. **Follow the prompts:**
   The script will ask you:
   - **Service Type:** What kind of business? (e.g., "roofer", "plumber", "electrician")
   - **City:** Which city? (e.g., "Dallas TX", "London UK", "Chicago IL")
   - **Confirm:** Type `y` and press Enter to start

4. **Watch it work!**
   You'll see a beautiful progress bar showing how many pages it's scraping. The script will:
   - Search Yellow Pages for businesses matching your criteria
   - Visit each business website to find email addresses
   - Save everything to `agency_leads.csv`

5. **Done!**
   When it finishes, open `agency_leads.csv` in Excel or Google Sheets.

---

## Understanding the Output

Your `agency_leads.csv` file will have these columns:

| Column | What's In It? |
|--------|--------------|
| **Business Name** | Name of the local business |
| **Phone Number** | Their main contact number |
| **Website URL** | Link to their website |
| **Email Address** | Email found on their site (blank if not found) |
| **Service Type** | The service type you searched for |
| **City Searched** | The city you searched in |
| **Address** | Business address (when available) |
| **Date Scraped** | When you ran the script |

**Example row:**
```
ABC Roofing,(555) 123-4567,https://abcroofing.com,info@abcroofing.com,roofer,Dallas TX,123 Main St,2024-01-15 14:30
```

---

## What to Do With Your Leads

### Immediate Actions
1. **Open the CSV in Excel or Google Sheets**
2. **Clean up the data:**
   - Delete any rows with blank Business Names
   - Remove duplicates (Excel: Data → Remove Duplicates)
3. **Prioritize leads with emails** — these are your warmest prospects

### Outreach Ideas
- **Cold Email:** Send a personalized email offering a free website audit
- **Cold Call:** Use the phone numbers to reach decision-makers directly
- **LinkedIn:** Search for the business name to find the owner on LinkedIn
- **Google Maps Review:** Leave a thoughtful review of their current site to get noticed

### CRM Integration
Import the CSV into:
- HubSpot (free CRM)
- Google Sheets (shared with your team)
- Streak (Gmail CRM)
- Pipedrive

---

## Troubleshooting

### Problem: "Python was not found" or "python is not recognized"

**Solution:** Python isn't installed or wasn't added to PATH.
1. Reinstall Python from python.org
2. **During installation, CHECK THE BOX that says "Add Python to PATH"**
3. Restart your computer
4. Try again

---

### Problem: "No module named 'requests'" or similar import errors

**Solution:** The required libraries aren't installed.
```
pip install requests beautifulsoup4 pandas fake-useragent streamlit rich tqdm
```
(Mac: replace `pip` with `pip3`)

---

### Problem: "streamlit" command not found

**Solution:** Streamlit wasn't installed.
```
pip install streamlit
```

---

### Problem: "0 leads found" or the scraper finishes too quickly

**Solution:** Yellow Pages may be blocking automated requests.
1. **Wait 5-10 minutes** and try again
2. Try a **different city** or **different service type**
3. Make sure your **internet connection is stable**
4. Some sites block scrapers — this is normal, just try again later
5. If using Standard Mode, try switching to Turbo Mode

---

### Problem: The scraper is very slow

**Solution:** The tool intentionally waits between requests (2-5 seconds) to avoid being blocked. This is GOOD — it means you won't get banned.
- To speed it up: Edit `agency_scraper.py` and change `MIN_DELAY = 2` to `MIN_DELAY = 1` and `MAX_DELAY = 5` to `MAX_DELAY = 3`
- **Warning:** Going too fast may get you blocked

---

### Problem: "Permission denied" when installing packages

**Solution (Windows):** Open Command Prompt as Administrator (right-click → Run as administrator)

**Solution (Mac/Linux):** Add `--user` to the pip command:
```
pip install --user -r requirements.txt
```

---

### Problem: "encoding" errors or weird characters in the CSV

**Solution:** The script saves with UTF-8 encoding (with BOM), which Excel handles correctly.
- If you see weird characters: Open the CSV in **Google Sheets** instead of Excel
- Or in Excel: File → Open → Browse → Select "All Files" → Select your CSV → Import Wizard → Select "UTF-8" encoding

---

### Problem: Script stops halfway through

**Solution:** This usually means your internet disconnected.
1. Check your WiFi/ethernet
2. The script saves partial results in `agency_leads.csv`
3. Re-run the script to continue — it will append new results

---

## Pro Tips

### Getting Better Results
1. **Be specific with service types:**
   - Instead of "contractor", try "roofing contractor" or "bathroom remodeler"
   - Instead of "cleaner", try "house cleaning service" or "maid service"

2. **Target mid-sized cities first:**
   - Small towns: < 50 leads (not enough)
   - Major metros: 100+ leads (perfect)
   - NYC/LA: 200+ leads (you may want to limit pages)

3. **Run the scraper at different times of day:**
   - Morning (9-11 AM): Lower competition, fewer blocks
   - Afternoon (2-4 PM): More business owners online

### Email Finding Tips
- Not all websites have emails visible — that's normal
- If a website has a "Contact Us" page, there's often an email there
- The script only scrapes the homepage for speed — for deeper email finding, use tools like Hunter.io

### Avoiding Blocks
- Don't run the script more than 3-5 times per hour on the same city
- Use the delays built into the script
- If you get blocked, wait 15-30 minutes before trying again

### Scaling Up
- Run the scraper for 5-10 different service types in your target city
- Target 3-5 cities to build a regional lead database
- Combine results into one master CSV using Excel's Power Query or Google Sheets IMPORTRANGE

---

## Technical Notes (For Your IT Person)

If you have a developer or tech-savvy friend, here's the technical stack:

- **Language:** Python 3.8+
- **Web Framework:** Streamlit
- **Libraries:** requests, beautifulsoup4, pandas, fake-useragent, streamlit, rich, tqdm
- **Scraping Engine:** BeautifulSoup + requests targeting Yellow Pages static HTML
- **Dual-Mode Engine:** Direct connection OR premium proxy API (ScraperAPI/ScrapingBee compatible)
- **Anti-Blocking:** Rotating User-Agents, random delays, session management
- **Data Export:** Pandas DataFrame → UTF-8 CSV with BOM

---

## Need Help?

If you run into issues not covered here:

1. Double-check all steps in this manual
2. Make sure Python is properly installed
3. Try the commands in a fresh Command Prompt window
4. Copy-paste the exact error message into Google — there's almost always a solution

**The tool is designed to be beginner-friendly. If it's not working, the problem is almost always:**
- Python not installed correctly
- Libraries not installed (`pip install -r requirements.txt`)
- Wrong folder (make sure you're in the same folder as `app.py` or `agency_scraper.py`)

---

*Happy Scraping! 🚀*

*Home Services Lead Scraper Pro — Your Unfair Advantage in Client Acquisition*
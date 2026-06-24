"""
Tutorial Video Recorder
Automated recording of complete app walkthrough using Selenium
Produces a video file showing login → usage → CSV download
"""

import time
import os
import sys
from datetime import datetime

# Check dependencies
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    print("✓ Selenium available")
except ImportError:
    print("❌ Selenium not found. Install with: pip install selenium webdriver-manager")
    sys.exit(1)

try:
    import imageio
    print("✓ imageio available for video creation")
except ImportError:
    print("❌ imageio not found. Install with: pip install imageio imageio-ffmpeg")
    sys.exit(1)

# Setup output
os.makedirs("tutorial_video", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
output_video = f"tutorial_video/tutorial_{timestamp}.mp4"
frames_dir = "tutorial_video/frames"
os.makedirs(frames_dir, exist_ok=True)

# Chrome setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1280,720")
chrome_options.add_argument("--disable-gpu")

print("\n" + "="*70)
print("TUTORIAL VIDEO RECORDER")
print("="*70)
print("\nThis script will:")
print("1. Open the app at http://localhost:8501")
print("2. Login with access code LEAD2026")
print("3. Navigate through all sections")
print("4. Generate leads and download CSV")
print("5. Compile everything into a tutorial video")
print("\n" + "="*70)

input("\nPress ENTER to start recording...")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)
frame_count = 0

def capture_frame(label):
    global frame_count
    frame_count += 1
    filename = f"{frames_dir}/frame_{frame_count:04d}_{label}.png"
    driver.save_screenshot(filename)
    print(f"  [{frame_count:2d}] Captured: {label}")
    time.sleep(1)  # Hold each frame for 1 second

try:
    print("\n🎬 STARTING RECORDING...")
    print("-" * 70)
    
    # Navigate to app
    driver.get("http://localhost:8501")
    time.sleep(3)
    capture_frame("01_app_login_page")
    
    # Login
    print("\n📝 Step 1: Login")
    access_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    access_input.send_keys("LEAD2026")
    time.sleep(1)
    
    try:
        unlock_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Unlock Tool')]")
    except:
        try:
            unlock_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        except:
            unlock_btn = driver.find_element(By.CSS_SELECTOR, "button[kind='primary']")
    
    capture_frame("02_code_entered")
    unlock_btn.click()
    time.sleep(4)
    capture_frame("03_logged_in_hero")
    
    # Show target selection
    print("\n🎯 Step 2: Target Selection")
    driver.execute_script("window.scrollBy(0, 300)")
    time.sleep(1)
    capture_frame("04_target_input_fields")
    
    # Click a service chip
    print("\n🔧 Step 3: Service Selection")
    try:
        plumber_chip = driver.find_element(By.XPATH, "//button[contains(text(), 'Plumber')]")
        plumber_chip.click()
        time.sleep(1)
        capture_frame("05_service_selected")
    except:
        capture_frame("05_service_selected_no_click")
    
    # Enter city
    print("\n📍 Step 4: City Input")
    try:
        city_input = driver.find_element(By.XPATH, "//input[@placeholder*='Dallas']")
        city_input.clear()
        city_input.send_keys("Dallas TX")
        time.sleep(1)
        capture_frame("06_city_entered")
    except:
        capture_frame("06_city_entered_alt")
    
    # Show coverage table
    print("\n🌍 Step 5: Coverage Table")
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(1)
    capture_frame("07_coverage_table_top")
    
    driver.execute_script("window.scrollBy(0, 300)")
    time.sleep(1)
    capture_frame("08_coverage_table_middle")
    
    # Show pro tips
    print("\n💡 Step 6: Pro Tips")
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(1)
    capture_frame("09_pro_tips")
    
    # Scroll back to generate button
    print("\n🚀 Step 7: Generate Leads")
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    driver.execute_script("window.scrollBy(0, 900)")
    time.sleep(1)
    capture_frame("10_generate_button")
    
    # Click generate
    try:
        generate_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Leads')]")
        generate_btn.click()
        print("  Clicked Generate Leads...")
        time.sleep(8)  # Wait for scraping
        capture_frame("11_scraping_in_progress")
    except:
        capture_frame("11_no_generate_click")
    
    # Show results
    print("\n📊 Step 8: Results")
    time.sleep(3)
    capture_frame("12_results_displayed")
    
    # Scroll to show CSV download
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        capture_frame("13_csv_download_button")
    except:
        capture_frame("13_download_alt")
    
    print("\n" + "-" * 70)
    print(f"✅ Captured {frame_count} frames")
    
finally:
    driver.quit()
    print("✓ Browser closed")

# Compile frames into video
print("\n🎬 COMPILING VIDEO...")
print("-" * 70)

frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
print(f"Processing {len(frame_files)} frames...")

# Create video from frames
fps = 1  # 1 frame per second (adjust as needed)
writer = imageio.get_writer(output_video, fps=fps, codec='libx264', quality=8)

for i, frame_file in enumerate(frame_files, 1):
    frame_path = os.path.join(frames_dir, frame_file)
    image = imageio.imread(frame_path)
    writer.append_data(image)
    if i % 5 == 0:
        print(f"  Processing: {i}/{len(frame_files)} frames")

writer.close()

# Get file size
size_mb = os.path.getsize(output_video) / (1024 * 1024)
print(f"\n✅ VIDEO CREATED!")
print(f"   Location: {output_video}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Duration: ~{len(frame_files)} seconds")
print(f"   Frames: {len(frame_files)}")

print("\n" + "="*70)
print("TUTORIAL VIDEO SECTIONS:")
print("="*70)
for i, frame_file in enumerate(frame_files, 1):
    label = frame_file.replace(f"frame_{i:04d}_", "").replace(".png", "")
    print(f"  {i:2d}. {label}")
print("="*70)

print("\n💡 TIP: Add voiceover using video editing software like:")
print("   • CapCut (free)")
print("   • DaVinci Resolve (free)")
print("   • Adobe Premiere Pro")
print("\n   Or use Audacity to record narration separately")
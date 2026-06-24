"""
Create tutorial video from existing screenshots
Produces a smooth slideshow video showing the complete app
"""

import os
import sys
from datetime import datetime

try:
    import imageio
    import imageio.v2 as imageio_v2
    print("✓ imageio available")
except ImportError:
    print("❌ Install: pip install imageio imageio-ffmpeg")
    sys.exit(1)

# Setup
os.makedirs("tutorial_video", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
output_video = f"tutorial_video/tutorial_slideshow_{timestamp}.mp4"

# Load screenshots in order
screenshots_dir = "screenshots"
screenshot_files = sorted([
    f for f in os.listdir(screenshots_dir) 
    if f.endswith('.png')
])

print("\n" + "="*70)
print("TUTORIAL VIDEO FROM SCREENSHOTS")
print("="*70)
print(f"\nFound {len(screenshot_files)} screenshots:")
for i, f in enumerate(screenshot_files, 1):
    label = f.replace(".png", "").replace("_", " ").title()
    print(f"  {i}. {label}")

if len(screenshot_files) < 10:
    print("\n⚠️  Warning: Less than 10 screenshots found.")
    resp = input("Continue anyway? (y/n): ")
    if resp.lower() != 'y':
        sys.exit(0)

print("\n🎬 Creating tutorial video...")
print("  Each screenshot shown for 2 seconds")
print("  Resolution: 1920x1080")
print("  FPS: 1")

# Create writer
writer = imageio_v2.get_writer(
    output_video, 
    fps=1,
    codec='libx264',
    quality=8,
    macro_block_size=8,
    pixelformat='yuv420p'
)

frames_per_screenshot = 2  # Show each screenshot for 2 seconds
total_frames = len(screenshot_files) * frames_per_screenshot

for idx, filename in enumerate(screenshot_files, 1):
    filepath = os.path.join(screenshots_dir, filename)
    
    # Read image
    img = imageio_v2.imread(filepath)
    
    # Add frame multiple times to extend duration
    for _ in range(frames_per_screenshot):
        writer.append_data(img)
    
    # Progress
    progress = (idx / len(screenshot_files)) * 100
    print(f"  [{idx:2d}/{len(screenshot_files)}] {filename} ({progress:.0f}%)")

writer.close()

# Stats
size_mb = os.path.getsize(output_video) / (1024 * 1024)
duration_sec = total_frames

print(f"\n{'='*70}")
print(f"✅ TUTORIAL VIDEO CREATED!")
print(f"{'='*70}")
print(f"  📁 File    : {output_video}")
print(f"  📦 Size    : {size_mb:.1f} MB")
print(f"  ⏱️  Duration: ~{duration_sec} seconds ({duration_sec//60}m {duration_sec%60}s)")
print(f"  🖼️  Frames  : {total_frames}")
print(f"  📐 Res     : 1920x1080")
print(f"{'='*70}")

print("\n📋 VIDEO SEQUENCE:")
for i, f in enumerate(screenshot_files, 1):
    label = f.replace(".png", "").replace("_", " ").title()
    print(f"  {i:2d}. {label}")

print("\n💡 ENHANCEMENT TIPS:")
print("  1. Record voiceover with Audacity (free)")
print("  2. Import video into CapCut (free)")
print("  3. Add text overlays explaining each section")
print("  4. Add background music")
print("  5. Export in 1080p for best quality")
print("\n📍 Output location:", output_video)
print("="*70)
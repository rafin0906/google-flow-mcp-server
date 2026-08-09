import base64
import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.boss_functions import create_project, generate_poster

img2_path = r"C:\Users\sohel\.gemini\antigravity-ide\brain\cda0ddde-a9b0-47f1-8391-1124c22c6ad0\media__1786266455262.png"
img3_path = r"C:\Users\sohel\.gemini\antigravity-ide\brain\cda0ddde-a9b0-47f1-8391-1124c22c6ad0\media__1786266457595.png"

print(f"Reading image 2 from {img2_path}...")
with open(img2_path, "rb") as f:
    b64_img2 = base64.b64encode(f.read()).decode("utf-8")

print(f"Reading image 3 from {img3_path}...")
with open(img3_path, "rb") as f:
    b64_img3 = base64.b64encode(f.read()).decode("utf-8")

images_b64 = [
    {"name": "dhaka_metro_train.png", "mime": "image/png", "b64": b64_img2},
    {"name": "card_turnstile.png", "mime": "image/png", "b64": b64_img3}
]

prompt = (
    "A professional news poster design in 4:3 aspect ratio, featuring the Dhaka Metro Rail train "
    "from the first uploaded image and the person holding/tapping a debit or credit card at the metro ticket turnstile gate from the second uploaded image.\n\n"
    "At the very top of the poster, display bold headline text: \"DHAKA METRO MAY SOON ALLOW PASSENGERS TO PAY FARES WITH DEBIT, CREDIT CARDS\".\n\n"
    "Include news branding overlays: \"SOZOO TODAY\" in the top left corner, and \"FROM: BDNEWS24.COM\" in the top right corner.\n\n"
    "Aesthetic & Style: Match the exact look and feel of the reference news poster example: dark cinematic background, sleek cyan and green lighting, sharp high-contrast photojournalism typography, modern broadcast graphics layout."
)

print("Step 1: Running Boss Function 1 (create_project)...")
proj_res = create_project(ratio="4:3", headless=True)
print(f"Project Created Result: {proj_res}")

print("\nStep 2: Running Boss Function 2 (generate_poster)...")
gen_res = generate_poster(
    project_url=proj_res["project_url"],
    prompt=prompt,
    images_b64=images_b64,
    headless=True
)
print(f"\nPoster Generated Result: {gen_res}")

import os
from google import genai
from PIL import Image

# 1. SETUP
# Paste your Gemini API Key here
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# 2. LOAD YOUR PHOTO
try:
    img = Image.open("sketch.jpg")
except FileNotFoundError:
    print("Error: 'sketch.jpg' not found in this folder.")
    exit()

print("Sending sketch to Gemini 3 Flash (Latest 2025 Model)...")

# 3. THE REQUEST
# Using the updated 2025 model ID
response = client.models.generate_content(
    model="gemini-3-flash-preview", 
    contents=[
        "You are an OpenSCAD engineer. Convert this hand-drawn sketch into 3D code. "
        "Use $fn=50; and difference() for any holes. Output ONLY raw code.",
        img
    ]
)

# 4. SAVE AND CLEAN
scad_code = response.text
# Removes markdown formatting if present
clean_code = scad_code.replace("```openscad", "").replace("```", "").strip()

with open("part.scad", "w") as f:
    f.write(clean_code)

print("\n--- SUCCESS ---")
print("Successfully created 'part.scad'.")
print("Open OpenSCAD and hit F5 to see your 3D model!")
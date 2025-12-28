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



# 3a. DYNAMICALLY LOAD ALL LIBRARIES
# This part looks into your folder and reads the text for the AI
library_folder = "libraries"
all_library_context = ""
library_list = []

if os.path.exists(library_folder):
    for filename in os.listdir(library_folder):
        if filename.endswith(".scad"):
            library_list.append(filename)
            path = os.path.join(library_folder, filename)
            with open(path, "r") as f:
                # We wrap each file in a header so the AI doesn't get confused
                all_library_context += f"\n--- LIBRARY: {filename} ---\n{f.read()}\n"

# 3b. THE REQUEST
# This is the updated version that gives the AI your library "Knowledge"
response = client.models.generate_content(
    model="gemini-3-flash-preview", 
    contents=[
        f"""You are a Senior Mechanical Engineer. 
        Convert the user's sketch or request into OpenSCAD code.

        KNOWLEDGE BASE (Libraries and Examples):
        {all_library_context}

        """
        INSTRUCTIONS:
        1. Scan the KNOWLEDGE BASE for relevant modules and 'AI REFERENCE EXAMPLES'.
        2. Follow the coordinate logic shown in the examples (e.g., centering math).
        3. Always include 'include <libraries/FILENAME.scad>;' for any library used.
        4. Output your response in this EXACT format:
           [DECODED LOGIC]: (A one-sentence summary of the math/standards used)
           [RESULT_CODE]: (The raw OpenSCAD code)
           """,
        img
    ]
)


# 4. PARSE AND SAVE
full_response = response.text

# Split the response into Logic and Code
if "[RESULT_CODE]:" in full_response:
    parts = full_response.split("[RESULT_CODE]:")
    decoded_logic = parts[0].replace("[DECODED LOGIC]:", "").strip()
    scad_code = parts[1].strip()
else:
    # Fallback if AI forgets the tag
    decoded_logic = "Standard generation"
    scad_code = full_response

# Aggressively remove Markdown formatting
clean_code = scad_code.replace("```openscad", "").replace("```scad", "").replace("```", "").strip()

# Store the logic in a variable so you can use it for your 'Yes' button later
print(f"AI LOGIC: {decoded_logic}")

with open("part.scad", "w") as f:
    f.write(clean_code)

# 5. RENDER TO STL
import subprocess

print("Attempting to render STL...")
try:
    # We add 'capture_output=True' to catch the specific OpenSCAD error message
    result = subprocess.run(
        ['/usr/bin/openscad', '-o', 'part.stl', 'part.scad'], 
        capture_output=True, 
        text=True, 
        check=True
    )
    print("--- SUCCESS: 'part.stl' created ---")

except subprocess.CalledProcessError as e:
    print("\n!!! OPENSCAD RENDER ERROR !!!")
    # This prints the ACTUAL error from OpenSCAD (e.g., "File not found" or "Syntax error")
    print(f"Error Message: {e.stderr}")
    
    # Check if it's a library path error
    if "libraries/iso_standards.scad" in e.stderr:
        print("\nSUGGESTION: OpenSCAD can't find your library. Check your folder name and 'include' path.")




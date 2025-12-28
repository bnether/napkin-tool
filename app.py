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
        f"""You are an expert OpenSCAD engineer. 
        I have provided a collection of standard libraries below.
        
        INSTRUCTIONS:
        1. Review the LIBRARY CONTENT to see available modules and functions.
        2. If the user's request matches a library capability, include that library 
           at the top using 'include <libraries/FILENAME.scad>'.
        3. Use high-level modules from the libraries (like 'hole_socket_head') instead of raw cylinders.
        4. If no libraries are relevant, generate standard OpenSCAD code using $fn=50.
        5. Output ONLY raw code. No explanations.

        AVAILABLE LIBRARIES: {', '.join(library_list)}
        
        LIBRARY CONTENT:
        {all_library_context}
        
        Convert this hand-drawn sketch into 3D code:""",
        img
    ]
)


# 4. SAVE AND CLEAN
scad_code = response.text

# THE "SAFE STUFF": Aggressively remove Markdown formatting
clean_code = scad_code.replace("```openscad", "") \
                      .replace("```scad", "") \
                      .replace("```", "") \
                      .strip()

# DEBUG: Print the code to your console so you can see what the AI wrote
print("\n--- GENERATED CODE START ---")
print(clean_code)
print("--- GENERATED CODE END ---\n")

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

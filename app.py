import os
import streamlit as st
from google import genai
from PIL import Image
from datetime import datetime

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
# Updated with correct string formatting
prompt_text = f"""You are a Senior Mechanical Engineer. 
Convert the user's sketch or request into OpenSCAD code.

KNOWLEDGE BASE (Libraries and Examples):
{all_library_context}

INSTRUCTIONS:
1. Scan the KNOWLEDGE BASE for relevant modules and 'AI REFERENCE EXAMPLES'.
2. Follow the coordinate logic shown in the examples (e.g., centering math).
3. Always include 'include <libraries/FILENAME.scad>;' for any library used.
4. Output your response in this EXACT format:
   [DECODED LOGIC]: (A one-sentence summary of the math/standards used)
   [RESULT_CODE]: (The raw OpenSCAD code)
"5. CRITICAL: For holes or subtractions, you MUST wrap the code in a difference() block. The first object is the base, and all following objects are the holes to be removed."
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview", 
    contents=[prompt_text, img]
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

st.subheader("3D Preview & Feedback")

try:
    # Use 'openscad' without path if it's in your system PATH
    result = subprocess.run(
        ['openscad', '-o', 'part.stl', 'part.scad'], 
        capture_output=True, 
        text=True, 
        check=True
    )
    st.success("✅ STL Rendered Successfully!")
    # Optional: If you want to show the code to the user
    with st.expander("View Generated OpenSCAD Code"):
        st.code(clean_code, language='cpp')

except subprocess.CalledProcessError as e:
    st.error(f"OpenSCAD Error: {e.stderr}")

# 6. USER FEEDBACK SYSTEM
st.divider()
st.write("### Is this part correct?")
col1, col2 = st.columns(2)

def save_feedback(category):
    os.makedirs("feedback", exist_ok=True)
    filename = "verified.scad" if category == "VERIFIED" else "review_needed.scad"
    path = os.path.join("feedback", filename)
    
    # Format the entry for your future training
    entry = f"""
/* ===========================================================
[USER_STATUS]: {category}
[TIMESTAMP]: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
[DECODED LOGIC]: {decoded_logic}
[RESULT CODE]:
{clean_code}
=========================================================== */
"""
    with open(path, "a") as f:
        f.write(entry)
    
    if category == "VERIFIED":
        st.toast("Awesome! Added to verified list.", icon="🚀")
    else:
        st.toast("Logged for engineering review.", icon="🔧")

with col1:
    if st.button("✅ Perfect", use_container_width=True):
        save_feedback("VERIFIED")

with col2:
    if st.button("❌ Needs Fixes", use_container_width=True):
        save_feedback("FAILED")



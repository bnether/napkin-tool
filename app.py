import os
import streamlit as st
from google import genai
from PIL import Image
from datetime import datetime

# 1. SETUP
# Paste your Gemini API Key here
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

# 2. USER INPUT & LOAD PHOTO
st.title("AI Mechanical Engineer")

# Add the text input here
user_prompt = st.text_input("What are we building?", placeholder="e.g., A 50mm cube with an M8 hole through the center")

try:
    # If you are using Streamlit's file uploader, use this:
    uploaded_file = st.file_uploader("Upload your sketch", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        # We save it locally so the AI can process 'sketch.jpg' as per your original code
        img.save("sketch.jpg")
    else:
        # Fallback for manual testing if no file is uploaded yet
        img = Image.open("sketch.jpg") 
        
except FileNotFoundError:
    st.warning("Please upload a 'sketch.jpg' or provide a prompt to begin.")
    st.stop() # Stops the script until an image is provided

print(f"Sending request: {user_prompt}")



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
    contents=[prompt_text, user_prompt, img] # Added user_prompt here
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
import os

st.subheader("3D Preview & Feedback")

try:
    # Get the current folder path
    current_dir = os.getcwd()
    
    # Set the Environment to include your libraries folder
    # This fixes the "can't find include file" error on websites
    my_env = os.environ.copy()
    my_env["OPENSCADPATH"] = os.path.join(current_dir, "libraries")

    # Run OpenSCAD
    # Note: We use 'openscad' instead of '/usr/bin/openscad' for web compatibility
    result = subprocess.run(
        ['openscad', '-o', 'part.stl', 'part.scad'], 
        env=my_env,
        capture_output=True, 
        text=True, 
        check=True
    )
    st.success("✅ STL Rendered Successfully!")

except subprocess.CalledProcessError as e:
    # THIS SECTION IS KEY: It shows you why it failed
    st.error("OpenSCAD failed to render the part.")
    with st.expander("Show Technical Error Logs"):
        st.text("--- STDERR (The Error) ---")
        st.code(e.stderr)
        st.text("--- STDOUT (The Output) ---")
        st.code(e.stdout)
        
except FileNotFoundError:
    st.error("CRITICAL: OpenSCAD is not installed on this server. Please ensure 'openscad' is in your packages.txt.")
    

# 6. USER FEEDBACK SYSTEM
st.divider() # This creates a physical line on the page
st.subheader("Human-in-the-Loop Feedback")
st.write("Help train the AI: Did this code follow the standards and logic correctly?")

# Create the layout for the buttons
col_a, col_b = st.columns(2)

# Define the function within the script flow
def save_feedback(category):
    os.makedirs("feedback", exist_ok=True)
    filename = "verified.scad" if category == "VERIFIED" else "review_needed.scad"
    path = os.path.join("feedback", filename)
    
    # We use 'clean_code' and 'decoded_logic' which were defined in Section 4
    entry = f"""
/* ===========================================================
[USER_STATUS]: {category}
[TIMESTAMP]: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
[USER PROMPT]: {user_prompt}
[DECODED LOGIC]: {decoded_logic}
[RESULT CODE]:
{clean_code}
=========================================================== */
"""
    with open(path, "a") as f:
        f.write(entry)
    
    if category == "VERIFIED":
        st.success("Saved to verified.scad! This will be used for future training.")
        st.balloons()
    else:
        st.warning("Logged to review_needed.scad. I'll check the math later.")

# Place the buttons in the columns
with col_a:
    if st.button("✅ Perfect (Add to Training)", use_container_width=True):
        save_feedback("VERIFIED")

with col_b:
    if st.button("❌ Needs Fixes (Flag for Review)", use_container_width=True):
        save_feedback("FAILED")


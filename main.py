import streamlit as st
from google import genai
import PIL.Image
import subprocess
from streamlit_stl import stl_from_file
import json
import re
import os
import shutil
import csv
from datetime import datetime
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Napkin", layout="wide", initial_sidebar_state="collapsed")

# --- STATE MANAGEMENT ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'testimonial_index' not in st.session_state:
    st.session_state.testimonial_index = 0
if 'home_tab' not in st.session_state:
    st.session_state.home_tab = "Why Napkin"

def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* --- GLOBAL LAYOUT & SCALING --- */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
    }
    
    /* NEW: Mobile-only padding and navbar spacing */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 3% !important;
            padding-right: 3% !important;
        }
        .stApp { margin-top: 110px !important; } 
    }

    .stApp { background-color: #0e1117; color: #ffffff; margin-top: 60px; }

    /* --- MODERN NAVBAR --- */
    .nav-wrapper {
        background-color: #0e1117;
        border-bottom: 1px solid #30363d;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 9999;
        display: flex;
        flex-wrap: wrap; /* NEW: Allows menu items to stack on phones */
        justify-content: center;
        align-items: center;
        padding: 0 10px;
    }

    .nav-item {
        padding: 18px 20px;
        color: #8b949e !important;
        text-decoration: none !important;
        font-size: 15px;
        font-weight: 500;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        white-space: nowrap; 
    }

    /* NEW: Slightly smaller nav text on tiny phones */
    @media (max-width: 480px) {
        .nav-item {
            padding: 10px 12px;
            font-size: 13px;
        }
    }

    .nav-item:hover {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff;
    }

    .nav-active {
        color: #ffffff !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* --- HERO SECTION --- */
    .hero-container {
        position: relative;
        width: 100%;
        height: 550px;
        background-image: linear-gradient(to bottom, rgba(14, 17, 23, 0) 50%, rgba(14, 17, 23, 1) 100%), url("app/static/home1.jpg");
        background-size: cover;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0px;
    }
    
    /* NEW: Shrinks hero image height on phones so content is visible */
    @media (max-width: 768px) {
        .hero-container { height: 300px !important; }
        .section-text { font-size: 1.6rem !important; }
        .section-content { width: 95% !important; }
    }

    .section-content { position: relative; z-index: 2; width: 70%; text-align: center; }
    .section-text { font-size: 2.8rem; font-weight: 800; color: white; line-height: 1.2; text-shadow: 2px 2px 15px rgba(0,0,0,0.9); }
    .highlight { color: #58a6ff; }

    /* --- UI ELEMENTS (Testimonials) --- */
    .testimonial-card {
        background: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d;
        display: flex; align-items: center; justify-content: center; min-height: 150px;
        max-width: 800px; margin: 0 auto;
    }

    /* NEW: Stacks user photo above text on portrait phones */
    @media (max-width: 480px) {
        .testimonial-card { flex-direction: column; text-align: center; }
        .testimonial-img { margin-right: 0px !important; margin-bottom: 15px; }
    }

    .testimonial-img { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; margin-right: 25px; border: 2px solid #3b82f6; }

    /* Pagination Dots */
    .dot-container { text-align: center; margin-top: 15px; }
    .dot { height: 10px; width: 10px; margin: 0 5px; background-color: #30363d; border-radius: 50%; display: inline-block; }
    .dot-active { background-color: #3b82f6; width: 25px; border-radius: 5px; }
    
    /* --- PRICING CARDS --- */
    .price-card { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 380px; margin-bottom: 25px;}
    .price-amt { font-size: 2.8rem; font-weight: 800; color: #58a6ff; }
    .per-month { font-size: 1rem; color: #8b949e; font-weight: 400; margin-left: 5px; }
    .currency-sub { font-size: 0.85rem; color: #8b949e; margin-top: -10px; margin-bottom: 15px; }

    .stButton>button { border-radius: 10px; height: 3.5em; background-color: #21262d; color: white; border: 1px solid #30363d; font-weight: 600; width: 100%; }
    button[kind="primary"] { background-color: #3b82f6 !important; border: none !important; }

    /* --- FOOTER --- */
    .footer-minimal {
        background-color: #1e3a8a; 
        border-top: 3px solid #3b82f6;
        padding: 40px 15px; 
        text-align: center; 
        color: #e2e8f0; 
        margin-top: 4rem;
        width: 100%;
    }

    header { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- NAVBAR LOGIC (Using URL Parameters for smooth switching) ---
pages = ["Home", "Make a Part", "Pricing", "Help", "Gallery", "Contact", "Profile", "Admin"]

params = st.query_params
if "p" in params:
    if params["p"] != st.session_state.page:
        st.session_state.page = params["p"]
        st.rerun()

nav_html = '<div class="nav-wrapper">'
for p in pages:
    active_class = "nav-active" if st.session_state.page == p else ""
    nav_html += f'<a href="/?p={p}" target="_self" class="nav-item {active_class}">{p}</a>'
nav_html += '</div>'

st.markdown(nav_html, unsafe_allow_html=True)

# Container for standard page content
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)


# --- ADMIN HELPER FUNCTIONS ---
def save_to_gold_standard(prompt, logic, code):
    file_path = "ai_training.scad"
    
    # 1. Determine the entry number for your records
    entry_num = 1
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
            entry_num = content.count("ENTRY #") + 1
    
    # 2. Get current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 3. Format the block (Prioritizing Logic)
    clean_code = code.replace(" [NEWLINE] ", "\n")
    
    entry = f"""
/* ENTRY #{entry_num} | {date_str}
   PROMPT: {prompt}
   LOGIC: {logic}
   CODE:
{clean_code}
*/

"""
    with open(file_path, "a") as f:
        f.write(entry)

def remove_log_entry(index):
    if os.path.exists("feedback_log.csv"):
        df = pd.read_csv("feedback_log.csv")
        # Store the row in session state for the Undo button
        st.session_state.last_deleted_row = df.iloc[index].to_dict()
        df = df.drop(df.index[index])
        df.to_csv("feedback_log.csv", index=False)

# --- PAGE ROUTING ---

# 1. HOME SECTION
if st.session_state.page == "Home":
    st.markdown("""
        <div class="hero-container">
            <div class="section-content">
                <div class="section-text">
                    Combining <span class="highlight">AI</span> with <span class="highlight">3D printing</span> 
                    to turn napkin sketches into real parts.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Interactive Tab Columns
    t1, t2, t3 = st.columns(3)
    if t1.button("Why Napkin", use_container_width=True, type="primary" if st.session_state.home_tab == "Why Napkin" else "secondary"):
        st.session_state.home_tab = "Why Napkin"; st.rerun()
    if t2.button("How to use", use_container_width=True, type="primary" if st.session_state.home_tab == "How to use" else "secondary"):
        st.session_state.home_tab = "How to use"; st.rerun()
    if t3.button("Try now", use_container_width=True, type="primary" if st.session_state.home_tab == "Try now" else "secondary"):
        st.session_state.home_tab = "Try now"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Tab Content Area
    if st.session_state.home_tab == "Why Napkin":
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.write("**Napkin is an AI design-to-manufacture tool that automates the creation of 3D models and 3D printed parts from simple hand-drawn sketches.**")
            st.markdown("""
                * **Eliminate Downtime:** Companies can lose up to millions of dollars per hour of production downtime. These bottlenecks can be minimised using this software to generate custom replacement parts in minutes.
                * **No CAD Skills Required:** Empower technicians to prototype and manufacture solutions remotely without specialised engineering software training.
                * **Industrial Intelligence:** The AI system has been built on a foundation of ISO standards and machinist logic for structurally sound, compliant designs.
                * **Evolving Capabilities:** Continuous improvement through advanced AI learning and the rapid evolution of 3D printing technology.
            """)
        with right:
            st.image("static/production1.jpg", use_container_width=True)
    
    elif st.session_state.home_tab == "How to use":
        # Create two columns to match the styling of the other tabs
        left, right = st.columns([1, 1], gap="large")
        
        with left:
            st.markdown("""
            1. **Upload or Describe:** Upload a photo of your hand-drawn sketch or just type out what you need in the specification box.
            2. **Be Specific:** For precision engineering, mention exact dimensions or hole types (e.g. 'M5 clearance hole').
            3. **Generate:** Click the 'Generate 3D Model' button. Our AI engine will translate your input into geometric code and generate a 3D model.
            4. **Print:** Send your part straight to the printer using our automatic cloud slicing feature, or export your .stl file for use in any slicing software yourself.
            """)
        
        with right:
            # Placing the video on the right to match image placement in other tabs
            st.video("https://www.youtube.com/watch?v=uTKkxl8y-BI")

    elif st.session_state.home_tab == "Try now":
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("### Ready to start printing?")
            st.write("Get a free trial to turn your napkin sketches into real parts today.")
            if st.button("Explore Pricing & Plans", type="primary"):
                set_page("Pricing")
        with right:
            st.image("static/print2.jpg", use_container_width=True)

    # Testimonials
    st.markdown("---")
    testimonials = [
        {"quote": "The speed from a sketch to a real part is unlike anything we've used.", "author": "Lead Engineer, Precision Dynamics", "img": "https://i.pravatar.cc/150?u=1"},
        {"quote": "This has revolutionised how we conduct emergency production part replacements.", "author": "Maintenance Lead, TechBuild", "img": "https://i.pravatar.cc/150?u=2"},
        {"quote": "Our maintenance staff have been empowered to create parts without any CAD training.", "author": "Maintenance Technician, TechBuild", "img": "https://i.pravatar.cc/150?u=3"},
        {"quote": "Our 3D printer fleet has been transformed into one of our most valuable assets", "author": "R&D Engineer, TechBuild", "img": "https://i.pravatar.cc/150?u=4"}
    ]
    
    # SAFETY CHECK: Ensure the index isn't larger than the current list (prevents crashes if you shrink the list)
    if st.session_state.testimonial_index >= len(testimonials):
        st.session_state.testimonial_index = 0
    
    curr_idx = st.session_state.testimonial_index
    curr = testimonials[curr_idx]
    
    # Use vertical_alignment="center" to keep arrows next to the middle of the box
    tc1, tc2, tc3 = st.columns([1, 6, 1], vertical_alignment="center")
    
    with tc1:
        if st.button("←", key="prev_t"): 
            st.session_state.testimonial_index = (curr_idx - 1) % len(testimonials)
            st.rerun()
            
    with tc2:
        st.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><i>"{curr["quote"]}"</i><br><b>— {curr["author"]}</b></div></div>', unsafe_allow_html=True)
        
        # Dots logic
        dots_html = '<div class="dot-container">'
        for i in range(len(testimonials)):
            active_class = "dot-active" if i == curr_idx else ""
            dots_html += f'<span class="dot {active_class}"></span>'
        dots_html += '</div>'
        st.markdown(dots_html, unsafe_allow_html=True)
    
    with tc3:
        if st.button("→", key="next_t"): 
            st.session_state.testimonial_index = (curr_idx + 1) % len(testimonials)
            st.rerun()


# 2. MAKE A PART
elif st.session_state.page == "Make a Part":
    # --- HELPER FUNCTION (Defined at the top of the page scope) ---
    def log_feedback_to_csv(category):
        file_path = "feedback_log.csv"
        file_exists = os.path.isfile(file_path)
        
        # Clean the code string to keep it on one line for the spreadsheet
        # We use .get() to prevent errors if the state was cleared
        code = st.session_state.get('last_code', "").replace("\n", " [NEWLINE] ")
        prompt = st.session_state.get('last_prompt', "")
        logic = st.session_state.get('last_logic', "")
        
        row = [
            category,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            prompt,
            logic,
            code
        ]

        with open(file_path, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Status", "Timestamp", "Prompt", "Logic", "Code"])
            writer.writerow(row)

    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        upload_choice = st.radio("Input Mode:", ["Sketch + Description", "Text Description Only"], horizontal=True)
        
        sketch_type = "3D"
        if upload_choice == "Sketch + Description":
            sketch_type = st.radio("Sketch Type:", ["3D", "2D (Multiple Views)"], horizontal=True)
            uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
            
            if uploaded_file: 
                try:
                    img = PIL.Image.open(uploaded_file).convert("RGB")
                    max_size = 1200
                    if img.width > max_size or img.height > max_size:
                        img.thumbnail((max_size, max_size))
                    
                    st.image(img, use_container_width=True)
                    st.session_state.current_img = img 
                except Exception as e:
                    st.error("Error processing image.")
        else:
            st.session_state.current_img = None

        user_context = st.text_area("Specifications", placeholder="e.g. A 50x50mm cube...", height=150)
        generate_btn = st.button("Generate 3D Model", type="primary", use_container_width=True)

    with col2:
        if generate_btn:
            if upload_choice == "Sketch + Description" and 'current_img' not in st.session_state:
                st.error("Please upload a photo first.")
            else:
                with st.spinner("Generating..."):
                    try:
                        exe = shutil.which("openscad")
                        if not exe:
                            st.error("Engine Error: OpenSCAD not found on server.")
                        else:
                            client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                            
                            # --- LOAD CONTEXT (Libraries + Training) ---
                            library_context = ""
                            if os.path.exists("libraries"):
                                for fn in os.listdir("libraries"):
                                    if fn.endswith(".scad"):
                                        with open(os.path.join("libraries", fn), "r") as f:
                                            library_context += f"\n--- LIBRARY: {fn} ---\n{f.read()}\n"
                            
                            training_context = ""
                            if os.path.exists("ai_training.scad"):
                                with open("ai_training.scad", "r") as f:
                                    training_context = f"\n--- GOLD STANDARD EXAMPLES ---\n{f.read()}\n"

                            type_instruction = "The provided image is a 2D flat profile." if sketch_type == "2D (Multiple Views)" else "The provided image is a 3D perspective sketch."

                            prompt = (
                                f"Act as a Senior Mechanical Engineer. {type_instruction} "
                                f"KNOWLEDGE BASE: {library_context} "
                                f"REFERENCE EXAMPLES: {training_context} " 
                                f"Create code based on: '{user_context}'. Use $fn=50;. "
                                f"INSTRUCTIONS: For holes, you MUST use difference() {{ base(); holes(); }}. "
                                f"Format: [DECODED LOGIC]: ... [RESULT_CODE]: ```openscad [code] ```"
                            )
                            
                            inputs = [prompt, st.session_state.current_img] if upload_choice == "Sketch + Description" else [prompt]
                            response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=inputs)
                            
                            scad_match = re.search(r"```openscad(.*?)```", response.text, re.DOTALL)
                            logic_match = re.search(r"\[DECODED LOGIC\]:(.*?)\[", response.text, re.DOTALL)
                            
                            if scad_match:
                                st.session_state.last_code = scad_match.group(1).strip()
                                st.session_state.last_logic = logic_match.group(1).strip() if logic_match else "Standard generation"
                                st.session_state.last_prompt = user_context
                                
                                with open("part.scad", "w") as f: 
                                    f.write(st.session_state.last_code)
                                
                                my_env = os.environ.copy()
                                my_env["OPENSCADPATH"] = os.path.join(os.getcwd(), "libraries")
                                subprocess.run([exe, "-o", "part.stl", "part.scad"], env=my_env, check=True)
                            else:
                                st.error("AI failed to return valid code.")
                    except Exception as e: 
                        st.error(f"Error: {e}")

        # --- DISPLAY RESULTS AND FEEDBACK BUTTONS ---
        if 'last_code' in st.session_state:
            stl_from_file("part.stl", color='#58a6ff')
            
            # Use columns for the download/print row
            d1, d2 = st.columns(2)
            with open("part.stl", "rb") as file:
                stl_data = file.read()
                d1.download_button("Download STL", data=stl_data, file_name="part.stl", use_container_width=True)
                d2.download_button("Print", data=stl_data, file_name="part.stl", use_container_width=True)
            
            st.markdown("---")
            st.write("**Feedback: Is this model correct?**")
            fb_col1, fb_col2 = st.columns(2)
            
            if fb_col1.button("Correct", use_container_width=True):
                log_feedback_to_csv("VERIFIED")
                st.success("Verified")

            if fb_col2.button("Incorrect", use_container_width=True):
                log_feedback_to_csv("FAILED")
                st.warning("Logged for manual review")
            
                    
# 3. PRICING
elif st.session_state.page == "Pricing":
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="price-card"><h3>Starter</h3><div class="price-amt">£0<span class="per-month">per month</span></div><div class="currency-sub">$0 USD | €0 EUR</div><p class="price-feat">1 week free trial</p><p class="price-feat">1 connected device</p><p class="price-feat">1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Join Free", key="p1", use_container_width=True)
    with p2:
        st.markdown('<div class="price-card" style="border-color:#58a6ff"><h3>Professional</h3><div class="price-amt">£65<span class="per-month">per month</span></div><div class="currency-sub">$82 USD | €78 EUR</div><p class="price-feat">Unlimited exports</p><p class="price-feat">1 connected device</p><p class="price-feat">1 connected printer</p></div>', unsafe_allow_html=True)
        st.button("Get Professional", type="primary", key="p2", use_container_width=True)
    with p3:
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom<span class="per-month"></span></div><div class="currency-sub">Tailored for large-scale operations</div><p class="price-feat">Unlimited exports</p><p class="price-feat">Unlimited connected devices</p><p class="price-feat">Unlimited connected printers</p></div>', unsafe_allow_html=True)
        st.button("Contact Sales", key="p3", use_container_width=True)

# 4. HELP
elif st.session_state.page == "Help":
    
    st.markdown("### Setting up your 3D Printer")
    st.markdown("""
    1. **Network Discovery:** Ensure your printer and computer are on the same Wi-Fi network.
    2. **API Access:** Locate your API Key or Access Code within your printer's network settings.
    3. **Direct Printing:** Once configured, you can send generated parts straight to the print bed from this software, without leaving the shop floor.
    """)
    st.markdown("---")
    st.markdown("### Frequently Asked Questions")
    with st.expander("How has this software been developed?"):
        st.write("""
        Unlike generic AI, this platform is engineered specifically for industrial environments:
        * **Parametric Precision:** Uses a mathematical modelling engine to guarantee exact physical dimensions instead of visual guesses.
        * **Machinist Logic:** Programmed with engineering rules for structural integrity, clearances, and 3D-printability.
        * **Professional Workflow:** Automatically applies ISO-compliant tolerances and mechanical heuristics.
        """)
    with st.expander("What type of parts can it make?"):
        st.write("""
        * Any component that is simple enough to be described by a small sketch and text prompt.
        * The AI will excel at engineering-specific parts and features; for example, a mounting bracket with an M6 clearance hole. This is because it has been trained on real-world industrial standards such as ISO/DIN tables.
        """)
    with st.expander("Does it work with resin printers?"):
        st.write("Yes, the .STL files are compatible with both FDM and SLA (resin) slicers.")
    with st.expander("How do I get the best results?"):
        st.write("""
        * **Be Specific:** Include exact dimensions (e.g., "50mm wide").
        * **Describe the Use:** Mention if it needs to fit a specific bolt (e.g., "M5 clearance hole").
        * **High Contrast:** If uploading a sketch, ensure the lines are dark and the background is plain.
        """)
    with st.expander("Why is the AI not generating my model correctly?"):
        st.write("""
        * **User error:** Firstly, check the accuracy of your drawing and description, ensuring that all features are clearly described. Watch our tutorial to learn how to give more effective prompts.
        * **AI error:** Although the AI is programmed specifically for engineering component design, there may still be errors with more complicated models. For these scenarios, traditional CAD modelling methods are required. However, we are aiming to continuously improve our system, and welcome any feedback when common or valuable designs are failing to generate.        
        """)

# 5. GALLERY
elif st.session_state.page == "Gallery":
    st.markdown("### Gallery")
    g1, g2 = st.columns(2)
    g1.image("static/print1.jpg", use_container_width=True)
    g2.image("static/production2.jpg", use_container_width=True)
    g3, g4 = st.columns(2)
    g3.image("static/gallery3.jpg", use_container_width=True)
    g4.image("static/gallery4.jpg", use_container_width=True)
    g5, g6 = st.columns(2)
    g5.image("static/gallery5.jpg", use_container_width=True)
    g6.image("static/gallery6.jpg", use_container_width=True)

# 6. CONTACT
elif st.session_state.page == "Contact":
    st.markdown("### Contact Us")
    with st.form("c"):
        st.text_input("Name")
        st.text_input("Company")
        st.text_input("Email")
        st.text_area("Message")
        st.form_submit_button("Send Message")


# 7. NEW PROFILE PAGE
elif st.session_state.page == "Profile":
    st.markdown("### User Profile")
    prof_col1, prof_col2 = st.columns([1, 2])
    with prof_col1:
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://i.pravatar.cc/150?u=napkin" style="border-radius: 50%; border: 4px solid #3b82f6; width: 150px;">
                <h4>John Doe</h4>
                <p style="color: #8b949e;">Senior Manufacturing Engineer</p>
            </div>
        """, unsafe_allow_html=True)
    with prof_col2:
        st.markdown("#### Account Information")
        st.text_input("Full Name", value="John Doe")
        st.text_input("Email Address", value="john.doe@manufacturing-corp.com")
        st.markdown("#### Statistics")
        stat1, stat2, stat3 = st.columns(3)
        stat1.metric("Parts Generated", "42")
        stat2.metric("Printers connected", "1")
        stat3.metric("Plan", "Professional")
        if st.button("Save Changes"):
            st.success("Profile Updated!")

# 8. ADMIN VERIFICATION SYSTEM
elif st.session_state.page == "Admin":
    st.markdown("### Verification Feedback")
    
    # --- TOP ACTIONS: DOWNLOAD & UNDO ---
    dl_col, undo_col = st.columns([2, 1])
    
    with dl_col:
        if os.path.exists("ai_training.scad"):
            with open("ai_training.scad", "r") as f:
                st.download_button(
                    label="Download AI Training File",
                    data=f.read(),
                    file_name="ai_training.scad",
                    mime="text/plain",
                    use_container_width=True  # Ensures standard height
                )
    
    with undo_col:
        # Check if there is something in the temporary buffer to restore
        if st.session_state.get('last_deleted_row'):
            if st.button("↩️ Undo last entry", use_container_width=True):
                # Restore the dictionary back to the CSV
                restored_row = st.session_state.last_deleted_row
                file_path = "feedback_log.csv"
                file_exists = os.path.isfile(file_path)
                with open(file_path, "a", newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=restored_row.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(restored_row)
                
                # Clear undo buffer and reset index to show the restored item
                st.session_state.last_deleted_row = None 
                st.session_state.admin_index = 0
                st.success("Entry Restored!")
                st.rerun()
        else:
            # Placeholder button to keep the layout height consistent even when empty
            st.button("Undo Last Entry", disabled=True, use_container_width=True)

    st.markdown("---")

    if not os.path.exists("feedback_log.csv") or os.stat("feedback_log.csv").st_size < 10:
        st.info("No pending feedback to review.")
    else:
        df = pd.read_csv("feedback_log.csv")
        
        # --- IRONCLAD INDEX MANAGEMENT ---
        if 'admin_index' not in st.session_state or st.session_state.admin_index is None:
            st.session_state.admin_index = 0

        try:
            current_idx = int(st.session_state.get('admin_index', 0))
        except (TypeError, ValueError):
            current_idx = 0
            st.session_state.admin_index = 0

        if df.empty:
            st.warning("Feedback log is empty.")
            st.stop()
        
        if current_idx >= len(df):
            st.session_state.admin_index = 0
            st.rerun()

        selection = st.selectbox(
            "Select entry to verify:", 
            range(len(df)), 
            index=int(st.session_state.admin_index),
            format_func=lambda x: f"{df.iloc[x]['Status']} | {str(df.iloc[x]['Prompt'])[:60]}..."
        )
        
        if selection != st.session_state.admin_index:
            st.session_state.admin_index = selection
            st.rerun()

        # Load data
        row = df.iloc[selection]
        col_edit, col_view = st.columns([1, 1], gap="large")
        
        with col_edit:
            st.markdown("#### Data")
            edit_prompt = st.text_input("Prompt", row['Prompt'])
            edit_logic = st.text_area("Logic", row['Logic'])
            raw_code = str(row['Code']).replace(" [NEWLINE] ", "\n")
            edit_code = st.text_area("Code", raw_code, height=400)
            
            st.markdown("---")
            st.markdown("#### Actions")
            
            act_col1, act_col2 = st.columns(2)
            
            # --- SAVE LOGIC ---
            with act_col1:
                if st.session_state.get('confirm_save') == selection:
                    if st.button("CONFIRM SAVE", type="primary", use_container_width=True):
                        save_to_gold_standard(edit_prompt, edit_logic, edit_code)
                        remove_log_entry(selection)
                        st.session_state.confirm_save = None
                        st.session_state.admin_index = 0 
                        st.success("Saved!")
                        st.rerun()
                    if st.button("Cancel", key="c_save", use_container_width=True):
                        st.session_state.confirm_save = None
                        st.rerun()
                else:
                    if st.button("Save to Training", use_container_width=True):
                        st.session_state.confirm_save = selection
                        st.session_state.confirm_delete = None
                        st.rerun()

            # --- DISCARD LOGIC ---
            with act_col2:
                if st.session_state.get('confirm_delete') == selection:
                    if st.button("CONFIRM DELETE", type="primary", use_container_width=True):
                        remove_log_entry(selection)
                        st.session_state.confirm_delete = None
                        st.session_state.admin_index = 0
                        st.warning("Discarded.")
                        st.rerun()
                    if st.button("Cancel", key="c_del", use_container_width=True):
                        st.session_state.confirm_delete = None
                        st.rerun()
                else:
                    if st.button("Discard Entry", use_container_width=True):
                        st.session_state.confirm_delete = selection
                        st.session_state.confirm_save = None
                        st.rerun()

        with col_view:
            st.markdown("#### Review Reference")
            st.info("Copy the code below into OpenSCAD to verify.")
            st.code(edit_code, language="cpp")
                    

# --- CLOSE CONTENT PADDING ---
# This must be outside of all the IF/ELIF blocks so it closes regardless of the page
st.markdown('</div>', unsafe_allow_html=True) 

# --- FOOTER ---
st.markdown("""
    <div class="footer-minimal">
        <p style="font-size: 0.9rem; margin-bottom: 15px; font-weight: 600; color: white;">FOLLOW US</p>
        <div style="display: flex; justify-content: center; align-items: center;">
            <div class="footer-icon-box"><img src="app/static/insta.png"></div>
            <div class="footer-icon-box"><img src="app/static/linkedin.png"></div>
            <div class="footer-icon-box"><img src="app/static/youtube.png"></div>
        </div>
        <p style="font-size:0.75rem; margin-top: 25px; opacity: 0.7; color: white;">© 2025 Napkin Manufacturing Tool. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)









































import streamlit as st
from google import genai
import PIL.Image
import subprocess
from streamlit_stl import stl_from_file
import json
import re
import os
import shutil

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
st.markdown(f"""
    <style>
    /* Global Layout */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    .stApp { background-color: #0e1117; color: #ffffff; margin-top: 60px; }

    /* --- NEW MODERN NAVBAR (NO BUTTONS) --- */
    .nav-wrapper {
        background-color: #0e1117;
        border-bottom: 1px solid #30363d;
        width: 100vw;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .nav-item {
        padding: 18px 25px;
        color: #8b949e !important;
        text-decoration: none !important;
        font-size: 15px;
        font-weight: 500;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
    }

    .nav-item:hover {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff;
    }

    .nav-active {
        color: #ffffff !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Standard Buttons (Generate, Pricing, etc) */
    .stButton>button { 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #21262d; 
        color: white; 
        border: 1px solid #30363d; 
        font-weight: 600; 
    }
    
    button[kind="primary"] { background-color: #3b82f6 !important; border: none !important; }

    /* Pricing & Testimonials */
    .price-card { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; text-align: center; min-height: 380px; margin-bottom: 25px;}
    .testimonial-card { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; display: flex; align-items: center; justify-content: center; min-height: 180px;}

    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- NEW NAVBAR LOGIC ---
pages = ["Home", "Make a Part", "Pricing", "Help", "Gallery", "Contact", "Profile"]

# 1. Listen for clicks via URL parameters
params = st.query_params
if "p" in params:
    if params["p"] != st.session_state.page:
        st.session_state.page = params["p"]
        st.rerun()

# 2. Build the HTML Navbar
nav_html = '<div class="nav-wrapper">'
for p in pages:
    active_class = "nav-active" if st.session_state.page == p else ""
    nav_html += f'<a href="/?p={p}" target="_self" class="nav-item {active_class}">{p}</a>'
nav_html += '</div>'

st.markdown(nav_html, unsafe_allow_html=True)

# Container for standard page content
st.markdown('<div style="padding: 0 5rem;">', unsafe_allow_html=True)

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
            st.write("**Napkin is an AI design-to-manufacture tool that automates the creation of 3D models from simple hand-drawn sketches.**")
            st.markdown("""
                * **Eliminate Downtime:** Companies can lose up to millions of dollars per hour of production downtime. These bottlenecks can be minimised by using this software to generate custom replacement parts in minutes.
                * **No CAD Skills Required:** Empower technicians to prototype and manufacture solutions remotely without specialised engineering software training.
                * **Industrial Intelligence:** The AI system has been built on a foundation of ISO standards and machinist logic for structurally sound, compliant designs.
                * **Evolving Capabilities:** Continuous improvement through advanced AI learning and the rapid evolution of 3D printing technology.
            """)
        with right:
            st.image("static/production1.jpg", use_container_width=True)
    
    elif st.session_state.home_tab == "How to use":
        st.markdown("""
        1. **Upload or Describe:** Upload a photo of your hand-drawn sketch or just type out what you need in the specification box.
        2. **Be Specific:** For precision engineering, mention exact dimensions or hole types (e.g. 'M5 clearance hole').
        3. **Generate:** Click the 'Generate 3D Model' button. Our AI engine will translate your input into geometric code and generate a 3D model.
        4. **Print:** Send your part straight to the printer using our automatic cloud slicing feature, or export your .stl file for use in any slicing software yourself.
        """)
        st.markdown("---")
        st.markdown("<div style='text-align:center;'><h3>Process Overview</h3></div>", unsafe_allow_html=True)
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
        {"quote": "Fundamental change for emergency production part replacements.", "author": "Maintenance Lead, TechBuild", "img": "https://i.pravatar.cc/150?u=2"}
    ]
    curr = testimonials[st.session_state.testimonial_index]
    tc1, tc2, tc3 = st.columns([1, 6, 1])
    if tc1.button("←", key="prev_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials); st.rerun()
    tc2.markdown(f'<div class="testimonial-card"><img src="{curr["img"]}" class="testimonial-img"><div><i>"{curr["quote"]}"</i><br><b>— {curr["author"]}</b></div></div>', unsafe_allow_html=True)
    if tc3.button("→", key="next_t"): st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials); st.rerun()


# 2. MAKE A PART
elif st.session_state.page == "Make a Part":
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        # Step 1: Selection for Input Mode
        upload_choice = st.radio("Input Mode:", ["Sketch + Description", "Text Description Only"], horizontal=True)
        
        # Step 2: New Selection for Sketch Type (Only shows if Sketch is selected)
        sketch_type = "3D"
        if upload_choice == "Sketch + Description":
            sketch_type = st.radio("Sketch Type:", ["3D", "2D (Multiple Views)"], horizontal=True, help="Choose 2D if you drew 2D projections of the part. Make sure to give at least 2 views if you are using this method.")
            uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'png'], label_visibility="collapsed")
            if uploaded_file: 
                st.image(PIL.Image.open(uploaded_file), use_container_width=True)
        else:
            uploaded_file = None

        user_context = st.text_area("Specifications", placeholder="e.g. A 50x50mm cube...", height=150)
        generate_btn = st.button("Generate 3D Model", type="primary", use_container_width=True)

    with col2:
        if generate_btn:
            with st.spinner("Generating..."):
                try:
                    exe = shutil.which("openscad")
                    if not exe:
                        st.error("Engine Error: OpenSCAD not found on server.")
                    else:
                        client = genai.Client(api_key=st.secrets["GEMINI_KEY"])
                        
                        # Step 3: Modified Prompt to handle 2D vs 3D
                        if sketch_type == "2D Flat Profile":
                            type_instruction = "The provided image is a 2D flat profile. Trace this shape and use linear_extrude() to give it thickness based on the description."
                        else:
                            type_instruction = "The provided image is a 3D perspective sketch. Interpret the depth and geometry accordingly."

                        prompt = (
                            f"Act as an OpenSCAD engineer. {type_instruction} "
                            f"Create code based on: '{user_context}'. Use $fn=50;. "
                            f"Provide a JSON 'METADATA' object. Format: ```openscad [code] ``` and ```json [metadata] ```"
                        )
                        
                        inputs = [prompt, PIL.Image.open(uploaded_file)] if uploaded_file else [prompt]
                        
                        # Using your model preference (2.0-flash-exp)
                        response = client.models.generate_content(model="gemini-2.0-flash-exp", contents=inputs)
                        
                        scad_match = re.search(r"```openscad(.*?)```", response.text, re.DOTALL)
                        if scad_match:
                            scad_code = scad_match.group(1).strip()
                            with open("part.scad", "w") as f: f.write(scad_code)
                            subprocess.run([exe, "-o", "part.stl", "part.scad"], check=True)
                            stl_from_file("part.stl", color='#58a6ff')
                            
                            st.download_button("Download STL", open("part.stl", "rb"), "part.stl", key="dl_stl", use_container_width=True)
                            st.download_button("Print", open("part.stl", "rb"), "part.stl", key="print_stl", use_container_width=True)
                        else:
                            st.error("AI failed to return valid OpenSCAD code. Try being more specific.")
                except Exception as e: 
                    st.error(f"Error: {e}")
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
        st.markdown('<div class="price-card"><h3>Enterprise</h3><div class="price-amt">Custom<span class="per-month">per month</span></div><div class="currency-sub">Tailored for large-scale operations</div><p class="price-feat">Unlimited exports</p><p class="price-feat">Unlimited connected devices</p><p class="price-feat">Unlimited connected printers</p></div>', unsafe_allow_html=True)
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

st.markdown('</div>', unsafe_allow_html=True) # End content padding

# --- FOOTER ---
st.markdown(f"""
    <div class="footer-minimal">
        <p style="font-size: 0.9rem; margin-bottom: 15px; font-weight: 600; color: white;">FOLLOW US</p>
        <div style="display: flex; justify-content: center; align-items: center;">
            <div class="footer-icon-box"><img src="app/static/insta.png"></div>
            <div class="footer-icon-box"><img src="app/static/linkedin.png"></div>
            <div class="footer-icon-box"><img src="app/static/youtube.png"></div>
        </div>
        <p style="font-size:0.75rem; margin-top: 25px; opacity: 0.7;">© 2025 Napkin Manufacturing Tool. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)













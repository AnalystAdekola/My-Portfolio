import streamlit as st
import sqlite3
import json
import os
from streamlit_quill import st_quill

# --- CONFIGURATION ---
st.set_page_config(page_title="Portfolio Architect", layout="wide")

# This creates a folder named 'portfolio_data' in your project directory
SAVE_DIR = "portfolio_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY, header TEXT, subtitle TEXT, 
                  description TEXT, link TEXT, folder_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- BEAUTIFUL HEADER ---
def render_header():
    st.markdown("""
        <style>
        .main-title {
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 3.5rem;
            background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0px;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-top: 0px;
            margin-bottom: 20px;
        }
        </style>
        <h1 class="main-title">Portfolio Architect</h1>
        <p class="subtitle">Curate your professional story with brilliance.</p>
        <hr>
        """, unsafe_allow_html=True)

# --- SAVE LOGIC ---
def save_project_files(folder_name, files):
    path = os.path.join(SAVE_DIR, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
    
    for f in files:
        with open(os.path.join(path, f.name), "wb") as save_file:
            save_file.write(f.getbuffer())
    return path

# --- NAVIGATION ---
render_header()
menu = st.sidebar.radio("Navigation", ["View Gallery", "Add New Project"])

# --- ADD NEW PROJECT ---
if menu == "Add New Project":
    st.subheader("🚀 Create a New Entry")
    
    with st.form("project_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        header = col1.text_input("Project Title")
        subtitle = col2.text_input("Sub-title / Role")
        link = st.text_input("Project Link (Live URL)")
        
        st.write("### Content & Styling")
        # The 'Brilliant' Rich Text Editor
        description = st_quill(key="editor", html=True, placeholder="Describe your masterpiece...")
        
        uploaded_files = st.file_uploader("Upload Images (Max 10)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        submit = st.form_submit_button("Publish Project")
        
        if submit:
            if not header or not uploaded_files:
                st.error("Missing Title or Images!")
            elif len(uploaded_files) > 10:
                st.error("Please limit to 10 images.")
            else:
                # 1. Create unique folder name
                folder_name = header.replace(" ", "_").lower()
                save_project_files(folder_name, uploaded_files)
                
                # 2. Save to Database
                conn = sqlite3.connect('portfolio.db')
                c = conn.cursor()
                c.execute("INSERT INTO projects (header, subtitle, description, link, folder_name) VALUES (?,?,?,?,?)",
                          (header, subtitle, description, link, folder_name))
                conn.commit()
                conn.close()
                st.success(f"Project '{header}' has been saved brilliantly!")

# --- VIEW GALLERY ---
else:
    st.subheader("📂 All Projects")
    
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        st.info("No projects found. Go to 'Add New Project' to get started!")

    for row in rows:
        with st.container(border=True):
            st.title(row[1])
            st.write(f"**{row[2]}**")
            
            # Render the styled description from Quill
            st.markdown(row[3], unsafe_allow_html=True)
            
            if row[4]:
                st.link_button("Visit Site", row[4])
            
            # Display Images
            folder_path = os.path.join(SAVE_DIR, row[5])
            if os.path.exists(folder_path):
                img_list = os.listdir(folder_path)
                if img_list:
                    cols = st.columns(min(len(img_list), 5))
                    for idx, img_name in enumerate(img_list[:10]):
                        cols[idx % 5].image(os.path.join(folder_path, img_name), use_container_width=True)
            
            st.divider()

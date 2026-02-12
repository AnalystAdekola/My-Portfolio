import streamlit as st
import sqlite3
import json
import os
import shutil
from streamlit_quill import st_quill

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="My Office Showcase", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a "Brilliant" look
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stButton>button {
        border-radius: 20px;
        background-color: #3a7bd5;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
    }
    .project-card {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #eee;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

SAVE_DIR = "showcase_data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('my_office_vault.db') # New name for a fresh start
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  header TEXT, subtitle TEXT, 
                  description TEXT, link TEXT, folder_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- HEADER COMPONENT ---
def render_header():
    st.markdown("""
        <div style="text-align: center; padding: 20px 0px;">
            <h1 style="font-family: 'Inter', sans-serif; color: #1E293B; font-size: 3.5rem; margin-bottom: 0;">My Office <span style="color: #3a7bd5;">Showcase</span></h1>
            <p style="color: #64748B; font-size: 1.2rem;">The easy, beautiful way to display your best work.</p>
        </div>
        <hr style="border: 0.5px solid #eee;">
        """, unsafe_allow_html=True)

# --- SAVE & DELETE LOGIC ---
def save_project(header, subtitle, description, link, files):
    folder_name = header.replace(" ", "_").lower()
    path = os.path.join(SAVE_DIR, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
    
    for f in files:
        with open(os.path.join(path, f.name), "wb") as save_file:
            save_file.write(f.getbuffer())
    
    conn = sqlite3.connect('my_office_vault.db')
    c = conn.cursor()
    c.execute("INSERT INTO projects (header, subtitle, description, link, folder_name) VALUES (?,?,?,?,?)",
              (header, subtitle, description, link, folder_name))
    conn.commit()
    conn.close()

def delete_project(p_id, folder_name):
    conn = sqlite3.connect('my_office_vault.db')
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id=?", (p_id,))
    conn.commit()
    conn.close()
    
    path = os.path.join(SAVE_DIR, folder_name)
    if os.path.exists(path):
        shutil.rmtree(path)
    st.rerun()

# --- MAIN APP FLOW ---
render_header()
menu = st.sidebar.radio("Navigation", ["📂 View Gallery", "✨ Add New Project"])

if menu == "✨ Add New Project":
    st.markdown("### 📝 Project Details")
    
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        h_input = col1.text_input("Project Title", placeholder="e.g. Modern Web Design")
        s_input = col2.text_input("Subtitle", placeholder="e.g. Lead Developer / UI Design")
        l_input = st.text_input("Project Link (Optional)", placeholder="https://yourwork.com")
        
        st.write("### 🎨 Content Styling")
        # The 'Brilliant' styling tool
        d_input = st_quill(html=True, placeholder="Tell the story of this project...")
        
        st.write("### 🖼️ Project Media")
        u_files = st.file_uploader("Upload up to 10 images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("Publish to Showcase")
        
        if submitted:
            if not h_input or not u_files:
                st.error("Please provide a title and at least one image.")
            elif len(u_files) > 10:
                st.error("Maximum 10 images allowed.")
            else:
                save_project(h_input, s_input, d_input, l_input, u_files)
                st.success("Project added beautifully!")
                st.balloons()

else:
    st.markdown("### 🖼️ Your Portfolio")
    conn = sqlite3.connect('my_office_vault.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = c.fetchall()
    conn.close()

    if not projects:
        st.info("Your gallery is empty. Start by adding a new project from the sidebar!")

    for p in projects:
        # p[0]=id, p[1]=header, p[2]=subtitle, p[3]=desc, p[4]=link, p[5]=folder
        with st.container():
            st.markdown(f"""
                <div class="project-card">
                    <h2 style="margin-bottom:0px; color:#1E293B;">{p[1]}</h2>
                    <p style="color:#3a7bd5; font-weight:600; margin-top:0px;">{p[2]}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show description
            st.markdown(p[3], unsafe_allow_html=True)
            
            # Show Images
            img_path = os.path.join(SAVE_DIR, p[5])
            if os.path.exists(img_path):
                imgs = os.listdir(img_path)
                if imgs:
                    cols = st.columns(5)
                    for idx, img_name in enumerate(imgs[:10]):
                        cols[idx % 5].image(os.path.join(img_path, img_name), use_container_width=True)

            # Footer buttons
            col_link, col_space, col_del = st.columns([2, 6, 1])
            if p[4]:
                col_link.link_button("🌐 View Project", p[4])
            
            if col_del.button("🗑️", key=f"del_{p[0]}", help="Delete this project"):
                delete_project(p[0], p[5])
            
            st.markdown("<br><hr style='border:0.1px solid #f0f0f0;'><br>", unsafe_allow_html=True)

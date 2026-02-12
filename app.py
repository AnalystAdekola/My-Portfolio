import streamlit as st
import sqlite3
import json
import os
import shutil
from streamlit_quill import st_quill

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="My Office Showcase", layout="wide")

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

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('my_office_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  header TEXT, subtitle TEXT, description TEXT, 
                  link TEXT, folder_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- ADMIN SECURITY ---
st.sidebar.title("🔐 Admin Access")
# CHANGE 'admin123' TO YOUR OWN SECRET PASSWORD
PASSWORD = "your_secret_password" 
user_pwd = st.sidebar.text_input("Enter Password to Edit", type="password")
is_admin = (user_pwd == PASSWORD)

# --- NAVIGATION ---
if is_admin:
    st.sidebar.success("Logged in as Admin")
    menu = st.sidebar.radio("Navigation", ["📂 View Gallery", "✨ Add New Project"])
else:
    st.sidebar.info("Viewer Mode: Add/Delete locked.")
    menu = "📂 View Gallery"

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #1E293B;'>My Office Showcase</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>Organized with AI. Designed for Brilliance.</p><hr>", unsafe_allow_html=True)


# --- ADD PROJECT (ADMIN ONLY) ---
if menu == "✨ Add New Project":
    st.subheader("Add a New Masterpiece")
    with st.form("upload_form"):
        h_input = st.text_input("Project Title")
        s_input = st.text_input("Subtitle (Your Role)")
        l_input = st.text_input("Project Link")
        d_input = st_quill(html=True, placeholder="Describe your work...")
        u_files = st.file_uploader("Upload Images (Max 10)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("Publish Now"):
            if h_input and u_files:
                folder_name = h_input.replace(" ", "_").lower()
                path = os.path.join(SAVE_DIR, folder_name)
                if not os.path.exists(path): os.makedirs(path)
                for f in u_files:
                    with open(os.path.join(path, f.name), "wb") as save_file:
                        save_file.write(f.getbuffer())
                
                conn = sqlite3.connect('my_office_final.db')
                c = conn.cursor()
                c.execute("INSERT INTO projects (header, subtitle, description, link, folder_name) VALUES (?,?,?,?,?)",
                          (h_input, s_input, d_input, l_input, folder_name))
                conn.commit()
                conn.close()
                st.success("Published!")
                st.rerun()

# --- VIEW GALLERY (PUBLIC) ---
else:
    conn = sqlite3.connect('my_office_final.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = c.fetchall()
    conn.close()

    for p in projects:
        # 1. Title & Subtitle
        st.markdown(f"<div class='project-header'>{p[1]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='project-subtitle'>{p[2]}</div>", unsafe_allow_html=True)
        
        # 2. BOLD IMAGES AT THE TOP
        img_path = os.path.join(SAVE_DIR, p[5])
        if os.path.exists(img_path):
            imgs = os.listdir(img_path)
            if imgs:
                # Big Featured Image
                st.image(os.path.join(img_path, imgs[0]), use_container_width=True)
                # Small thumbnails below
                if len(imgs) > 1:
                    cols = st.columns(min(len(imgs)-1, 4))
                    for idx, img_name in enumerate(imgs[1:5]):
                        cols[idx].image(os.path.join(img_path, img_name), use_container_width=True)

        # 3. DESCRIPTION & LINK
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(p[3], unsafe_allow_html=True)
        
        col_btn, col_del = st.columns([8, 1])
        if p[4]:
            col_btn.link_button("🚀 View Live Project", p[4])
        
        # 4. DELETE (ADMIN ONLY)
        if is_admin:
            if col_del.button("🗑️", key=f"del_{p[0]}"):
                conn = sqlite3.connect('my_office_final.db')
                c = conn.cursor()
                c.execute("DELETE FROM projects WHERE id=?", (p[0],))
                conn.commit()
                conn.close()
                if os.path.exists(img_path): shutil.rmtree(img_path)
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)





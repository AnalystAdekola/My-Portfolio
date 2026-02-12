import streamlit as st
import sqlite3
import json
import os
from streamlit_quill import st_quill

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects 
                 (id INTEGER PRIMARY KEY, header TEXT, subtitle TEXT, 
                  description TEXT, link TEXT, save_dir TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- APP LAYOUT ---
st.set_page_config(page_title="Brilliant Portfolio Builder", layout="wide")
st.sidebar.title("Settings")

# Step 1: Tell the app where your "Main" folder is
BASE_SAVE_PATH = st.sidebar.text_input("Local Folder Path", value=os.getcwd(), help="Paste the path to your portfolio folder here.")

menu = st.sidebar.selectbox("Menu", ["View Gallery", "Add New Project"])

# --- FEATURE: SAVE TO LOCAL ---
def save_files_locally(project_name, uploaded_files):
    # Create a specific folder for this project inside your main folder
    project_path = os.path.join(BASE_SAVE_PATH, project_name.replace(" ", "_"))
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    
    for file in uploaded_files:
        with open(os.path.join(project_path, file.name), "wb") as f:
            f.write(file.getbuffer())
    return project_path

# --- ADD PROJECT PAGE ---
if menu == "Add New Project":
    st.header("🎨 Build a Brilliant Project")
    
    col1, col2 = st.columns(2)
    with col1:
        header = st.text_input("Project Header")
        subtitle = st.text_input("Sub-title")
    with col2:
        link = st.text_input("Project Link (Optional)")

    st.write("### Style your Content")
    description = st_quill(key="editor", html=True)

    uploaded_files = st.file_uploader("Upload up to 10 images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if st.button("🚀 Save & Publish"):
        if not header or not uploaded_files:
            st.warning("Please add a title and at least one image.")
        elif len(uploaded_files) > 10:
            st.error("Maximum 10 images allowed.")
        else:
            # 1. Save images to your physical folder
            saved_folder_path = save_files_locally(header, uploaded_files)
            
            # 2. Save details to database
            conn = sqlite3.connect('portfolio.db')
            c = conn.cursor()
            c.execute("INSERT INTO projects (header, subtitle, description, link, save_dir) VALUES (?,?,?,?,?)",
                      (header, subtitle, description, link, saved_folder_path))
            conn.commit()
            conn.close()
            st.success(f"Project saved locally to: {saved_folder_path}")

# --- VIEW GALLERY PAGE ---
else:
    st.header("📂 Your Projects")
    conn = sqlite3.connect('portfolio.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        with st.expander(f"⭐ {row[1]} - {row[2]}"):
            st.markdown(row[3], unsafe_allow_html=True) # The "Brilliant" styled text
            if row[4]:
                st.info(f"Link: {row[4]}")
            
            # Display images from the local folder
            img_dir = row[5]
            if os.path.exists(img_dir):
                files = os.listdir(img_dir)
                cols = st.columns(5) # Show in a grid
                for i, f_name in enumerate(files[:10]):
                    cols[i % 5].image(os.path.join(img_dir, f_name), use_container_width=True)
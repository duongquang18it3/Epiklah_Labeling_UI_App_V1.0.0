import streamlit as st
from streamlit_option_menu import option_menu
from tools.utilities import load_css
import json

import streamlit_javascript as st_js
from data_annotation import DataAnnotation
import sqlite3
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
st.set_page_config(
    page_title="Epiklah",
    page_icon="favicon.ico",
    layout="wide"
)


load_css()

names = ["Admin", "User1"]
username = ["admin", "user1"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, username, hashed_passwords,
    "login_form", "123456", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")


if authentication_status or 'logged_in' in st.session_state: 
    # User is logged in
    st.sidebar.title(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")
    
    class Model:
                menuTitle = "Epiklah"

                option2 = "Data Preview"

                menuIcon = "menu-up"

                icon2 = "activity"



    def view(model):
        
            if 'ui_width' not in st.session_state or 'device_type' not in st.session_state or 'device_width' not in st.session_state:
                    # Get UI width
                    ui_width = st_js.st_javascript("window.innerWidth", key="ui_width_comp")
                    device_width = st_js.st_javascript("window.screen.width", key="device_width_comp")

                    if ui_width > 0 and device_width > 0:
                        # Add 20% of current screen width to compensate for the sidebar
                        ui_width = round(ui_width + (20 * ui_width / 100))

                        if device_width > 768:
                            device_type = 'desktop'
                        else:
                            device_type = 'mobile'

                        st.session_state['ui_width'] = ui_width
                        st.session_state['device_type'] = device_type
                        st.session_state['device_width'] = device_width

                        st.experimental_rerun()
            else:
                    DataAnnotation().view(DataAnnotation.Model(), st.session_state['ui_width'], st.session_state['device_type'],
                                        st.session_state['device_width'])
    view(Model()) 
    def show_logout_button():
            if st.sidebar.button('Log out'):
                # Đặt `logged_in` thành False để biểu thị việc đăng xuất
                st.session_state['logged_in'] = False
                # Bạn cũng có thể muốn xóa tên người dùng khỏi session_state nếu muốn
                if 'username' in st.session_state:
                    del st.session_state['username']
                 # Yêu cầu chạy lại ứng dụng
                st.experimental_rerun()
    def main():
        
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False 
             # Nếu không, khởi tạo trạng thái đăng nhập là False
            
        if st.session_state['logged_in']:
            show_logout_button()
           

    if __name__ == "__main__":
            main()


import streamlit as st
import os
import json
from PIL import Image
import streamlit_authenticator as stauth
import pickle
from pathlib import Path
import fitz  # Import PyMuPDF for PDF to image conversion

logo_url = "https://static.wixstatic.com/media/c063b5_683758ce9cd74f7c8210a6cf5b297fd9~mv2.jpg/v1/fill/w_275,h_75,al_c,q_80,usm_0.66_1.00_0.01,enc_auto/v6_transparent_edited.jpg"
st.sidebar.image(logo_url, width=200, caption="")
st.title("Upload Files Page")
st.sidebar.markdown("# Upload Files ")

# Authentication (same as previous code)
names = ["Admin", "User1"]
username = ["admin", "user1"]

file_path = (Path(__file__).parents[1] / "hashed_pw.pkl")
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, username, hashed_passwords,
                                    "login_form", "123456", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")


if authentication_status or 'logged_in' in st.session_state:
    def upload_file(uploaded_file, username):
        if uploaded_file is not None:
            images_folder = "docs/images/"
            json_folder = "docs/json/"

            # Tạo tên file mới với tiền tố là username
            new_file_name = f"{username}_{uploaded_file.name}"

            # Tạo thư mục nếu chưa tồn tại
            for folder in [images_folder, json_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            if os.path.exists(os.path.join(images_folder, new_file_name)):
                st.write("File already exists")
                return False

            if len(new_file_name) > 100:
                st.write("File name too long")
                return False

            if uploaded_file.type in ['image/jpeg', 'image/png', 'image/jpg']:  # Check for image types
                with open(os.path.join(images_folder, new_file_name), "wb") as f:
                    f.write(uploaded_file.getbuffer())

                img_file = Image.open(os.path.join(images_folder, new_file_name))

                annotations_json = {
                    "meta": {
                        "version": "v0.1",
                        "split": "train",
                        "image_id": len(os.listdir(images_folder)),
                        "image_size": {
                            "width": img_file.width,
                            "height": img_file.height
                        }
                    },
                    "words": []
                }

                file_name_without_extension = new_file_name.split(".")[0]
                with open(os.path.join(json_folder, file_name_without_extension + ".json"), "w") as f:
                    json.dump(annotations_json, f, indent=2)

                st.success(f"Image file '{uploaded_file.name}' uploaded successfully")
                return True

            elif uploaded_file.type == 'application/pdf':  # Handle PDF files
                try:
                    with open(os.path.join(images_folder, new_file_name), "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Convert PDF to images using PyMuPDF
                    pdf_doc = fitz.open(os.path.join(images_folder, new_file_name))
                    for page_num in range(len(pdf_doc)):
                        page = pdf_doc.load_page(page_num)
                        pixmap = page.get_pixmap(dpi=200)  # Adjust DPI
                        # Specify output format (PNG by default)
                        output_format = "PNG"  # You can change this to "JPEG" or "JPG"

                        # Construct unique output filename for each image
                        pdf_filename, _ = os.path.splitext(new_file_name)
                        output_filename = f"{pdf_filename}_page_{page_num + 1}.{output_format.lower()}"

                        # Save extracted image with unique name
                        pixmap.save(os.path.join(images_folder, output_filename))

                        # Update annotations_json (optional, if needed for your application)
                        # ... (add logic to update annotations_json for each converted image)
                        # Tạo file JSON cho mỗi trang ảnh
                        annotations_json = {
                            "meta": {
                                "version": "v0.1",
                                "split": "train",
                                "image_id": len(os.listdir(images_folder)),
                                "image_size": {
                                    "width": pixmap.width,
                                    "height": pixmap.height
                                },
                                "page_number": page_num + 1
                            },
                            "words": []
                        }

                        file_name_without_extension = f"{pdf_filename}_page_{page_num + 1}"
                        with open(os.path.join(json_folder, file_name_without_extension + ".json"), "w") as f:
                            json.dump(annotations_json, f, indent=2)

                    st.success(f"PDF file '{uploaded_file.name}' converted to images successfully")
                    return True

                except Exception as e:
                    st.error(f"Error converting PDF: {e}")
                    return False

            else:
                st.write(f"Unsupported file type: {uploaded_file.type}")
                return False

    def main():

        if 'uploaded_files_info' not in st.session_state:
            st.session_state['uploaded_files_info'] = {}

        uploaded_files = st.file_uploader("Choose a file or multiple files", accept_multiple_files=True)

        if uploaded_files:
            current_user = st.session_state['username']
            if current_user not in st.session_state['uploaded_files_info']:
                st.session_state['uploaded_files_info'][current_user] = []

            for uploaded_file in uploaded_files:
                if upload_file(uploaded_file, current_user):
                    if uploaded_file not in st.session_state['uploaded_files_info'][current_user]:
                        st.session_state['uploaded_files_info'][current_user].append(uploaded_file)

        # Hiển thị danh sách file của người dùng hiện tại (same as previous code)

    if __name__ == "__main__":
        main()
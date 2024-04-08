import streamlit as st
from PIL import Image
import streamlit_nested_layout
from streamlit_sparrow_labeling import st_sparrow_labeling
from streamlit_sparrow_labeling import DataProcessor
import json
import math
import os
from natsort import natsorted
from tools import agstyler
from tools.agstyler import PINLEFT
import pandas as pd
from toolbar_main import component_toolbar_main
import fitz 
import streamlit_javascript as st_js
class DataAnnotation:
    class Model:
        

        img_file = None
        rects_file = None
        labels_file = "docs/labels.json"
        groups_file = "docs/groups.json"

        assign_labels_text = "Assign Labels"
        text_caption_1 = "Check 'Assign Labels' to enable editing of labels and values, move and resize the boxes to annotate the document."
        text_caption_2 = "Add annotations by clicking and dragging on the document, when 'Assign Labels' is unchecked."

        labels = ["", "invoice_no", "invoice_date", "seller", "client", "seller_tax_id", "client_tax_id", "iban", "item_desc",
                  "item_qty", "item_net_price", "item_net_worth", "item_vat", "item_gross_worth", "total_net_worth", "total_vat",
                  "total_gross_worth"]

        selected_field = "Selected Field: "
        save_text = "Save"
        saved_text = "Saved!"

        subheader_1 = "Select"
        subheader_2 = "Upload"
        annotation_text = "Annotation"
        no_annotation_file = "No annotation file selected"
        no_annotation_mapping = "Please annotate the document. Uncheck 'Assign Labels' and draw new annotations"

        download_text = "Download"
        download_hint = "Download the annotated structure in JSON format"

        annotation_selection_help = "Select an annotation file to load"
        upload_help = "Upload a file to annotate"
        upload_button_text = "Upload"
        upload_button_text_desc = "Choose a file"

        assign_labels_text = "Assign Labels"
        assign_labels_help = "Check to enable editing of labels and values"

        
        done_text = "Done"

        grouping_id = "ID"
        grouping_value = "Value"



        error_text = "Value is too long. Please shorten it."
        selection_must_be_continuous = "Please select continuous rows"

    ## Code Tony add vo phan hien thi file   
   
        
    def view(self, model, ui_width, device_type, device_width):
        st.write(f"Welcome {st.session_state['username']}")
        
        with open(model.labels_file, "r") as f:
            labels_json = json.load(f)

        labels_list = labels_json["labels"]
        labels = ['']
        for label in labels_list:
            labels.append(label['name'])
        model.labels = labels

        with open(model.groups_file, "r") as f:
            groups_json = json.load(f)

        groups_list = groups_json["groups"]
        groups = ['']
        for group in groups_list:
            groups.append(group['name'])
        model.groups = groups         
        if 'uploaded_files_info' in st.session_state:
            all_files = []
            current_user = st.session_state['username']
            if current_user == 'admin':
                for user_files in st.session_state['uploaded_files_info'].values():
                    all_files.extend(user_files)
            else:
                all_files = st.session_state['uploaded_files_info'].get(current_user, [])

            if all_files:
                preview_col, json_table_col = st.columns([4, 4])
                with preview_col:
                    st.subheader("File Preview")
                    if all_files:
                        file_to_preview = all_files[0]  # Hoặc sử dụng một tiêu chí chọn file khác nếu bạn muốn
                    else:
                        file_to_preview = None
                    
                    if file_to_preview is not None:
                            file_type = file_to_preview.type.split('/')[1]
                            if file_type in ["jpeg", "png", "jpg"]:
                                with st.sidebar:
                                    st.markdown("---")
                                    st.subheader(model.subheader_1)

                                    placeholder_upload = st.empty()
                                    
                                    file_names = self.get_existing_file_names('docs/images/', current_user)
                                    file_options = [file.name for file in all_files]
                                    
                                    if 'annotation_index' not in st.session_state:
                                        st.session_state['annotation_index'] = 0
                                        annotation_index = 0
                                    else:
                                        annotation_index = st.session_state['annotation_index']
                               
                                    annotation_selection = placeholder_upload.selectbox(model.annotation_text, file_names,
                                                                                                    index=annotation_index,
                                                                                                    help=model.annotation_selection_help)

                                    annotation_index = self.get_annotation_index(annotation_selection, file_names)

                                    file_extension = self.get_file_extension(annotation_selection, 'docs/images/')
                                    model.img_file = f"docs/images/{annotation_selection}" + file_extension
                                    model.rects_file = f"docs/json/{annotation_selection}.json"

                                    completed_check = st.empty()

                                    
                                                    
                            else:
                                    st.warning("Now you can go to Upload page to upload documents")





        

        # st.title(model.pageTitle + " - " + annotation_selection)

        if model.img_file is None:
            st.caption(model.no_annotation_file)
            return

        saved_state = self.fetch_annotations(model.rects_file)

        # annotation file has been changed
        if annotation_index != st.session_state['annotation_index']:
            annotation_v = saved_state['meta']['version']
            if annotation_v == "v0.1":
                st.session_state["annotation_done"] = False
            else:
                st.session_state["annotation_done"] = True
        # store the annotation file index
        st.session_state['annotation_index'] = annotation_index

        # first load
        if "annotation_done" not in st.session_state:
            annotation_v = saved_state['meta']['version']
            if annotation_v == "v0.1":
                st.session_state["annotation_done"] = False
            else:
                st.session_state["annotation_done"] = True

        

        assign_labels = st.checkbox(model.assign_labels_text, True, help=model.assign_labels_help)
        mode = "transform" if assign_labels else "rect"

        docImg = Image.open(model.img_file)

        data_processor = DataProcessor()

        with st.container():
            doc_height = saved_state['meta']['image_size']['height']
            doc_width = saved_state['meta']['image_size']['width']
            canvas_width, number_of_columns = self.canvas_available_width(ui_width, doc_width, device_type,
                                                                          device_width)

            if number_of_columns > 1:
                col1, col2 = st.columns([number_of_columns, 10 - number_of_columns])
                with col1:
                    result_rects = self.render_doc(model, docImg, saved_state, mode, canvas_width, doc_height, doc_width)
                with col2:
                    
                    
                        self.render_form(model, result_rects, data_processor, annotation_selection)
                    
            else:
                result_rects = self.render_doc(model, docImg, saved_state, mode, canvas_width, doc_height, doc_width)
                
                self.render_form(model, result_rects, data_processor, annotation_selection)
                

    def render_doc(self, model, docImg, saved_state, mode, canvas_width, doc_height, doc_width):
        with st.container():
            height = 1296
            width = 864

            result_rects = st_sparrow_labeling(
                fill_color="rgba(0, 151, 255, 0.3)",
                stroke_width=2,
                stroke_color="rgba(0, 50, 255, 0.7)",
                background_image=docImg,
                initial_rects=saved_state,
                height=height,
                width=width,
                drawing_mode=mode,
                display_toolbar=True,
                update_streamlit=True,
                canvas_width=canvas_width,
                doc_height=doc_height,
                doc_width=doc_width,
                image_rescale=True,
                key="doc_annotation" + model.img_file
            )

            st.caption(model.text_caption_1)
            st.caption(model.text_caption_2)

            return result_rects

    def render_form(self, model, result_rects, data_processor, annotation_selection):
        with st.container():
            if result_rects is not None:
                with st.form(key="fields_form"):
                    toolbar = st.empty()

                    self.render_form_view(result_rects.rects_data['words'], model.labels, result_rects,
                                          data_processor)

                    with toolbar:
                        submit = st.form_submit_button(model.save_text, type="primary")
                        if submit:
                            for word in result_rects.rects_data['words']:
                                if len(word['value']) > 1000:
                                    st.error(model.error_text)
                                    return

                            with open(model.rects_file, "w") as f:
                                json.dump(result_rects.rects_data, f, indent=2)
                            st.session_state[model.rects_file] = result_rects.rects_data
                            # st.write(model.saved_text)
                            st.experimental_rerun()

                if len(result_rects.rects_data['words']) == 0:
                    st.caption(model.no_annotation_mapping)
                    return
                else:
                    with open(model.rects_file, 'rb') as file:
                        st.download_button(label=model.download_text,
                                           data=file,
                                           file_name=annotation_selection + ".json",
                                           mime='application/json',
                                           help=model.download_hint)

    def render_form_view(self, words, labels, result_rects, data_processor):
        data = []
        for i, rect in enumerate(words):
            group, label = rect['label'].split(":", 1) if ":" in rect['label'] else (None, rect['label'])
            data.append({'id': i, 'value': rect['value'], 'label': label})
        df = pd.DataFrame(data)

        formatter = {
            'id': ('ID', {**PINLEFT, 'hide': True}),
            'value': ('Value', {**PINLEFT, 'editable': True}),
            'label': ('Label', {**PINLEFT,
                                'width': 80,
                                'editable': True,
                                'cellEditor': 'agSelectCellEditor',
                                'cellEditorParams': {
                                    'values': labels
                                }})
        }

        go = {
            'rowClassRules': {
                'row-selected': 'data.id === ' + str(result_rects.current_rect_index)
            }
        }

        green_light = "#abf7b1"
        css = {
            '.row-selected': {
                'background-color': f'{green_light} !important'
            }
        }

        response = agstyler.draw_grid(
            df,
            formatter=formatter,
            fit_columns=True,
            grid_options=go,
            css=css
        )

        data = response['data'].values.tolist()

        for i, rect in enumerate(words):
            value = data[i][1]
            label = data[i][2]
            data_processor.update_rect_data(result_rects.rects_data, i, value, label)

    def canvas_available_width(self, ui_width, doc_width, device_type, device_width):
        doc_width_pct = (doc_width * 100) / ui_width
        if doc_width_pct < 45:
            canvas_width_pct = 37
        elif doc_width_pct < 55:
            canvas_width_pct = 49
        else:
            canvas_width_pct = 60

        if ui_width > 700 and canvas_width_pct == 37 and device_type == "desktop":
            return math.floor(canvas_width_pct * ui_width / 100), 4
        elif ui_width > 700 and canvas_width_pct == 49 and device_type == "desktop":
            return math.floor(canvas_width_pct * ui_width / 100), 5
        elif ui_width > 700 and canvas_width_pct == 60 and device_type == "desktop":
            return math.floor(canvas_width_pct * ui_width / 100), 6
        else:
            if device_type == "desktop":
                ui_width = device_width - math.floor((device_width * 22) / 100)
            elif device_type == "mobile":
                ui_width = device_width - math.floor((device_width * 13) / 100)
            return ui_width, 1

    def fetch_annotations(self, rects_file):
        for key in st.session_state:
            if key.startswith("docs/json/") and key != rects_file:
                del st.session_state[key]

        if rects_file not in st.session_state:
            with open(rects_file, "r") as f:
                saved_state = json.load(f)
                st.session_state[rects_file] = saved_state
        else:
            saved_state = st.session_state[rects_file]

        return saved_state

    

    def get_existing_file_names(self, dir_name, username=None):
    # Nếu là admin và không cung cấp username, trả về tất cả files không bắt đầu bằng dấu chấm (.)
        if username == "admin":
            return natsorted([os.path.splitext(f)[0] for f in os.listdir(dir_name) if not f.startswith('.')])
        else:
            # Nếu không phải admin, chỉ trả về files bắt đầu bằng username
            user_prefix = f"{username}"
            return natsorted([os.path.splitext(f)[0] for f in os.listdir(dir_name) if f.startswith(user_prefix) and not f.startswith('.')])

    def get_file_extension(self, file_name, dir_name):
        # get list of files, excluding hidden files
        files = [f for f in os.listdir(dir_name) if not f.startswith('.')]
        for f in files:
            if file_name is not  None and os.path.splitext(f)[0] == file_name:
                return os.path.splitext(f)[1]

    def get_annotation_index(self, file, files_list):
        return files_list.index(file)
def show_logout_button():
    if st.sidebar.button('Log out'):
    # Đặt `logged_in` thành False để biểu thị việc đăng xuất
        st.session_state['logged_in'] = False
    # Bạn cũng có thể muốn xóa tên người dùng khỏi session_state nếu muốn
        if 'username' in st.session_state:
            del st.session_state['username']
        st.experimental_rerun()  # Yêu cầu chạy lại ứng dụng
def main():
   
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
            show_logout_button()
            DataAnnotation().view(DataAnnotation.Model(), st.session_state['ui_width'], st.session_state['device_type'],
                                    st.session_state['device_width'])




    
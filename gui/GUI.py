import dearpygui.dearpygui as dpg
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
libs_dir = os.path.join(parent_dir, 'libs')
sys.path.append(libs_dir)

from libs.SkylanderDumpProcessor import SkylanderDumpProcessor

file1_path = ""
file2_path = ""
output_name = ""

def select_file1_callback(sender, app_data):
    global file1_path
    file1_path = app_data['file_path_name']
    dpg.set_value("file1_text", f"Skylander: {file1_path}")
    validate_inputs()

def select_file2_callback(sender, app_data):
    global file2_path
    file2_path = app_data['file_path_name']
    dpg.set_value("file2_text", f"Tag dump: {file2_path}")
    validate_inputs()

def process_files_callback():
    global file1_path, file2_path, output_name
    output_name = dpg.get_value("output_name_input")

    if not output_name.strip(): 
        file1_name = os.path.splitext(os.path.basename(file1_path))[0] 
        file2_name = os.path.splitext(os.path.basename(file2_path))[0] 
        output_name = f"{file1_name}{file2_name}" 

    print(f"Selected Skylander: {file1_path}")
    print(f"Selected dump: {file2_path}")
    print(f"Output Name: {output_name}")

    processor = SkylanderDumpProcessor(file2_path, file1_path, output_name)
    processor.process()
    
    output_path = os.path.abspath(output_name)
    dpg.set_value("log_text", f"Result saved to: {output_path+".dump"}")

def validate_inputs():
    """Enable or disable the button based on whether files are selected."""
    if file1_path and file2_path:
        dpg.enable_item("run_button")
        dpg.bind_item_theme("run_button", enabled_button_theme)
        dpg.hide_item("run_button_tooltip") 
    else:
        dpg.disable_item("run_button")
        dpg.bind_item_theme("run_button", disabled_button_theme)
        dpg.show_item("run_button_tooltip") 

dpg.create_context()

with dpg.theme(tag="enabled_button_theme") as enabled_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 128, 0, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 180, 0, 255))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255)) 

with dpg.theme(tag="disabled_button_theme") as disabled_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (128, 128, 128, 255)) 
        dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200, 255))  

with dpg.theme(tag="file_button_theme") as file_button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 128, 0, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 180, 0, 255))  
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  

with dpg.window(label="File Selector App", tag="main_window"):
    dpg.add_text("Skylander file:")
    dpg.add_button(label="Select Skylander file", callback=lambda: dpg.show_item("file1_dialog"), tag="file1_button")
    dpg.bind_item_theme("file1_button", file_button_theme) 
    dpg.add_text("", tag="file1_text")
    
    dpg.add_text("Tag dump:")
    dpg.add_button(label="Select tag dump file", callback=lambda: dpg.show_item("file2_dialog"), tag="file2_button")
    dpg.bind_item_theme("file2_button", file_button_theme)  
    dpg.add_text("", tag="file2_text")
    
    dpg.add_text("Add custom name of output:")
    dpg.add_input_text(tag="output_name_input", hint="Custom output name")

    dpg.add_spacer(height=10) 
    dpg.add_button(label="Make skylander!", callback=process_files_callback, tag="run_button")
    dpg.bind_item_theme("run_button", disabled_button_theme)  
    dpg.disable_item("run_button")  

    with dpg.tooltip("run_button", tag="run_button_tooltip"):
        dpg.add_text("Select both files to enable this button.")
    
    # Log output area
    dpg.add_spacer(height=10)
    dpg.add_text("", tag="log_text", color=(0, 128, 255, 255))

with dpg.file_dialog(directory_selector=False, show=False, callback=select_file1_callback, tag="file1_dialog", width=500, height=400):
    dpg.add_file_extension(".sky", color=(150, 255, 150, 255))

with dpg.file_dialog(directory_selector=False, show=False, callback=select_file2_callback, tag="file2_dialog", width=500, height=400):
    dpg.add_file_extension(".bin", color=(150, 255, 150, 255))

dpg.create_viewport(title='Skylib GUI', width=800, height=500)
dpg.setup_dearpygui()

dpg.set_primary_window("main_window", True)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

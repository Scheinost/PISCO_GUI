"""
Title: Quantification of phenocrysts content on volcanic rocks: Improvements and new low-cost techniques.

Authors: Alexander Scheinost, Mauricio Rivera, Mauricio Torreblanca-Gaymer, Yuvineza Gomez-Leyton, Felipe Rojas, Alfredo Esquivel

Publications DOI: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

PISCO (Photomicrography Interface System of Capture and Operation)

"""
import os
import sys
import tkinter
from tkinter import filedialog
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import font
from tkinter import PhotoImage
import matplotlib_scalebar.scalebar as sb
import matplotlib.pyplot as plt
import functions as fn
import cv2
import time
from ttkthemes import ThemedTk
from PIL import Image, ImageTk 


# useful functions
# this initial function tries to connect with the camera module from the raspberry
# it enables to use the interface in a different device apart from the raspberry 
try:
    from picamera import PiCamera
    import picamerax as picamera
except ModuleNotFoundError:
    print("picamera module is not installed")

def functions_calibration(argument):
    global submit
    if argument:
        filter_type = filter_type_combobox.get()
        calib = ["'" + str(lowerx.get()) + str(lowery.get()) + "'", "'" + str(upperx.get()) + str(uppery.get()) + "'"]
        ser = serial.Serial('/dev/ttyACM0', 9600)
        time.sleep(5)
        go = '55551500'
        ser.write(go.encode())
        for i in calib:
            ser.write(i.encode())
            time.sleep(1)
            fn.preview(5, filter_type)
    else:
        submit = True

#Set variables
folder_path = None
Submit = None

#################### GUI CODE #######################
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

window = ThemedTk(theme = "winxpblue")
window.title("PISCO v1.3")
window.iconbitmap(resource_path("LogoCkelar.ico"))

# Modifica la carga del iconphoto así:
try:
    icon_image = Image.open(resource_path("icono.png"))
    photo = ImageTk.PhotoImage(icon_image)
    window.iconphoto(True, photo)  # Cambiado a True para hacerlo permanente
except Exception as e:
    print(f"Error loading icon: {e}")

my_tabs = ttk.Notebook(window)
my_tabs.pack()


window_width = window.winfo_screenwidth() // 5
window_height = window.winfo_screenheight() // 2
window.geometry(f"{window_width}x{window_height}")



font_size = int(window_height / 50)
font = font.Font(size=font_size)

window.option_add("*Font", font)

tab1 = tkinter.Frame(my_tabs)
tab2 = tkinter.Frame(my_tabs)
tab3 = tkinter.Frame(my_tabs)
tab4 = tkinter.Frame(my_tabs)

my_tabs.add(tab1, text="General")
my_tabs.add(tab2, text="Advanced")
my_tabs.add(tab3, text="Calibration")
my_tabs.add(tab4, text="Post-process")

#############################################################################
#############################################################################
########################      TAB1: USER INPUTS      ########################

# USER INPUT
inputs_frame = tkinter.LabelFrame(tab1, text="User Inputs", padx=5, pady=5)
inputs_frame.grid(row=0, column=0, sticky="news")

sample_code_label = tkinter.Label(inputs_frame, text="Sample Code", width=19, anchor="w")
sample_code_label.grid(row=0, column=0, sticky="w")

sample_code_entry = tkinter.Entry(inputs_frame, width=23)
sample_code_entry.grid(row=0, column=1)

filter_type_label = tkinter.Label(inputs_frame, text="Filter")
filter_type_label.grid(row=1, column=0, sticky="w")

filter_type_combobox = ttk.Combobox(inputs_frame, values=["Plane-polarized light (PPL)", "Cross-polarized light (XPL)"], width=20)
filter_type_combobox.grid(row=1, column=1)

for widget in inputs_frame.winfo_children():
    widget.grid_configure(padx=5, pady=5)

# FRAME FOR SINGLE PHOTO
single_photo_frame = tkinter.LabelFrame(tab1, text="Single Photo", padx=5, pady=5)
single_photo_frame.grid(row=2, column=0, sticky="news")

folder_label = tkinter.Label(single_photo_frame, text="Folder", width=19, padx=5)
folder_label.grid(row=0, column=0, sticky="news")

def check_selection(mode):
    global folder_path
    sample_code = sample_code_entry.get()
    filter_type = filter_type_combobox.get()
    folder_path = fn.create_subfolder(mode, sample_code,filter_type)
    sequence_button.config(state="normal" if mode != "single_photo" else "disabled")

single_folder_button = tkinter.Button(single_photo_frame, text="Select Folder", command=lambda: check_selection("single_photo"))
single_folder_button.grid(row=0, column=1, sticky="news")

def single_photo():
    filter_type = filter_type_combobox.get()
    sample_code = sample_code_entry.get()
    fn.single_photo(filter_type, sample_code) if fn.check_fields(filter_type, sample_code) else None

single_photo_button = tkinter.Button(single_photo_frame, text="Take Photo", width=16, command=lambda: single_photo())
single_photo_button.grid(row=1, column=1, sticky="news")

def preview():
    filter_type = filter_type_combobox.get()
    fn.preview(20, filter_type)

preview_button = tkinter.Button(single_photo_frame, text="Preview", command=lambda: preview())
preview_button.grid(row=1, column=0, sticky="news")

for widget in single_photo_frame.winfo_children():
    widget.grid_configure(padx=5, pady=5)

# FRAME FOR PIAUTOSTAGE
piauto_frame = tkinter.LabelFrame(tab1, text="Modified PiAutoStage", padx=5, pady=5)
piauto_frame.grid(row=3, column=0, sticky="news")

sequence_folder_label = tkinter.Label(piauto_frame, text="Sequence Photos", width=18)
sequence_folder_label.grid(row=0, column=0, sticky="w")

sequence_folder_button = tkinter.Button(piauto_frame, text="Select Folder", command=lambda: check_selection("piauto"), width=16)
sequence_folder_button.grid(row=0, column=1, sticky="news")

def start_seq():
    sample_code = sample_code_entry.get()
    filter_type = filter_type_combobox.get()
    folder_path = fn.create_subfolder(filter_type, sample_code) if fn.check_fields(filter_type, sample_code) else None
    
    # Calcular el número de columnas y filas
    photo_width = 2028  # Ancho de cada foto en píxeles
    photo_height = 1550  # Alto de cada foto en píxeles
    
    if not submit:
        col = 20
        row = 16
        fn.piautostage("auto", 50, 0, photo_width, photo_height, col, row, 0, 0, 0, 0, folder_path)
    else:
        x_min = int(lowerx.get())
        y_min = int(lowery.get())
        x_max = int(upperx.get())
        y_max = int(uppery.get())
        
        # Calcular el número de columnas y filas basados en el área de captura
        col = (x_max - x_min) // photo_width
        row = (y_max - y_min) // photo_height
        
        fn.piautostage("calibrated", 50, 0, photo_width, photo_height, col, row, x_min, y_min, x_max, y_max, folder_path)

sequence_button = tkinter.Button(piauto_frame, text="Start Sequence", command=lambda: start_seq(), state="disabled", width=16)
sequence_button.grid(row=1, column=0, sticky="news", columnspan=2)

for widget in piauto_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

##########################################################################
##########################################################################
########################      TAB2: ADVANCED      ########################
# FRAME FOR PARAMETERS
parameter_frame = tkinter.LabelFrame(tab2, text="Parameters", padx=5, pady=5)
parameter_frame.grid(row=0, column=0, sticky="news")

iso_label = tkinter.Label(parameter_frame, text="ISO", width=17, anchor="w")
iso_label.grid(row=0, column=0, sticky="w")

shutter_label = tkinter.Label(parameter_frame, text="Shutter speed", width=10, anchor="w")
shutter_label.grid(row=1, column=0, sticky="w")

resolution_label = tkinter.Label(parameter_frame, text="Resolution", width=10, anchor="w")
resolution_label.grid(row=3, column=0, sticky="w")

size_label = tkinter.Label(parameter_frame, text="Frame size", width=10, anchor="w")
size_label.grid(row=4, column=0, sticky="w")

iso_entry = tkinter.Entry(parameter_frame, width=22)
iso_entry.grid(row=0, column=1, columnspan=2)

shutter_entry = tkinter.Entry(parameter_frame, width=22)
shutter_entry.grid(row=1, column=1, columnspan=2)

resx_entry = tkinter.Entry(parameter_frame, width=9)
resx_entry.grid(row=3, column=1)

resy_entry = tkinter.Entry(parameter_frame, width=9)
resy_entry.grid(row=3, column=2)

col_entry = tkinter.Entry(parameter_frame, width=9)
col_entry.grid(row=4, column=1)

row_entry = tkinter.Entry(parameter_frame, width=9)
row_entry.grid(row=4, column=2)

def adv_seq():
    sample_code = sample_code_entry.get()
    filter_type = filter_type_combobox.get()
    if value == 0:
        ISO = int(iso_entry.get())
        resx = int(resx_entry.get())
        resy = int(resy_entry.get())
        shutt = int(shutter_entry.get())
        ncol = int(col_entry.get())
        nrow = int(row_entry.get())
        fn.adv_sequence(ISO, resx, resy, shutt, ncol, nrow, 0, 0, 0, 0)
    else:
        fn.create_subdirectories(filter_type, sample_code) if fn.check_fields(filter_type, sample_code) else None
        fn.piautostage("auto", 50, 2028, 1550, 0, 20, 16, 0, 0, 0, 0)

# def piautostage(auto,iso,resolution,shutter,wb,col,row):
run_button = tkinter.Button(parameter_frame, text="Start Sequence", command=adv_seq)
run_button.grid(row=5, column=1, sticky="news", columnspan=2)

for widget in parameter_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# FRAME FOR MOVE TEST
movetest_frame = tkinter.LabelFrame(tab2, text="Move test", padx=5, pady=5)
movetest_frame.grid(row=1, column=0, sticky="news")

coordinates_label = tkinter.Label(movetest_frame, text="Coordinates", width=17, anchor="w")
coordinates_label.grid(row=0, column=0, sticky="w")

cordx_entry = tkinter.Entry(movetest_frame, width=9)
cordx_entry.grid(row=0, column=1)

cordy_entry = tkinter.Entry(movetest_frame, width=9)
cordy_entry.grid(row=0, column=2)

def get_coord():
    coordx = cordx_entry.get()
    coordy = cordy_entry.get()
    fn.move_test(coordx, coordy)

move_button = tkinter.Button(movetest_frame, text="Go", command=get_coord)
move_button.grid(row=1, column=1, sticky="news", columnspan=2)

for widget in movetest_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# FRAME FOR PREVIEW

preview_frame = tkinter.LabelFrame(tab2, text="Preview", padx=5, pady=5)
preview_frame.grid(row=2, column=0, sticky="news")

def start_long_preview():
    global preview_active
    preview_active = True

    def update_preview():
        if preview_active:
            filter_type = filter_type_combobox.get()
            fn.preview(20, filter_type)
            window.after(100, update_preview)

    update_preview()

def stop_preview():
    global preview_active
    preview_active = False

long_preview_button = tkinter.Button(preview_frame, text="Start Preview", fg="white", bg="#1cbd47", width= 16, command=lambda:start_long_preview())
long_preview_button.grid(row=0, column=0, sticky="news")

stop_button = tkinter.Button(preview_frame, text="Stop Preview", fg="white", bg="#ad3834", width= 16, command=lambda:stop_preview())
stop_button.grid(row=0, column=1, sticky="news")

for widget in preview_frame.winfo_children():
    widget.grid_configure(padx=10, pady=5)

################################################################################
################################################################################
########################      TAB3: CALIBRATION      ###########################

calibration_frame = tkinter.LabelFrame(tab3, text="Calibration Inputs", padx=5, pady=5)
calibration_frame.grid(row=0, column=0, sticky="news")

newx_label = tkinter.Label(calibration_frame, text="X", width=15)
newx_label.grid(row=0, column=1, sticky="w")

newy_label = tkinter.Label(calibration_frame, text="Y", width=10)
newy_label.grid(row=0, column=2, sticky="w")

lowerleft_label = tkinter.Label(calibration_frame, text="Lower left", width=10)
lowerleft_label.grid(row=1, column=0)

upperright_label = tkinter.Label(calibration_frame, text="Upper right", width=10)
upperright_label.grid(row=2, column=0, sticky="w")

lowerx = tkinter.Entry(calibration_frame, width=10)
lowerx.grid(row=1, column=1)

lowery = tkinter.Entry(calibration_frame, width=10)
lowery.grid(row=1, column=2)

upperx = tkinter.Entry(calibration_frame, width=10)
upperx.grid(row=2, column=1)

uppery = tkinter.Entry(calibration_frame, width=10)
uppery.grid(row=2, column=2)

calibration_preview_button = tkinter.Button(calibration_frame, text="Preview", width=10, command=lambda: functions_calibration(True))
calibration_preview_button.grid(row=3, column=1, sticky="news")

submit_button = tkinter.Button(calibration_frame, text="Submit", width=10, command=lambda: functions_calibration(False))
submit_button.grid(row=3, column=2, sticky="news")

for widget in calibration_frame.winfo_children():
    widget.grid_configure(padx=5, pady=5)

################################################################################
################################################################################
########################      TAB4: POSTPROCESSING      ########################

img_path = tkinter.StringVar()
image_path = ""

def select_image():
    global image_path
    image_path = filedialog.askopenfilename(title='Select image directory')
    print(image_path)

scale_frame = tkinter.LabelFrame(tab4, text="Insert Scale", padx=5, pady=5)
scale_frame.grid(row=0, column=0, sticky="news")

image_label = tkinter.Label(scale_frame, text="Select Image", width=16, anchor="w")
image_label.grid(row=0, column=0, sticky="w")

image_button = tkinter.Button(scale_frame, text="Select Image", width=16, command=select_image)
image_button.grid(row=0, column=1, sticky="news")

mag_label = tkinter.Label(scale_frame, text="Select Magnification", width=16, anchor="w")
mag_label.grid(row=1, column=0, sticky="w")

mag_combobox = ttk.Combobox(scale_frame, values=["2.5x", "4x", "5x", "10x", "16x", "20x", "40x"])
mag_combobox.grid(row=1, column=1)

select_label = tkinter.Label(scale_frame, text="Insert lenght ", width=16, anchor="w")
select_label.grid(row=2, column=0, sticky="w")

scale_entry = tkinter.Entry(scale_frame, width=23)
scale_entry.grid(row=2, column=1)

cm_mm_label = tkinter.Label(scale_frame, text="Scale Unit ", width=16, anchor="w")
cm_mm_label.grid(row=3, column=0, sticky="w")

cm_mm_combobox = ttk.Combobox(scale_frame, values=["Centimeter (cm)", "Millimeter (mm)", "Micrometer (µm)"])
cm_mm_combobox.grid(row=3, column=1)

pos_label = tkinter.Label(scale_frame, text="Position ", width=16, anchor="w")
pos_label.grid(row=4, column=0, sticky="w")

pos_combobox = ttk.Combobox(scale_frame, values=["Upper left", "Upper right", "Lower left", "Lower right"])
pos_combobox.grid(row=4, column=1)

font_label = tkinter.Label(scale_frame, text="Font Color", width=16, anchor="w")
font_label.grid(row=5, column=0, sticky="w")

def choose_color(button):
    if button == "font_button":
        color_code = colorchooser.askcolor(title="Choose color")[1]
        fontc_button.config(bg=color_code)
        global font_col
        font_col = color_code
    elif button == "background_button":
        color_code = colorchooser.askcolor(title="Choose color")[1]
        background_button.config(bg=color_code)
        global bg_col
        bg_col = color_code

font_col = "#FFFFFF"
bg_col = "#FFFFFF"

fontc_button = tkinter.Button(scale_frame, width=8, command=lambda: choose_color("font_button"), )
fontc_button.grid(row=5, column=1)

background_button = tkinter.Button(scale_frame, width=8, state="disabled",
                                   command=lambda: choose_color("background_button"), background="#c2c2c2")
background_button.grid(row=6, column=1)

def active():
    if x.get() == 1:
        background_button.config(state="active")
        background_button.config(background="#F0F0F0")
    else:
        background_button.config(state="disabled")
        background_button.config(background="#c2c2c2")

x = tkinter.IntVar()
desb_check = tkinter.Checkbutton(scale_frame, text="Colored background", variable=x, onvalue=1, offvalue=0,
                                 command=active, anchor="w")
desb_check.grid(row=6, column=0)

mags = ["2.5x", "4x", "5x", "10x", "16x", "20x", "40x"]
scale = [31, 62, 78, 155, 248, 310, 620]  # pixels values to 100 µm

def insert_scale(font_col, bg_col):
    if image_path == "" or scale_entry.get() == "" or mag_combobox.get() == "":
        tkinter.messagebox.showerror(title=("Error"), message=("Please fill Image, Scale or Magnification."))
    else:
        img = cv2.imread(image_path)
        height, width, _ = img.shape
        dpi = 300

        index = mags.index(mag_combobox.get())
        fixed = float(scale_entry.get())
        cm_mm = cm_mm_combobox.get().lower()
        position = str(pos_combobox.get()).lower()
        if x.get() == 1:
            if cm_mm == "centimeter (cm)":
                scalebar = sb.ScaleBar((100 / (scale[index] * 10000)), "cm", location=position, color=font_col,
                                       box_color=bg_col, fixed_value=fixed)
            elif cm_mm == "millimeter (mm)":
                scalebar = sb.ScaleBar((100 / (scale[index] * 1000)), "mm", location=position, color=font_col,
                                       box_color=bg_col, fixed_value=fixed)
            elif cm_mm == "micrometer (µm)":
                scalebar = sb.ScaleBar((100 / scale[index]), "µm", location=position, color=font_col, box_color=bg_col,
                                       fixed_value=fixed)
        else:
            if cm_mm == "centimeter (cm)":
                scalebar = sb.ScaleBar((100 / (scale[index] * 10000)), "cm", location=position, color=font_col,
                                       box_color=bg_col, box_alpha=0, fixed_value=fixed)
            elif cm_mm == "millimeter (mm)":
                scalebar = sb.ScaleBar((100 / (scale[index] * 1000)), "mm", location=position, color=font_col,
                                       box_color=bg_col, box_alpha=0, fixed_value=fixed)
            elif cm_mm == "micrometer (µm)":
                scalebar = sb.ScaleBar((100 / scale[index]), "µm", location=position, color=font_col, box_color=bg_col,
                                       box_alpha=0, fixed_value=fixed)

        target_width_pixels = 2050
        target_height_pixels = 1550
        fig = plt.figure(figsize=(target_width_pixels / dpi, target_height_pixels / dpi), dpi=dpi)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax = plt.gca()
        ax.add_artist(scalebar)

        plt.axis("off")
        savedname = ''.join((image_path[:-4], '_scale_', str(fixed), image_path[-4:]))
        if os.path.exists(savedname):
            response = tkinter.messagebox.askyesno(title="File Exists!",
                                                   message="Do you want to overwrite the existing file?")
            if not response:
                return
        plt.savefig(savedname, bbox_inches="tight", pad_inches=0)
        plt.show()

button2 = tkinter.Button(scale_frame, text="Insert Scale", width=16, command=lambda: insert_scale(font_col, bg_col))
button2.grid(row=7, column=0, sticky="news", columnspan=2)

for widget in scale_frame.winfo_children():
    widget.grid_configure(padx=5, pady=5)
window.mainloop()
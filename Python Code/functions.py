"""
Title: Quantification of phenocrysts content on volcanic rocks: Improvements and new low-cost techniques.

Authors: Alexander Scheinost, Mauricio Rivera, Mauricio Torreblanca-Gaymer, Yuvineza Gomez-Leyton, Felipe Rojas, Alfredo Esquivel

Publications DOI: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

PISCO (Photomicrography Interface System of Capture and Operation)
"""

import time, os
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import messagebox
import shutil

current_time = time.strftime("%d_%m_%Y")

def check_fields(filter_type, sample_code):
    if filter_type == "":
        messagebox.showerror("Error", "Please enter a filter type.")
        return False
    elif sample_code == "":
        messagebox.showerror("Error", "Please select a sample code.")
        return False
    else:
        return True

def create_folder(path, folder_name):
    folder_path = os.path.join(path, folder_name)
    if os.path.exists(folder_path):
        choice = messagebox.askyesno("Folder Exists",
                                     f"Folder '{folder_name}' already exists. Do you want to overwrite it?")
        if choice:
            shutil.rmtree(folder_path)
            os.mkdir(folder_path)
        else:
            print("Operation Cancelled.")
    else:
        os.mkdir(folder_path)
    return folder_path

def function_filter_type(sample_code, filter_type):
    if filter_type == "Plane-polarized light (PPL)":
        return sample_code + "_PPL"
    else:
        return sample_code + "_NC"

def create_subfolder(folder_type, sample_code, filter_type):
    source_path = filedialog.askdirectory(title='Select directory to save the sequence')
    if folder_type == "single_photo":
        sample_code = function_filter_type(sample_code, filter_type)
        sample_code = sample_code + "_" + current_time
        folder_path = create_folder(source_path, sample_code)
    else:
        sample_code = function_filter_type(sample_code, filter_type)
        sample_code = sample_code + "_captured_sequence"
        folder_path = create_folder(source_path, sample_code)
    return folder_path

def preview(t, filter_type):
    with picamera.PiCamera() as camera:
        if filter_type == "Plane-polarized light (PPL)":
            time.exposure = 1000
        else:
            time.exposure = 100000
        camera.resolution = (2028, 1550)
        camera.iso = 10
        camera.start_preview()
        time.sleep(t)
        camera.stop_preview()

def move_test(cx, cy):
    coordinate = "'" + str(cx) + str(cy) + "'"
    ser = serial.Serial('/dev/ttyACM0', 9600)
    time.sleep(5)
    go = '55551800'
    ser.write(go.encode())
    time.sleep(1)
    ser.write(coordinate.encode())
    ser.close()

def single_photo(filter_type, sample_code):
    imagetime = time.strftime("%Y_%m_%d_%H_%M_%S")  # Year,month,day,Hour,Minute,Second
    camera = PiCamera()
    time.sleep(2)
    camera.iso = 10
    camera.resolution = (2028, 1550)
    if filter_type == "Plane-polarized light (PPL)":
        camera.shutter_speed = 1000
    else:
        camera.shutter_speed = 3000000
    camera.start_preview()
    time.sleep(4)
    camera.stop_preview()
    file_name = path + "/" + sample_code + imagetime + ".jpg"  # samplecode_Year_Month_Day_Hour_Minute_Second
    camera.capture(file_name)
    camera.close()

def submit(check):
    if check == "piauto":
        state = True
    else:
        state = False
    return state

def piautostage(stage_type, isx, shutter, resx, resy, col, row, x_min, y_min, x_max, y_max, folder_path):
    """
    Start of modified PiAutoStage script.
    The original version of R. Alex Steiner and Tyrone.O. Rooney
    Publications DOI: https://doi.org/10.1029/2021GC009693
    """
    res = [resx, resy]
    def position(a, b):
        if a < 1000:
            a1 = '0' + str(a)
        else:
            a1 = str(a)
        if b < 1000:
            b1 = '0' + str(b)
        else:
            b1 = str(b)
        return a1 + b1

    os.chdir(folder_path)

    ## HOME POSITION ##
    home = position(1050, 2100)

    ## STAGE LIMITS ##
    if stage_type == "calibrated":
        x_min, x_max, y_min, y_max = 750, 1800, 1650, 2400
    else:
        x_min, x_max, y_min, y_max = x_min, y_min, x_max, y_max
    gx = 0
    count = 1000
    
    ser = serial.Serial('/dev/ttyACM0', 9600)
    time.sleep(2)
    go = '55551500'  # SENDS THE GOCODE TO ATTACH THE ARDUINO PINS TO THE SERVOS ######
    ser.write(go.encode())
    time.sleep(1)

    ###### CALCULATES THE NUMBER AND SIZE OF STEPS ######
    if stage_type == "calibrated":
        x_step = int((x_max - x_min) / 20)
        y_step = int((y_max - y_min) / 16)
    else:
        x_step = abs(int((x_max - x_min) / int(col)))
        y_step = abs(int((y_max - y_min) / int(row)))

    ######## FOCUS AND IMAGE PARAMETER SEQUENCE STARTS HERE ########

    pos = ['10501900', '07001700', '07002100', '14002100', '14001700']
    listaq = []
    listag = []
    for i in range(len(pos)):
        ser.write((pos[i]).encode())
        time.sleep(1)
        with picamera.PiCamera() as camera:
            camera.resolution = res
            camera.iso = isx
            camera.start_preview()
            time.sleep(2)
            q = camera.exposure_speed
            g = camera.awb_gains
            listaq.append(q)
            listag.append(g)
            camera.stop_preview()

    qfloat = sum(listaq) / len(listaq)
    q = min(listaq)

    ###### THE CAPTURE PARAMETERS ARE AUTOMATICALLY SET ######
    if shutter != 0:
        q = shutter
    if gx != 0:
        g = gx

    ###### START THE CAPTURE SEQUENCE #####
    i = 0
    x = x_min
    time.sleep(1)

    ###### THIS CICLE TRANSPORTS THE CARRIAGE ALONG THE X AXIS ######
    while i <= (col - 1):
        print('\nColumn  ' + str(i + 1) + ' of ' + str(col))
        y = y_max
        j = 0

        ###### THIS CICLE TRANSPORTS THE CARRIAGE ALONG THE Y AXIS ######
        while j <= (row - 1):
            time.sleep(1)
            coord = position(x, y)
            ser.write(coord.encode())
            with picamera.PiCamera() as camera:
                camera.iso = isx
                camera.resolution = (2028, 1550)
                time.sleep(1)
                camera.shutter_speed = q
                camera.exposure_mode = 'off'
                camera.awb_mode = 'off'
                camera.awb_gains = g
                filename = str(count) + '.jpg'
                camera.capture(filename)
                count = count + 1
            y = y - y_step
            j = j + 1
        x = x + x_step
        i = i + 1
    ser.write(home.encode())
    ser.close()

    """
    End of modified PiAutoStage script.

    The original version of R. Alex Steiner and Tyrone.O. Rooney
    Publications DOI: https://doi.org/10.1029/2021GC009693
    """
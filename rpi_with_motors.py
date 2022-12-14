#!/usr/bin/env python
import sys

sys.path.append('/usr/lib/python3/dist-packages')
import time
# import RPi.GPIO as GPIO
import picamera
import datetime
import os
import subprocess
os.chdir('/home/camera/Pictures/')
# from smbus2 import SMBus, i2c_msg
import serial
from PyQt5.QtWidgets import (QApplication, QDialog, QMainWindow, QFileDialog, QMessageBox)
from PyQt5.Qt import Qt
from PyQt5.uic import loadUi
from ui import Ui_MainWindow
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


print("STARTING SETUP")

# Serial setup
# ========================
ser = serial.Serial("/dev/ttyS0", 9600)


# Camera setup
# ========================
cam = picamera.PiCamera()
# GPIO.setmode (GPIO.BOARD)
# GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print("CAMERA OK")

# Variable definitions
# =======================
number_of_PIs = 1
number_of_photos = 1
rpi_status = -1  # Master = 0, Slave = 1-7 undefined = -1
network_status = 0  # 0 = not ok; 1 = ok
master_ip = ""

#Zmienne sciezek
move_script_location = "/home/camera/cut_photo.sh"
#Photo_folder_location = "/home/camera/Pictures/"
sciezka = "/home/camera/Pictures/"
time.sleep(1)
print("SETUP FINISHED")


# GUI setup
# =======================

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        global master_ip
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton_3.clicked.connect(self.save_settings)  # save_settings
        self.pushButton_4.clicked.connect(self.setup_connection)  # Conncetion setup
        self.pushButton_2.clicked.connect(self.close_program)  # Close
        self.pushButton.clicked.connect(self.start_program)  # Start
        self.radioButton.clicked.connect(self.radio_master)
        self.radioButton_2.clicked.connect(self.radio_slave)
        try:
            kit = MotorKit(i2c=board.I2C())
            master_ip = str(subprocess.getoutput('hostname -I'))
            master_ip = master_ip[:-1]
            print("MASTER IP: ", master_ip)
        except:
            self.program()

    # Button Start pressed
    def start_program(self):
        global number_of_photos
        global rpi_status
        global network_status
        if network_status == 1 and rpi_status == 0:
            self.label.setText("Starting process...")
            # Taking photos
            for i in range(number_of_photos):
                self.label.setText("Photo " + str(i + 1) + "/" + str(number_of_photos) + "...")
                print("Photo " + str(i + 1) + "/" + str(number_of_photos) + "...")
                msg = 9
                ser.write(msg.to_bytes(1, 'big'))  # 'Take a photo' signal
                time.sleep(1)
                received_data = ser.read()
                received_data_int = int.from_bytes(received_data, 'big')
                if received_data_int == 9:
                    self.take_photo(rpi_status, i + 1)
                    self.rotate_motor()
            self.label.setText("Process Completed")
            # Shutting down network
            print("SENDING MASTER SIGNAL TO SHUTDOWN NETWORK")
            msg = 0
            ser.write(msg.to_bytes(1, 'big'))
            print("WAITING FOR SLAVE SIGNAL")
            time.sleep(1)
            received_data = ser.read()
            received_data_int = int.from_bytes(received_data, 'big')
            if received_data_int == msg:
                print("NETWORK SHUTDOWN COMPLETE")
                self.label.setText("Network Closed")
                network_status = 0
                
                while(True): # Counting files in folder
                    file_count = 0
                    # Iterate directory
                    for path in os.listdir(sciezka):
                        # check if current path is a file
                        if os.path.isfile(os.path.join(sciezka, path)):
                            file_count += 1
                    #print('File count:', file_count)
                    if(file_count >= number_of_photos*number_of_PIs):
                        
                
            else:
                print("NETWORK SHUTDOWN ERROR")
                self.label.setText("Network Error")
                #+++++++++++++++++
                time.sleep(1)
                print("PROCESS COMPLETED")
                self.label.setText("Process Completed")
                #+++++++++++++++++
                
        elif network_status == 0:
            self.label.setText("Set up network first")
        elif rpi_status != 0:
            self.label.setText("To Start select this RPI as Master")

    # Button Close pressed
    def close_program(self):
        self.label.setText("Close pressed")

    # Button Save pressed
    def save_settings(self):
        global number_of_PIs
        global number_of_photos
        # global os.chdir
        number_of_photos = int(self.comboBox.currentText())
        number_of_PIs = int(self.lineEdit.text())
        os.chdir = self.lineEdit_2.text()
        self.label.setText("Settings Saved")

    # Button Set up pressed
    def setup_connection(self):
        global network_status
        global number_of_PIs
        global rpi_status
        global my_ip
        if rpi_status == 0:  # need to set up network
            print("SENDING MASTER SIGNAL TO SETUP NETWORK")
            msg = 1
            ser.write(msg.to_bytes(1, 'big'))
            print("WAITING FOR SLAVE SIGNAL")
            time.sleep(1)
            print("SLEPT")
            received_data = ser.read()
            print("RECEIVED DATA")
            received_data_int = int.from_bytes(received_data, 'big')
            print("CONVERTED DATA")
            if received_data_int == number_of_PIs:
                print("NETWORK SETUP COMPLETE")
                self.label.setText("Network Ok")
                network_status = 1
            else:
                print("NETWORK SETUP FAILED")
                self.label.setText("Network Fail")
                
            #Wysylanie ip szeregowo
            master_ip_tab = master_ip.split('.')
            #zawartosc = master_ip_tab[-1]
            #zawartosc = zawartosc[:-1]
            #master_ip_tab[-1] = zawartosc
            for element in master_ip_tab:
                msg = int(element)
                ser.write(msg.to_bytes(1, 'big'))
            print("SENDING IP ADDRESS")
            time.sleep(1)
            string_received = ""
            for element in range(4):
                received_data = ser.read()
                received_data_int = int.from_bytes(received_data, 'big')
                received_data_str = str(received_data_int)
                string_received = string_received + received_data_str
                if element < 3:
                    string_received = string_received + "."
            if string_received == master_ip:
                print("Received IP OK ")
            else:
                print("Received IP error") 
        else:
            print("ONLY MASTER CAN SETUP")
            self.label.setText("Only Master can Setup")

    # Radio Master selected
    def radio_master(self):
        global rpi_status
        self.label.setText("RPI set as Master")
        rpi_status = 0

    # Radio Slave selected
    def radio_slave(self):
        global rpi_status
        self.label.setText("RPI set as Slave")
        rpi_status = -1

    def program(self):
        print("STARTING PROGRAM")
        global network_status
        global rpi_status
        global master_ip
        ktore_zdjecie = 0
        while True:
            print("")
            # Assigning rpi_status
            if (network_status == 0 and rpi_status == -1):  # Network not setup and RPI Status undefined
                print("WAITING FOR MASTER SIGNAL")
                received_data = ser.read()
                received_data_int = int.from_bytes(received_data, 'big')
                if received_data_int >= 1 and received_data_int < 9:  # 0 = networkoff; 9 = take photo ; 1~9 = pass on incremented signal
                    rpi_status = received_data_int  # RPI Slave number was received
                    #self.change_hostname("SLAVE" + str(rpi_status))
                    network_status = 2 #need to get ip
                    msg = rpi_status + 1
                    ser.write(msg.to_bytes(1, 'big'))
                    print("FORWARDING MASTER SIGNAL")
            #Saving and forwarding master ip
            if network_status ==2:
                
                print("WAITING FOR MASTER IP")
                #received_data = ser.read()
                #received_data_str = str.from_bytes(received_data, 'big')
                #master_ip = received_data_str
                #print("MASTER IP: ", master_ip)
                string_received = ""
                for i in range(4):                
                    received_data = ser.read()
                    ser.write(received_data)    
                    received_data_int = int.from_bytes(received_data, 'big')
                    received_data_str = str(received_data_int)
                    string_received = string_received + received_data_str
                    if i < 3:
                        string_received = string_received + "."
                master_ip = string_received
                print("FORWARDED IP ADDRESS")            
                network_status = 1 #ready for 'take photo' signal
                
            # Taking photos and shutting down network            
            if network_status == 1 and rpi_status >= 1:  # Network setup and RPI Slave
                received_data = ser.read()
                received_data_int = int.from_bytes(received_data, 'big')
                if received_data_int == 9:  # Revieved signal to take photo
                    print("RECEIVED SIGNAL TO TAKE PHOTO")
                    print("FORWARDING SINGAL")
                    ser.write(received_data_int.to_bytes(1, 'big'))
                    print("TAKING PHOTO")
                    ktore_zdjecie += 1
                    self.take_photo(rpi_status, ktore_zdjecie)
                if received_data_int == 0:  # Recieved signal to shut down network
                    print("RECEIVED SIGNAL TO SHUT DOWN NETWORK")
                    print("FORWARDING SINGAL")
                    ser.write(received_data_int.to_bytes(1, 'big'))
                    print("SHUTTING DOWN NETWORK")
                    network_status = 0
                    ktore_zdjecie = 0
                    rpi_status = -1
            else:  # RPI as Master
                print("")
            time.sleep(0.5)

    def take_photo(self, rpi_status, which_photo):
        filename = datetime.datetime.now().strftime(
            "%Y-%m-%d-%H.%M.%S" + "_" + str(rpi_status) + "_" + str(which_photo) + ".jpg")
        cam.start_preview()
        cam.capture(filename)
        print("CAPTURED %s" % filename)
        cam.stop_preview()

    # To do
    def rotate_motor(self):
        #++++++++++++++
        kit = MotoKit(i2c=board.I2C())
        #++++++++++++++
        global number_of_photos
        # 200 steps /360 degrees for NEMA 17 JK42HS40-0504 stepper motor
        single_step = 1.8  # degrees
        degrees_per_photo = 360 / number_of_photos
        steps_per_photo = degrees_per_photo / single_step
        for i in range(int(steps_per_photo)):
            kit.stepper1.onestep(style=stepper.DOUBLE)
        print("MOTOR ROTATED")

    # Not used
    def print_label(self, text):
        print(text)
        self.label.setText(str(text))

    # Not used
    def serial_port(self, value):
        value = 0
        ser.write(value.to_bytes(1, 'big'))
        received_data = ser.read()
        received_data_int = int.from_bytes(received_data, 'big')
        print("ARDUINO BUTTON: " + str(received_data_int))  # str(received_data))#str(received_data, 'utf-8'))
        print(received_data_int)
        return received_data_int

    def move_photos(self, source):
        if source[-1] != "/":
            source = source + "/"
        os.system("sh " + move_script_location + " " + source)

    def change_hostname(self, new_hostname):
        os.system("sudo hostnamectl set-hostname " + new_hostname)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

# Koniec programu
# ==================================================

# Syf
# =================
# import spidev

## SPI setup
##=======================
## We only have SPI bus 0 available to us on the Pi
# bus = 0

##Device is the chip select pin. Set to 0 or 1, depending on the connections
# device = 1

## Enable SPI
# spi = spidev.SpiDev()

## Open a connection to a specific bus and device (chip select pin)
# spi.open(bus, device)

## Set SPI speed and mode
# spi.mode = 0
# spi.max_speed_hz = 500000

# wyslane_dane = [1, 2, 3]

# odczytane_dane = spi.xfer(wyslane_dane)
# print (odczytane_dane)
# if odczytane_dane[0] == 1:


##I2C setup
##========================
# channel = 1 # Pin3 = SDA, Pin5 = SCL
# data = 00
# address = 0x08
# i2c_bus = SMBus(channel) #tworze obiekt magistrali
# print ("I2C OK")


# def writeNumber(value):
#    i2c_bus.write_byte(address, value)
#    return-1

# def readNumber():
#    number = i2c_bus.read_byte(address, 1)
#    return number

# def powiadom_slavea(value):
#   writeNumber(value)
#    print ("INFORMED ARDUINO SLAVE")
#   echo_signal = readNumber()
#   if echo_signal == 1:
#       print ("ARDUINO BUTTON PRESSED")
#        return 1
#    else:
#        print ("ARDUINO BUTTON NOT PRESSED")
#        return 0

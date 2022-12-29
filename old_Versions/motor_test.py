import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import picamera

def rotate_motor():
        #++++++++++++++
        kit = MotorKit(i2c=board.I2C())
        #++++++++++++++
        number_of_photos = 1
        #1600 steps = 360dgr dla stolu
        # 200 steps /360 degrees for NEMA 17 JK42HS40-0504 stepper motor
        n_zebow_silnika = 20
        n_zebow_stolu = 160
        przelozenie = n_zebow_stolu/n_zebow_silnika
        single_step = 1.8  # degrees
        degrees_per_photo = przelozenie * 360 / number_of_photos
        steps_per_photo = degrees_per_photo / single_step
        for i in range(int(steps_per_photo)):
            kit.stepper1.onestep(style=stepper.DOUBLE)
        print("MOTOR ROTATED")
        
def take_photo():
    cam = picamera.PiCamera()
    cam.start_preview()
    #os.system("scrot -u filename")
    sleep(5)
    cam.stop_preview()

rotate_motor()
#take_photo()
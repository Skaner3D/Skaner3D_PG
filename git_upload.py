import os 
import argparse

parser = argparse.ArgumentParser(description="update scanner repo on every camera device.")
parser.add_argument('--foreward',action='store_true')
parser.add_argument('-v', action='store_true')
args = parser.parse_args()
haslo = "haslo123"
update_exe = "python git_update.py"

if args.foreward==True:
    for num in range(8):
        try:
            os.system("sshpass -p "+haslo+" ssh camera@camera"+str(num)+".local "+update_exe)
        except:
            if args.v==True:
                print("WARNING: Problem occured with camera number "+str(num) )
    exit()



os.chdir("/home/camera/Skaner/")
os.system("git pull origin master")

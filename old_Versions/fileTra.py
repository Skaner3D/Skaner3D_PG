import os



master_ip = "192.168.17.234"
path_master = "/home/projekt1/Desktop/Pliki/PB/Zdjecia"
sciezka = "/home/camera/Pictures/"
haslo = "haslo123"
pliki_str = ""

for path in os.listdir(sciezka):
    filename = os.path.join(sciezka,path)
    
    if os.path.isfile(filename):
        pliki_str = pliki_str + filename +" "
print(pliki_str )
os.system("sshpass -p "+haslo+" scp "+pliki_str+"projekt1@"+master_ip+":"+path_master)
#os.system("sshpass -p -o StrictHostKeyChecking=no "+haslo+" scp "+pliki_str+"projekt1@"+master_ip+":"+path_master)
#os.system("rm -f "+sciezka+"*")

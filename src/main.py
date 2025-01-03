from src.models.hospital import Hospital
import threading
import time


## Registration Tread
def register_tread(url: str, hospital:Hospital):
    while True:
        flag = hospital.register(url+"/register")
        if flag:
            print('Resgisterd with Success')
            break
        else:
            print('Registration Faild, Trying again in 15 seconds')
            time.sleep(15)
            
def update_snapshot_tread(url, hospital:Hospital):
    while True:
        if(hospital.entity_id):
            try:
                hospital.take_snapshot(url + f"/snapshot/{hospital.entity_id}")
            except Exception:
                pass
        time.sleep(10)
            
url = 'http://localhost:8000/api'
h = Hospital('test', 15)

# Starting the Register Tread
registerTread = threading.Thread(target=register_tread, args=(url, h))
registerTread.start()

# Starting the Register Tread
snapShotTread = threading.Thread(target=update_snapshot_tread, args=(url, h))
snapShotTread.start()

# Main thread can continue doing other things

while True:
    h.admit_patient(url + "accept-person")
    time.sleep(5)

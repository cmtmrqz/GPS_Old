import bluetooth
from threading import Thread
from Queue import Queue
from clases import *

def readTemps(bd_addr, port, tempsInfo, camioncito):
    sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
    connected = connect(sock,bd_addr,port)
    
    while connected:
        print("Ok")
        try:
            data = ""
            lock = False
            while 1:
                try:
                    data += sock.recv(1024)
                    data_end = data.find('\n')
                    if data_end != -1:
                        rec = data[:data_end+1]
                        rec =  rec.replace('*', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        rec = rec.replace('Camioncito',str(camioncito))
                        if len(re.findall(r'Host',rec))==0 and len(re.findall(r'NAN',rec))==0:
                            tempsInfo.put(rec.split('\n')[0])
                        data = data[data_end+1:]
                except KeyboardInterrupt:
                    sock.close()
                    break
            sock.close()
            
        except Exception as e:
            print (e)
            print("Not ok")
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
            print ("Reconnecting...")
            connected = connect(sock, bd_addr, port)

def connect(sock, bd_addr, port):
    lock = False
    while not(lock):
        try:
            sock.connect((bd_addr,port))
            print ("Connected")
            return True
        except Exception as e:
            sock.close()
            time.sleep(2)
            sock = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
            
def Main():
    tempsInfo = Queue()
    port = 1
    
    try:
        from camion import camioncito
    except:
        camioncito = "13"
        
    try:
            from macAddress import bd_addr
    except:
            bd_addr = "98:D3:31:FB:1A:D6" #//The address from the HC-05 sensor

    print(bd_addr)
    #thread1 = Thread(target=readTemps)
    #thread1.setDaemon(True)
    #thread1.start()

    readTemps(bd_addr, port, tempsInfo, camioncito)
    
Main()
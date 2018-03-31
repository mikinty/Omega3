import serial
from random import randint
import time

ard = serial.Serial('COM11', 9600, timeout=0)

def generateMatrix():
    m = []
    for i in range(8):
        l = []
        for j in range(8):
            x = randint(0,1)
            l.append(x)
        m.append(l)
    return m

def sendMatrix(m):
    ard.write(b's')
    for i in m:
        for j in i:
            ard.write(str(j).encode())

while(True):
    m = generateMatrix()
    print('Printing:')
    print(m)
    sendMatrix(m)
    time.sleep(1)
    print(ard.read(1000))
    time.sleep(1)
            

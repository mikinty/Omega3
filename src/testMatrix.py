'''
Simple demonstration of sending matrix information to an arduino
'''

import serial
from random import randint
import time
import serial.tools.list_ports

# detect and begin serial commuincation with first Arduino
ports = list(serial.tools.list_ports.comports())

arduinos = [p[0] for p in ports if p[0].startswith('/dev/ttyACM')]
ard = serial.Serial(arduinos[0], timeout=0)

def generateMatrix():
    '''
    Creates a randomly generated 8x8 bit matrix
    '''
    m = []
    for i in range(8):
        l = []
        for j in range(8):
            x = randint(0,1)
            l.append(x)
        m.append(l)
    return m

def sendMatrix(m):
    '''
    Sends a 8x8 bit matrix to the detected Arduino
    '''
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
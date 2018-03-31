import serial

ard = serial.Serial('/dev/ttyACM4', 9600)

while(True):
	ard.write(b'1')
	pause(1)
	ard.write(b'2')
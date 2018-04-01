/*
 * The following program is an LED matrix listener to serial port in order to display
 * neural network data. Each arduino controls one hidden layer.
 */
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

Adafruit_8x8matrix h1 = Adafruit_8x8matrix();
Adafruit_8x8matrix h2 = Adafruit_8x8matrix();
Adafruit_8x8matrix h3 = Adafruit_8x8matrix();

// Keep track of where we're writing on the matrix
uint16_t curX = 0;
uint16_t curY = 0;

int numAddr = 3;
int adrLength = 3;
int adrTotal = 9; // numAddr * adrLength
int adrPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
int addresses[9]; // store the addresses
int currMatrix = 1;
// int dAdr[3]; // digital version of address

// finds the address indicated by startPin - (startPin + 2)
int findAddr(int startPin) {
  int currAdr = 0;
  for (int i = 0; i < adrLength; i++) {
    if (digitalRead(startPin + i) == HIGH) {
      addresses[startPin + i] = 1;
      currAdr += 1 << i;
    }  else {
      addresses[startPin + i] = 0;
    }
  }
  
  // dAdr[startPin/3] = currAdr;
  return currAdr;
}


void setup() {
  /*** DIGITAL PINS ***/
  // set up digital pins to read the address
  for (int i = 0; i < adrTotal; i++) {
    pinMode(adrPins[i], INPUT);
  }
  
  /*** SERIAL PORT ***/
  // baudrate of 9600
  Serial.begin(9600);
  
  // do not wait for Serial communication
  Serial.setTimeout(0);
  
  delay(500);
  
  /*** Assign matrices ***/
  // read the addresses
  Serial.println("Detecting LED matrices...");
  
  int adr1 = findAddr(2);
  int adr2 = findAddr(5);
  int adr3 = findAddr(8);
  Serial.print("Addresses: ");
  Serial.print(adr1);
  Serial.print(" ");
  Serial.print(adr2);
  Serial.print(" ");
  Serial.println(adr3);
  
  // turn on the matrix according to the address given
  switch(adr1) {
    case 1:
      h1.begin(0x71);
      break;
    case 2:
      h1.begin(0x72);
      break;
    case 3:
      h1.begin(0x73);
      break;
    case 4:
      h1.begin(0x74);
      break;
    case 5:
      h1.begin(0x75);
      break;
    case 6:
      h1.begin(0x76);
      break;
  }
  
  switch(adr2) {
    case 1:
      h2.begin(0x71);
      break;
    case 2:
      h2.begin(0x72);
      break;
    case 3:
      h2.begin(0x73);
      break;
    case 4:
      h2.begin(0x74);
      break;
    case 5:
      h2.begin(0x75);
      break;
    case 6:
      h2.begin(0x76);
      break;
  }
  
  switch(adr3) {
    case 1:
      h3.begin(0x71);
      break;
    case 2:
      h3.begin(0x72);
      break;
    case 3:
      h3.begin(0x73);
      break;
    case 4:
      h3.begin(0x74);
      break;
    case 5:
      h3.begin(0x75);
      break;
    case 6:
      h3.begin(0x76);
      break;
  }
}

void loop() {
  if(Serial.available()) {
    // read input from serial
    int in = Serial.read();
    
    // start signal for printing a matrix
    if(in == 's') {
      // reset values
      curX = 0;
      curY = 0;
    } else if (in == '0') { // display values on matrix
      curX++;
    } else if (in == '1') {
      switch(currMatrix) {
        case 1:
          h1.drawPixel(curX,curY, LED_ON);
          h1.writeDisplay();
          break;
        case 2:
          h2.drawPixel(curX,curY, LED_ON);
          h2.writeDisplay();
          break;
        case 3:
          h3.drawPixel(curX,curY, LED_ON);
          h3.writeDisplay();
          break;
      }
      
      curX++; // increment for next spot
    } else if (in == '2') { // choose another matrix to control
      h1.clear();
      h1.writeDisplay();
      currMatrix = 1;
    } else if (in == '3') {
      h2.clear();
      h2.writeDisplay();
      currMatrix = 2;
    } else if (in == '4') {
      h3.clear();
      h3.writeDisplay();
      currMatrix = 3;
    }
    
    // wrap around the matrix rows
    if (curX >= 8) {
      curX=0;
      curY++;
    }
  }
}

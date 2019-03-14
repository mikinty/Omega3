/*
 * The following program is an LED matrix listener to serial port in order to display
 * neural network data. The program is designed for an Arduino Mega that controls
 * all 6 LED matrices in both hidden layers
 */
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

#define NUM_MATRIX 6
#define ADR_LENGTH 3
#define NUM_FUNCS  7

// for '2', '3', ... representing matrixNum 0, 1, ...
#define MATRIX_NUM_SEL_OFFSET 50
#define MATRIX_ADR_OFFSET 0x70

// initialize matrix objects
Adafruit_8x8matrix MATRICES[6] = {
  Adafruit_8x8matrix(),
  Adafruit_8x8matrix(),
  Adafruit_8x8matrix(),
  Adafruit_8x8matrix(),
  Adafruit_8x8matrix(),
  Adafruit_8x8matrix()
};

// Keep track of where we're writing on the matrix
uint16_t curX = 0;
uint16_t curY = 0;

// Defines where each LED matrix is addressed to
const int adrPins[6][3] = {
  {22, 24, 26}, 
  {28, 30, 32}, 
  {34, 36, 38},
  {40, 42, 44},
  {46, 48, 50},
  {51, 52, 53}
};

// store the addresses
int addresses[6][3];

// TODO: FILL THESE OUT
// Inputs from the function blocks
const int funcPins[7] = { 23, 25, 27, 29, 31, 33, 35 }; 

int currMatrix = 0;

/**
 * Finds the address indicated by pins adrPins[matrixNum][0, 1, 2]
 * 
 * Also stores the detected address in addresses[6][3]
 */
int findAddr(int matrixNum) {
  int currAdr = 0;
  
  for (int i = 0; i < ADR_LENGTH; i++) {
    if (digitalRead(adrPins[matrixNum][i]) == HIGH) {
      addresses[matrixNum][i] = 1;
      currAdr += 1 << i;
    }  else {
      addresses[matrixNum][i] = 0;
    }
  }
  
  return currAdr;
}

/**
 * Tells the Raspberry Pi which function pins are activated
 */
void readFuncPins() {
  Serial.print('f');
  
  for (int i = 0; i < NUM_FUNCS; i++) {
    if (digitalRead(funcPins[i]) == HIGH) {
      Serial.print(1);
    } else {
      Serial.print(0);
    }
  }
}

// Initializes a matrix object
void initMatrix(int matrixNum, int address) {
  switch (matrixNum) {
    case 1:
      MATRICES[matrixNum].begin(address);
      break;
    case 2:
      MATRICES[matrixNum].begin(address);
      break;
    case 3:
      MATRICES[matrixNum].begin(address);
      break;
    case 4:
      MATRICES[matrixNum].begin(address);
      break;
    case 5:
      MATRICES[matrixNum].begin(address);
      break;
    case 6:
      MATRICES[matrixNum].begin(address);
      break;
    default:
      MATRICES[matrixNum].begin(address);
  }
}

void setup() {
  /*** DIGITAL PIN INPUTS ***/
  for (int i = 0; i < NUM_MATRIX; i++) {
    for (int j = 0; j < ADR_LENGTH; j++) {
      pinMode(adrPins[i][j], INPUT);  
    }
  }

  for (int i = 0; i < NUM_FUNCS; i++) {
    pinMode(funcPins[i], INPUT);
  }

  /*** SERIAL PORT ***/
  Serial.begin(9600);
  
  // don't wait for serial comm., allows for faster matrix update
  Serial.setTimeout(0);
  
  /*** I2C SETUP WITH LED MATRICES ***/
  Serial.println("Detecting LED matrices...");

  // Initialize matrices according to detected addresses 
  for (int i = 0; i < NUM_MATRIX; i++) {
    int addr = findAddr(i);
    initMatrix(i, addr + MATRIX_ADR_OFFSET);

    // TODO: the rpi should pick up this info to build the architecture
    Serial.println(addr);
  }

  // Tell the RPi what function blocks are present
  readFuncPins();
}


/** 
 * Main Program
 * 
 * Here, the Arduino listens to display commands from the RPi.
 * 
 * Note that we assume that the user never moves blocks during a 
 * single run, because otherwise, we would have to redetect matrices
 * before each update. However, this is a reasonable assumption to make,
 * because practically, there is no reason you should be changing 
 * your NN architecture in the middle of training.
 */
void loop() {
  if(Serial.available()) {
    // read input from serial
    int in = Serial.read();
    
    /*** Interpret serial communication ***/
    
    /** Start signal for printing a matrix **/
    if (in == 's') {
      // reset values
      curX = 0;
      curY = 0;
    } 
    /** Writing values on the matrix **/
    else if (in == '0') { // display values on matrix
      curX++;
    } else if (in == '1') {
      MATRICES[currMatrix].drawPixel(curX, curY, LED_ON);
      
      curX++; // increment for next spot
    } 
    /** Choose another matrix to control **/
    else {
      currMatrix = in - MATRIX_NUM_SEL_OFFSET;
      MATRICES[currMatrix].clear();
    }
    
    // wrap around the matrix rows
    if (curX >= 8) {
      curX = 0;
      curY++;
    }

    // display matrices
    for (int i = 0; i < NUM_MATRIX; i++) {
      MATRICES[i].writeDisplay();
    }
  }
}

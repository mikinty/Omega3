/** 
 * Minimal working example of testing a connection with LED matrix 
 * via I2C connection. This code is primarily used to test that constructed
 * neuron blocks work.
 */
#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

/**
 * Since we have a maximum of 6 matrices, we only need a 3-bit address.
 * The address pins are detected by inputs on the Arduino. In the code 
 * below, the adrPins[] define which pins are used to read the address.
 */
int adrLength = 3;
int adrPins[] = {5, 6, 7};
int adr[3];

void setup() {
  Serial.begin(9600);
  Serial.println("8x8 LED Matrix Test");

  // read the address inputs
  for (int i = 0; i < adrLength; i++) {
    pinMode(adrPins[i], INPUT); 
  }
  
  // change this line below to the matrix address that was detected.
  matrix.begin(0x71);
}

// preset test images
static const uint8_t PROGMEM
  smile_bmp[] = { 
    B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10100101,
    B10011001,
    B01000010,
    B00111100 
  },

  neutral_bmp[] = { 
    B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10111101,
    B10000001,
    B01000010,
    B00111100 
  },

  frown_bmp[] = { 
    B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10011001,
    B10100101,
    B01000010,
    B00111100 
  };

void loop() {
  // detect the hard-coded address for the LED matrix.
  int currAdr = 0;
  Serial.print("Detected Address: ");
  for (int i = 0; i < adrLength; i++) {
    if (digitalRead(adrPins[i]) == HIGH) {
      adr[i] = 1;
      currAdr += 1 << i;
    } else {
      adr[i] = 0;
    }
  }

  Serial.print(currAdr);
  Serial.print(" (");
  Serial.print(adr[2]);
  Serial.print(adr[1]);
  Serial.print(adr[0]);
  Serial.println(")");
  
  // display preset images on LED matrix
  matrix.clear();
  matrix.drawBitmap(0, 0, smile_bmp, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(500);

  matrix.clear();
  matrix.drawBitmap(0, 0, neutral_bmp, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(500);

  matrix.clear();
  matrix.drawBitmap(0, 0, frown_bmp, 8, 8, LED_ON);
  matrix.writeDisplay();
  delay(500);
}

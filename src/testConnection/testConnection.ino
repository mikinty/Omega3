/*************************************************** 
  Minimal working example of testing a connection with LED matrix 
  via I2C connection. License for the library included below:
  
  This is a library for our I2C LED Backpacks

  Designed specifically to work with the Adafruit LED Matrix backpacks 
  ----> http://www.adafruit.com/products/872
  ----> http://www.adafruit.com/products/871
  ----> http://www.adafruit.com/products/870

  These displays use I2C to communicate, 2 pins are required to 
  interface. There are multiple selectable I2C addresses. For backpacks
  with 2 Address Select pins: 0x70, 0x71, 0x72 or 0x73. For backpacks
  with 3 Address Select pins: 0x70 thru 0x77

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();

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
  
  matrix.begin(0x71);
}

static const uint8_t PROGMEM
  smile_bmp[] =
  { B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10100101,
    B10011001,
    B01000010,
    B00111100 },
  neutral_bmp[] =
  { B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10111101,
    B10000001,
    B01000010,
    B00111100 },
  frown_bmp[] =
  { B00111100,
    B01000010,
    B10100101,
    B10000001,
    B10011001,
    B10100101,
    B01000010,
    B00111100 };

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

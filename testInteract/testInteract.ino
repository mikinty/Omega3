#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"


Adafruit_8x8matrix matrix = Adafruit_8x8matrix();


void setup() {
  Serial.begin(9600);
  Serial.println("test interact");

  matrix.begin(0x70);

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
  if(Serial.available() > 0) {
    int in = Serial.read();
    if(in==1) {
      matrix.clear();
      matrix.drawBitmap(0,0, smile_bmp, 8, 8, LED_ON);
      matrix.writeDisplay();
    }
    if(in==2) {
      matrix.clear();
      matrix.drawBitmap(0,0, frown_bmp, 8, 8, LED_ON);
      matrix.writeDisplay();
    }
  }
  delay(10);

}

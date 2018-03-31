#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include "Adafruit_LEDBackpack.h"

Adafruit_8x8matrix matrix = Adafruit_8x8matrix();
uint16_t curX=0;
uint16_t curY=0;

void setup() {
  Serial.begin(9600);
  // Serial.println("initializing\n");

  matrix.begin(0x71);
  matrix.clear();
  matrix.writeDisplay();
}

void loop() {
  if(Serial.available()) {
    int in = Serial.read();
    
    if(in=='s') {
      curX=0;
      curY=0;
      matrix.clear();
      matrix.writeDisplay();
    }
    Serial.print(in);
    if(in=='0') {
      curX++;
    }
    
    if(in=='1') {
      matrix.drawPixel(curX,curY, LED_ON);
      matrix.writeDisplay();
      curX++;
    }
    
    if(curX==8) {
      curX=0;
      curY++;
    }
  }
}

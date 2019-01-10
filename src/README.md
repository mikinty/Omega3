# Omega<sup>3</sup> Source Code

This directory contains the source code used to implement Omega<sup>3</sup>. 
Here, we have files that test and implement the Raspberry Pi to Arduino communication interface.
The idea is that we have a Raspberry Pi that runs the neural network training code, and then sends data to the Arduino, which then displays the information on the LED matrix peripherals.

## Hardware

- Raspberry Pi 3 Model B
- Arduino Mega R2560 (can also be implemented with two Arduino UNOs)
- 8x8 LED Matrix HT16K33

## Directory Structure

- __Raspberry Pi__
  - `neuralnet.py`: the Raspberry Pi code that implements the neural network. The program takes in user input, communicates to the Arduino to display information on the LED matrices, and also plots input/output data in live-time.
  - `targetFuncs.py`: library that contains test functions to train the neural network on.
- __Arduino__
  - `testConnection`: a minimal implementation of detecting LED backpacks via hard-wired I2C addressing and displaying static information.
  - `testMatrix`: interface between the Raspberry Pi and the LED matrices. Essentially translates Rasberry Pi neural network data into images to be shown on the LED matrices.
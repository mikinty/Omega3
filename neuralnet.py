from __future__ import print_function
import random
import math
import time
import serial
import serial.tools.list_ports

# target functions
import targetFuncs

# pybrain imports
from pybrain.structure import FeedForwardNetwork
from pybrain.tools.shortcuts import buildNetwork  # network
from pybrain.datasets import SupervisedDataSet  # dataset
from pybrain.supervised.trainers import BackpropTrainer # training alg
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection

# plotting library
import numpy as np
import matplotlib.pyplot as plt

# hook up arduino to serial port
ports = list(serial.tools.list_ports.comports())

hidden2Serial = '55333303934351915152'
hidden1Serial = '855393139313517121F1'

print(ports)
arduinoS1 = [p[0] for p in ports if (hidden1Serial in p[2])]
arduinoS2 = [p[0] for p in ports if (hidden2Serial in p[2])]

# print(arduinoS1, arduinoS2)

ard1 = serial.Serial(arduinoS1[0], timeout=0)
ard2 = serial.Serial(arduinoS2[0], timeout=0)

# Type of NN we are using
net = FeedForwardNetwork()
netOne = FeedForwardNetwork()

# parameters
numEpochs = 300
learningRate = 10
numFeatures = 7
numTrain = 100
numHiddenUnits1 = 3
numHiddenUnits2 = 3
(xMin, xMax, yMin, yMax) = (-4, 4, -4, 4) # dim. of LED matrix
displayRate = 0.2 # period of display time

def sigmoid(x):
  return 1 / (1 + math.exp(-x))


# function for sending data to matrix
def sendMatrix(m, layer, matrixNum):
   arduino = ard1 # default

   # choose the arduino based on layer
   if layer == 2:
      arduino = ard2

   arduino.write(b's') # signal start

   arduino.write(str(matrixNum).encode()) # indicate which neuron

   # send over data for matrix display
   for i in m:
      for j in i:
         arduino.write(str(j).encode())


# print out NN weights
def pesos_conexiones(n):
   paramArr = {}
   for mod in n.modules:
      for conn in n.connections[mod]:
         temp = []
         # print(conn)
         for cc in range(len(conn.params)):
            # print(conn.whichBuffers(cc), conn.params[cc])
            temp.append(conn.params[cc])

         if len(temp) == 21:
            paramArr['h1'] = temp
         elif len(temp) == 9:
            paramArr['h2'] = temp

   return paramArr


# generate data for the model to train on
def generateData(N, funNumber):
   inputArr = []
   outputArr = []

   # create our input data
   for x in range(N):
      # generate random values
      xVal = random.uniform(xMin, xMax)
      yVal = random.uniform(yMin, yMax)

      # NN input data with features
      inputArr.append([xVal, yVal, xVal*xVal, yVal*yVal, xVal*yVal, math.sin(xVal), math.sin(yVal)])

      # Choose function
      lib = {
        0: targetFuncs.yGeZero,
        1: targetFuncs.xGeZero,
        2: targetFuncs.checkerboard,
        3: targetFuncs.circle,
        4: targetFuncs.diag,
        5: targetFuncs.chess,
        6: targetFuncs.corners,
        7: targetFuncs.kite
      }

      # Labels for input data
      # if targetFuncs.checkerboard(xVal, yVal):
      if (lib[funNumber])(xVal, yVal):
         outputArr.append([1])
      else:
         outputArr.append([0])

   print('Output DATA')
   print(outputArr)

   return inputArr, outputArr, lib[funNumber]


def setupNN(inputArr, outputArr, numFeatures, nodesH1, nodesH2):
   # Globals
   global in_to_hidden
   global hidden_to_hidden2
   global hidden2_to_out

   # Create NN layers. Numbers indicate dimension = number of nodes in layer
   inLayer = LinearLayer(numFeatures)
   hiddenLayer = SigmoidLayer(nodesH1)
   hiddenLayer2 = SigmoidLayer(nodesH2)
   outLayer = LinearLayer(1)

   # Add NN components
   net.addInputModule(inLayer)
   net.addModule(hiddenLayer)
   net.addModule(hiddenLayer2)
   net.addOutputModule(outLayer)

   # Make neural network connections
   in_to_hidden = FullConnection(inLayer, hiddenLayer)
   hidden_to_hidden2 = FullConnection(hiddenLayer, hiddenLayer2)
   hidden2_to_out = FullConnection(hiddenLayer2, outLayer)


   net.addConnection(in_to_hidden)
   net.addConnection(hidden_to_hidden2) # lazy full connection
   net.addConnection(hidden2_to_out)

   # Chris: don't delete this
   net.sorted = False
   net.sortModules() # random command to make this work

   # add dataset to the NN
   ds = SupervisedDataSet(7,1)

   for i,j in zip(inputArr, outputArr):
      ds.addSample(tuple(i),(tuple(j)))

   # training algorithm
   m1 = BackpropTrainer(net, ds)

   return m1


def trainNN(model, numEpochs):
   for epoch in range(numEpochs):
      # Give time for the LED Matrix to show things
      print('epoch', epoch)
      time.sleep(displayRate)
      params = pesos_conexiones(net)
      # print(params)

      # TRAIN NN and report error
      model.trainEpochs(learningRate)
      print('Model train error:', model.train()) #error

      # parse params
      h1Params = params['h1']
      inToH1 = h1Params[0:7]
      inToH2 = h1Params[7:14]
      inToH3 = h1Params[14:]

      h2Params = params['h2']
      hToH1 = h2Params[0:3]
      hToH2 = h2Params[3:6]
      hToH3 = h2Params[6:]

      # for plotting
      xRefPos = []
      xRefNeg = []
      yRefPos = []
      yRefNeg = []

      ### Print to LED Matrix ###
      # print('Output Layer:')
      outputMatrix = []
      hOne1 = []
      hOne2 = []
      hOne3 = []

      hTwo1 = []
      hTwo2 = []
      hTwo3 = []

      # Compute the node values
      for x in range(-4, 4):
         outputList = []
         hO1 = []
         hO2 = []
         hO3 = []

         hT1 = []
         hT2 = []
         hT3 = []

         for y in range(-4, 4):
            inArr = [x,y, x*x, y*y, x*y, math.sin(x), math.sin(y)]

            # predict with NN
            compute = net.activate(inArr)

            ## compute hidden layers ##
            bias = 0

            # hidden layer 1
            temp1 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(inArr, inToH1)) + bias) >= 0.5)
            temp2 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(inArr, inToH2)) + bias) >= 0.5)
            temp3 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(inArr, inToH3)) + bias) >= 0.5)

            hO1.append(temp1)
            hO2.append(temp2)
            hO3.append(temp3)

            hLayer1 = [temp1, temp2, temp3]

            # hidden layer 2
            temp21 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(hLayer1, hToH1)) + bias) >= 0.5)
            temp22 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(hLayer1, hToH2)) + bias) >= 0.5)
            temp23 = 0 + (sigmoid(sum(i[0]*i[1] for i in zip(hLayer1, hToH3)) + bias) >= 0.5)


            hT1.append(temp21)
            hT2.append(temp22)
            hT3.append(temp23)

            if compute >= 0.5:
               # print("1", end='')
               outputList.append(1)
               xRefPos.append(x)
               yRefPos.append(y)
            else:
               # print("0", end='')
               outputList.append(0)
               xRefNeg.append(x)
               yRefNeg.append(y)

         outputMatrix.append(outputList)
         hOne1.append(hO1)
         hOne2.append(hO2)
         hOne3.append(hO3)
         hTwo1.append(hT1)
         hTwo2.append(hT2)
         hTwo3.append(hT3)

         #print()

      #print()

      # plot output prediction
      ax2.cla()
      ax2.plot(xRefPos, yRefPos, 'g+', xRefNeg, yRefNeg, 'ro', markersize=20)
      plt.pause(0.1)
      """
      plt.clf()
      plt.plot(xRefPos, yRefPos, 'g+', xRefNeg, yRefNeg, 'ro', markersize=20)
      plt.pause(0.1)
      """

      # display data on LED matrices
      sendMatrix(hOne1, 1, 2)
      sendMatrix(hOne2, 1, 3)
      sendMatrix(hOne3, 1, 4)
      sendMatrix(hTwo1, 2, 2)
      sendMatrix(hTwo2, 2, 3)
      sendMatrix(hTwo3, 2, 4)

      # sendMatrix(outputMatrix, 5)


if __name__ == '__main__':
   functionList = {
        0: 'y >= 0',
        1: 'x >= 0',
        2: 'checkerboard',
        3: 'circle',
        4: 'diagonal',
        5: 'chess',
        6: 'corners',
        7: 'kite'
      }

   print("FUNCTION LIST:")
   for x in range(8):
      print(str(x)+".", functionList[x])

   num = min(int(input("What function would you like to try? ")), 7)

   # creating input data
   inputData, outputData, refFunc = generateData(numTrain, num)

   # set up model
   model = setupNN(inputData, outputData, numFeatures, numHiddenUnits1, numHiddenUnits2)

   # set up plotting
   plt.ion() # interactive plotting

   # Reference solution
   xRefPos = []
   xRefNeg = []
   yRefPos = []
   yRefNeg = []

   # REF FUNCTION
   for x in range(-4, 4):
      for y in range(-4, 4):
         if refFunc(x, y):
            xRefPos.append(x)
            yRefPos.append(y)
            print('+', end='')
         else:
            xRefNeg.append(x)
            yRefNeg.append(y)
            print('-', end='')
      print()

   xrp = []
   yrp = []
   xrn = []
   yrn = []

   for x in range(len(inputData)):
      tempX = int(inputData[x][0])
      tempY = int(inputData[x][1])

      if outputData[x][0] > 0:
         xrp.append(tempX)
         yrp.append(tempY)
      else:
         xrn.append(tempX)
         yrn.append(tempY)


   # reference solution
   global f, ax1, ax2

   f,(ax1, ax3, ax2) = plt.subplots(1, 3)
   ax1.set_xlim([-5, 4])
   ax1.set_ylim([-5, 4])
   ax2.set_xlim([-5, 4])
   ax2.set_ylim([-5, 4])
   ax3.set_xlim([-5, 4])
   ax3.set_ylim([-5, 4])
   ax1.plot(xRefPos, yRefPos, 'g+', xRefNeg, yRefNeg, 'ro', markersize=20)
   ax3.plot(xrp, yrp, 'g+', xrn, yrn, 'ro', markersize=20)

   # train model
   trainNN(model, numEpochs)


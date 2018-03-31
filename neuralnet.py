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

# hook up arduino to serial port
ports = list(serial.tools.list_ports.comports())

arduinos = [p[0] for p in ports if p[0].startswith('/dev/ttyACM')]
print(arduinos)
ard = serial.Serial(arduinos[0], timeout=0)

# Type of NN we are using
net = FeedForwardNetwork()
netOne = FeedForwardNetwork()

# parameters
numEpochs = 300
numFeatures = 7
numTrain = 100
(xMin, xMax, yMin, yMax) = (-4, 4, -4, 4) # dim. of LED matrix
displayRate = 0.5 # period of display time

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

# function for sending data to matrix
def sendMatrix(m):
    ard.write(b's') # signal start
    for i in m:
        for j in i:
            ard.write(str(j).encode())

# print out NN weights
def pesos_conexiones(n):
    paramArr = []
    for mod in n.modules:
        for conn in n.connections[mod]:
            temp = []
            for cc in range(len(conn.params)):
                print(conn.whichBuffers(cc), conn.params[cc])
                temp.append(conn.params[cc])
            paramArr.append(temp)
    return paramArr



def calcInstant(inArr, paramArr, index, index2):
   hidden1 = []
   for x in range(0, 3):
      total = 0
      for y in range(0, numFeatures):
         total = paramArr[numFeatures*x + y]*inArr[y]+total
      hidden1.append(sigmoid(total))
   # print("hidden1:", hidden1)

   hidden2 = []
   for x in range(0,2):
      total = 0
      for y in range(0,3):
         total=paramArr[3*x+y+21]*hidden1[y]+total
      hidden2.append(sigmoid(total))
   # print("hidden2:", hidden2)

   total = 0

   for x in range(0, 2):
      total = total+hidden2[x]*paramArr[27+x]
   if index == 2:
      print("Total:", total)
   elif index > -1:
      if hidden2[index] > 0.5:
         print("1", end='')
      else:
         print("0", end='')
   elif index2 > -1:
      if hidden1[index2] > 0.5:
         print("1", end='')
      else:
         print("0", end ='')

def generateData(N, funNumber):
   inputArr = []
   outputArr = []

   # create our input data
   for x in range(N):
      # generate random values
      xVal = random.uniform(xMin, xMax)
      yVal = random.uniform(yMin, yMax)

      # NN input data
      inputArr.append([xVal, yVal, xVal*xVal, yVal*yVal, xVal*yVal, math.sin(xVal), math.sin(yVal)])

      # Choose function
      lib = {
        0: targetFuncs.yGeZero,
        1: targetFuncs.xGeZero,
        2: targetFuncs.checkerboard,
        3: targetFuncs.circle
      }

      # Labels for input data
      # if targetFuncs.checkerboard(xVal, yVal):
      if (lib[funNumber])(xVal, yVal):
         outputArr.append([1])
      else:
         outputArr.append([0])

   print('Output DATA')
   print(outputArr)

   return inputArr, outputArr


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

   inL1 = LinearLayer(numFeatures)
   hL1 = SigmoidLayer(nodesH1)
   oL1 = LinearLayer(1)

   # Add NN components
   net.addInputModule(inLayer)
   net.addModule(hiddenLayer)
   net.addModule(hiddenLayer2)
   net.addOutputModule(outLayer)

   # Only one hidden layer
   netOne.addInputModule(inL1)
   netOne.addModule(hL1)
   netOne.addOutputModule(oL1)

   # Make neural network connections
   in_to_hidden = FullConnection(inLayer, hiddenLayer)
   hidden_to_hidden2 = FullConnection(hiddenLayer, hiddenLayer2)
   hidden2_to_out = FullConnection(hiddenLayer2, outLayer)

   i2h1 = FullConnection(inL1, hL1)
   h2o1 = FullConnection(hL1, oL1)

   net.addConnection(in_to_hidden)
   net.addConnection(hidden_to_hidden2) # lazy full connection
   net.addConnection(hidden2_to_out)

   netOne.addConnection(i2h1)
   netOne.addConnection(h2o1)

   # Chris: don't delete this
   net.sorted = False
   net.sortModules() # random command to make this work

   netOne.sorted = False
   netOne.sortModules()

   # add dataset to the NN
   ds = SupervisedDataSet(7,1)

   for i,j in zip(inputArr, outputArr):
      ds.addSample(tuple(i),(tuple(j)))

   # training algorithm
   m1 = BackpropTrainer(net, ds)
   m2 = BackpropTrainer(netOne, ds)

   return m1, m2


def trainNN(model, numEpochs):
   for epoch in range(numEpochs):
      # Give time for the LED Matrix to show things
      print('epoch', epoch)
      time.sleep(displayRate)
      params = pesos_conexiones(net)
      print(params)

      # TRAIN NN and report error
      print('Model train error:', model.train()) #error

      # for debugging purposes
      # params1 = in_to_hidden.params
      #print("in_to_hidden:", params1)
      #params2 = hidden_to_hidden2.params
      ##print("hidden_to_hidden2:",  params2)
      #params3 = hidden2_to_out.params
      #print("hidden2_to_out:",  params3)

      # parse params
      inToH1 = params[0][0:7]
      inToH2 = params[0][7:14]
      inToH3 = params[0][14:]

      hToH1 = params[1][0:3]
      hToH2 = params[1][3:]

      ### Print to LED Matrix ###
      print('Sending to LED matrix:')
      outputMatrix = []
      hOne1 = []
      hOne2 = []
      hOne3 = []

      hTwo1 = []
      hTwo2 = []

      # Compute the node values
      for x in range(-4, 4):
         outputList = []
         hO1 = []
         hO2 = []
         hO3 = []

         hT1 = []
         hT2 = []

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


            hT1.append(temp21)
            hT2.append(temp22)

            if compute > 0.5:
               print("1", end='')
               outputList.append(1)
            else:
               print("0", end='')
               outputList.append(0)

         outputMatrix.append(outputList)
         hOne1.append(hO1)
         hOne2.append(hO2)
         hOne3.append(hO3)
         hTwo1.append(hT1)
         hTwo2.append(hT2)

         print()

      print()
      print(hOne1)
      print(hOne2)
      print(hOne3)
      print(hTwo1)
      print(hTwo2)
      # sendMatrix(outputMatrix)
      sendMatrix(hTwo2)

      """
      # debugging prints
      for k in range(0, 3):
         print("hidden1[", k, "]")
         for x in range(-4, 4):
         # print "h",h,
            for y in range(-4, 4):
               inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
               calcInstant(inArr,tempArr,-1,k)
            print()

      for h in range(0, 2):
         print("hidden2[", h, "]")
         for x in range(-4, 4):
         # print "h",h,
            for y in range(-4,4):
               inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
               calcInstant(inArr,tempArr,h,-1)
            print("\n")

      """

"""
for i,j in zip(inputArr, outputArr):
   compute = net.activate(i)

  # print('Target: ', j , ' Output: ', compute)
"""
"""
print("final display array: row outside, col inside")
for x in range(-4,4):
   for y in range(-4,4):
      compute = net.activate([x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)])
      print(compute + " ")
   print(' \n')
#print(ds)
"""

if __name__ == '__main__':
   inputData, outputData = generateData(numTrain, 2)
   model1, model2 = setupNN(inputData, outputData, numFeatures, 3, 2)
   trainNN(model1, numEpochs)


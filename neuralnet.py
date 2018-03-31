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
           # print conn
            for cc in range(len(conn.params)):
                #print conn.whichBuffers(cc), conn.params[cc]
                paramArr.append(conn.params[cc])
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

   return BackpropTrainer(net,ds) # training algorithm


def trainNN(model, numEpochs):
   for epoch in range(numEpochs):
      # Give time for the LED Matrix to show things
      print('epoch', epoch)
      time.sleep(displayRate)
      # tempArr = pesos_conexiones(net)

      # TRAIN NN and report error
      print('Model train error:', model.train()) #error

      # for debugging purposes
      #params1 = in_to_hidden.params
      #print("in_to_hidden:", params1)
      #params2 = hidden_to_hidden2.params
      #print("hidden_to_hidden2:",  params2)
      #params3 = hidden2_to_out.params

      ### Print to LED Matrix ###
      print('Sending to LED matrix:')
      outputMatrix = []
      for x in range(-4, 4):
         outputList = []
         for y in range(-4, 4):
            inArr = [x,y, x*x, y*y, x*y, math.sin(x), math.sin(y)]

            # predict with NN
            compute = net.activate(inArr)

            if compute > 0.5:
               print("1", end='')
               outputList.append(1)
            else:
               print("0", end='')
               outputList.append(0)
         outputMatrix.append(outputList)
         print("\n")

      sendMatrix(outputMatrix)

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
   inputData, outputData = generateData(numTrain, 1)
   model = setupNN(inputData, outputData, numFeatures, 3, 2)
   trainNN(model, numEpochs)


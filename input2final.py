import random
import math
import time
import serial
from __future__ import print_function

# pybrain imports
from pybrain.structure import FeedForwardNetwork
from pybrain.tools.shortcuts import buildNetwork  # network
from pybrain.datasets import SupervisedDataSet  # dataset
from pybrain.supervised.trainers import BackpropTrainer # training alg
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection

# hook up arduino to serial port
ard = serial.Serial('/dev/cu.usbmodem1421')
inputArr=[]
outputArr=[]

# parameters
numEpochs = 300
numFeatures = 7
numTrain = 50

# create our input data
for x in range (0, numTrain):
   # generate random values
   xVal = random.uniform(-4,4)
   yVal = random.uniform(-4,4)

   # NN input data
   inputArr.append([xVal, yVal, xVal*xVal, yVal*yVal, xVal*yVal, math.sin(xVal), math.sin(yVal)])

   # Labels for input data
   if yVal>0:
      outputArr.append([0])
   else:
      outputArr.append([1])

# data to be inputted by user
testArr = []
for row in range(-4,4):
   for col in range(-4,4):
      testArr.append([[row,col],[row, col, row*row, col*col, row*col, math.sin(row), math.sin(col)]])

# Create NN layers. Numbers indicate dimension = number of nodes in layer
net = FeedForwardNetwork()
inLayer = LinearLayer(7)
hiddenLayer = SigmoidLayer(3)
hiddenLayer2 = SigmoidLayer(2)
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
net.sorted=False
net.sortModules() # random command to make this work

ds = SupervisedDataSet(7,1)

for i,j in zip(inputArr, outputArr):
   ds.addSample(tuple(i),(tuple(j)))

back = BackpropTrainer(net,ds) # training algorithm

#epochs: how many times we will try to fit this dataset
#300

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

# function for sending data to matrix
def sendMatrix(m):
    ard.write(b's')
    for i in m:
        for j in i:
            ard.write(str(j).encode())
    ard.write(b's')

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
   hidden1=[]
   for x in range(0, 3):
      total = 0
      for y in range(0, numFeatures):
         total = paramArr[numFeatures*x + y]*inArr[y]+total
      hidden1.append(sigmoid(total))   
  # print("hidden1:", hidden1)

   hidden2=[]
   for x in range(0,2):
      total = 0
      for y in range(0,3):
         total=paramArr[3*x+y+21]*hidden1[y]+total
      hidden2.append(sigmoid(total))   
   # print("hidden2:", hidden2)

   total=0
   for x in range(0,2):
      total = total+hidden2[x]*paramArr[27+x]
   if (index==2):
      print("Total:", total)
   elif index>-1:
      if hidden2[index]>0.5:
         print("1", end='')
      else:
         print("0", end='')
   elif index2>-1:
      if hidden1[index2]>0.5:
         print("1", end='')
      else:
         print("0", end ='')

for epoch in xrange(300):
   time.sleep(1)
   tempArr= pesos_conexiones(net)
   #print (tempArr)

   # TRAIN NN and report error
   print('Back train error:', back.train()) #error

   # for debugging purposes
   params1 = in_to_hidden.params
   #print("in_to_hidden:", params1)
   params2 = hidden_to_hidden2.params
   #print("hidden_to_hidden2:",  params2)
   params3 = hidden2_to_out.params

   ### Print to LED Matrix ###
   outputMatrix = []
   for x in range(-4,4):
      outputList = []
      for y in range(-4,4):
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

   # debugging prints
   for k in range(0,3):
      print("hidden1[", k, "]")
      for x in range(-4,4):
        # print "h",h,
         for y in range(-4,4):
            inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
            calcInstant(inArr,tempArr,-1,k)
         print()



   for h in range(0,2):
      print("hidden2[", h, "]")
      for x in range(-4,4):
        # print "h",h,
         for y in range(-4,4):
            inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
            calcInstant(inArr,tempArr,h,-1)
         print("\n")

  # update output node

for i,j in zip(inputArr,outputArr):
   compute = net.activate(i)
   
  # print('Target: ', j , ' Output: ', compute)
"""
print("final display array: row outside, col inside")
for x in range(-4,4):
   for y in range(-4,4):
      compute = net.activate([x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)])
      print(compute + " ")
   print(' \n')
#print(ds)
"""




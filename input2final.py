from pybrain.structure import FeedForwardNetwork
import random
import math
import time
import serial

ard = serial.Serial('/dev/cu.usbmodem1421')
inputArr=[]
outputArr=[]

# create our input data
for x in range (0,50):
   # generate random values
   xVal = random.uniform(-4,4)
   yVal = random.uniform(-4,4)

   # NN features
   inputArr.append([xVal, yVal, xVal*xVal, yVal*yVal, xVal*yVal, math.sin(xVal), math.sin(yVal)])

   # output data
   if yVal>0:
      outputArr.append([0])
   else:
      outputArr.append([1])

# data to be inputted by user
testArr = []
for row in range(-4,4):
   for col in range(-4,4):
      testArr.append([[row,col],[row, col, row*row, col*col, row*col, math.sin(row), math.sin(col)]])

from pybrain.tools.shortcuts import buildNetwork  # network
from pybrain.datasets import SupervisedDataSet  # dataset
from pybrain.supervised.trainers import BackpropTrainer # training alg

# network 2
net = FeedForwardNetwork()
from pybrain.structure import LinearLayer, SigmoidLayer
inLayer = LinearLayer(7)
hiddenLayer = SigmoidLayer(3)
hiddenLayer2 = SigmoidLayer(2)
outLayer = LinearLayer(1)

# Add NN components
net.addInputModule(inLayer)
net.addModule(hiddenLayer)
net.addModule(hiddenLayer2)
net.addOutputModule(outLayer)


# make neural network connections
from pybrain.structure import FullConnection
in_to_hidden = FullConnection(inLayer, hiddenLayer)
hidden_to_hidden2 = FullConnection(hiddenLayer, hiddenLayer2)
hidden2_to_out = FullConnection(hiddenLayer2, outLayer)



net.addConnection(in_to_hidden)
net.addConnection(hidden_to_hidden2) #lazy full connection
net.addConnection(hidden2_to_out)



net.sorted=False
net.sortModules() #random command to make this work

#network 1
#net = buildNetwork (7, 14,1, bias=True) # what is bias

ds = SupervisedDataSet(7,1)

for i,j in zip(inputArr, outputArr):
   ds.addSample(tuple(i),(tuple(j)))

back = BackpropTrainer(net,ds) #training algorithm

#epochs: how many times we will try to fit this dataset
#300
def sendMatrix(m):
    ard.write(b's')
    for i in m:
        for j in i:
            ard.write(b""+str(j))
    ard.write(b's')

def pesos_conexiones(n):
    paramArr = []
    for mod in n.modules:
        for conn in n.connections[mod]:
           # print conn
            for cc in range(len(conn.params)):
                #print conn.whichBuffers(cc), conn.params[cc]
                paramArr.append(conn.params[cc])
    return paramArr

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def calcInstant(inArr, paramArr,index,index2):
   hidden1=[]
   for x in range(0,3):
      total = 0
      for y in range(0,7):
         total=paramArr[7*x+y]*inArr[y]+total
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
      print "total:", total
   elif index>-1:
      if hidden2[index]>0.5:
         print "1",
      else:
         print "0",
   elif index2>-1:
      if hidden1[index2]>0.5:
         print "1",
      else:
         print "0",

for epoch in xrange(300):
   time.sleep(1)
   tempArr= pesos_conexiones(net)
   #print (tempArr)
   print(back.train()) #error
   params1 = in_to_hidden.params
   #print("in_to_hidden:", params1)
   params2 = hidden_to_hidden2.params
   #print("hidden_to_hidden2:",  params2)
   params3 = hidden2_to_out.params
   outputMatrix = []
   for x in range(-4,4):
      outputList = []
      for y in range(-4,4):
         inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
         compute = net.activate(inArr)
         if compute>0.5:
            print "1",
            outputList.append(1)
         else:
            print "0",
            outputList.append(0)
      outputMatrix.append(outputList)
      print "\n"
   sendMatrix(outputMatrix)

   for k in range(0,3):
      print "hidden1[",k,"]" 
      for x in range(-4,4):
        # print "h",h,
         for y in range(-4,4):
            inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
            calcInstant(inArr,tempArr,-1,k)
         print "\n"



   for h in range(0,2):
      print "hidden2[",h,"]" 
      for x in range(-4,4):
        # print "h",h,
         for y in range(-4,4):
            inArr = [x,y,x*x, y*y,x*y,math.sin(x), math.sin(y)]
            calcInstant(inArr,tempArr,h,-1)
         print "\n"

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




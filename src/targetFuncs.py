'''
Library of target functions to use for NN

Since we are only dealing with binary data, we require that
all functions return either True or False for 1, 0 respectively
'''

from math import sqrt

# circle radius
r = 3

def yGeZero(x, y):
  return y > 0

def xGeZero(x, y):
  return x > 0

def checkerboard(x, y):
  return ((x >= 0) and (y >= 0)) or ((x <= 0) and (y <= 0))

def circle(x, y):
  return sqrt(x*x + y*y) <= r

def diag(x, y):
  return (int(x) == int(y)) or (int(x) == int(y+1)) or (int(x) == int(y-1))

def chess(x, y):
  return (int(x) % 2 != 0) and (int(y) % 2 != 0)

def line(x, y):
  return x == y

def corners(x, y):
  return (x >= 2 and y >= 2) or (x >= 2 and y <= -3) or (x <= -3 and y >= 2) or (x <= -3 and y <= -3)

def kite(x, y):
  return ((abs(y) >= abs(x)) or (y <= -abs(x)))

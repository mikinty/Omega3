### Library of target functions to use for NN ###

# Since we are only dealing with binary data, we require that 
# all functions return either true or false for 1, 0 respectively

def yGeZero(x, y):
  return y > 0

def xGeZero(x, y):
  return x > 0

def checkerboard(x, y):
  return ((x >= 0) and (y >= 0)) or ((x <= 0) and (y <= 0))

def circle(x, y, r):
  return sqrt(x*x + y*y) <= r



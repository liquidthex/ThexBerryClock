#!/usr/bin/python

import time
from datetime import date
import math
from rgbmatrix import RGBMatrix
import Image
import ImageDraw
import ImageFont

def startUp():
  log("Starting up ThexBerryClock...")
  global matrix, canvas, font, mode, iterations, itime
  itime = time.time()
  mode = 0
  iterations = 0
  matrix = RGBMatrix(32, 2)
  canvas = matrix.CreateFrameCanvas()
  font = ImageFont.load("pilfonts/timR08.pil")

def shutDown():
  log("Main loop exited after " + str(iterations) + " iterations. Shutting down.")
  exit

def mainLoop():
  global image, draw, itime
  itime = time.time()
  image = Image.new("RGB", (64,32))
  draw = ImageDraw.Draw(image)

  if (mode == 0):
    mainClock()

  rainbowBorder()

  renderDisplay()

def renderDisplay():
  setimage(image, canvas)
  matrix.SwapOnVSync(canvas)

def mainClock():
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, int(time.time())/60)
  draw.text((5, 0), time.strftime("%I:%M:%S %p"), font=font, fill=rgb_to_hex((r,g,b)))

def rainbowBorder():
  (w,h) = image.size
  pix = image.load()
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
#  (r,g,b) = makeColorGradient(1.666, 2.666, 3.666, 0, 2, 4, 128, 127, 8, iterations)
  
  for x in range(0,w):
    for y in range(0,h):
      if (x == 0 or x == 63 or y == 0 or y == 31):
        pix[x, y] = (r, g, b)

def makeColorGradient(f1, f2, f3, p1, p2, p3, center, width, len, i):
  r = int(math.floor(math.sin(f1*i + p1) * width + center))
  g = int(math.floor(math.sin(f2*i + p2) * width + center))
  b = int(math.floor(math.sin(f3*i + p3) * width + center))
  return (r,g,b)

def setimage(im,mx):
  (w,h) = im.size
  pix = im.load()
  for x in range(w):
    for y in range(h):
      (r, g, b) = pix[x, y]
      mx.SetPixel(x, y, r, g, b)

def rgb_to_hex(rgb):
  return '#%02x%02x%02x' % rgb

def log(msg):
  print msg

iterations = 0
startUp()
while 1:
  mainLoop()
  iterations = iterations + 1
shutDown()

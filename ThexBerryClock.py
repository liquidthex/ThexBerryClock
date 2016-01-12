#!/usr/bin/python

import thread
import time
from datetime import date
import math
from rgbmatrix import RGBMatrix
import Image
import ImageDraw
import ImageFont

def startUp():
  log("Starting up ThexBerryClock...")
  global matrix, canvas, font, mode, iterations, bitcoin, sleep, itime, timers, timerFreqList, timerFuncList
  sleep = 0.01
  mode = effect_startupSplash
  iterations = 0
  bitcoin = 0
  itime = int(time.time())
  timers = {'bitcoin':itime};
  timerFreqList = {'bitcoin':20};
  timerFuncList = {'bitcoin':getBitcoinPrice};
  matrix = RGBMatrix(32, 2)
  matrix.pwmBits = 11
  matrix.brightness = 50
  canvas = matrix.CreateFrameCanvas()
  font = ImageFont.load("pilfonts/timR08.pil")

def shutDown():
  log("Main loop exited after " + str(iterations) + " iterations. Shutting down.")
  exit

def getBitcoinPrice():
  global bitcoin
  bitcoin = bitcoin + 5 

def mainLoop():
  global image, draw, itime

  # Keep track of the current iteration's time
  itime = int(time.time())

  # Set up the image canvas
  image = Image.new("RGB", (64,32))
  draw = ImageDraw.Draw(image)

  # Execute the current mode
  mode()

  # Perform frequency-based timers
  for timer in timerFreqList:
    timeSince = itime - timers[timer]
    if timeSince > timerFreqList[timer]:
      timers[timer] = itime
      thread.start_new_thread( timerFuncList[timer], () )

  # Output the image canvas to display
  renderDisplay()

  # Pause for garbage collection
  time.sleep(sleep)

def renderDisplay():
  setimage(image, canvas)
  matrix.SwapOnVSync(canvas)

def effect_startupSplash():
  rainbowBorder()
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
  (r2,g2,b2) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+5)
  (r3,g3,b3) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+10)
  (r4,g4,b4) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+15)
  draw.text((5, -1), time.strftime("%I:%M:%S %p"), font=font, fill=rgb_to_hex((r,g,b)))
  draw.text((1, 7), "THEXBERRY", font=font, fill=rgb_to_hex((r2,g2,b2)))
  draw.text((1, 14), "THEXBERRY", font=font, fill=rgb_to_hex((r3,g3,b3)))
  draw.text((1, 21), "THEXBERRY", font=font, fill=rgb_to_hex((r4,g4,b4)))
  if iterations > 10:
    global mode
    mode = mainClock

def effect_flashBorder(duration):
  if not duration:
    duration = 60

def mainClock():
  h = time.strftime("%I")
  m = time.strftime("%M")
  s = time.strftime("%S")
  ampm = time.strftime("%p")

  # Pre-420
  if (h == "12" and (m == "52" or m == "53")) or (h == "7" and (m == "9" or m == "10")):
   (r,g,b) = makeColorGradient(1.666, 2.666, 3.666, 0, 2, 4, 128, 127, 8, int(iterations/3))
  else:
   (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, int(time.time())/60)

  # Colon Blink Color
  if (itime % 2 == 0):
    (r1,g1,b1) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
  else:
    (r1,g1,b1) = (r,g,b)

  draw.text((5, -1), str(h), font=font, fill=rgb_to_hex((r,g,b)))
  draw.text((15, -1), ":", font=font, fill=rgb_to_hex((r1,g1,b1)))
  draw.text((18, -1), str(m), font=font, fill=rgb_to_hex((r,g,b)))
  draw.text((28, -1), ":", font=font, fill=rgb_to_hex((r1,g1,b1)))
  draw.text((31, -1), str(s), font=font, fill=rgb_to_hex((r,g,b)))
  draw.text((43, -1), str(ampm), font=font, fill=rgb_to_hex((r,g,b)))

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

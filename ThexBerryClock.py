#!/usr/bin/python

## Configuration -- Note there is more config down lower in the startUp function, such as brightness
basePath = '/opt/ThexBerryClock'
logFile = '/tmp/TBC.log'
blockHeightFile = '/tmp/latestBlockheight.txt'
interruptFile = '/tmp/TBC-INTERRUPT.txt'

# App will stay in foreground & verbose logging
debugMode = False

# Main script
import thread
import time
import datetime
from datetime import date
import math
from rgbmatrix import RGBMatrix
import Image
import ImageDraw
import ImageFont
import locale
import signal
import json
import os
import sys
import logging
from exchanges.bitstamp import Bitstamp

locale.setlocale( locale.LC_ALL, 'en_GB.utf8' )

def startUp():
  log("Starting up ThexBerryClock...")
  global TBC, iterations, itime

  iterations = 0
  itime = int(time.time())
  TBC = {}
  TBC['epoch']=datetime.datetime.utcfromtimestamp(0)
  TBC['bhdisplay'] = 0
  TBC['sleep'] = 0.01
  TBC['clockmode'] = effect_startupSplash
  TBC['bitcoin'] = 0
  TBC['btcopen'] = 0
  TBC['rainbowBorderMode'] = 0
  TBC['timers'] = {'bitcoin':0,'bhflipper':0};
  TBC['timerFreqList'] = {'bitcoin':60,'bhflipper':10};
  TBC['timerFuncList'] = {'bitcoin':getBitcoinPrice,'bhflipper':blockheight_flipDisplay};
  TBC['matrix'] = RGBMatrix(32, 2)
  TBC['matrix'].pwmBits = 11
  TBC['matrix'].brightness = 50
  TBC['canvas'] = TBC['matrix'].CreateFrameCanvas()
  TBC['font'] = ImageFont.load(basePath + "/pilfonts/timR08.pil")
  TBC['blockheight'] = 0
  thread.start_new_thread( startup_blockheight, () )
  signal.signal(signal.SIGUSR1, interruptHandler)

def startup_blockheight():
  liveUpdate(blockHeightFile, 0)

def shutDown():
  log("Main loop exited after " + str(iterations) + " iterations. Shutting down.")
  exit

def mainLoop():
  global TBC
  global image, draw, itime

  # Keep track of the current iteration's time
  itime = int(time.time())

  # Set up the image canvas
  image = Image.new("RGB", (64,32))
  draw = ImageDraw.Draw(image)

  # Determine the mode to be in
  h = time.strftime("%I")
  m = time.strftime("%M")
  s = time.strftime("%S")
  if (h == "04" and (m == "19" or m == "20")) or (h == "07" and (m == "09" or m == "10")):
    TBC['clockmode'] = clock420
    rainbowBorder()

  if m == "00" and (s == "00" or s == "01"):
    effect_borderPulse()

  # Execute the current clock line
  TBC['clockmode']()

  if TBC['clockmode'] == mainClock:
    bitcoinDisplay()
    blockheightDisplay()

  # Perform frequency-based timers
  for timer in TBC['timerFreqList']:
    timeSince = itime - TBC['timers'][timer]
    if timeSince >= TBC['timerFreqList'][timer]:
      TBC['timers'][timer] = itime
      thread.start_new_thread( TBC['timerFuncList'][timer], () )

  # Output the image canvas to display
  renderDisplay()

  # Pause for garbage collection
  time.sleep(TBC['sleep'])

def renderDisplay():
  setimage(image, TBC['canvas'])
  TBC['matrix'].SwapOnVSync(TBC['canvas'])

def interruptHandler(a, b):
  thread.start_new_thread( liveUpdate, (interruptFile,1) )

def liveUpdate(confFile, removeConf):
  conf = getInterruptConfig(confFile, removeConf)
  if not conf:
    return
  if conf['mode'] == 'heightupdate':
    try:
      if TBC['blockheight'] != conf['data']['height']:
        TBC['blockheight'] = conf['data']['height']
        TBC['blockheight_date'] = conf['data']['time']
        TBC['blockheight_tx'] = conf['data']['n_tx']
        TBC['blockheight_bytes'] = conf['data']['size']
        TBC['blockheight_time'] = itime
    except:
      TBC['blockheight'] = 0
    log("Blockheight update: " + str(conf['data']['height']))

def getInterruptConfig(interruptFile,removeInterrupt):
  if not os.path.isfile(interruptFile):
    return
  with open(interruptFile,'r') as f:
    data = json.load(f)
  if removeInterrupt == 1:
    os.remove(interruptFile)
  return data

def getBitcoinPrice():
  global TBC
  (TBC['bitcoin'],btco) = Bitstamp.get_current_price()
  TBC['btcopen'] = float(TBC['bitcoin']-btco)


def effect_borderPulse():
  (w,h) = image.size
  pix = image.load()
  (r,g,b) = makeColorGradient(1.666, 2.666, 3.666, 0, 2, 4, 128, 127, 8, iterations)
  for x in range(0,w):
    for y in range(0,h):
      if (x == 0 or x == 63 or y == 0 or y == 31):
        pix[x, y] = (r, g, b)

def effect_startupSplash():
  rainbowBorder()
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
  (r2,g2,b2) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+5)
  (r3,g3,b3) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+10)
  (r4,g4,b4) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+15)
  draw.text((5, -1), time.strftime("%I:%M:%S ")+time.strftime("%p").upper(), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  draw.text((1, 7), "THEXBERRY", font=TBC['font'], fill=rgb_to_hex((r2,g2,b2)))
  draw.text((1, 14), "THEXBERRY", font=TBC['font'], fill=rgb_to_hex((r3,g3,b3)))
  draw.text((1, 21), "THEXBERRY", font=TBC['font'], fill=rgb_to_hex((r4,g4,b4)))
  if iterations > 10:
    TBC['clockmode'] = mainClock

def mainClock():
  h = time.strftime("%I")
  m = time.strftime("%M")
  s = time.strftime("%S")
  ampm = time.strftime("%p").upper()

  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, int(time.time())/60)

  # Colon Blink Color
  if (itime % 2 == 0):
    (r1,g1,b1) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
  else:
    (r1,g1,b1) = (r,g,b)

  draw.text((5, -1), str(h), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  draw.text((15, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
  draw.text((18, -1), str(m), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  draw.text((28, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
  draw.text((31, -1), str(s), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  draw.text((43, -1), str(ampm), font=TBC['font'], fill=rgb_to_hex((r,g,b)))

def blockheight_flipDisplay():
  if TBC['bhdisplay'] == 1:
    TBC['bhdisplay'] = 0
  else:
    TBC['bhdisplay'] = 1

def blockheightDisplay():
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, int(time.time())/60)
  if (TBC['blockheight'] == 0):
    return
#  (r,g,b) = makeColorGradient(.1, .1, .1, 0.2, 0.5, 0.8, 128, 127, 255, iterations)
  bhdate = datetime.datetime.strptime(TBC['blockheight_date'], "%Y-%m-%dT%H:%M:%SZ")
  secsSinceUpdate = itime - (bhdate-TBC['epoch']).total_seconds()
  secsSince = itime - TBC['blockheight_time']

#  secsSinceUpdate = itime - TBC['blockheight_time']
  percent = secsSince * 5
  if percent < 100:
    if percent <= 0:
      percent = 1
    gr=linear_gradient("#FFFFFF",rgb_to_hex((r, g, b)),percent,100)
    r=gr['r'][0]
    g=gr['g'][0]
    b=gr['b'][0]
#  txt = str(TBC['blockheight']) + " " + str(TBC['blockheight_tx']) + "tx"
  txt = "        " + str(TBC['blockheight'])
  ago = int(secsSinceUpdate/60)
  if TBC['bhdisplay'] == 0:
    txt = str(ago) + " min " + str(TBC['blockheight_bytes']/1024) + "KB"
  
  draw.text((1, 14), str(txt), font=TBC['font'], fill=rgb_to_hex((r,g,b)))

def bitcoinDisplay():
  (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, int(time.time())/60)
  btcs = locale.currency(TBC['btcopen'], grouping=False, symbol=False)
  # TODO: Pixel Up/Down arrows
  if btcs.startswith("-"):
    btcstr = btcs[1:]
    (r1,g1,b1) = (255,0,0)
  else:
    btcstr = btcs
    (r1,g1,b1) = (0,255,0)
  draw.text((3, 7), str(TBC['bitcoin']), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
#  draw.text((32, 7), "$", font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  draw.text((34, 7), "$" + str(btcstr), font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
#  draw.text((60, 7), ")", font=TBC['font'], fill=rgb_to_hex((r,g,b)))

def clock420():
  global TBC
  h = time.strftime("%I")
  m = time.strftime("%M")
  s = time.strftime("%S")
  ampm = time.strftime("%p").upper()
  if (h == "04" and m == "21") or (h == "07" and m == "11"):
    TBC['clockmode'] = mainClock

  (r1,g1,b1) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations+10)

  if m == "20" or m == "10":
    TBC['rainbowBorderMode'] = 1
    if itime % 2 == 0:
      (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
      draw.text((5, -1), str(h), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
      draw.text((15, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
      draw.text((18, -1), str(m), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
      draw.text((28, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
      draw.text((31, -1), str(s), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
      draw.text((43, -1), str(ampm), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
    else:
      (r,g,b) = makeColorGradient(1.666, 2.666, 3.666, 0, 2, 4, 128, 127, 8, iterations)
      draw.text((5, -1), "CHEERS!!!!!", font=TBC['font'], fill=rgb_to_hex((r,g,b)))
  else:
    TBC['rainbowBorderMode'] = 0
    (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
    draw.text((5, -1), str(h), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
    draw.text((15, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
    draw.text((18, -1), str(m), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
    draw.text((28, -1), ":", font=TBC['font'], fill=rgb_to_hex((r1,g1,b1)))
    draw.text((31, -1), str(s), font=TBC['font'], fill=rgb_to_hex((r,g,b)))
    draw.text((43, -1), str(ampm), font=TBC['font'], fill=rgb_to_hex((r,g,b)))

def rainbowBorder():
  (w,h) = image.size
  pix = image.load()
  if (TBC['rainbowBorderMode'] == 1):
    (r,g,b) = makeColorGradient(1.666, 2.666, 3.666, 0, 2, 4, 128, 127, 8, iterations)
  else:
    (r,g,b) = makeColorGradient(.1, .1, .1, 0, 2, 4, 128, 127, 255, iterations)
  
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

def RGB_to_hex(RGB):
  # Components need to be integers for hex to make sense
  RGB = [int(x) for x in RGB]
  return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])

def hex_to_RGB(hex):
  # Pass 16 to the integer function for change of base
  return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def linear_gradient(start_hex, finish_hex, i, n):
  s = hex_to_RGB(start_hex)
  f = hex_to_RGB(finish_hex)
  vector = [
    int(s[j] + (float(i)/(n-1))*(f[j]-s[j]))
    for j in range(3)
  ]
  return color_dict([vector])

def color_dict(gradient):
  return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}

def log(msg):
  logger.debug(str(msg))

def usage():
  print "-----------------------------"
  print "ThexBerryClock"
  print "-----------------------------"
  print "ThexBerryClock.py daemon - Launch clock daemon"

def commandLine():
  try:
    a1 = sys.argv[1]
  except:
    a1 = ''
  if a1 == "daemon":
    return True
  usage()

def TBCLoop():
  global iterations
  startUp()
  while 1:
    mainLoop()
    iterations = iterations + 1
  shutDown()

if commandLine() == True:
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.DEBUG)
  fh = logging.FileHandler(logFile, "w")
  fh.setLevel(logging.DEBUG)
  logger.addHandler(fh)
  TBCLoop()

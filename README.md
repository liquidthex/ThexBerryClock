# ThexBerryClock
Custom clock project!

This is a fairly custom / personalized project for a clock that has the following features:
* A clock (duh)
* Bitcoin price & daily price change updated every 20 seconds from Bitstamp.net
* Real-time blockchain height updates
* Visual alerts: 4:20 & 7:10, top of the hour

As a huge warning this project is complete spaghetti code. I've made essentially no attempts to make this extensible at all. I wish I could have but it's just a clock :)

---

Hardware:

Raspberry Pi Model A+

Adafruit RGB HAT (modified to connect Pins 4 & 18 for the PWM timing hack described here: https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/lib/Makefile#L58)

Adafruit 64x32 RGB LED Matrix

---

Software:

Henner Zeller's rpi-rgb-led-matrix libraries: https://github.com/hzeller/rpi-rgb-led-matrix/

Bitcoin Price API Library from: https://github.com/dursk/bitcoin-price-api

Adapted linear gradient code from Ben Southgate http://bsou.io/posts/color-gradients-with-python

BlockCypher API for live bitcoin updates

---

Developed by Liquidthex

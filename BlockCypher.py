# Register @ Blockcypher.com for free
token = 'd310eeab1ac7817e6322bf11695eace8'

# Point to your web server
webHookUrl = "http://theurgist.org/blockcypher.php"

# Register event:
# curl -d '{"event": "new-block", "url": "http://theurgist.org/blockcypher.php"}' https://api.blockcypher.com/v1/btc/main/hooks?token=

# List events:
# curl https://api.blockcypher.com/v1/btc/main/hooks?token=

import requests
import time

def getHooks():
  print "Checking for WebHook..."
  url = 'https://api.blockcypher.com/v1/btc/main/hooks?token=' + token
  r = requests.get(url)
  print r.text
  print "------------------"
  return r.text

def addHook():
  print "Adding WebHook..."
  url = 'https://api.blockcypher.com/v1/btc/main/hooks?token=' + token
  r = requests.post(url, data = '{"event":"new-block","url":"'+webHookUrl+'"}')
  print r.text
  print "------------------"

def tryHookup():
  hooks = getHooks()
  if hooks == "[]":
    print "No Hook Found..."
    addHook()
    return 0
  else:
    print "Found something."
    return 1

hookedUp = 0
while hookedUp == 0:
  hookedUp = tryHookup()
  time.sleep(1)

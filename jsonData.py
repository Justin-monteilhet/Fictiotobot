import requests
import json

bin_id = "60645abe18592d461f0403e1"
url = "https://api.jsonbin.io/v3/b/"
api_key = "$2b$10$Jio5aYBxDvfAR1SZN7IoguoBPdxjGxy3yosoKG0R9PrcVAHUp1omW"

def read():
  headers = {
    'X-Master-Key': api_key
  }
  bin_url = url + bin_id + '/latest'
  try:
    req = requests.get(bin_url, json=None, headers=headers, timeout = 5)
  except requests.RequestException as e:
    print("Error : ", e)
  response = json.loads(req.text)
  if 'message' in response:
        print("Error : " + response['message'])
        return None
  return response['record']

def update(newDic):
  headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': api_key
  }
  data = newDic
  bin_url = url + bin_id
  req = requests.put(bin_url, json=data, headers=headers)
  return json.loads(req.text)

def reset():
  headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': api_key
  }
  bin_url = url + bin_id
  req = requests.put(bin_url, json={"users":{}}, headers=headers)
  return json.loads(req.text)


  

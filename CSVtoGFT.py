# Copyright (C) 2011 Google Inc.

import urllib2, urllib, json, simplejson, sys, httplib, csv, string

# Get your authentication stuff from your Google account
client_id = "your_client_id"
client_secret = "your_client_secret"
redirect_uri = "redirect_uri"
api_key = "your_api_key"

class ManipulateFusionTable:
  def __init__(self):
    self.access_token = ""
    self.params = ""
		
  # Authentication based on OAuth2 protocol
  def authentication(self):
    print "copy and paste the url below into browser address bar and hit enter"
    print "https://accounts.google.com/o/oauth2/auth?%s%s%s%s" % \
      ("client_id=%s&" % (client_id),
      "redirect_uri=%s&" % (redirect_uri),
      "scope=https://www.googleapis.com/auth/fusiontables&",
      "response_type=code")

    code = raw_input("Enter code (parameter of URL): ")
    data = urllib.urlencode({
      "code": code,
      "client_id": client_id,
      "client_secret": client_secret,
      "redirect_uri": redirect_uri,
      "grant_type": "authorization_code"
    })

    serv_req = urllib2.Request(url="https://accounts.google.com/o/oauth2/token",
       data=data)

    serv_resp = urllib2.urlopen(serv_req)
    response = serv_resp.read()
    tokens = simplejson.loads(response)
    access_token = tokens["access_token"]
    self.access_token = access_token
    self.params = "?key=%s&access_token=%s" % \
      (api_key, self.access_token)
    
  # Create the table based on the table name(user input)
  def createTable(self):
    print "Import Table"
    # Let user define the Fusion Table Name
    tableName = raw_input("Please input the Fusion Table name: ")
    table = {
 	  tableName: {
 	    "Latitude": "LOCATION",
 	    "Longitude": "LOCATION",
 	    "Tweets": "STRING"
 	  } 
 	}
    table_name = table.keys()[0]
    cols_and_datatypes = ",".join(["'%s': %s" % (col[0], col[1]) 
                                   for col in table.get(table_name).items()])
    query = "CREATE TABLE '%s' (%s)" % (table_name, cols_and_datatypes)
    response = json.loads(self.runQuery(query))
    tableId = response.values()[1][0][0]
    return tableId
  
  # Insert all rows in the CSV file
  def insertRows(self, tableId, csvPath):
    with open(csvPath, 'rb') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',')
      for row in spamreader:
        try:
          lat = float(row[0])
          long = float(row[1])
          tweet = row[2]
          newTweet = []
          for str in tweet:
            if (str in string.lowercase) | (str in string.uppercase):
              newTweet.append(str)
              newString = "".join(newTweet)

          query = "INSERT INTO %s(Latitude, Longitude, Tweets) VALUES"\
            "(%.5f, %.5f, '%s')" % (tableId, long, lat, newString)  # Single quotes
          self.runQuery(query)
        except:
          continue

  # Send the request
  def runQuery(self, query):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request('https://www.googleapis.com/fusiontables/v1/query?%s' % \
	    (urllib.urlencode({'access_token': self.access_token,
          'sql': query})),
    	headers={'Content-Length':0})      # Manually set length to avoid 411 error
    request.get_method = lambda: 'POST'    # Change HTTP request method
    response = opener.open(request).read()
    return response


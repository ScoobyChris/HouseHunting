import http.client
import xml.etree.ElementTree as etree
import ast
import json

def getStationList():
    # Get XML from TFL
    strData = ""
    placemarkList = list()
    stationList = list()
    
    print("Connecting to TFL and issuing GET request")
    url = "/tfl/businessandpartners/syndication/feed.aspx?email=erica.chris.mawer@gmail.com&feedId=16"
    conn = http.client.HTTPConnection("www.tfl.gov.uk")
    conn.request("GET", url)
    print("Request successfully sent")
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    if r1.reason == "OK":
        print("Response received ok")
        data1 = r1.read()
        strData = data1.decode("utf-8")
        # And now extract the station names
        root = etree.fromstring(strData)
        placemarkList = root.findall('.//Placemark')

        print("Number of elements is " + str(len(placemarkList)))
        for pm in placemarkList:
            name = pm.findtext('name').strip()
            coordsList = pm.findtext('Point/coordinates').strip().split(",")
            lng = coordsList[0].replace("-.", "-0.")
            lat = coordsList[1].replace("-.", "-0.")
            if coordsList[0].startswith("."):
                lng = coordsList[0].replace(".", "0.")
            if coordsList[1].startswith("."):
                lat = coordsList[1].replace(".", "0.")
            stationList.append((name, lng, lat))

    print("Closing connection")
    conn.close()

    return stationList

def getCrimeStats(stationList):

    server = "policeapi2.rkh.co.uk"
    base_url = "/api/locate-neighbourhood?q="

    for (stationname, lng, lat) in stationList:
        strData = ""

        # Connection here as putting it outside the loop overloads the server!
        conn = http.client.HTTPConnection(server)
        
        # Find the neighbourhood team code
        conn.request("GET", base_url + lat + "," + lng)
        print("Request: " + server + base_url + lat + "," + lng + " successfully sent")
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        if r1.reason == "OK":
            data1 = r1.read()
            strData = data1.decode("utf-8")

            # Format will be something like this so need to extract force and neighbourhood:
            # {
            #    "force": "metropolitan",
            #    "neighbourhood": "00BKX6"
            # }
            forceDict = ast.literal_eval(strData)
            print(forceDict)
            conn.request("GET", "/api/" + forceDict['force'] + "/" + forceDict['neighbourhood'] + "/crime")
            r1 = conn.getresponse()
            if r1.reason == "OK":
                print(r1.status, r1.reason)
                data1 = r1.read()
                strData = data1.decode("utf-8")
                jdata = json.loads(strData)
                print(jdata)


                #crimeDict = ast.literal_eval(strData)
                #print(crimeDict)
                
            else:
                print("ERROR: received: ", r1.status, r1.reason)
        else:
            print("ERROR: received: ", r1.status, r1.reason)

        print("Station: ", stationname)
        print(strData)

        # And close the connection
        conn.close()






print("Get station list")
stationList = getStationList()
print ("Returned from station list " + str(stationList))
print("Getting crime stats for all stations")
getCrimeStats(stationList)

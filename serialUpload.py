#essential imports for fetching serial data and managing firebase database
from serial import Serial
import firebase_admin
from firebase_admin import credentials, firestore

#imports for timestamp
import time
import datetime


def checkSensorValue(sensorValue, minimum, maximum):
    if sensorValue > maximum or sensorValue < minimum:
        return True
    else:
        return False

def main():

    #create credentials certificate from locally stored private key
    cred = credentials.Certificate('./yourFirebaseJSONKeyPath')

    #login as admin with the credentials
    firebase_admin.initialize_app(cred)

    #connect to the firestore database
    db = firestore.client()
    doc_ref = db.collection(u'users/oWWajW5e8paKINCNuW5WuPN7lhJ2/Greenhouses/FlW10npLhWBABvxUp0Fg/Plants')

    #collect incoming serial data from port ttyACM0 where the Arduino board is connected
    arduino = Serial('/dev/ttyACM0', 9600, timeout=.1)

    #initialize fields data that will be updated after each serial data receival
    dbEntry = { 
                'Soil_humidity': "",
                'Temperature': "",
                'Air_humidity': "",
                'Light_intensity': ""
            }

    #get timestamp
    prevTimestamp = datetime.datetime.now()
    #print(timestamp.minute)

    plantId = 'jCOddC70Dj8b0ChsiwfO' #this id currently accesses the plant Rose

    #display plants data to the terminal if connection successful
    plants = doc_ref.stream()
    for plant in plants:
        print(f'{plant.id} => {plant.to_dict()}')
        #get the parameters from a specific plant
        if f'{plant.id}' == plantId:
            #create dictionary
            plantParams = plant.to_dict()
            #print values for minimum and maximum parameters
            keyValues = {}
            for key, value in plantParams.items():
                if 'Min' in key or 'Max' in key:
                    #print(key, value)
                    keyValues[key] = value
            print(keyValues)

    emergency = False

    while True:

        #get current timestamp
        crtTimestamp = datetime.datetime.now()   

        #check if 1 minutes have passed to upload new values to firestore
        if (crtTimestamp - prevTimestamp).total_seconds() / 60.0 >= 1 and emergency == False:
            #update the previous timestamp with the current one for the next data upload
            prevTimestamp = crtTimestamp
            #update the sensor values of a certain plant
            doc_ref.document(plantId).update(
                {
                    'Humidity': dbEntry['Air_humidity'],
                    'Light_Intensity': dbEntry['Light_intensity'],
                    'Soil_Humidity': dbEntry['Soil_humidity'],
                    'Temperature': dbEntry['Temperature'],
                    'Message': 'Parameters okay'
                }
            )
        #check for emergency value
        elif emergency == True:
            #keep updating the sensor values of a certain plant
            doc_ref.document(plantId).update(
                {
                    'Humidity': dbEntry['Air_humidity'],
                    'Light_Intensity': dbEntry['Light_intensity'],
                    'Soil_Humidity': dbEntry['Soil_humidity'],
                    'Temperature': dbEntry['Temperature'],
                    'Message': 'Parameters out of range!'
                }
            )
            #turn off emergency
            emergency = False

        #read serial data and decode it
        data = arduino.readline()[:-2].decode("utf-8")
        
        #relevant data is read
        if data != "":

            #splitting the received line of values to get the soil humidity, temperature, air humidity and light intensity
            fields = data.split("#")
            print(fields)

            if len(fields) == 4:
                
                #create the database entry as dictionary
                dbEntry = {
                    'Soil_humidity': fields[0],
                    'Temperature': fields[1] + '°C',
                    'Air_humidity': fields[2] + '%',
                    'Light_intensity': fields[3] + ' lumens'
                }

                #check if the temperature, humidity, soil humidity and light intensity if in the right limits
                if checkSensorValue(float(fields[1]), float(keyValues['MinTemperature']), float(keyValues['MaxTemperature'])) == True or checkSensorValue(float(fields[2]), float(keyValues['MinHumidity']), float(keyValues['MaxHumidity'])) == True or checkSensorValue(float(fields[3]), float(keyValues['MinLumens']), float(keyValues['MaxLumens'])) == True or checkSensorValue(float(fields[0]), float(keyValues['MinSoilHumidity']), float(keyValues['MaxSoilHumidity'])) == True:
                    emergency = True
                else:
                    emergency = False
                print(emergency)
main()

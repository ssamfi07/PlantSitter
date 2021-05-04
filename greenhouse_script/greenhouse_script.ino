#include <Adafruit_Sensor.h>

//library for DHT11 temperature and humidity sensor
#include <DHT.h>
#include <DHT_U.h>

//defining Arduino Pins for sensors
#define LightPin A0
#define SoilHumidityPin A1
#define DHT11Pin 7

//input voltage
#define Vin 5

//photoresistor resistance divider value 10k
#define Rdiv 10000

//defining the dht object
DHT dht(DHT11Pin, DHT11);

float soilHumiditySensorValue = 0; 
float lightSensorValue = 0; 

void setup() 
{
  // put your setup code here, to run once:
  Serial.begin(9600);
  //setting up dht11
  dht.begin();
  pinMode(DHT11Pin, INPUT);
}

void loop() 
{
  //enable pin 12 and 13 - turns on soil humidity sensor and photoresistor
  //digitalWrite(12, HIGH);
  digitalWrite(13, HIGH);
  
  //make 100 measurements for data stability (light and soil humidity) 1ms in between
  soilHumiditySensorValue = 0; 
  lightSensorValue = 0; 
  for (int i = 0; i < 100; i++) 
  { 
    soilHumiditySensorValue += analogRead(SoilHumidityPin);
    //lightSensorValue += analogRead(LightPin);
    delay(1); 
  } 
  //disable pin 12 and 13 - turns off soil humidity sensor and photoresistor
  //digitalWrite(12, LOW);
  digitalWrite(13, LOW);
  //get the actual value as the average of 100 measurements (analog value)
  soilHumiditySensorValue /= 100.0; 
  //lightSensorValue /= 100;

  //measure light intensity in analog
  lightSensorValue = analogRead(LightPin);
  
  //send serial data
  //soil humidity
  //Serial.print(" Soil Humidity: ");
  Serial.print(soilHumiditySensorValue);
  Serial.print("#");
  
  //dht11 values
  //Serial.print(" Temperature = ");
  Serial.print(dht.readTemperature());
  Serial.print("#");
  //Serial.print("°C Humidity = ");
  Serial.print(dht.readHumidity());
  Serial.print("#");

  //photoresistor in lumens
  //Serial.print("%  LightIntensity = ");
  Serial.println(sensorRawToLumens(lightSensorValue));

  //total delay of 5.1 seconds between readings
  delay(5000);
  
}

//function used to convert the analog value read from the photoresistor pin to lumens
int sensorRawToLumens(float lightSensorValue)
{
  //conversion analog to voltage
  float Vout = lightSensorValue * (Vin / float(1023));

  //conversion voltage to resistance
  float photoResistance = (Rdiv * (Vin - Vout)) / Vout; 

  //conversion resitance to lumen
  int lumens = 500 / (photoResistance / 1000); 
  return lumens;
}

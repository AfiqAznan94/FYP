#include <LiquidCrystal_I2C.h>

// set the LCD number of columns and rows
int lcdColumns = 16;
int lcdRows = 2;


// set LCD address, number of columns and rows
// if you don't know your display address, run an I2C scanner sketch
LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);  


#ifdef ESP32
  #include <WiFi.h>
#else
  #include <ESP8266WiFi.h>
#endif

#include <ESP8266mDNS.h>
#include <WebSocketsServer.h>

  WebSocketsServer webSocket = WebSocketsServer(31725);
  

// Replace with your network credentials
const char* ssid = "";
const char* password = "";

#define lock D3
WiFiClientSecure client;
bool State = HIGH;

void setup() {
   Serial.begin(115200);
  // initialize LCD
  lcd.init();
  // turn on LCD backlight                      
  lcd.backlight();
   // set cursor to first column, first row
  lcd.setCursor(0, 0);
  // print message
  lcd.print("SYSTEM");
  delay(500);
  // clears the display to print new message
  //lcd.clear();
  // set cursor to first column, second row
  lcd.setCursor(0,1);
  lcd.print("      READY");
  String dnsname = "doorlock";

  pinMode(lock, OUTPUT);
  digitalWrite(lock, State);
  
  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  // Print ESP32 Local IP Address
  Serial.println(WiFi.localIP());


  if (MDNS.begin(dnsname)) {             // Start the mDNS responder for doorlock.local

    MDNS.addService("http", "tcp", 80);
    Serial.println("mDNS responder started at");
    Serial.print(dnsname);

  }else{
    Serial.println("Error setting up MDNS responder!");
  }
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  
}




void webSocketEvent(byte num, WStype_t type, uint8_t * payload, size_t length)
{
  if(type == WStype_TEXT)
  {

     //Serial.printf("[%u] get Text: %s\r\n", num, payload);
     String _payload = String((char *) &payload[0]);
     String statusd = getValue(_payload, '/', 0) ;
     Serial.println(statusd);
     Serial.println(statusd.length());
     if(statusd == "success"){
      notifyClients("stoptimer");
      digitalWrite(lock, LOW);
      notifyClients("unlocked");
      delay(10000);
      digitalWrite(lock, HIGH);
      notifyClients("locked");
     }
     else if(statusd == "lcd1"){
      String line1 = getValue(_payload, '/', 1);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(line1);
     }
     else if(statusd == "lcd2"){
      String line1 = getValue(_payload, '/', 1);
      String line2 = getValue(_payload, '/', 2);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(line1);
      lcd.setCursor(0, 1);
      lcd.print(line2);
     }
  }
 
  else  // event is not TEXT. Display the details in the serial monitor
  {
    //Serial.print("WStype = ");   Serial.println(type);  
    //Serial.print("WS payload = ");
// since payload is a pointer we need to type cast to char
    //for(int i = 0; i < length; i++) { Serial.print((char) payload[i]); }
    //Serial.println();
  }
}
      
      //notifyClients();

void loop() {
  
  MDNS.update();
  webSocket.loop();
}


String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}


void notifyClients(String text) {
  webSocket.broadcastTXT(text);
}
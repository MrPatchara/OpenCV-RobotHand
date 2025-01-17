#include <Arduino.h>
#include <ESP32Servo.h>
#define numOfValsRec 5
#define digitsPerValRec 1

Servo servoThumb;
Servo servoIndex;
Servo servoMiddle;
Servo servoRing;
Servo servoPinky;


int valsRec[numOfValsRec];
int stringLength = numOfValsRec * digitsPerValRec + 1; //$00000
int counter = 0;
bool counterStart = false;
String receivedString;

void setup() {
  Serial.begin(115200);
  servoThumb.attach(15);
  servoIndex.attach(16);
  servoMiddle.attach(17);
  servoRing.attach(18);
  servoPinky.attach(19);
}

void receiveData() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '$') {
      counterStart = true;
    }
    if (counterStart) {
      if (counter < stringLength) {
        receivedString = String(receivedString + c);
        counter++;
      }
      if (counter >= stringLength) {
        for (int i = 0; i < numOfValsRec; i++) {
          int num = (i * digitsPerValRec) + 1;
          valsRec[i] = receivedString.substring(num, num + digitsPerValRec).toInt();
        }
        receivedString = "";
        counter = 0;
        counterStart = false;
      }
    }
  }
}

void loop() {
  receiveData();
  if (valsRec[0] == 1) {servoThumb.write(180);}else{servoThumb.write(0);}
  if (valsRec[1] == 1) {servoIndex.write(180);}else{servoIndex.write(0);}
  if (valsRec[2] == 1) {servoMiddle.write(180);}else{servoMiddle.write(0);}
  if (valsRec[3] == 1) {servoRing.write(180);}else{servoRing.write(0);}
  if (valsRec[4] == 1) {servoPinky.write(180);}else{servoPinky.write(0);}
}


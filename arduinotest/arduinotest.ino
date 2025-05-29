#include <Servo.h>

Servo myservo;

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  myservo.attach(9);
}

void loop() {
  if (Serial.available() > 0){
    int msg = Serial.parseInt();
    myservo.write(msg);

  }

}

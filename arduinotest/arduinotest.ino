#include <Servo.h>

Servo servo_x;
Servo servo_y;

String msg;

int ind_com;

int pos_x;
int pos_y;

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  servo_x.attach(5);
  servo_y.attach(6);
  
}



void loop() {
  if (Serial.available() > 0){
    msg = Serial.readStringUntil('\n');
    ind_com = msg.indexOf(',');
    pos_x = (msg.substring(0,ind_com)).toInt();
    pos_y = (msg.substring(ind_com + 1)).toInt();
    servo_x.write(pos_x);
    servo_y.write(pos_y);
  }

}

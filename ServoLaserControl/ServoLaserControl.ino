#include <Servo.h>

Servo servo_x;
Servo servo_y;

String msg;

const int laser_pin = 2;

int ind_com_1;
int ind_com_2;

int pos_x;
int pos_y;
int las_ctrl;


void setup() {
  Serial.begin(9600);
  
  servo_x.attach(5);
  servo_y.attach(6);

  pinMode(laser_pin, OUTPUT); 
}


void loop() {
  
  if (Serial.available() > 0){
    msg = Serial.readStringUntil('\n');
    ind_com_1 = msg.indexOf(',');
    ind_com_2 = msg.indexOf(',', ind_com_1 +1 );
    pos_x = (msg.substring(0,ind_com_1)).toInt();
    pos_y = (msg.substring(ind_com_1 + 1, ind_com_2)).toInt();
    las_ctrl = (msg.substring(ind_com_2 +1).toInt());
    servo_x.write(pos_x);
    servo_y.write(pos_y);

    if (las_ctrl == 1){
      digitalWrite(laser_pin,HIGH);
    }
    else{
      digitalWrite(laser_pin,LOW);
    }
  
  }




}

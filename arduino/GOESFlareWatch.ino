/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Blink
*/

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  
  Serial.begin(9600);           // set up Serial library at 9600 bps
}

// the loop function runs over and over again forever
void loop() {

    if (Serial.available()) {
      int inByte = Serial.read();
//      Serial.write(inByte);
      if ( inByte == '0' ) {
        digitalWrite(10, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(11, LOW);
        digitalWrite(12, LOW);
        digitalWrite(13, LOW);
        delay(1000);                       // wait for a second
      } else if ( inByte == '1') {
        digitalWrite(10, LOW);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(11, HIGH);
        digitalWrite(12, LOW);
        digitalWrite(13, LOW);
      } else if ( inByte == '2') {
        digitalWrite(10, LOW);   
        digitalWrite(11, LOW);
        digitalWrite(12, HIGH);
        digitalWrite(13, LOW);

      } else if ( inByte == '3') {
        digitalWrite(10, LOW);   
        digitalWrite(11, LOW);
        digitalWrite(12, LOW);
        digitalWrite(13, HIGH);
      }
    }
}


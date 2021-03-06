/*
  GOESFlareWatch4LED - Version with 4 LEDs

  This program receives through the serial interface
  data from its brother Python program about the size of 
  the current solar activity: 1, 2, 3, and 4.

  The program in python is called the same, and is in an jupyter notebook.

  Author: Andre Csillaghy, raumschiff.org
  August 2019
  
  (Origin is the program BLIK.)
  
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
        digitalWrite(10, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(11, HIGH);
        digitalWrite(12, LOW);
        digitalWrite(13, LOW);
      } else if ( inByte == '2') {
        digitalWrite(10, HIGH);   
        digitalWrite(11, HIGH);
        digitalWrite(12, HIGH);
        digitalWrite(13, LOW);
      } else if ( inByte == '3') {
        digitalWrite(10, HIGH);   
        digitalWrite(11, HIGH);
        digitalWrite(12, HIGH);
        digitalWrite(13, HIGH);
      } else {
        digitalWrite(10, HIGH);   
        digitalWrite(11, HIGH);
        digitalWrite(12, HIGH);
        digitalWrite(13, HIGH);
      }
    }
}

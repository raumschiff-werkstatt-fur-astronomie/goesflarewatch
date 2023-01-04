/*
  GOESFlareWatch8LED - Version with 4 LEDs

  This program receives through the serial interface
  data from its brother Python program about the size of 
  the current solar activity: 1, 2, 3, and 4.

  The program in python is called the same, and is in an jupyter notebook.

  Author: Andre Csillaghy, raumschiff.org
  August 2019
  
  (Origin is the program BLIK.)
  
*/

#include <SPI.h>
#include <WiFiNINA.h>


// the setup function runs once when you press reset or power the board

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(13, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(12, OUTPUT);

  Serial.begin(9600);           // set up Serial library at 9600 bps
}

// the loop function runs over and over again forever
void loop() {

    if (Serial.available()) {
      int inByte = Serial.read();
      Serial.write(inByte);
      if ( inByte == '0' ) {
        Serial.write('x');
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, LOW);
        digitalWrite(11, LOW);
        digitalWrite(10, LOW);
        digitalWrite(9, LOW);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        delay(1000);                       // wait for a second
      } else if ( inByte == '1') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, LOW);
        digitalWrite(10, LOW);
        digitalWrite(9, LOW);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
      } else if ( inByte == '2') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, LOW);
        digitalWrite(9, LOW);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
      } else if ( inByte == '3') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, LOW);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
     } else if ( inByte == '4') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
     } else if ( inByte == '5') {
       Serial.write('b');
       digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, HIGH);
        digitalWrite(7, LOW);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
     } else if ( inByte == '6') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, HIGH);
        digitalWrite(7, HIGH);
        digitalWrite(6, LOW);
        //delay(1000);                       // wait for a second
     } else if ( inByte == '7') {
        digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(12, HIGH);
        digitalWrite(11, HIGH);
        digitalWrite(10, HIGH);
        digitalWrite(9, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, HIGH);
        digitalWrite(7, HIGH);
        digitalWrite(6, HIGH);
        delay(1000);                       // wait for a second
      } else { // THIS SHOULD NOT HAPPEN
        digitalWrite(13, HIGH);   
        digitalWrite(12, LOW);
        digitalWrite(11, HIGH);
        digitalWrite(10, LOW);
        digitalWrite(9, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(8, LOW);
        digitalWrite(7, HIGH);
        digitalWrite(6, LOW);
        delay(1000);                       // wait for a second
      }
    }
}

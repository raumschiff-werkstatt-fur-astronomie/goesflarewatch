/*

This is just a test to see how to drive the white LED strip,
using a MOSFET to bring in the 12 V
*/

#define RED_LED 6
#define BLUE_LED 5
#define GREEN_LED 9

int brightMax = 255;

int gBright = 0;
int rBright = 0;
int bBright = 0;

int fadeSpeed = 10;
int waitTime = 1000;

void setup() {
   pinMode(GREEN_LED, OUTPUT);
   pinMode(RED_LED, OUTPUT);
   pinMode(BLUE_LED, OUTPUT);
   
   pinMode(LED_BUILTIN, OUTPUT);

}

void loop() { 

//  analogWrite(RED_LED,1);
  digitalWrite(LED_BUILTIN, LOW);

// with this circuit, increasing rBright actually diminishes the
// brightness...

  rBright=0;
   for (int i = 0; i < brightMax; i++) {
       analogWrite(RED_LED, rBright);
       rBright +=1;
       delay(fadeSpeed);
   }
 
//   for (int i = 0; i < 256; i++) {
//       analogWrite(BLUE_LED, bBright);
//       bBright += 1;
//       delay(fadeSpeed);
//   } 
//
//   for (int i = 0; i < 256; i++) {
//       analogWrite(GREEN_LED, gBright);
//       gBright +=1;
//       delay(fadeSpeed);
//   } 
 

  delay(waitTime);
  
//  analogWrite(RED_LED,1);
  digitalWrite(LED_BUILTIN, HIGH);


   for (int i = 0; i < brightMax; i++) {
//       analogWrite(GREEN_LED, brightness);
       analogWrite(RED_LED, rBright);
//       analogWrite(BLUE_LED, brightness);
 
       rBright -= 1;
       delay(fadeSpeed);
   }

     delay(1000);


}

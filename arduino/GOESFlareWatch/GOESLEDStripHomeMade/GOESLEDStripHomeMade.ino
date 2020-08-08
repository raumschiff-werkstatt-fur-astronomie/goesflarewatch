/*

This is just a test to see how to drive the white LED strip,
using a MOSFET to bring in the 12 V
*/

#define RED_LED 6
#define BLUE_LED 5
#define GREEN_LED 4

int brightMax = 255;

int gBright = 0;
int rBright = 0;
int bBright = 0;

int fadeSpeed = 10;
int waitTime = 1000;

long randomN;

void setup() {
   pinMode(GREEN_LED, OUTPUT);
   pinMode(RED_LED, OUTPUT);
   pinMode(BLUE_LED, OUTPUT);
   
   pinMode(LED_BUILTIN, OUTPUT);

   Serial.begin(9600);     

}

void loop() { 

   if (Serial.available()) {
    
      int rByte = Serial.parseInt();
      int gByte = Serial.parseInt();
      int bByte = Serial.parseInt();
      //inByte = inByte - '0';

//  analogWrite(RED_LED,1);
    Serial.print("I received: ");
    Serial.print(rByte, DEC);      
    Serial.print(", ");
    Serial.print(gByte, DEC);     
    Serial.print(", ");
    Serial.println(bByte, DEC);      
   
    digitalWrite(LED_BUILTIN, HIGH);

// with this circuit, increasing rBright actually diminishes the
// brightness...

//  rBright=0;
//   for (int i = 0; i < brightMax; i++) {

//       analogWrite(RED_LED, 255);       
//       analogWrite(GREEN_LED, 255);
//       analogWrite(BLUE_LED, 255);

//       delay(1000);
// test
       
       analogWrite(RED_LED, rByte);
       analogWrite(GREEN_LED, gByte);
       analogWrite(BLUE_LED, bByte);

       
       Serial.print("random:  ");
       for (int i = 0; i < 6000; i++) {
          randomN = random(50)-25;
          analogWrite(RED_LED, rByte+randomN);
          randomN = random(50)-25;
          analogWrite(GREEN_LED, gByte+randomN);
          randomN = random(50)-25;
          analogWrite(BLUE_LED, bByte+randomN);
              
//          Serial.print(rByte+randomN, DEC);      
//          Serial.println(' ');      
   
          delay(13);
       }
       
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
 
//dlay(waitTime);
  
//  analogWrite(RED_LED,1);
//digitalWrite(LED_BUILTIN, LOW);


//   for (int i = 0; i < brightMax; i++) {
//       analogWrite(GREEN_LED, brightness);
//       analogWrite(RED_LED, rBright);
//       analogWrite(BLUE_LED, brightness);
 
//       rBright -= 1;
//     delay(fadeSpeed);
// }

     delay(1000);

   }}

/*

*/

#define RED_LED 6
#define BLUE_LED 5
#define GREEN_LED 9

int brightness = 1000;

int gBright = 0;
int rBright = 0;
int bBright = 0;

int fadeSpeed = 10;

void setup() {
   pinMode(GREEN_LED, OUTPUT);
   pinMode(RED_LED, OUTPUT);
   pinMode(BLUE_LED, OUTPUT);
   
   pinMode(LED_BUILTIN, OUTPUT);

}

void loop() { 

  /*analogWrite(RED_LED,255);*/
  digitalWrite(LED_BUILTIN, HIGH);

  rBright=0;
   for (int i = 0; i < 1024; i++) {
       analogWrite(RED_LED, rBright);
       rBright +=1;
       delay(fadeSpeed);
   }
 
   for (int i = 0; i < 256; i++) {
       analogWrite(BLUE_LED, bBright);
       bBright += 1;
       delay(fadeSpeed);
   } 

   for (int i = 0; i < 256; i++) {
       analogWrite(GREEN_LED, gBright);
       gBright +=1;
       delay(fadeSpeed);
   } 
 

  delay(1000);
  
  /*analogWrite(RED_LED,0);*/
  digitalWrite(LED_BUILTIN, LOW);

 

   brightness =1024;
   for (int i = 0; i < 1024; i++) {
       analogWrite(GREEN_LED, brightness);
       analogWrite(RED_LED, brightness);
       analogWrite(BLUE_LED, brightness);
 
       brightness -= 1;
       delay(fadeSpeed);
   }

     delay(1000);

  


}

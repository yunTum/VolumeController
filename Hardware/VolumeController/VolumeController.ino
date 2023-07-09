const int LED_PIN = 13;
int tct_val = 0;
int tggl_state = false;
int tggl_val = 0;
int vlm_val = 0;
char mes[10];

void setup() {
  // put your setup code here, to run once:
  pinMode(2, INPUT);
  pinMode(4, INPUT);
  pinMode(14, INPUT);
  //pinMode( LED_PIN, OUTPUT );
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  tggl_val = analogRead( A0 );
  tct_val = analogRead( A1 );
  vlm_val = analogRead( A2 );
  if( tggl_val > 512) {
    tggl_state = true;
  } else {
    tggl_state = false;
  }
  
  if( tct_val < 100 && tggl_state ) {
    Serial.write("#tct1,");

  } else if( 400 < tct_val && tct_val < 570 && tggl_state ) {
    Serial.write("#tct2,");            

  } else if( (600 < tct_val && tct_val < 800) &&  tggl_state ) {
    Serial.write("#tct3,");       

  }   if( tct_val < 100 && !tggl_state) {
    Serial.write("#tct4,");

  } else if( 400 < tct_val && tct_val < 570 && !tggl_state) {
    Serial.write("#tct5,");            

  } else if( 600 < tct_val && tct_val < 800 && !tggl_state) {
    Serial.write("#tct6,");
    
  } else if ( 1000 < tct_val  ){
    Serial.write("#default,"); 
  }
  Serial.println(vlm_val);
  delay(200);
  
}

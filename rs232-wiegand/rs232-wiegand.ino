#define RS232_WAIT_TIME 2000
#define MAX_BYTES 100   

unsigned char databytes[MAX_BYTES]; 

unsigned char Outdatabytes[MAX_BYTES];      
unsigned char Outdatabytes2[MAX_BYTES];

unsigned int bytecount = 0;
unsigned int rs232_counter = 0;
unsigned int SerialFlagDone = 0;
unsigned int SerialFlagStart = 1;
unsigned int SerialFlagFinished = 0;
void setup() {
  // put your setup code here, to run once:
  // configure seriall ports
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  //receive all characteers in serial
  if(Serial.available()){
    char byte1 = Serial.read();
    SerialFlagDone = 0;
    rs232_counter = RS232_WAIT_TIME;
    databytes[bytecount] = byte1;
    bytecount++;
    }

   if(!SerialFlagDone){
    if (--rs232_counter == 0)
        SerialFlagDone = 1;   
      }
    

    if(bytecount>0 && SerialFlagDone){
      
      String AllInputData = "";
      for(int x = 0; x<bytecount;x++){
        AllInputData+= databytes[x];    
        }
        
      int  ind1=AllInputData.indexOf('|');
      String antenna = AllInputData.substring(0,ind1);  
      int ind2=AllInputData.indexOf('|',ind1+1);
      String data = AllInputData.substring(ind1+1,ind2); 
      
      bytecount = 0;
      SerialFlagDone=0;
            
      }
    
  
}

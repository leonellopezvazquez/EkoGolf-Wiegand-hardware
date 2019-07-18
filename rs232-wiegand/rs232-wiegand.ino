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
  Serial3.begin(9600);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  //receive all characteers in serial
  if(Serial1.available()){
    char byte1 = Serial1.read();
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
      
      int flag =  Send_to_Controller();
            
      }
    
  
}


int Send_to_Controller(){
  String AllInputData = "";
      for(int x = 0; x<bytecount;x++){
        AllInputData+= databytes[x];    
        }

      if (AllInputData==""){
        return 0;
        
        }
        
      int  ind1=AllInputData.indexOf('|');
      String antenna = AllInputData.substring(0,ind1);  
      int ind2=AllInputData.indexOf('|',ind1+1);
      String data = AllInputData.substring(ind1+1,ind2); 

      ///depending of the antenna mux, send it to each controller
     
      if(antenna=="1"){
          for(int x =0; x<data.length();x++){
            Serial2.write(data[x]);  
          }
        }

      if(antenna=="2"){
        for(int x =0; x<data.length();x++){
            Serial3.write(data[x]);  
          }
        }
      
      bytecount = 0;
      SerialFlagDone=0;
      
      return 1;
  }

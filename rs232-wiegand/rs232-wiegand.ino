void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600);
    Serial1.begin(9600);
    Serial2.begin(9600);
    Serial3.begin(9600);
    Serial1.setTimeout(70);
}

void loop() {
  // put your main code here, to run repeatedly:

  if(Serial1.available()){
    String AllInputData = "";
    AllInputData = Serial1.readString();

        int  ind1=AllInputData.indexOf('|');
      String antenna = AllInputData.substring(0,ind1); 
       
      int ind2=AllInputData.indexOf('|',ind1+1);
      String data = AllInputData.substring(ind1+1,ind2); 
      ///depending of the antenna mux, send it to each controller
      
      if(antenna=="1"){
          for(int x =0; x<data.length();x++){ 
            Serial2.write(data[x]);  
            Serial.println(data[x]);
          }
        }

      if(antenna=="2"){
        for(int x =0; x<data.length();x++){
            Serial3.write(data[x]);  
          }
        }
    
    }
  
}

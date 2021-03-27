
int main(){
	char *data = "password"; 
	char *attempt = "password"; 
	
	int retValue = 0;	

	int i = 0;
	for (i = 0; i < 8; i++, attempt++){
		if (*attempt != data[i]){
			retValue += 1; 
		} 
	}
	return (retValue == 0); 
}


int main(){
	char *data = "password"; 
	char *attempt = "password"; 
	
	int retValue = 0;	

	int i = 0;
	for (i = 0; i < 2; i++, attempt++){
		if (*attempt != data[i]){
			retValue += 1; 
		} 
	}
	
	if (retValue == 0){
		return 42; 
	} else {
		return 99;
	}
}

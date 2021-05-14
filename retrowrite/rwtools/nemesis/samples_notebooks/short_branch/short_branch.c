
int main(){
	int secret = 4;
	if (secret < 10){
		if (secret > 1){
			secret *= 10; 
		} else {
			secret = 0; 
		}
		return secret; 
	}	
	secret *= 2;
}

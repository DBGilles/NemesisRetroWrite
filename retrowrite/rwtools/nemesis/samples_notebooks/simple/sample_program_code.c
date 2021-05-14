
int main(){
	int a = 10; 
	int b = 20; 
	if (a < b){
		int temp = b; 
		b = a; 
		a = temp; 
	} 
	return a;  
}

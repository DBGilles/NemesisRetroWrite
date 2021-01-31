
int func(int a, int b){
	if (a < b){
		int swap = a; 
		b = swap; 
		a = b; 	
		return a * b; 	
	} else if (a > b) {
		return a + b ; 
	} else { 
		return b*b; 
	} 
}

int main(){
	int x, y; 
	x = 10; 
	y = 20; 
	func(x, y); 	
}

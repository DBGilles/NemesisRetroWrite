
int main(){
	int a, b, c, d; 
	a = 100; 
	b = 20; 
	c = 30; 
	d = 40; 
	int result = 0; 
	// branch dependent secret 
	if (a < b){
		if (c < d){
			a = a + b;
			result = 0; 
		} else {
			b = b + c; 
			result = 1;
		}
	} else{ 
		if (c > d){
			c = c + b;
			result = 2; 
		} else {
			d = b + d; 
			result = 3;
		}
	}
	
	// whatever branch, this one doesn't have to be balanced 
	if (d > 100){
		result *= 2; 
    }
	return result;    
}

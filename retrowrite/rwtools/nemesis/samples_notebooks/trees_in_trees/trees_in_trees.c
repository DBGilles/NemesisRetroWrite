
int main(){
	int a, b, c, d; 
	a = 100; 
	b = 20; 
	c = 30; 
	d = 40; 
	if (a < b){
		if (c < d){
			a = a + b;
			return a; 
		} else {
			b = b + c; 
			return b;
		}
	} else{ 
		if (c > d){
			c = c + b;
			return c; 
		} else {
			d = b + d; 
			return d;
		}
	}

}

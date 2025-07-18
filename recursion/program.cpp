#include <iostream>
using namespace std;

int bhaajym(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * bhaajym ( n - 1 );
}

int main() {
    int smkhyaa = 5;
    int prinaam = bhaajym ( smkhyaa );
    cout << prinaam << endl;
    return 0;
}

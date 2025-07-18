#include <iostream>
using namespace std;

int main() {
    int x = 10;
    int y = 0;
    while (x > 0) {
        if (x % 2 == 0) {
            cout << x << endl;
            y = y + x;
        } else {
            y = y - 1;
        }
        x = x - 1;
    }
    cout << y << endl;
    return 0;
}
#include <stdio.h>
int main() {
    int a = 3;
    int b = a + 2;
    printf("%d\n", b);
    a = 10;
    if (a > 5) {
        printf("%d\n", a);
    }
    else {
        printf("%d\n", 0);
    }
    int i = 0;
    while (i < 5) {
        printf("%d\n", i);
        i = i + 1;
    }
    return 0;
}
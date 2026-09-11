int main() {
    int arr[5];
    for (int i = 0; i < 5; i++) {
        arr[i] = i * i;
    }

    printf("Array contents:\n");
    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d\n", i, arr[i]);
    }

    int x = 42;
    int *ptr = &x;
    printf("Value via pointer = %d\n", *ptr);
    *ptr = 100;
    printf("x after pointer modification = %d\n", x);

    return 0;
}

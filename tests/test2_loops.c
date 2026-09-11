int main() {
    printf("For loop:\n");
    for (int i = 0; i < 5; i++) {
        printf("i = %d\n", i);
    }

    printf("While loop with break/continue:\n");
    int j = 0;
    while (j < 10) {
        j = j + 1;
        if (j % 2 == 0) {
            continue;
        }
        if (j > 7) {
            break;
        }
        printf("j = %d\n", j);
    }
    return 0;
}

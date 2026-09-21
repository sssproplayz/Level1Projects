#include <stdio.h>
#define MAXSIZE 5
int queue[MAXSIZE];
int front = -1, rear = -1;
// INSERTION
void enqueue(int val) {
    if (rear == MAXSIZE - 1) {
        printf("QUEUE OVERFLOW!!\n");
    } else {
        if (front == -1)
            front = 0;
        rear++;
        queue[rear] = val;
    printf("%d inserted into queue.\n", val);}}
// DELETION
void dequeue() {
    if (front == -1 || front > rear) {
        printf("QUEUE UNDERFLOW!!\n");
    } else {
        printf("%d deleted from queue.\n", queue[front]);
        front++;
        // Reset queue when it becomes empty
        if (front > rear) {
            front = -1;
            rear = -1;}}}
// TRAVERSAL
void display() {
    if (front == -1 || front > rear) {
        printf("QUEUE IS EMPTY!!\n");
    } else {
        printf("Queue: ");
        for (int i = front; i <= rear; i++) {
            printf("%d ", queue[i]);}
    printf("\n");}}
int main() {
    int choice, val;
    while (1) {
        printf("\n===== QUEUE MENU =====\n");
        printf("1. Insert (Enqueue)\n");
        printf("2. Delete (Dequeue)\n");
        printf("3. Traverse (Display)\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        switch (choice) {
            case 1:
                printf("Enter value to insert: ");
                scanf("%d", &val);
                enqueue(val);
                break;
            case 2:
                dequeue();
                break   ;
            case 3:
                display();
                break;
            case 4:
                printf("Exiting program...\n");
                return 0;
            default:
                printf("INVALID CHOICE!!\n");}}
    return 0;}

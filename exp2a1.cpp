#include <stdio.h>
#include <stdlib.h>
struct node {
    int data;
    struct node *next;
};
struct node *head = NULL;
// Insert in ascending order
void insert(int value) {
    struct node *newNode, *temp;
    newNode = (struct node *)malloc(sizeof(struct node));
    newNode->data = value;
    newNode->next = NULL;
    // Insert at beginning
    if (head == NULL || value < head->data) {
        newNode->next = head;
        head = newNode;
        return;
    }
    // Find correct position
    temp = head;
    while (temp->next != NULL && temp->next->data < value) {
        temp = temp->next;
    }
    newNode->next = temp->next;
    temp->next = newNode;
}
// Delete a node
void deleteNode(int value) {
    struct node *temp, *prev;
    if (head == NULL) {
        printf("List is empty.\n");
        return;
    }
    // Delete first node
    if (head->data == value) {
        temp = head;
        head = head->next;
        free(temp);
        printf("%d deleted.\n", value);
        return;
    }
    temp = head;
    while (temp != NULL && temp->data != value) {
        prev = temp;
        temp = temp->next;
    }
    if (temp == NULL) {
        printf("%d not found.\n", value);
        return;
    }
    prev->next = temp->next;
    free(temp);
    printf("%d deleted.\n", value);
}
// Display the list
void display() {
    struct node *temp = head;
    if (head == NULL) {
        printf("List is empty.\n");
        return;
    }
    printf("Linked List: ");
    while (temp != NULL) {
        printf("%d -> ", temp->data);
        temp = temp->next;
    }
    printf("NULL\n");
}
// Reverse the list
void reverse() {
    struct node *prev = NULL;
    struct node *current = head;
    struct node *next = NULL;
    while (current != NULL) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }
    head = prev;
    printf("List reversed.\n");
}
int main() {
    int choice, value;
    while (1) {
        printf("\n--- ORDERED LINKED LIST ---\n");
        printf("1. Insert\n");
        printf("2. Delete\n");
        printf("3. Display\n");
        printf("4. Reverse\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        switch (choice) {
            case 1:
                printf("Enter value: ");
                scanf("%d", &value);
                insert(value);
                break;
            case 2:
                printf("Enter value to delete: ");
                scanf("%d", &value);
                deleteNode(value);
                break;
            case 3:
                display();
                break;
            case 4:
                reverse();
                break;
            case 5:
                exit(0);
            default:
                printf("Invalid choice.\n");
        }
    }
    return 0;
}

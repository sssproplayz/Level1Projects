#include <stdio.h>
#include <stdlib.h>
struct Node
{
    int data;
    struct Node *next;
};
struct Node *top = NULL;
void push()
{
    struct Node *newNode;
    int value;
    newNode = (struct Node *)malloc(sizeof(struct Node));
    printf("Enter element: ");
    scanf("%d", &value);
    newNode->data = value;
    newNode->next = top;
    top = newNode;
    printf("Element inserted.\n");
}
void pop()
{
    struct Node *temp;
    if (top == NULL)
    {
        printf("Stack is empty.\n");
    }
    else
    {
        temp = top;
        printf("Deleted element: %d\n", top->data);
        top = top->next;
        free(temp);
    }
}
void display()
{
    struct Node *temp = top;
    if (top == NULL)
    {
        printf("Stack is empty.\n");
    }
    else
    {
        while (temp != NULL)
        {
            printf("%d\n", temp->data);
            temp = temp->next;
        }
    }
}
void search()
{
    struct Node *temp = top;
    int value, found = 0;
    printf("Enter element to search: ");
    scanf("%d", &value);
    while (temp != NULL)
    {
        if (temp->data == value)
        {
            found = 1;
            break;
        }
        temp = temp->next;
    }
    if (found == 1)
        printf("Element found.\n");
    else
        printf("Element not found.\n");
}
int main()
{
    int choice;
    do
    {
        printf("\n1. Push\n");
        printf("2. Pop\n");
        printf("3. Display\n");
        printf("4. Search\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        switch (choice)
        {
            case 1:
                push();
                break;
            case 2:
                pop();
                break;
            case 3:
                display();
                break;
            case 4:
                search();
                break;
            case 5:
                printf("Exiting...\n");
                break;
            default:
                printf("Invalid choice.\n");
        }
    } while (choice != 5);
    return 0;
}

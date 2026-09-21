#include <iostream>
struct Node {
    int data;
    Node* next;};
Node* createList() {
    return nullptr;}
Node* insertBeginning(Node* start, int newValue) {
    Node* newNode = new Node;
    newNode->data = newValue;
    newNode->next = start;
    start = newNode;
    return start;}
void traverseList(Node* start) {
    Node* temp = start;
    if (temp == nullptr) {
        std::cout << "List is empty" << std::endl;
        return;    }
    while (temp != nullptr) {
        std::cout << temp->data << " -> ";
        temp = temp->next;    }
    std::cout << "NULL" << std::endl;}
Node* searchList(Node* start, int target) {
    Node* temp = start;
    while (temp != nullptr) {
        if (temp->data == target) {
            return temp;         }
        temp = temp->next;    }
    return nullptr;}
Node* deleteValue(Node* start, int target) {
    if (start == nullptr) {
        std::cout << "List is empty. Nothing to delete." << std::endl;
        return nullptr;    }
    Node* temp;
    if (start->data == target) {
        temp = start;
        start = start->next;
        delete temp;
        return start;    }
    Node* current = start;
    while (current->next != nullptr && current->next->data != target) {
        current = current->next;    }
    if (current->next != nullptr) {
        temp = current->next;
        current->next = current->next->next;
        delete temp;    } else {
        std::cout << "Value " << target << " not found in the list." << std::endl;    }
    return start;}
int main() {
    Node* start = createList();
    std::cout << "1. List pointer initialized.\n";
    int choice = 0;
    int value = 0;
    Node* searchResult = nullptr;
    while (true) {
        std::cout << "\n===============================\n";
        std::cout << "      LINKED LIST OPERATIONS   \n";
        std::cout << "===============================\n";
        std::cout << "1. Insert at Beginning\n";
        std::cout << "2. Traverse List (Display)\n";
        std::cout << "3. Search for a Value\n";
        std::cout << "4. Delete a Value\n";
        std::cout << "5. Exit\n";
        std::cout << "Enter your choice (1-5): ";
        std::cin >> choice;
        switch (choice) {
            case 1:
                std::cout << "Enter value to insert: ";
                std::cin >> value;
                start = insertBeginning(start, value);
                std::cout << "Inserted " << value << " successfully.\n";
                break;
            case 2:
                std::cout << "\nCurrent List: ";
                traverseList(start);
                break;
            case 3:
                std::cout << "Enter value to search for: ";
                std::cin >> value;
                searchResult = searchList(start, value);
                if (searchResult != nullptr) {
                    std::cout << "Found value " << searchResult->data << " at memory address: " << searchResult << "\n";
                } else {
                    std::cout << "Value " << value << " not found in the list.\n";                }
                break;
            case 4:
                std::cout << "Enter value to delete: ";
                std::cin >> value;
                start = deleteValue(start, value);
                break;
            case 5:
                std::cout << "Cleaning up memory and exiting program...\n";
                while (start != nullptr) {
                    Node* temp = start;
                    start = start->next;
                    delete temp;                }
                std::cout << "Goodbye!\n";
                return 0;
            default:
                std::cout << "Invalid choice! Please select an option between 1 and 5.\n";
                break;        }    }
    return 0;}

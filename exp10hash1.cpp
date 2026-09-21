#include <iostream>
using namespace std;

int main()
{
    int size, n;

    cout << "Enter hash table size: ";
    cin >> size;

    int table[size];

    for(int i = 0; i < size; i++)
        table[i] = -1;

    cout << "Enter number of keys: ";
    cin >> n;

    cout << "Enter " << n << " keys:\n";

    for(int i = 0; i < n; i++)
    {
        int key;
        cin >> key;

        int index = key % size;
        int j = 1;

        while(table[index] != -1)
        {
            index = (key + j * j) % size;
            j++;
        }

        table[index] = key;
    }

    cout << "\nQuadratic Hash Table:\n";

    for(int i = 0; i < size; i++)
    {
        cout << i << " -> " << table[i] << endl;
    }

    return 0;
}

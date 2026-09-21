#include<stdio.h>
#include<stdlib.h>
void sort(int arr[],int n){
    for(int i = 0;i<n-1;i++){
        for(int j = i+1;j<n;j++){
            if(arr[i]>arr[j]){
            int temp = arr[i];
            arr[i]= arr[j];
            arr[j] = temp;
        }
        }
    }
}
int main(){
    int n;
    printf("Enter no. of elements: ");
    scanf("%d",&n);
    int arr[n];
    for(int i =0;i<n;i++){
        printf("Enter the element: ");
        scanf("%d",&arr[i]);
    }
    sort(arr,n);
    for(int i = 0;i<n;i++){
        printf("%d ",arr[i]);
    }
}

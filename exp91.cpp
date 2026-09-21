#include<stdio.h>
#include<stdlib.h>

int main(){
int n;
printf("Enter the no. of elements to be inserted: ");
scanf("%d",&n);
int arr[n+1];
for(int i=0;i<n;i++)
{
    int val;
    printf("\nEnter %d element: ",i);
    scanf("%d",&arr[i]);
}
int max = arr[0];
for(int i =0;i<n;i++){
    if(arr[i]>max){
        max = arr[i];
    }
}
int arr1[max+1];
for(int i =0;i<max+1;i++){
    arr1[i] = 0;
}
for(int i=0;i<n;i++){
    arr1[arr[i]]++;
}
for(int i=1;i<max+1;i++){
    arr1[i] = arr1[i]+arr1[i-1];
}
int arr_fin[arr1[max]];
for(int i = 0;i<n;i++){
    arr_fin[arr1[arr[i]]-1]=arr[i];
    arr1[arr[i]]--;
}
for(int i=0;i<n;i++){
    printf("%d ",arr_fin[i]);
}
}

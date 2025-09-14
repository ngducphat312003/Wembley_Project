number = int(input("Enter a number: "))
temp = 0
temp1 = 0
for i in range(1, number +1):
    sum = 0
    temp1 = i
    while temp1 >= 10:
        temp = temp1 % 10
        temp1 = temp1 // 10
        sum += temp*temp*temp
    sum += temp1 * temp1 * temp1
    if sum == i:
        print(f"{i} is an Armstrong number")
    
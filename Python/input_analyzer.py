User_Inputs = []

print('Input Analyzer')
while True:
    User_Input = input('Enter a number (or type done to exit): \n')
    if User_Input == 'done':
        print('Goodbye!')
        break
    try:
        number = float(User_Input)
        User_Inputs.append(number)
        print(f'You entered: {number}')
    except ValueError:
        print('Error, please enter a valid number')

count = 0
for itervar in User_Inputs:
    count = count + 1

print('\nYou entered the following numbers this session')

print(User_Inputs)

print(f'count of numbers entered: {count}')

if count > 0:
    average = sum(User_Inputs)/count
    print(f'average of numbers entered: {average:.2f}')
else:
    print('No numbers were entered this session, so the average cannot be computed')
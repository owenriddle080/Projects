print('Pay Calculator')
# Define pay function
def compute_pay(rate, hours_worked):
    if hours_worked > 40:
        regular_pay = 40 * rate
        overtime_pay = (hours_worked - 40) * (rate * 1.5)
        total_pay = (regular_pay + overtime_pay)
        return regular_pay, overtime_pay, total_pay
    else:
        regular_pay = hours_worked * rate
        overtime_pay = 0
        total_pay = regular_pay
        return regular_pay, overtime_pay, total_pay
try:
    # Get user inputs for pay and hours worked
    hours_worked = float(input('Enter hours worked: \n'))
    rate = float(input('Enter pay rate: \n'))

    regular_pay, overtime_pay, total_pay = compute_pay(rate, hours_worked)

    if overtime_pay > 0:
        print('Nice! you got some overtime this pay-period.')
        print('Regular Pay: ', regular_pay,'Overtime Pay: ',overtime_pay,'Total Pay: ',total_pay)
    else:
        print('Pay: ', regular_pay)
except:
        print('error! please enter a numeric input')
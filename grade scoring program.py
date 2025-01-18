#Simple program to output grade based on score

print('Grade Scoring Program')
def computegrade(score):
   if score > 1.0 or score < 0.0:
      grade = 'Error 1, enter a valid score'
   elif score >= 0.9:
      grade = 'A'
   elif score >= 0.8:
      grade = 'B'
   elif score >= 0.7:
      grade = 'C'
   elif score >= 0.6:
      grade = 'D'
   else:
      grade = 'F' 
   return grade

try:
   score = float(input('Enter score:  \n'))

   grade = computegrade(score)

   print('Grade: ', grade)

except:
   print('Error 2, enter a valid score')

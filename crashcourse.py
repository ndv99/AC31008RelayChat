# comments are like this

"""
This is a big comment
t h i c c
"""

# variables:
number = 69
some_text = "Some text"
a_boolean = True

# print:
print("Something")
print(some_text)
print(a_boolean)

# methods/functions:
def method_name():
    another_number = 420
    print(another_number)

def method_with_vars(var1, var2):
    print(var1)
    print(var2)

method_name()
method_with_vars(69, 420)

# if blocks:
if a_boolean == True:
    print("The boolean is true!")
else:
    print("The boolean is false!")

if a_boolean:
    print("true but shorter")

# lists and loops
a_list = []

a_list.append("Text1")
a_list.append("Text2")

print(a_list)

for item in a_list:
    print(item)

bool2 = True
while bool2:
    print("something")
    bool2 = False

# classes
class CrashCourse:

    def __init__(self):
        self.some_class_value = 1
    
    def get_some_class_value(self):
        return self.some_class_value
    
    def set_some_class_value(self, new_value):
        self.some_class_value = new_value

crash_course = CrashCourse()

print(crash_course.get_some_class_value())

# inputs
an_input = input("input something pls\n")
crash_course.set_some_class_value(an_input)

print(crash_course.get_some_class_value())

# type casting
a_string_of_nums = "420"
int_nums = int(a_string_of_nums)
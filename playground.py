import re


string = "This is Python \u200ctutorial"
str_en = string.encode("ascii", "ignore")
str_de = str_en.decode()
print(str_de)

breakpoint()

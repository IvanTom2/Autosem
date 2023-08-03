import re

rx = r"(?=.*(cc2a))(?=.*(abc))(?!.*(228b))(?!.*(ggg))"
txt = "abc 228b cc2a 322a"

res = re.match(rx, txt)
print(res)

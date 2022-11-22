import ast
import re

a = str(
    "Parameters \n"\
    "----------\n"\
    "num_kernels  : int, number of random convolutional kernels (default 10,000)\n"\
    "normalise    : boolean, whether or not to normalise the input time\n"\
    "series per instance (default True)\n"\
    "n_jobs             : int, optional (default=1) The number of jobs to run in\n"\
    "parallel for `transform`. ``-1`` means using all processors.\n"\
    "random_state : int (ignored unless int due to compatability with Numba),\n"\
    "random seed (optional, default None)"
)

s2 = "n_estimatorsint, default=100\n" \
     "The number of trees in the forest."


print(a)

print(f"re::: {re.search('Parameters', a)}")

b = re.search('Parameters', a)
c = b.start()
print(c)
print(len(a))
print(a[446])
r = '[a-z_0-9 ]+ : '
param_start = re.search(r, a)
print(param_start)

el = re.search(r, a[param_start.end():])
print(el)

el = re.search("(?<=(default)[=| ]).*(?=[)])", a)
print(el.group())
lil = eval(el.group())
print(lil)
el = re.search("(?<=(default)[=| ]).*(?=[)|\n])",s2)
print(el)

print("------------------------")
matcher = "(?<=(default)[=| ]).*(?=(\)|\)\n|(?<=[^)])\n)+)"
el = re.search(matcher,s2)
print(el)
el = re.search(matcher, a)
print(el)

description_match = '(((?<=        )|, | \()+)(.|\n|\r|\t)*'

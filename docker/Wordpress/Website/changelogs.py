import random


def random_ip():
    return '.'.join(str(random.randint(1, 254)) for i in range(4))


logs = open('access.log').read()
logs = logs.split('\n')

result = ''

for l in logs:
    res = l[l.find(' '):]
    print random_ip() + res

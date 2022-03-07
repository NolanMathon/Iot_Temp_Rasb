valArduino = "C19.5|195T"

def is_good_temp(string):
    
    if string[:1] != 'C':
        return -1

    if string[-1] != 'T':
        return -1

    if '|' not in string:
        return -1

    temp = float(string[1:string.index('|')])

    validator = float(string[string.index('|')+1:-1])
    validator /= 10

    if validator == temp:
        return temp
    
    return -1

print(is_good_temp(valArduino))
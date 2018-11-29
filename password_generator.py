def leetspeak(password):
    charList = list(password)
    for x in range(0, len(charList)):
        if (charList[x] == 'a') or (charList[x] == 'A'):
                
                charList[x] = '4'
        if (charList[x] == 'e') or (charList[x] == 'E'):
                charList[x] = '3'
        if (charList[x] == 'l') or (charList[x] == 'L'):
                charList[x] = '1'
        if (charList[x] == 't') or (charList[x] == 'T'):
                charList[x] = '7'
        if (charList[x] == 'o') or (charList[x] == 'O'):
                charList[x] = '0'

    returnString = ''.join(charList)
    return returnString


def reverse(password):
    return password[::-1]

def uppercase(password):
    return str.upper(password)

def lowercase(password):
    return str.lower(password)

def generate_password_list(passwords):
    passwordSet = set()
    passwordSet.add(passwords)
    passwordSet.add(leetspeak(passwords))
    passwordSet.add(reverse(passwords))
    passwordSet.add(uppercase(passwords))
    passwordSet.add(lowercase(passwords))
    return passwordSet

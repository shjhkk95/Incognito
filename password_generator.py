def leetspeak(password):
    intab = "aeltoAELTO"
    outtab = "4317043170"
    trans = str.maketrans(intab, outtab)
    return password.translate(trans)

def reverse(password):
    return password[::-1]

def uppercase(password):
    return str.upper(password)

def lowercase(password):
    return str.lower(password)

def generate_password_list(passwords):
    size = len(passwords)
    password_set = set(passwords)
    for i in range(size):
        password_set.update([leetspeak(passwords[i]), reverse(passwords[i]), 
            uppercase(passwords[i]), lowercase(passwords[i])])
    return list(password_set)

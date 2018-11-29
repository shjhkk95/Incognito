def leetspeak(password):
    letters = 'aelto'
    leetspeak = '43170'
    trans = str.maketrans(letters, leetspeak)
    return password.lower().translate(trans)

def reverse(password):
    return password[::-1]

def uppercase(password):
    return password.upper()

def lowercase(password):
    return password.lower()

def generate_all_passwords(passwords):
    """ Modifies passwords set to include all transformations """
    passwords |= ({leetspeak(password) for password in passwords} 
                | {reverse(password) for password in passwords} 
                | {uppercase(password) for password in passwords} 
                | {lowercase(password) for password in passwords})
    return passwords

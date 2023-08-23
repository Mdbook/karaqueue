import string
import random
 
# initializing size of string
N = 10
 
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

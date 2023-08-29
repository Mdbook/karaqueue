import string
import random
  
def Generate_ID(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

import unittest
import tests
import random
import string

def RandomString(chars, number):
    return ''.join(random.choice( chars ) for x in range(number))

    
if __name__ == '__main__':
    unittest.main()

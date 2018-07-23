def dummy():
    print('I am the dummy function')
    return 0

def foobar():
    print('I am foo')
    dummy()
    print('I am bar')
    
foobar()
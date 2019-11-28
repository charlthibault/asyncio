print('\n\n####################################################')
print('Generateur...')
print('####################################################')
def simple_print_gen(msg):
    print(msg)
    yield


for _ in simple_print_gen('from_generator'):
    pass

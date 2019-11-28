print('####################################################')
print('Une coroutine est un objet awaitable ...')
print('####################################################')
async def simple_print(msg):
    print(msg)
    return


for _ in simple_print('from_coroutine').__await__():
    pass

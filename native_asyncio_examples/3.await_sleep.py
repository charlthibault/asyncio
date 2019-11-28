import asyncio


async def simple_print(msg):
    print(msg)
    return


print('\n\n####################################################')
print('Sleep 0...')
print('####################################################')
async def sleep0():
    await simple_print('1')
    await asyncio.sleep(0)
    await simple_print('2')


for _ in sleep0().__await__():
    pass


print('\n\n####################################################')
print('Sleep 1...')
print('####################################################')
async def sleep1():
    await simple_print('1')
    await asyncio.sleep(1)
    await simple_print('2')


for _ in sleep1().__await__():
    pass
import random

s = 15
n = 3

# Array aleatório
sol_orig = [random.randint(0,1) for i in range(s)]

# Cópias (lembrar que a atribuição de listas em python é sempre referência, a cópia é feita por fatiamento)
sol = sol_orig[:]
sol_diff = sol[:]

indexes = [i for i in range(s)]
    
flip_indexes = random.sample(indexes, k=n)

print('Operações do Flip:')
for i in flip_indexes:
    sol[i] = int(not bool(sol_orig[i]))
    print('i = %d; de: %d, para: %d' % (i, sol_orig[i], sol[i]))

for i in range(len(sol)):
    sol_diff[i] = int(sol_orig[i] != sol[i])

print('\n       Indexes:', indexes)
print(' Solução antes:', sol_orig)
print('Solução depois:', sol)
print('     Diferença:', sol_diff)


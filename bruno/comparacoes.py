import pandas as pd

path = 'solutions-new/'
bases = ['wines', 'moba', 'seizure']

for base in bases:
    arquivo = path + base + '/' + 'tabela_' + base + '.csv'
    csv = pd.read_csv(arquivo)
    

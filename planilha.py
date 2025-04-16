import pandas as pd

# Carregar a planilha e verificar as abas
data = pd.read_excel("vendas_pizzariav2.xlsx", sheet_name=None)
print(data.keys())  # Isso vai imprimir as abas presentes na planilha

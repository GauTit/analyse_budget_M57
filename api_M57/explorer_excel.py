"""
Script pour explorer la structure du fichier Excel de transposition
"""

import pandas as pd
from pathlib import Path

fichier_excel = Path("api_M57/docs/Table de transposition des comptes M14D_M57A_2026_vdef.xlsx")

print("="*80)
print("EXPLORATION DU FICHIER EXCEL")
print("="*80)

# Lire avec header=None pour voir les vraies données
df = pd.read_excel(fichier_excel, sheet_name='Version_2026', header=None)

print(f"\nDimensions: {df.shape}")
print(f"\nPremières 20 lignes complètes:")
print(df.head(20))

print(f"\n\nDernières 10 lignes:")
print(df.tail(10))

# Chercher des patterns
print(f"\n\nRecherche de comptes connus:")
for compte_test in ['7022', '73111', '6411', '752']:
    rows = df[df.apply(lambda row: row.astype(str).str.contains(compte_test, na=False).any(), axis=1)]
    if not rows.empty:
        print(f"\nCompte {compte_test} trouvé:")
        print(rows)

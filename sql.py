
def mapear_tipo(tipo, tamanho):
    tipos_firebird = {
        7: "SMALLINT",
        8: "INTEGER",
        9: "QUAD",
        10: "FLOAT",
        12: "DATE",
        13: "TIME",
        14: f"CHAR({tamanho})",
        16: f"NUMERIC({tamanho})",
        23: "BOOLEAN",
        27: "DOUBLE",
        35: "TIMESTAMP",
        37: f"VARCHAR({tamanho})",
        40: "CSTRING",
        45: "BLOB_ID",
        261: "BLOB"
    }
    return tipos_firebird.get(tipo, "UNKNOWN")
    
    
def gerar_alter_table(estrutura_principal, estrutura_espelho):
    comandos = []
    for tabela, colunas in estrutura_espelho.items():
        if tabela not in estrutura_principal:
            comando_create = f"CREATE TABLE {tabela} (\n"
            colunas_def = []
            for coluna, (tipo, tamanho) in colunas.items():
                tipo_sql = mapear_tipo(tipo, tamanho)
                colunas_def.append(f"    {coluna} {tipo_sql}")
            comando_create += ",\n".join(colunas_def) + "\n);"
            comandos.append(comando_create)
        else:
            for coluna, (tipo, tamanho) in colunas.items():
                if coluna not in estrutura_principal[tabela]:
                    tipo_sql = mapear_tipo(tipo, tamanho)
                    comando = f"ALTER TABLE {tabela} ADD {coluna} {tipo_sql};"
                    comandos.append(comando)
    return comandos
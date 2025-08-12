from flask import Flask, request, jsonify, render_template
import os
import fdb
from sql import gerar_alter_table

#Criado e refatorado por Luiz macedo

app = Flask(__name__)

def get_db_structure(db_path, user, password):
    if not os.path.exists(db_path):
        raise ValueError(f"Arquivo de banco de dados não encontrado: {db_path}")
    
    fbclient_path = r"C:\Program Files\Firebird\Firebird_3_0\fbclient.dll"
    if not os.path.exists(fbclient_path):
        raise ValueError(f"DLL fbclient.dll não encontrada em: {fbclient_path}")
    
    try:
        app.logger.info(f"Tentando conectar ao banco {db_path} com DLL em {fbclient_path}")
        conn = fdb.connect(
            dsn=db_path,
            user=user,
            password=password,
            fb_library_name=fbclient_path
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT 
            RF.RDB$RELATION_NAME AS TABELA, 
            RF.RDB$FIELD_NAME AS COLUNA,
            F.RDB$FIELD_TYPE AS TIPO, 
            F.RDB$FIELD_LENGTH AS TAMANHO
            FROM RDB$RELATION_FIELDS RF
            LEFT JOIN RDB$FIELDS F 
            ON RF.RDB$FIELD_SOURCE = F.RDB$FIELD_NAME
            WHERE RF.RDB$RELATION_NAME NOT LIKE 'RDB$%'
        """)

        estrutura = {}
        for tabela, coluna, tipo, tamanho in cur.fetchall():
            tabela, coluna = tabela.strip(), coluna.strip()
            if tabela not in estrutura:
                estrutura[tabela] = {}
            estrutura[tabela][coluna] = (tipo, tamanho)

        conn.close()
        return estrutura
    except fdb.OperationalError as e:
        raise ValueError(f"Erro de conexão com o banco: {str(e)}")
    except Exception as e:
        raise ValueError(f"Erro inesperado: {str(e)}")


@app.route('/depara')
def index():
    return render_template('formulario.html')


@app.route('/comparar', methods=['POST'])
def comparar():
    try:
        data = request.json
        app.logger.info('Dados recebidos: %s', data)
        estrutura_principal = get_db_structure(data["banco_principal"], data["usuario"], data["senha"])
        estrutura_espelho = get_db_structure(data["banco_espelho"], data["usuario"], data["senha"])
        alter_commands = gerar_alter_table(estrutura_principal, estrutura_espelho)
        app.logger.info('Comandos gerados: %s', alter_commands)
        return jsonify({"status": "success", "alter_table": alter_commands})
    except Exception as e:
        app.logger.error('Erro no /comparar: %s', str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
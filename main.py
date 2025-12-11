from flask import Flask, request, jsonify, render_template
import os
import fdb
from sql import gerar_alter_table
#Criado e refatorado por Luiz macedo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        banco_principal_file = request.files['banco_principal']
        banco_espelho_file = request.files['banco_espelho']
        save_dir = os.path.join(BASE_DIR, 'bancos')
        os.makedirs(save_dir, exist_ok=True)
        banco_principal_path = os.path.join(save_dir, banco_principal_file.filename)
        banco_espelho_path = os.path.join(save_dir, banco_espelho_file.filename)
        banco_principal_file.save(banco_principal_path)
        banco_espelho_file.save(banco_espelho_path)
        estrutura_principal = get_db_structure(banco_principal_path, usuario, senha)
        estrutura_espelho = get_db_structure(banco_espelho_path, usuario, senha)
        alter_commands = gerar_alter_table(estrutura_principal, estrutura_espelho)

        return jsonify({"status": "success", "alter_table": alter_commands})

    except Exception as e:
        app.logger.error('Erro no /comparar: %s', str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 

function comparar() {
    var data = {
        banco_principal: document.getElementById('banco_principal').value,
        banco_espelho: document.getElementById('banco_espelho').value,
        usuario: document.getElementById('usuario').value,
        senha: document.getElementById('senha').value
    };

    fetch('/comparar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error(`Erro no servidor: ${response.status}`);
        return response.json();
    })
    .then(data => {
        const content = Array.isArray(data.alter_table)
            ? data.alter_table.join("\n")
            : "Nenhuma alteração encontrada ou erro no processamento.";
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'alter_table_commands.txt'; 
        document.body.appendChild(a);
        a.click();
     
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Erro:', error);
        document.getElementById('resultado').innerText = `Falha: ${error.message}`;
        alert('Erro: ' + error.message);
    });
}
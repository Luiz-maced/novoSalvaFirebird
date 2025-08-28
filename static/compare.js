let arquivoPrincipal = null;
let arquivoEspelho = null;

function initDrop(dropId, inputId, callback) {
    const dropzone = document.getElementById(dropId);
    const fileInput = document.getElementById(inputId);

    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            dropzone.textContent = `Arquivo: ${file.name}`;
            callback(file);
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('over');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('over');

        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            dropzone.textContent = `Arquivo: ${file.name}`;
            callback(file);
        }
    });
}

initDrop('drop_principal', 'file_principal', (file) => arquivoPrincipal = file);
initDrop('drop_espelho', 'file_espelho', (file) => arquivoEspelho = file);

function comparar() {
    if (!arquivoPrincipal || !arquivoEspelho) {
        alert("Por favor, selecione os dois arquivos antes de comparar.");
        return;
    }

    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;

    const formData = new FormData();
    formData.append('banco_principal', arquivoPrincipal);
    formData.append('banco_espelho', arquivoEspelho);
    formData.append('usuario', usuario);
    formData.append('senha', senha);

    const xhr = new XMLHttpRequest();
    const btn = document.querySelector('.submit');

    // Criar barra de progresso
    let progressBar = document.createElement('progress');
    progressBar.value = 0;
    progressBar.max = 100;
    btn.parentNode.insertBefore(progressBar, btn.nextSibling);

    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            let percent = Math.round((e.loaded / e.total) * 100);
            progressBar.value = percent;
            btn.textContent = `Enviando... ${percent}%`;
        }
    });

    xhr.onreadystatechange = () => {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            btn.textContent = 'Comparar';
            progressBar.remove();

            if (xhr.status >= 200 && xhr.status < 300) {
                const data = JSON.parse(xhr.responseText);
                if (data.status === "success") {
                    const content = Array.isArray(data.alter_table)
                        ? data.alter_table.join("\n")
                        : "Nenhuma alteração encontrada.";
                    const blob = new Blob([content], { type: 'text/plain' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'alter_table_commands.txt';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert(`Erro: ${data.message}`);
                }
            } else {
                alert(`Erro no servidor: ${xhr.status}`);
            }
        }
    };

    xhr.open('POST', '/comparar', true);
    xhr.send(formData);
}

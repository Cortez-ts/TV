from flask import Flask, request, render_template_string, redirect, url_for
import xml.etree.ElementTree as ET
import datetime
import os
import time

app = Flask(__name__)
entries = []

template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Entradas - NF-e</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #111; /* Fundo preto */
            color: #eee;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
        }

        .title {
            text-align: center;
            margin-bottom: 20px;
            color: #66cdaa; /* Verde azulado */
        }

        .upload-container {
            border: 2px dashed #66cdaa; /* Verde azulado */
            border-radius: 10px; /* Bordas curvas */
            padding: 20px;
            cursor: pointer;
            text-align: center;
            width: 80%;
            margin: 0 auto;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .upload-container.dragover {
            background-color: #333;
        }

        .entry {
            border: 1px solid #66cdaa; /* Verde azulado */
            border-radius: 10px; /* Bordas curvas */
            padding: 10px;
            margin-bottom: 10px;
            width: 80%;
            margin: 10px auto;
        }

        .entry h2 {
            margin-top: 0;
            color: #66cdaa; /* Verde azulado */
        }

        @media (max-width: 768px) {
            .upload-container {
                width: 100%;
                height: 150px;
            }

            .entry {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Painel de Entradas - NF-e</h1>
        <div class="upload-container">
            <form id="upload-form" action="/" method="post" enctype="multipart/form-data">
                <div class="drop-zone" id="drop-zone">
                    Arraste e solte o arquivo XML aqui ou clique para selecionar
                </div>
                <input type="file" name="file" accept=".xml" id="file-input" style="display: none;">
                <button type="submit" id="submit-button" style="display: none;">Importar XML</button>
            </form>
        </div>

        <hr>

        <div>
            {% if error_message %}
                <p style="color: red;">{{ error_message }}</p>
            {% endif %}
            {% for entry in entries %}
                <div class="entry">
                    <h2>Fornecedor: {{ entry.supplier }}</h2>
                    <p><strong>NF-e:</strong> {{ entry.invoice }}</p>
                    <p><strong>Valor:</strong> R$ {{ entry.value }}</p>
                    <p><small>Recebido às {{ entry.time }}</small></p>
                </div>
            {% endfor %}
        </div>
    </div>

    <script>
        const dropZone = document.getElementById("drop-zone");
        const fileInput = document.getElementById("file-input");
        const submitButton = document.getElementById("submit-button");
        const uploadForm = document.getElementById("upload-form");

        dropZone.addEventListener("click", () => fileInput.click());

        dropZone.addEventListener("dragover", (event) => {
            event.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

        dropZone.addEventListener("drop", (event) => {
            event.preventDefault();
            dropZone.classList.remove("dragover");

            const files = event.dataTransfer.files;
            if (files.length) {
                const file = files[0];
                if (file.type === "application/xml" || file.name.endsWith(".xml")) {
                    fileInput.files = files;
                    uploadForm.submit();
                } else {
                    alert("Por favor, selecione um arquivo XML.");
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    global entries
    error_message = None

    pasta_nfe = r"C:\Users\Pólux\Documents\NF-e\XML"

    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            try:
                tree = ET.parse(file)
                root = tree.getroot()

                namespace = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
                supplier = root.find(".//ns:xNome", namespace)
                invoice = root.find(".//ns:nNF", namespace)
                value = root.find(".//ns:vNF", namespace)
                date = root.find(".//ns:dhSaiEnt", namespace)

                # Verifica se o arquivo já foi processado
                if any(entry["invoice"] == invoice.text for entry in entries):
                    error_message = "Este arquivo já foi processado."
                else:
                    new_entry = {
                        "supplier": supplier.text if supplier is not None else "Desconhecido",
                        "invoice": invoice.text if invoice is not None else "N/A",
                        "value": f"{float(value.text):.2f}" if value is not None else "0.00",
                        "time": datetime.datetime.now().strftime("%H:%M:%S"),
                        "date": date.text if date is not None else "Data não encontrada"
                    }

                    entries.insert(0, new_entry)

            except FileNotFoundError:
                error_message = "Arquivo XML não encontrado."
            except ET.ParseError:
                error_message = "Erro ao analisar o arquivo XML. Verifique a formatação."
            except AttributeError:
                error_message = "Arquivo XML inválido. Verifique se ele contém os campos necessários (xNome, nNF, vNF)."
            except Exception as e:
                error_message = f"Ocorreu um erro: {e}"

        if error_message:
            return render_template_string(template, entries=entries, error_message=error_message)

        return redirect(url_for('index'))

    return render_template_string(template, entries=entries, error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
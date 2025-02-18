import os
import xml.etree.ElementTree as ET
import datetime
import streamlit as st
import time

# Função para carregar e processar os arquivos XMLs
def carregar_nfes(pasta_xml):
    nfes = []
    if not os.path.exists(pasta_xml):
        return nfes  # Retorna lista vazia se a pasta não existir
    
    arquivos = os.listdir(pasta_xml)
    # st.write("📂 Arquivos na pasta:", arquivos)  # Debug para verificar XMLs (removido)

    for arquivo in arquivos:
        if arquivo.endswith(".xml"):
            caminho_completo = os.path.join(pasta_xml, arquivo)
            try:
                tree = ET.parse(caminho_completo)
                root = tree.getroot()

                # Extração de dados básicos
                ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
                numero_nfe = root.find(".//ns:ide/ns:nNF", ns)
                data_emissao = root.find(".//ns:ide/ns:dhEmi", ns)
                emitente = root.find(".//ns:emit/ns:xNome", ns)
                valor = root.find(".//ns:det/ns:prod/ns:vProd", ns)

                # Formatar data de emissão para "dd/mm/aaaa"
                if data_emissao is not None:
                    data_emissao_formatada = datetime.datetime.strptime(data_emissao.text[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
                else:
                    data_emissao_formatada = "Desconhecido"

                nfes.append({
                    "numero": numero_nfe.text if numero_nfe is not None else "Desconhecido",
                    "data": data_emissao_formatada,
                    "emitente": emitente.text if emitente is not None else "Desconhecido",
                    "valor": valor.text if valor is not None else "Desconhecido"
                })
            except Exception as e:
                st.error(f"Erro ao processar {arquivo}: {e}")

    return nfes

# Definir pasta com os XMLs
pasta_xml = "./xmls"
if not os.path.exists(pasta_xml):
    os.makedirs(pasta_xml)

# Upload de arquivos XML diretamente pelo Streamlit
uploaded_file = st.file_uploader("📤 Enviar NF-e (XML)", type="xml")
if uploaded_file is not None:
    caminho_arquivo = os.path.join(pasta_xml, uploaded_file.name)
    with open(caminho_arquivo, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"NF-e {uploaded_file.name} adicionada!")
    st.experimental_rerun()

# Carregar as NF-e
nfes = carregar_nfes(pasta_xml)

# Ordenar NF-e por data de emissão (do mais recente para o mais antigo)
nfes.sort(key=lambda x: x['data'], reverse=True)

# Limitar a exibição a 15 NF-e
nfes_exibidas = nfes[:15]

data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
notas_hoje = [nfe for nfe in nfes_exibidas if nfe['data'] == data_atual]

st.title("📋 Visualização de NF-e")
st.metric(label="Notas recebidas hoje", value=len(notas_hoje))

st.subheader("🔍 Detalhes das Notas Fiscais")
for nfe in nfes_exibidas:
    st.write(f"📝 **NF {nfe['numero']}**")
    st.write(f"Emitente: {nfe['emitente']}")
    st.write(f"Data de Emissão: {nfe['data']}")
    st.write(f"Valor: R$ {nfe['valor']}")

st.caption("🔄 Atualizado automaticamente conforme novos XMLs são adicionados.")

# Adicionar código para forçar atualização a cada 10 segundos
time.sleep(10)
st.experimental_rerun()

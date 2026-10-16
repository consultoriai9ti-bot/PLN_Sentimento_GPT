MIT License

Copyright (c) 2026 AI Software Architecture

Permissão concedida, de forma gratuita, a qualquer pessoa que obtenha uma cópia...

import json
import streamlit as st
from openai import AzureOpenAI

Configuração da Página do Streamlit

st.set_page_config(
page_title="Extrator de Dados Inteligente | Azure AI",
page_icon="🤖",
layout="centered"
)

Estilização visual moderna com CSS injetado

st.markdown("""

""", unsafe_allow_html=True)

Cabeçalho da Aplicação na Tela Principal

st.markdown('🤖 Extrator de Dados Inteligente', unsafe_allow_html=True)
st.markdown('Utilizando Azure OpenAI e Modelos Avançados para análise estruturada de texto em uma única tela.', unsafe_allow_html=True)

Guia Didático para Configuração do Secrets (Exibido de forma limpa na barra lateral)

with st.sidebar:
header = "⚙️ Configuração & Credenciais"
st.header(header)
st.markdown("""
Para configurar o seu ambiente local com as credenciais do Azure Foundry, crie uma pasta .streamlit na raiz e um arquivo secrets.toml com o seguinte formato:

```toml
[azure_openai]
api_key = "SUA_API_KEY"
endpoint = "SEU_ENDPOINT"
deployment_name = "gpt-4.1-mini"
```
""")
st.info("O sistema tentará ler do `st.secrets` automaticamente, utilizando fallback seguro integrado caso não encontre.")


Verificação de credenciais via st.secrets ou fallback didático fornecido

try:
AZURE_API_KEY = st.secrets["azure_openai"]["api_key"]
AZURE_ENDPOINT = st.secrets["azure_openai"]["endpoint"]
DEPLOYMENT_NAME = st.secrets["azure_openai"]["deployment_name"]
except Exception:
AZURE_API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
AZURE_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
DEPLOYMENT_NAME = "gpt-4.1-mini"

Inicialização do Cliente Azure OpenAI com Cache

@st.cache_resource
def get_azure_client():
return AzureOpenAI(
api_key=AZURE_API_KEY,
api_version="2024-02-15-preview",
azure_endpoint=AZURE_ENDPOINT
)

try:
client = get_azure_client()
except Exception as e:
st.error(f"Erro ao inicializar o cliente Azure OpenAI: {e}")

Layout Principal em Tela Única

st.markdown("---")
texto_usuario = st.text_area(
"Insira o texto para extração inteligente de dados:",
placeholder="Ex: Reunião crítica marcada com João e Carlos para amanhã às 14h...",
height=140
)

Botão de Ação Única

if st.button("Processar Texto", type="primary", use_container_width=True):
if not texto_usuario.strip():
st.warning("Por favor, digite um texto válido antes de prosseguir.")
else:
with st.spinner("Conectando ao Azure OpenAI e processando dados..."):
try:
system_prompt = (
"Você é um assistente especialista em extração de dados e análise de texto. "
"Sua tarefa é analisar o texto fornecido pelo usuário e retornar ESTRITAMENTE "
"um objeto JSON válido (sem blocos de código markdown adicionais ou texto fora do JSON) "
"contendo exatamente as seguintes chaves:\n"
"1. 'sentimento': string descritiva do sentimento geral (ex: Positivo, Neutro, Negativo).\n"
"2. 'porcentagem_sentimento': número inteiro de 0 a 100 indicando a intensidade/confiança do sentimento predominante.\n"
"3. 'assunto_principal': string resumindo o tema central do texto.\n"
"4. 'pessoas_citadas': lista de strings contendo os nomes das pessoas mencionadas no texto (vazia se não houver).\n"
"5. 'nivel_de_urgencia': string estritamente igual a 'Baixo', 'Medio' ou 'Alto'."
)

            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto_usuario}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )

            conteudo_resposta = response.choices[0].message.content
            dados_analisados = json.loads(conteudo_resposta)

            st.success("Análise concluída com sucesso!")
            st.markdown("### 📊 Resultados da Extração")

            # Métricas em colunas unificadas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Urgência", value=dados_analisados.get("nivel_de_urgencia", "N/A"))
            with col2:
                st.metric(label="Sentimento", value=dados_analisados.get("sentimento", "N/A"))
            with col3:
                porcentagem = dados_analisados.get("porcentagem_sentimento", 0)
                st.metric(label="Intensidade", value=f"{porcentagem}%")

            st.markdown(f"**Assunto Principal:** {dados_analisados.get('assunto_principal', 'N/A')}")
            
            pessoas = dados_analisados.get("pessoas_citadas", [])
            if pessoas:
                st.markdown("**Pessoas Citadas:**")
                for p in pessoas:
                    st.markdown(f"- {p}")
            else:
                st.markdown("**Pessoas Citadas:** Nenhuma identificada.")

            with st.expander("🔍 Visualizar JSON Bruto da API"):
                st.json(dados_analisados)

        except json.JSONDecodeError:
            st.error("Erro ao decodificar a resposta do modelo para JSON.")
            st.text(conteudo_resposta)
        except Exception as e:
            st.error(f"Erro na comunicação com o Azure OpenAI: {e}")

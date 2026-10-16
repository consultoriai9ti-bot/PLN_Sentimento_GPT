import json
import os
import streamlit as st
from openai import AzureOpenAI

# ==========================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="NEO-EXTRACT // AI Core",
    page_icon="⚡",
    layout="centered",
)

# ==========================================
# ESTILIZAÇÃO CSS FUTURISTA (CYBER / SCI-FI)
# ==========================================
st.markdown(
    """
    <style>
    /* Tema geral escuro com toque tecnológico */
    .stApp {
        background-color: #050b14;
        color: #00f0ff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Cabeçalhos estilizados */
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 1px;
    }

    /* Caixa de texto / Text Area */
    .stTextArea textarea {
        background-color: #0b192c !important;
        color: #00f0ff !important;
        border: 1px solid #1e3e62 !important;
        border-radius: 6px !important;
        box-shadow: inset 0 0 8px rgba(0, 240, 255, 0.1);
    }
    .stTextArea textarea:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4) !important;
    }

    /* Botão Principal Futurista */
    .stButton button {
        background: linear-gradient(90deg, #0077b6 0%, #00f0ff 100%) !important;
        color: #050b14 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.8);
    }

    /* Métricas estilizadas */
    div[data-testid="stMetric"] {
        background-color: #0b192c;
        border: 1px solid #1e3e62;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.05);
    }
    div[data-testid="stMetric"] label {
        color: #8da4ef !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00f0ff !important;
        text-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
    }

    /* Sidebar futurista */
    [data-testid="stSidebar"] {
        background-color: #080f1a;
        border-right: 1px solid #1e3e62;
    }
    
    /* Divisor neon */
    hr {
        border-color: #1e3e62 !important;
        box-shadow: 0 0 5px rgba(0, 240, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# INSTRUÇÕES DE CONFIGURAÇÃO (SECRETS)
# ==========================================
with st.sidebar:
  st.header("⚙️ SYSTEM CONFIG")
  st.markdown(
      """
        <div style="font-size: 0.9em; color: #a5b4fc;">
        Para inicializar o link neural localmente, configure a pasta <b>`.streamlit`</b> e crie o arquivo <b>`secrets.toml`</b>:
        </div>
        
        ```toml
        AZURE_OPENAI_API_KEY = "sua_chave_aqui"
        AZURE_OPENAI_ENDPOINT = "[https://seu-recurso.services.ai.azure.com/](https://seu-recurso.services.ai.azure.com/)"
        AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
        ```
        """,
      unsafe_allow_html=True,
  )


# ==========================================
# CARREGAMENTO DE CREDENCIAIS
# ==========================================
def obter_cliente_azure():
  try:
    # Tenta carregar do Streamlit Secrets (Ideal para produção e Streamlit Community Cloud)
    api_key = st.secrets["AZURE_OPENAI_API_KEY"]
    endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
    deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
  except Exception:
    # Fallback para fins educacionais/testes caso secrets.toml não exista
    api_key = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
    endpoint = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
    deployment = "gpt-4.1-mini"

  client = AzureOpenAI(
      api_key=api_key,
      api_version="2024-02-01",
      azure_endpoint=endpoint,
  )
  return client, deployment


# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.title("⚡ NEO-EXTRACT // AI CORE")
st.markdown(
    "<span style='color: #8da4ef;'>Insira o fluxo de dados textuais para"
    " processamento neural de sentimento, extração de entidades e nível de"
    " urgência via <b style='color: #00f0ff;'>Azure OpenAI</b>.</span>",
    unsafe_allow_html=True,
)

texto_usuario = st.text_area(
    "Fluxo de Entrada de Dados:",
    placeholder=(
        "Exemplo: 'O sistema de faturamento caiu novamente hoje de manhã e a"
        " diretoria está cobrando uma solução imediata! Preciso de ajuda"
        " urgente do suporte.'"
    ),
    height=150,
)

if st.button("PROCESSAR DADOS", type="primary"):
  if not texto_usuario.strip():
    st.warning("⚠️ Insira dados válidos no campo de texto antes de processar.")
  else:
    with st.spinner("🔄 Estabelecendo conexão neural e processando..."):
      try:
        client, deployment_name = obter_cliente_azure()

        system_prompt = (
            "Você é um assistente especialista em análise de dados textuais.\n"
            "Analise o texto fornecido pelo usuário e retorne ESTRITAMENTE um"
            " JSON válido contendo exatamente as seguintes chaves:\n"
            '1. "sentimento": (string descrevendo o sentimento geral, ex: Positivo,'
            " Neutro, Negativo)\n"
            '2. "porcentagem_sentimento": (número inteiro de 0 a 100 indicando a'
            " intensidade ou confiança daquele sentimento)\n"
            '3. "assunto_principal": (string resumindo o tema central do'
            " texto)\n"
            '4. "pessoas_citadas": (lista de strings com os nomes das pessoas'
            " mencionadas; se nenhuma, retorne lista vazia [])\n"
            '5. "nivel_de_urgencia": (string contendo estritamente um destes'
            ' valores: "Baixo", "Medio" ou "Alto")\n\n'
            "NÃO inclua nenhuma formatação markdown extra (como ```json) ou"
            " comentários fora do objeto JSON."
        )

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto_usuario},
            ],
            temperature=0.3,
        )

        conteudo_resposta = response.choices[0].message.content.strip()

        # Limpeza defensiva caso o modelo retorne blocos markdown por engano
        if conteudo_resposta.startswith("```json"):
          conteudo_resposta = conteudo_resposta[7:]
        if conteudo_resposta.endswith("```"):
          conteudo_resposta = conteudo_resposta[:-3]
        conteudo_resposta = conteudo_resposta.strip()

        dados_json = json.loads(conteudo_resposta)

        st.success("✔ Processamento neural concluído com sucesso!")
        st.divider()

        # Exibição estruturada dos resultados
        st.subheader("📊 PAINEL DE RESULTADOS")

        col1, col2 = st.columns(2)

        with col1:
          st.metric(
              label="SENTIMENTO DETECTADO",
              value=dados_json.get("sentimento", "N/A"),
              delta=f"{dados_json.get('porcentagem_sentimento', 0)}% de intensidade",
          )
          st.metric(
              label="NÍVEL DE URGÊNCIA",
              value=dados_json.get("nivel_de_urgencia", "N/A"),
          )

        with col2:
          st.text_input(
              "ASSUNTO PRINCIPAL",
              value=dados_json.get("assunto_principal", "N/A"),
              disabled=True,
          )

          pessoas = dados_json.get("pessoas_citadas", [])
          if pessoas:
            st.markdown(
                "<div style='font-weight: bold; margin-bottom: 5px; color:"
                " #8da4ef;'>PESSOAS CITADAS:</div>",
                unsafe_allow_html=True,
            )
            for p in pessoas:
              st.markdown(f"<span style='color: #00f0ff;'>▸ {p}</span>", unsafe_allow_html=True)
          else:
            st.markdown(
                "<div style='color: #8da4ef; font-weight: bold;'>PESSOAS"
                " CITADAS: <span style='color: #a5b4fc; font-weight: normal;'>Nenhuma"
                " identificada.</span></div>",
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown("### 🗄️ PAYLOAD JSON BRUTO")
        st.json(dados_json)

      except json.JSONDecodeError:
        st.error(
            "Erro crítico: O modelo retornou uma resposta incompatível com o"
            " formato JSON."
        )
        st.text(conteudo_resposta)
      except Exception as e:
        st.error(f"Erro na interface de comunicação com a Azure OpenAI: {e}")

# ==========================================
# RODAPÉ - LICENÇA MIT
# ==========================================
st.markdown("---")
st.caption(
    "MIT License — Extrator de Dados Inteligente (Neon Core Interface)"
)

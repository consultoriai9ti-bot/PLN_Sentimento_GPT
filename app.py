import json
import os
import streamlit as st
from openai import AzureOpenAI

# ==========================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Extrator de Dados Inteligente - Azure OpenAI",
    page_icon="🤖",
    layout="centered",
)


# ==========================================
# INSTRUÇÕES DE CONFIGURAÇÃO (SECRETS)
# ==========================================
with st.sidebar:
  st.header("⚙️ Configuração")
  st.markdown(
      """
        Para que este aplicativo funcione localmente, crie uma pasta chamada **`.streamlit`** na raiz do seu projeto e dentro dela um arquivo chamado **`secrets.toml`** com o seguinte conteúdo:
        
        ```toml
        AZURE_OPENAI_API_KEY = "sua_chave_aqui"
        AZURE_OPENAI_ENDPOINT = "[https://seu-recurso.services.ai.azure.com/](https://seu-recurso.services.ai.azure.com/)"
        AZURE_OPENAI_DEPLOYMENT = "gpt-4.1-mini"
        ```
        """
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
    # ATENÇÃO: Em produção, utilize sempre o st.secrets ou variáveis de ambiente.
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
st.title("📊 Extrator de Dados Inteligente")
st.markdown(
    "Insira um texto abaixo para realizar a análise inteligente de sentimento,"
    " extração de assunto, entidades e nível de urgência usando **Azure"
    " OpenAI**."
)

texto_usuario = st.text_area(
    "Digite o texto para análise:",
    placeholder=(
        "Exemplo: 'O sistema de faturamento caiu novamente hoje de manhã e a"
        " diretoria está cobrando uma solução imediata! Preciso de ajuda"
        " urgente do suporte.'"
    ),
    height=150,
)

if st.button("Processar Texto", type="primary"):
  if not texto_usuario.strip():
    st.warning("Por favor, digite algum texto antes de processar.")
  else:
    with st.spinner("Analisando com Azure OpenAI..."):
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

        st.success("Análise concluída com sucesso!")
        st.divider()

        # Exibição estruturada dos resultados
        st.subheader("📋 Resultados da Extração")

        col1, col2 = st.columns(2)

        with col1:
          st.metric(
              label="Sentimento",
              value=dados_json.get("sentimento", "N/A"),
              delta=f"{dados_json.get('porcentagem_sentimento', 0)}% de intensidade",
          )
          st.metric(
              label="Nível de Urgência",
              value=dados_json.get("nivel_de_urgencia", "N/A"),
          )

        with col2:
          st.text_input(
              "Assunto Principal",
              value=dados_json.get("assunto_principal", "N/A"),
              disabled=True,
          )

          pessoas = dados_json.get("pessoas_citadas", [])
          if pessoas:
            st.write("**Pessoas Citadas:**")
            for p in pessoas:
              st.markdown(f"- {p}")
          else:
            st.write("**Pessoas Citadas:** Nenhuma identificada.")

        st.divider()
        st.markdown("### 🔍 JSON Bruto Retornado pela API")
        st.json(dados_json)

      except json.JSONDecodeError:
        st.error(
            "O modelo retornou uma resposta que não pôde ser interpretada"
            " como JSON válido."
        )
        st.text(conteudo_resposta)
      except Exception as e:
        st.error(
            f"Ocorreu um erro ao comunicar com a API da Azure OpenAI: {e}"
        )

# ==========================================
# RODAPÉ - LICENÇA MIT
# ==========================================
st.markdown("---")
st.caption(
    "MIT License — Extrator de Dados Inteligente com Azure OpenAI e Streamlit"
)

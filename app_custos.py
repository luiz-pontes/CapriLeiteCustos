import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA & BRAND BOARD MULTVET
# ==========================================
st.set_page_config(
    page_title="MultVet CapriLeite Custos - Gestão de Leite de Cabra",
    page_icon="🐐",
    layout="wide"
)

# Estilização CSS com a Brand Board da MultVet
st.markdown("""
    <style>
    :root {
        --multvet-primary: #1e5631;
        --multvet-secondary: #2e7d32;
        --multvet-bg: #f4f6f8;
    }
    
    .stApp {
        background-color: var(--multvet-bg);
    }
    
    .brand-header {
        background: linear-gradient(135deg, #1e5631 0%, #2e7d32 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    .brand-header h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .brand-header p {
        color: #e8f5e9 !important;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }

    .metric-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 10px;
        border-left: 5px solid var(--multvet-primary);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .report-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
        border-left: 6px solid var(--multvet-primary);
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-top: 20px;
    }

    .stButton > button {
        background-color: var(--multvet-secondary) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: var(--multvet-primary) !important;
    }

    @media print {
        [data-testid="stSidebar"], header, footer, .stButton, .no-print {
            display: none !important;
        }
        .report-box {
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CABEÇALHO DO APLICATIVO
# ==========================================
st.markdown("""
    <div class="brand-header">
        <h1>🐐 MultVet CapriLeite Custos</h1>
        <p>MultVet Saúde na Prática | Calculadora de Custo do Litro de Leite de Cabra & Lucratividade</p>
    </div>
""", unsafe_allow_html=True)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Chave de API não encontrada nos Secrets! Adicione GEMINI_API_KEY nos Secrets do Streamlit Cloud.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ==========================================
# 3. FORMULÁRIO DE DADOS FINANCEIROS
# ==========================================
st.subheader("📋 Dados da Produção e Custos Diários")

col1, col2, col3 = st.columns(3)

with col1:
    num_cabras = st.number_input("Nº de Cabras em Lactação", min_value=1, value=15, step=1)
    prod_diaria = st.number_input("Produção Total Diária (Litros/dia)", min_value=0.1, value=37.5, step=0.5)
    preco_litro = st.number_input("Preço de Venda do Litro (R$)", min_value=0.1, value=3.50, step=0.10)

with col2:
    custo_volumoso_dia = st.number_input("Custo Diário com Volumoso (R$)", min_value=0.0, value=25.0, step=1.0)
    custo_concentrado_dia = st.number_input("Custo Diário com Concentrado/Ração (R$)", min_value=0.0, value=45.0, step=1.0)

with col3:
    custo_outros_dia = st.number_input("Outros Custos Diários (Mão de obra, med., energia - R$)", min_value=0.0, value=15.0, step=1.0)

st.markdown("---")

# ==========================================
# 4. CÁLCULOS MATEMÁTICOS EM TEMPO REAL
# ==========================================
custo_total_dia = custo_volumoso_dia + custo_concentrado_dia + custo_outros_dia
custo_por_litro = custo_total_dia / prod_diaria if prod_diaria > 0 else 0.0
receita_diaria = prod_diaria * preco_litro
lucro_diario = receita_diaria - custo_total_dia
lucro_mensal = lucro_diario * 30
margem_lucro_pct = (lucro_diario / receita_diaria * 100) if receita_diaria > 0 else 0.0

# Exibição dos cards de resultados
m1, m2, m3, m4 = st.columns(4)
m1.metric("Custo / Litro", f"R$ {custo_por_litro:.2f}")
m2.metric("Preço de Venda / Litro", f"R$ {preco_litro:.2f}")
m3.metric("Lucro Líquido / Dia", f"R$ {lucro_diario:.2f}", delta=f"{margem_lucro_pct:.1f}% Margem")
m4.metric("Lucro Líquido / Mês (Estimado)", f"R$ {lucro_mensal:.2f}")

st.markdown("---")

# ==========================================
# 5. ANÁLISE CONSULTIVA COM IA
# ==========================================
if st.button("📊 Gerar Análise Econômica da Produção"):
    with st.spinner("O Médico Veterinário Virtual da MultVet está analisando a viabilidade financeira..."):
        try:
            data_atual = datetime.now().strftime("%d/%m/%Y")
            
            model = genai.GenerativeModel('gemini-3.6-flash')
            
            prompt = f"""
            Você é um assistente técnico gerando um relatório financeiro e zootécnico veterinário oficial.
            Crie um diagnóstico econômico do lote de caprinos leiteiros.

            INFORMAÇÕES OBRIGATÓRIAS DO CABEÇALHO:
            - Marca: MULTVET SAÚDE NA PRÁTICA - CAPRILEITE CUSTOS
            - Responsável Técnico: Dr. Luiz Pontes - Médico Veterinário
            - Data de Emissão: {data_atual}

            DADOS FINANCEIROS ENVIADOS:
            - Cabras em Lactação: {num_cabras}
            - Produção Total: {prod_diaria} L/dia (Média: {prod_diaria/num_cabras:.2f} L/cabra/dia)
            - Custo do Volumoso/dia: R$ {custo_volumoso_dia:.2f}
            - Custo do Concentrado/dia: R$ {custo_concentrado_dia:.2f}
            - Outros Custos/dia: R$ {custo_outros_dia:.2f}
            - Custo Total Diário: R$ {custo_total_dia:.2f}
            - Custo Real por Litro Produzido: R$ {custo_por_litro:.2f}
            - Preço de Venda do Litro: R$ {preco_litro:.2f}
            - Lucro Líquido Diário: R$ {lucro_diario:.2f}
            - Lucro Líquido Mensal Estimado: R$ {lucro_mensal:.2f}
            - Margem de Lucro: {margem_lucro_pct:.1f}%

            ESTRUTURA DO DIAGNÓSTICO:
            1. Cabeçalho formatado com os dados acima.
            2. Diagnóstico da Saúde Financeira do Capril (Análise se a margem está excelente, moderada ou crítica).
            3. Participação do Custo de Ração na Receita (% gasto em alimentação vs faturamento total).
            4. Recomendações Práticas do Dr. Luiz Pontes para Aumentar a Margem por Litro (Estratégia de volumoso, ajuste de concentrado e gestão).
            """
            
            response = model.generate_content(prompt)
            
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown(response.text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.success("✅ Diagnóstico Econômico gerado com sucesso!")
            st.markdown("---")
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="📄 Baixar Diagnóstico Financeiro (.txt)",
                    data=response.text,
                    file_name=f"Diagnostico_CapriLeite_Custos_{data_atual.replace('/', '-')}.txt",
                    mime="text/plain"
                )
            with c2:
                st.info("💡 **Para Imprimir ou Salvar em PDF:** Pressione **Ctrl + P** no teclado.")
            
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar a análise: {e}")

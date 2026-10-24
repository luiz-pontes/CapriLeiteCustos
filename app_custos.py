import json
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
from calculos import DEFAULTS, CUSTOS, calcular, validar

st.set_page_config(page_title='MultVet — LucroLeite Caprinos PRO', page_icon='🐐', layout='wide')
# Não retirar este bloqueio antes da integração e dos testes do controle de acesso.
# Não há opção pública de contornar a manutenção.
try:
    revisao_local = st.secrets.get('REVISAO_LOCAL', False) is True
except FileNotFoundError:
    revisao_local = False
if not revisao_local:
    st.warning('O MultVet LucroLeite Caprinos PRO está temporariamente em manutenção.')
    st.stop()

st.markdown('''<style>.stApp{background:#f5f4ed;color:#173e32}h1,h2,h3{color:#173e32!important}[data-testid="stMetric"]{background:white;padding:16px;border-radius:12px;border-top:4px solid #c4a45d}</style>''', unsafe_allow_html=True)
st.title('🐐 MultVet — LucroLeite Caprinos PRO')
st.caption('Custos e resultado econômico da produção de leite de cabra')
st.info('Ambiente de revisão. Acesso comercial previsto: 12 meses, sem renovação automática. Preço definido: R$ 52,75. A integração de compra ainda não está ativa nesta versão.')
LABELS = dict(cabras='Cabras em lactação', litros='Produção total de leite (L/dia)', preco='Preço de venda (R$/L)', dias='Dias do período', volumoso='Volumoso', concentrado='Concentrado / ração', sanidade='Sanidade', mao_obra='Mão de obra paga', energia='Energia, água e combustível', outros='Outros gastos pagos', manutencao='Manutenção', depreciacao='Depreciação rateada', mao_obra_familiar='Mão de obra familiar estimada', capital='Custo de oportunidade do capital')
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
with st.expander('Restaurar dados de um arquivo JSON'):
    arquivo = st.file_uploader('Selecione o arquivo exportado pela LucroLeite', type='json')
    if st.button('Carregar dados', disabled=arquivo is None):
        try:
            if arquivo.size > 100_000:
                raise ValueError('Arquivo muito grande.')
            obj = json.loads(arquivo.getvalue())
            if obj.get('aplicativo') != 'multvet_lucroleite' or obj.get('versao') != 1:
                raise ValueError('Arquivo de outro aplicativo ou versão.')
            st.session_state.update(validar(obj['dados']))
            st.success('Dados carregados.')
        except (ValueError, KeyError, TypeError, AttributeError) as erro:
            st.error(f'Não foi possível importar: {erro}')
st.subheader('Produção e venda')
cols = st.columns(2)
for i, k in enumerate(('cabras','litros','preco','dias')):
    with cols[i % 2]:
        st.number_input(LABELS[k], min_value=1 if k in ('cabras','dias') else 0., step=1 if k in ('cabras','dias') else .1, key=k)
st.subheader('Custos do grupo de cabras — R$/dia')
st.caption('Rateie despesas mensais e anuais por dia. Inclua os custos atribuíveis ao leite; evite contabilizar a mesma despesa duas vezes. Valores de exemplo devem ser substituídos.')
cols = st.columns(2)
for i,k in enumerate(CUSTOS):
    with cols[i%2]:
        st.number_input(LABELS[k]+' (R$/dia)', min_value=0., step=1., key=k)
d = {k:st.session_state[k] for k in DEFAULTS}
r = calcular(d)
def br(v):
    return f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if v is not None else 'Não calculável'
cols = st.columns(3)
cols[0].metric('Custo total informado / litro', 'R$ '+br(r['custo_litro']) if r['custo_litro'] is not None else 'Sem produção')
cols[1].metric('Resultado estimado / dia', 'R$ '+br(r['resultado']))
cols[2].metric('Resultado no período', 'R$ '+br(r['resultado_periodo']))
st.caption('O resultado considera apenas os custos informados. A projeção mantém produção, preço e despesas constantes durante o período.')
if not d['litros']:
    st.warning('Sem produção de leite: o custo por litro não pode ser calculado. Os custos diários continuam no resultado.')
st.subheader('Detalhamento')
NOMES = dict(coe='COE — Custo Operacional Efetivo (R$/dia)', cot='COT — Custo Operacional Total (R$/dia)', total='Custo total informado (R$/dia)', receita='Receita do leite (R$/dia)', resultado='Resultado estimado (R$/dia)', resultado_periodo='Resultado no período (R$)', litros_cabra='Produção média (L/cabra/dia)', custo_litro='Preço de equilíbrio (R$/L)', margem='Margem sobre a receita (%)', equilibrio_litros='Produção de equilíbrio ao preço informado (L/dia)')
st.table([{'Indicador':v,'Valor':br(r[k])} for k,v in NOMES.items()])
st.caption('COE: gastos operacionais pagos. COT: COE + depreciação + mão de obra familiar estimada. Custo total informado: COT + custo de oportunidade do capital. A produção de equilíbrio supõe despesas constantes; não representa uma recomendação de aumento de produção.')
agora = datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M')
relatorio = '\n'.join(['MULTVET — LUCROLEITE CAPRINOS PRO', 'Relatório de planejamento econômico', 'Emissão: '+agora+' (Brasília)', '', 'ENTRADAS'] + [f'{LABELS[k]}: {br(v)}' for k,v in d.items()] + ['', 'INDICADORES'] + [f'{v}: {br(r[k])}' for k,v in NOMES.items()] + ['', 'COE: gastos pagos; COT: COE + depreciação + mão de obra familiar.', 'Total: COT + custo de oportunidade do capital.', 'Estimativa baseada nos valores informados, com condições constantes no período.', 'Este relatório não é um laudo nem uma prescrição nutricional.'])
st.download_button('Baixar relatório (.txt)', relatorio, 'Relatorio_LucroLeite.txt', 'text/plain')
st.download_button('Salvar dados (.json)', json.dumps(dict(aplicativo='multvet_lucroleite', versao=1, dados=d), ensure_ascii=False, indent=2), 'Dados_LucroLeite.json', 'application/json')
st.info('Salve o JSON antes de sair. Os campos permanecem apenas durante a sessão e podem ser perdidos ao fechar ou recarregar. O relatório TXT serve para consulta; o JSON permite restaurar os dados.')

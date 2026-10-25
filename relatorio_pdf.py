"""Relatório determinístico em PDF; usa o mesmo motor da calculadora."""
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from calculos import calcular

VERDE=colors.HexColor('#173e32')
DOURADO=colors.HexColor('#c4a45d')
def br(v):
    return 'Não calculável' if v is None else f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

def gerar_pdf(dados):
    r=calcular(dados)
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=40,leftMargin=40,topMargin=38,bottomMargin=40,title='MultVet - LucroLeite Caprinos PRO',author='MultVet')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='MarcaMV',fontName='Helvetica-Bold',fontSize=11,textColor=VERDE,spaceAfter=6))
    styles.add(ParagraphStyle(name='TituloMV',fontName='Helvetica-Bold',fontSize=22,leading=26,textColor=VERDE,spaceAfter=8))
    styles.add(ParagraphStyle(name='SecaoMV',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=VERDE,spaceBefore=13,spaceAfter=7))
    styles.add(ParagraphStyle(name='NotaMV',fontName='Helvetica',fontSize=9,leading=13,textColor=colors.HexColor('#46564d')))
    styles.add(ParagraphStyle(name='CelulaMV',fontName='Helvetica',fontSize=9,leading=12))
    styles.add(ParagraphStyle(name='ValorMV',parent=styles['CelulaMV'],alignment=TA_RIGHT))
    story=[Paragraph('MULTVET',styles['MarcaMV']),Paragraph('LucroLeite Caprinos PRO',styles['TituloMV']),Paragraph('Relatório de planejamento econômico da produção de leite de cabra',styles['NotaMV']),Paragraph('Emissão: '+datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y às %H:%M')+' (Brasília)',styles['NotaMV'])]
    def secao(titulo,rows):
        story.append(Paragraph(titulo,styles['SecaoMV']))
        data=[[Paragraph(a,styles['CelulaMV']),Paragraph(b,styles['ValorMV'])] for a,b in rows]
        table=Table(data,colWidths=[355,160],hAlign='LEFT')
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#f0f3ed'),colors.white]),('LINEBELOW',(0,-1),(-1,-1),.7,DOURADO)]))
        story.append(table)
    secao('Produção e período',[('Cabras em lactação',str(int(dados['cabras']))),('Produção total de leite',br(dados['litros'])+' L/dia'),('Preço de venda do leite','R$ '+br(dados['preco'])+'/L'),('Período projetado',str(int(dados['dias']))+' dias')])
    secao('Custos informados - valores diários',[(label,'R$ '+br(dados[key])) for key,label in [('volumoso','Volumoso'),('concentrado','Concentrado / ração'),('sanidade','Sanidade'),('mao_obra','Mão de obra paga'),('energia','Energia, água e combustível'),('outros','Outros gastos pagos'),('manutencao','Manutenção'),('depreciacao','Depreciação rateada'),('mao_obra_familiar','Mão de obra familiar estimada'),('capital','Custo de oportunidade do capital')]])
    story.append(PageBreak())
    story.append(Paragraph('LucroLeite - Indicadores econômicos',styles['TituloMV']))
    secao('Resultados e ponto de equilíbrio',[(label,('R$ '+br(r[key])) if moeda else br(r[key])) for key,label,moeda in [('coe','COE - Custo Operacional Efetivo (R$/dia)',True),('cot','COT - Custo Operacional Total (R$/dia)',True),('total','Custo total informado (R$/dia)',True),('receita','Receita do leite (R$/dia)',True),('custo_litro','Custo por litro / preço de equilíbrio (R$/L)',True),('resultado','Resultado estimado por dia (R$)',True),('resultado_periodo','Resultado estimado no período (R$)',True),('margem','Margem sobre a receita (%)',False),('litros_cabra','Produção média (L/cabra/dia)',False),('equilibrio_litros','Produção de equilíbrio ao preço informado (L/dia)',False)]])
    story.append(Spacer(1,12))
    story.append(Paragraph('Como interpretar',styles['SecaoMV']))
    story.append(Paragraph('COE: gastos operacionais pagos. COT: COE + depreciação + mão de obra familiar estimada. O custo total informado acrescenta o custo de oportunidade do capital ao COT.',styles['NotaMV']))
    story.append(Spacer(1,6))
    story.append(Paragraph('Os resultados dependem dos custos preenchidos. A projeção mantém produção, preço e despesas constantes no período. A produção de equilíbrio supõe despesas constantes e não representa recomendação de aumento de produção. Sem produção ou receita, alguns indicadores não são calculáveis. Este relatório auxilia o planejamento; não é laudo nem prescrição nutricional.',styles['NotaMV']))
    def rodape(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(DOURADO);canvas.line(40,30,A4[0]-40,30);canvas.setFont('Helvetica',8);canvas.setFillColor(VERDE);canvas.drawString(40,18,'MultVet | Planejamento econômico');canvas.drawRightString(A4[0]-40,18,f'Página {doc.page}');canvas.restoreState()
    doc.build(story,onFirstPage=rodape,onLaterPages=rodape)
    return buffer.getvalue()

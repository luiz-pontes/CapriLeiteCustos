from math import isfinite

CUSTOS = ('volumoso', 'concentrado', 'sanidade', 'mao_obra', 'energia', 'outros', 'manutencao', 'depreciacao', 'mao_obra_familiar', 'capital')
DEFAULTS = dict(cabras=15, litros=37.5, preco=3.5, dias=30, volumoso=25., concentrado=45., sanidade=0., mao_obra=0., energia=0., outros=15., manutencao=0., depreciacao=0., mao_obra_familiar=0., capital=0.)

def validar(dados):
    if not isinstance(dados, dict) or set(dados) != set(DEFAULTS):
        raise ValueError('Arquivo incompatível: confira os campos da LucroLeite.')
    for k, v in dados.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or v < 0:
            raise ValueError(f'Valor inválido no campo {k}.')
    for k in ('cabras', 'dias'):
        if dados[k] < 1 or int(dados[k]) != dados[k]:
            raise ValueError(f'{k} deve ser um inteiro positivo.')
    return dict(dados)

def calcular(dados):
    d = validar(dados)
    coe = sum(d[k] for k in CUSTOS[:7])
    cot = coe + d['depreciacao'] + d['mao_obra_familiar']
    total = cot + d['capital']
    receita = d['litros'] * d['preco']
    resultado = receita - total
    return dict(coe=coe, cot=cot, total=total, receita=receita, resultado=resultado,
                resultado_periodo=resultado*d['dias'], litros_cabra=d['litros']/d['cabras'],
                custo_litro=total/d['litros'] if d['litros'] else None,
                margem=resultado/receita*100 if receita else None,
                equilibrio_litros=total/d['preco'] if d['preco'] else None)

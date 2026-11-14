from arquivos_enunciado.code_base_EP1 import *

class FormulaMarcada():
    def __init__(self, sinal, formula):
        self.sinal = sinal
        self.formula = formula

    def __str__(self):
        sinal = 'T' if self.sinal else 'F'
        return '(' + sinal + ',' + str(self.formula) + ')'

    __repr__ = __str__


def classificar_tipo_regra_comp(fm):
    s, f = fm.sinal, fm.formula

    if isinstance(f, Variable): #átomo
        return ('literal', None, [])

    elif isinstance(f, Implies): #implicação
        filho_esq, filho_dir = f.children
        if s == False:
            tipo = 'alpha'
            regra = 'α→'
            comp_esq = FormulaMarcada(True, filho_esq)
            comp_dir = FormulaMarcada(False, filho_dir)

        else:
            tipo = 'beta'
            regra = 'β→'
            comp_esq = FormulaMarcada(False, filho_esq)
            comp_dir = FormulaMarcada(True, filho_dir)
        return (tipo, regra, [comp_esq, comp_dir])

    elif isinstance(f, Not):
        filho, = f.children
        tipo = 'alpha'
        if s:
            regra = 'α¬'
            comp = FormulaMarcada(False, filho)
        else:
            #Beta negação foi tratada como tipo alpha porque na tabela Beta1 = Beta2
            #logo não faz sentido dividir em dois ramos idênticos
            regra = 'β¬'
            comp = FormulaMarcada(True, filho)
        return (tipo, regra, [comp])

    elif isinstance(f, And):
        comps = [FormulaMarcada(s,filho) for filho in f.children]
        if s:
            tipo = 'alpha'
            regra = 'α∧'
        else:
            tipo = 'beta'
            regra = 'β∧'
        return (tipo, regra, comps)

    elif isinstance(f, Or):
        comps = [FormulaMarcada(s, filho) for filho in f.children]
        if s:
            tipo = 'beta'
            regra = 'β∨'
        else:
            tipo = 'alpha'
            regra = 'α∨'
        return (tipo, regra, comps)
    else:
        raise TypeError(f"Fórmula desconhecida: {f}")




if __name__ == '__main__':
    P, Q, R, S = vars('P', 'Q', 'R', 'S')  # cria os átomos uma vez só

    # Cada teste: (sinal, fórmula, resultado esperado escrito como texto)
    testes = [
        # átomo
        (True,  P,              "('literal', None, [])"),
        (False, P,              "('literal', None, [])"),

        # implicação
        (True,  P >> Q,         "('beta', 'β→', [(F,P), (T,Q)])"),
        (False, R >> S,         "('alpha', 'α→', [(T,R), (F,S)])"),
        (True,  (P & Q) >> R,   "('beta', 'β→', [(F,P ^ Q), (T,R)])"),

        # negação (sempre alpha, um componente com o sinal trocado)
        (True,  ~P,             "('alpha', 'α¬', [(F,P)])"),
        (False, ~P,             "('alpha', 'β¬', [(T,P)])"),
        (True,  ~(P >> S),      "('alpha', 'α¬', [(F,P => S)])"),
        (False, ~~P,            "('alpha', 'β¬', [(T,¬P)])"),  # tira só uma negação

        # conjunção (2 e 3 filhos)
        (True,  P & Q,          "('alpha', 'α∧', [(T,P), (T,Q)])"),
        (False, P & Q,          "('beta', 'β∧', [(F,P), (F,Q)])"),
        (True,  P & Q & R,      "('alpha', 'α∧', [(T,P), (T,Q), (T,R)])"),
        (False, P & Q & R,      "('beta', 'β∧', [(F,P), (F,Q), (F,R)])"),

        # disjunção (2 e 3 filhos)
        (True,  P | Q,          "('beta', 'β∨', [(T,P), (T,Q)])"),
        (False, P | Q,          "('alpha', 'α∨', [(F,P), (F,Q)])"),
        (True,  P | Q | R,      "('beta', 'β∨', [(T,P), (T,Q), (T,R)])"),
        (False, P | Q | R,      "('alpha', 'α∨', [(F,P), (F,Q), (F,R)])"),

        # fórmulas compostas: só o conectivo principal é quebrado
        (True,  (P | Q) & ~R,   "('alpha', 'α∧', [(T,P v Q), (T,¬R)])"),
        (False, ~(P & Q),       "('alpha', 'β¬', [(T,P ^ Q)])"),

        # P & Q >> R significa P & (Q >> R), e não (P & Q) >> R.
        (True,  P & Q >> R,     "('alpha', 'α∧', [(T,P), (T,Q => R)])"),
    ]

    acertos = 0
    for sinal, formula, esperado in testes:
        fm = FormulaMarcada(sinal, formula)
        obtido = str(classificar_tipo_regra_comp(fm))
        if obtido == esperado:
            acertos += 1
            print('ok   ', fm)
        else:
            print('ERRO ', fm)
            print('      esperado:', esperado)
            print('      obtido:  ', obtido)

    # Fórmula fora da linguagem do enunciado: deve dar TypeError
    try:
        classificar_tipo_regra_comp(FormulaMarcada(True, P.iff(Q)))
        print('ERRO  (T,P <=> Q) deveria dar TypeError')
    except TypeError:
        acertos += 1
        print('ok    (T,P <=> Q) dá TypeError')

    print(f'\n{acertos}/{len(testes) + 1} testes passaram')

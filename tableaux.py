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


class Ramo:
    def __init__(self):
        self.pendentes = []
        self.literais = {}
        self.fechado = False

    def contradicao(self, fm):
        s, f = fm.sinal, fm.formula
        return f.name in self.literais and s != self.literais[f.name]


    def adicionar(self,fm):
        s, f = fm.sinal, fm.formula
        if isinstance(f, Variable):
            if self.contradicao(fm):
                self.fechado = True

            else:
                self.literais[f.name] = s
        else:
            self.pendentes.append(fm)

    def copiar(self):
        copia = Ramo()
        copia.pendentes = self.pendentes.copy()
        copia.literais = self.literais.copy()
        copia.fechado = self.fechado
        return copia

    def escolher(self): #escolhe o que expandir
        if not self.pendentes:
            return None
        for i, fm in enumerate(self.pendentes):
            tipo, _, _ = classificar_tipo_regra_comp(fm)
            if tipo == 'alpha':
                return self.pendentes.pop(i)
        #não tem nenhuma regra alpha
        return self.pendentes.pop(0)

    def __str__(self):
        return 'pendentes: ' + str(self.pendentes) + ' | ' + 'literais: ' + str(self.literais) + ' | ' + 'fechado: ' + str(self.fechado)


def provar(sequente):
    ramo = Ramo()
    for pre in sequente.premises:
        fm = FormulaMarcada(True, pre)
        ramo.adicionar(fm)

    fm = FormulaMarcada(False, sequente.conclusion)
    ramo.adicionar(fm)

    pilha = [ramo]
    regras_aplicadas = []

    while pilha:
        ramo_vez = pilha.pop()

        if ramo_vez.fechado:
            continue

        fm = ramo_vez.escolher()

        if fm is None:
            #o ramo terminou aberto, logo a validade é falsa
            return (False, ramo_vez, regras_aplicadas)

        tipo, regra, comps = classificar_tipo_regra_comp(fm)
        regras_aplicadas.append((regra, fm))
        if tipo == 'alpha':
            for comp in comps:
                ramo_vez.adicionar(comp)
            pilha.append(ramo_vez)
        else:
            for comp in comps:
                copia = ramo_vez.copiar()
                copia.adicionar(comp)
                pilha.append(copia)

    return (True, None, regras_aplicadas)


def contra_exemplo(sequente, ramo):
    valoracao = {}
    for atomo in sorted(sequente.variables()):
        valoracao[atomo] = ramo.literais.get(atomo, True) #por padrão, se o ramo não contém o literal, ele tem valor-livre, adota-se True
    return valoracao


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

    print(f'\n{acertos}/{len(testes) + 1} testes de classificação passaram')

    # -----------------------------------------------------------------
    # Testes do Ramo (passos 3 e 4)
    # -----------------------------------------------------------------
    print('\n--- Ramo ---')

    def T(f):
        return FormulaMarcada(True, f)

    def F(f):
        return FormulaMarcada(False, f)

    def ramo_com(fms):
        """Cria um ramo vazio e adiciona, em ordem, as fórmulas marcadas da lista."""
        r = Ramo()
        for fm in fms:
            r.adicionar(fm)
        return r

    # passo 3: separação entre literais e pendentes, e cópia independente
    r1 = ramo_com([T(P >> Q), F(Q), T(P)])
    r2 = r1.copiar()
    r2.adicionar(T(R))
    r2.adicionar(F(P | R))

    # passo 4: fechamento
    r3 = ramo_com([T(P)])
    r4 = r3.copiar()
    r4.adicionar(F(P))       # fecha só a cópia
    r5 = ramo_com([T(P), F(P)])
    r6 = r5.copiar()         # cópia de um ramo já fechado

    # Cada teste: (descrição, valor obtido, valor esperado)
    testes_ramo = [
        ('original não muda quando a cópia muda', str(r1),
         "pendentes: [(T,P => Q)] | literais: {'Q': False, 'P': True} | fechado: False"),
        ('cópia recebe o que foi adicionado nela', str(r2),
         "pendentes: [(T,P => Q), (F,P v R)] | literais: {'Q': False, 'P': True, 'R': True} | fechado: False"),
        ('cópia tem lista própria',      r1.pendentes is r2.pendentes, False),
        ('cópia tem dicionário próprio', r1.literais is r2.literais,   False),

        ('mesmo sinal repetido não fecha (T P, F Q, T P)',
         ramo_com([T(P), F(Q), T(P)]).fechado, False),
        ('sinais opostos fecham (T P, F P)', r5.fechado, True),
        ('compostas não fecham direto (T P>>Q, F P>>Q)',
         ramo_com([T(P >> Q), F(P >> Q)]).fechado, False),
        ('fechar a cópia não fecha o original', (r3.fechado, r4.fechado), (False, True)),
        ('cópia de ramo fechado continua fechada', r6.fechado, True),
    ]

    acertos_ramo = 0
    for descricao, obtido, esperado in testes_ramo:
        if obtido == esperado:
            acertos_ramo += 1
            print('ok   ', descricao)
        else:
            print('ERRO ', descricao)
            print('      esperado:', esperado)
            print('      obtido:  ', obtido)

    print(f'\n{acertos_ramo}/{len(testes_ramo)} testes do Ramo passaram')

    # -----------------------------------------------------------------
    # Testes do escolher (passo 5): α antes de β
    # -----------------------------------------------------------------
    print('\n--- escolher ---')

    # caso do roteiro: β, α, α -> as duas α saem primeiro, na ordem da lista
    r7 = ramo_com([T(P | Q), T(P & Q), F(P >> Q)])
    escolhas_r7 = [str(r7.escolher()) for _ in range(4)]

    # só β: saem na ordem em que entraram
    r8 = ramo_com([T(P | Q), T(P >> Q)])
    escolhas_r8 = [str(r8.escolher()) for _ in range(2)]

    # negação conta como α, inclusive a β¬ (F ~C)
    r9 = ramo_com([T(P | Q), F(~P)])
    primeira_r9 = str(r9.escolher())

    # escolher não mexe nos literais nem no fechado
    r10 = ramo_com([T(P), F(Q), T(P & R)])
    r10.escolher()

    testes_escolher = [
        ('α antes de β, depois None quando esvazia', escolhas_r7,
         ['(T,P ^ Q)', '(F,P => Q)', '(T,P v Q)', 'None']),
        ('pendentes fica vazia no final',  r7.pendentes, []),
        ('só β: sai a primeira da lista',  escolhas_r8, ['(T,P v Q)', '(T,P => Q)']),
        ('F ~P é α e sai antes da β',      primeira_r9, '(F,¬P)'),
        ('escolher tira só a fórmula escolhida', str(r10),
         "pendentes: [] | literais: {'P': True, 'Q': False} | fechado: False"),
        ('ramo vazio devolve None',        Ramo().escolher(), None),
    ]

    acertos_escolher = 0
    for descricao, obtido, esperado in testes_escolher:
        if obtido == esperado:
            acertos_escolher += 1
            print('ok   ', descricao)
        else:
            print('ERRO ', descricao)
            print('      esperado:', esperado)
            print('      obtido:  ', obtido)

    print(f'\n{acertos_escolher}/{len(testes_escolher)} testes do escolher passaram')

import sys
from tableaux import *

P, Q, R, S, A, B = vars('P', 'Q', 'R', 'S', 'A', 'B')

REGRAS_ESPERADAS = {'α¬', 'α∧', 'α∨', 'α→', 'β¬', 'β∧', 'β∨', 'β→'}

CASOS_DE_TESTE = [
    ('Classicos (validos)', 'Modus Ponens',
     ArgumentForm(P, P >> Q, conclusion=Q), True),
    ('Classicos (validos)', 'Modus Tollens',
     ArgumentForm(P >> Q, ~Q, conclusion=~P), True),
    ('Classicos (validos)', 'Silogismo Disjuntivo',
     ArgumentForm(P | Q, ~P, conclusion=Q), True),
    ('Classicos (validos)', 'Silogismo Hipotetico',
     ArgumentForm(P >> Q, Q >> R, conclusion=(P >> R)), True),
    ('Classicos (validos)', 'Lei de De Morgan',
     ArgumentForm(~(P & Q), conclusion=(~P | ~Q)), True),
    ('Classicos (validos)', 'Conjuncao n-aria (3 filhos)',
     ArgumentForm(P & Q & R, conclusion=(Q & R)), True),

    ('Teoremas sem premissas', 'Terceiro Excluido',
     ArgumentForm(conclusion=(P | ~P)), True),
    ('Teoremas sem premissas', 'Lei de Peirce',
     ArgumentForm(conclusion=(((P >> Q) >> P) >> P)), True),
    ('Teoremas sem premissas', 'Distributividade (∨ sobre ∧)',
     ArgumentForm(conclusion=((P | (Q & R)) >> ((P | Q) & (P | R)))), True),

    ('Casos de borda e compostos', 'Identidade (fechamento imediato, sem regras)',
     ArgumentForm(P, conclusion=P), True),
    ('Casos de borda e compostos', 'Principio da Explosao (premissas contraditorias)',
     ArgumentForm(P, ~P, conclusion=Q), True),
    ('Casos de borda e compostos', 'Dupla Negacao',
     ArgumentForm(~~P, conclusion=P), True),
    ('Casos de borda e compostos', 'Disjuncao n-aria e prioridade α antes de β',
     ArgumentForm(P | Q | R, (~P) & (~Q), conclusion=R), True),
    ('Casos de borda e compostos', 'Formula composta com 4 atomos (valida)',
     ArgumentForm(((A | B) >> Q) & (~S), A, conclusion=(Q & ~S)), True),

    ('Falacias e invalidos', 'Afirmacao do Consequente',
     ArgumentForm(P >> Q, Q, conclusion=P), False),
    ('Falacias e invalidos', 'Negacao do Antecedente',
     ArgumentForm(P >> Q, ~P, conclusion=~Q), False),
    ('Falacias e invalidos', 'Non Sequitur (sem regras)',
     ArgumentForm(P, conclusion=Q), False),
    ('Falacias e invalidos', 'Falacia do Terceiro Excluido',
     ArgumentForm(P | Q, P, conclusion=~Q), False),
    ('Falacias e invalidos', 'Contra-exemplo com atomo livre',
     ArgumentForm(P | Q, conclusion=(P & R)), False),
    ('Falacias e invalidos', 'Formula composta com 4 atomos (invalida)',
     ArgumentForm(((A | B) >> Q) & (~S), conclusion=(Q & ~S)), False),
]


def verificar_sequente(sequente, esperado_valido):
    """Executa provar() e valida o resultado contra a tabela-verdade e o formato esperado."""
    valido, ramo, regras = provar(sequente)
    erros = []

    if valido != esperado_valido:
        erros.append(f'esperado valido={esperado_valido}, obtido {valido}')

    tt_valido = sequente.is_valid_truth_table()
    if valido != tt_valido:
        erros.append(f'divergencia com tabela-verdade (tabela={tt_valido}, provar={valido})')

    if valido:
        if ramo is not None:
            erros.append('sequente valido retornou ramo nao nulo')
    else:
        if ramo is None or ramo.fechado:
            erros.append('sequente invalido sem ramo aberto')
        else:
            val = contra_exemplo(sequente, ramo)
            if not all(p.evaluate(**val) for p in sequente.premises):
                erros.append(f'contra-exemplo nao satisfaz todas as premissas: {val}')
            if sequente.conclusion.evaluate(**val) is not False:
                erros.append(f'contra-exemplo nao falsifica a conclusao: {val}')

    for item in regras:
        if not (isinstance(item, tuple) and len(item) == 2
                and isinstance(item[0], str) and isinstance(item[1], FormulaMarcada)):
            erros.append(f'item invalido na lista de regras: {item!r}')

    regras_usadas = {r for r, _ in regras if isinstance(r, str)}
    return (len(erros) == 0, erros, regras_usadas)


def verificar_erros_linguagem():
    """Verifica se operadores fora da linguagem do enunciado lancam TypeError."""
    casos_invalidos = [
        ('Bicondicional (P <=> Q)', ArgumentForm(P.iff(Q), conclusion=P)),
        ('Implicacao reversa (P << Q)', ArgumentForm(P << Q, conclusion=P)),
        ('Constante booleana (True)', ArgumentForm(True, conclusion=P)),
    ]
    acertos = 0
    falhas = []
    for nome, seq in casos_invalidos:
        try:
            provar(seq)
            falhas.append(f'{nome}: nao lancou TypeError')
        except TypeError:
            acertos += 1
    return (acertos, len(casos_invalidos), falhas)


def executar_testes():
    """Roda todos os casos de teste, imprime as saidas do provador e valida invariantes."""
    total = len(CASOS_DE_TESTE)
    aprovados = 0
    regras_cobertas = set()
    categoria_atual = None

    for idx, (categoria, nome, sequente, esperado_valido) in enumerate(CASOS_DE_TESTE, start=1):
        if categoria != categoria_atual:
            categoria_atual = categoria
            print(f'\n=== {categoria} ===')

        print(f'\n[{idx}/{total}] {nome}')
        imprimir_resultado(sequente)

        ok, erros, regras_usadas = verificar_sequente(sequente, esperado_valido)
        regras_cobertas.update(regras_usadas)

        if ok:
            aprovados += 1
            estado = 'VALIDO' if esperado_valido else 'INVALIDO'
            print(f'Verificacao: OK ({estado}, compativel com tabela-verdade)')
        else:
            print('Verificacao: ERRO (' + '; '.join(erros) + ')')

    print('\n=== Erros de linguagem (TypeError) ===')
    acertos_lang, total_lang, falhas_lang = verificar_erros_linguagem()
    if falhas_lang:
        for falha in falhas_lang:
            print('ERRO:', falha)
    else:
        print(f'ok   {acertos_lang}/{total_lang} formulas fora da linguagem lancaram TypeError')

    faltantes = sorted(REGRAS_ESPERADAS - regras_cobertas)

    print('\n=== Resumo ===')
    print(f'Sequentes aprovados: {aprovados}/{total}')
    print(f'Erros de linguagem (TypeError): {acertos_lang}/{total_lang}')
    print(f'Regras exercitadas: {len(regras_cobertas)}/{len(REGRAS_ESPERADAS)} ({", ".join(sorted(regras_cobertas))})')
    if faltantes:
        print('Regras NAO exercitadas: ' + ', '.join(faltantes))

    if aprovados != total or acertos_lang != total_lang or faltantes:
        sys.exit(1)


if __name__ == '__main__':
    executar_testes()

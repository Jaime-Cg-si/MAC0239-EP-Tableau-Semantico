# Exercício Programa - MAC0239: Lógica e Verificação de Programas

## Integrantes:


## O que é

Provador de sequentes `A1, ..., An ⊢ B` do cálculo proposicional por **tableaux semânticos**.
Para cada sequente, o programa diz se ele é válido; se não for, mostra um contra-exemplo;
e, nos dois casos, mostra a sequência de regras aplicadas `[(regra, fórmula), ...]`.

## Estrutura das pastas

```
meu_projeto/
├── tableaux.py               # implementação do provador
├── arquivos_enunciado/
│   ├── code_base_EP1.py      # código-base fornecido (fórmulas, ArgumentForm, tabela-verdade)
│   ├── code_base_EP1_demo.py # exemplos de uso do código-base
│   └── ep.tableaux.pdf       # enunciado
└── relatorio/
```

Requer Python 3 (testado com Python 3.13). Não há dependências externas.

## Como usar o provador

```python
from tableaux import *

P, Q, R = vars('P', 'Q', 'R')   # todos os átomos usados precisam ser criados

imprimir_resultado(ArgumentForm(P, P >> Q, conclusion=Q))      # P, P → Q ⊢ Q
imprimir_resultado(ArgumentForm(P >> Q, Q, conclusion=P))      # P → Q, Q ⊢ P
imprimir_resultado(ArgumentForm(conclusion=P | ~P))            # ⊢ P ∨ ¬P (sem premissas)
```

Saída dos dois primeiros:

```
Sequente: P, P => Q ⊢ Q
Resultado: VÁLIDO
Regras: [('β→', (T,P => Q))]

Sequente: P => Q, Q ⊢ P
Resultado: INVÁLIDO
Contra-exemplo: P = False, Q = True
Regras: [('β→', (T,P => Q))]
```

Átomos que não aparecem no ramo aberto podem ter qualquer valor; eles recebem `True`
e aparecem marcados como `(valor livre)` no contra-exemplo.

### Conectivos

| Notação da aula | No Python |
|---|---|
| ¬A | `~A` |
| A ∧ B | `A & B` |
| A ∨ B | `A \| B` |
| A → B | `A >> B` |

### Funções disponíveis

| Função | Devolve |
|---|---|
| `imprimir_resultado(sequente)` | nada; imprime o sequente, a validade, o contra-exemplo (se houver) e as regras |
| `provar(sequente)` | `(valido, ramo, regras)`: `valido` é `True`/`False`; `ramo` é o ramo aberto (ou `None` se válido); `regras` é a lista `[(regra, fórmula marcada), ...]` |
| `contra_exemplo(sequente, ramo)` | dicionário `{átomo: valor}` com todos os átomos do sequente (só para sequentes inválidos) |


### Testes unitários

```
python3 tableaux.py
```

Roda os testes das partes internas (classificação das fórmulas, ramo, escolha de regras).
Eles não substituem o script de testes da entrega.

## Cuidados ao escrever sequentes

- **Prioridade do `>>`:** no Python, `>>` tem prioridade sobre `&` e `|`.
  `P & Q >> R` significa `P & (Q >> R)`, e não `(P & Q) >> R`.
  Coloque parênteses em volta de toda implicação.
- **Um átomo só:** `R = vars('R')` devolve um gerador, não um átomo.
  Use `R, = vars('R')` (com a vírgula) ou crie todos de uma vez: `P, Q, R = vars('P', 'Q', 'R')`.
- Só `~`, `&`, `|` e `>>` fazem parte da linguagem do enunciado. Outros tipos do código-base
  (`<=>`, `<<`, constantes `True`/`False`) geram `TypeError`.

## Decisões de implementação (para o relatório)

**Estruturas**
- `FormulaMarcada`: par (sinal, fórmula); `True` representa T e `False` representa F.
- `Ramo`: lista de fórmulas marcadas ainda não expandidas (`pendentes`), dicionário
  `{nome do átomo: sinal}` com os literais encontrados (`literais`) e o indicador `fechado`.
- Pilha de ramos no algoritmo principal.

**Estratégias**
- **Escolha da regra em um ramo:** α antes de β. Regras α não ramificam;
  adiar as β evita expandir as mesmas fórmulas em vários ramos e pode fechar o ramo antes de dividir.
- **Escolha do ramo:** busca em profundidade com pilha; o algoritmo para no primeiro
  ramo aberto e completamente expandido (sequente inválido) ou quando todos os ramos fecham (válido).

**Detalhes**
- **β¬ tratada como α:** na tabela do enunciado, `F ~C` tem β1 = β2 = `T C`; dividir o ramo
  criaria dois ramos idênticos. O nome `β¬` é mantido no registro.
- **`&` e `|` com n filhos:** o código-base transforma `P & Q & R` em um único `And` com 3 filhos;
  as regras foram generalizadas (por exemplo, `F P & Q & R` abre 3 ramos).
- **Fechamento só em átomos:** ao adicionar um literal, verifica-se se o mesmo átomo já está no
  ramo com o sinal oposto. Fórmulas compostas contraditórias fecham depois de expandidas.
- **Valor livre:** átomos ausentes do ramo aberto recebem `True` no contra-exemplo.
- **Registro de regras:** uma lista única, na ordem de aplicação, cobrindo todos os ramos visitados.
  Em sequentes inválidos, termina no primeiro ramo aberto encontrado.

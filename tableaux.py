from arquivos_enunciado.code_base_EP1 import *

class FormulaMarcada():
    def __init__(self, sinal, formula):
        self.sinal = sinal
        self.formula = formula

    def __str__(self):
        sinal = 'T' if self.sinal else 'F'
        return '(' + sinal + ',' + str(self.formula) + ')'



if __name__ == '__main__':
    P, Q = vars('P', 'Q') #cria dois toys objects de variable
    fm = FormulaMarcada(True, P >> Q)
    print(fm)

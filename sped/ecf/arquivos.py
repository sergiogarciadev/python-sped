# -*- coding: utf-8 -*-

from .. import arquivos
from . import blocos
from . import registros
from .blocos import Bloco0
from .blocos import BlocoC
from .blocos import BlocoE
from .blocos import BlocoJ
from .blocos import BlocoK
from .blocos import BlocoL
from .blocos import BlocoM
from .blocos import BlocoN
from .blocos import BlocoP
from .blocos import BlocoT
from .blocos import BlocoU
from .blocos import BlocoX
from .blocos import BlocoY
from .blocos import Bloco9
from .registros import Registro0000
from .registros import Registro9900
from .registros import Registro9999


class ArquivoDigital(arquivos.ArquivoDigital):
    registro_abertura = Registro0000
    registro_encerramento = Registro9999
    registros = registros
    blocos = blocos

    def __init__(self):
        super(ArquivoDigital, self).__init__()
        self._blocos['0'] = Bloco0()
        self._blocos['C'] = BlocoC()
        self._blocos['E'] = BlocoE()
        self._blocos['J'] = BlocoJ()
        self._blocos['K'] = BlocoK()
        self._blocos['L'] = BlocoL()
        self._blocos['M'] = BlocoM()
        self._blocos['N'] = BlocoN()
        self._blocos['P'] = BlocoP()
        self._blocos['T'] = BlocoT()
        self._blocos['U'] = BlocoU()
        self._blocos['X'] = BlocoX()
        self._blocos['Y'] = BlocoY()
        self._blocos['9'] = Bloco9()

    def prepare(self):
        bloco_9 = self._blocos['9'] = Bloco9()

        for bloco in self._blocos.values():
            regs = {}
            for reg in bloco.registros:
                if reg.REG not in regs:
                    regs[reg.REG] = 0
                regs[reg.REG] += 1
            if bloco == self._blocos['0']:
                regs['0000'] = 1
            if bloco == bloco_9:
                regs['9999'] = 1
                regs['9900'] += len(regs.keys())
            for reg in regs.keys():
                registro = Registro9900()
                registro.REG_BLC = reg
                registro.QTD_REG_BLC = regs[reg]
                bloco_9.add(registro)

        reg_count = 2
        for bloco in self._blocos.values():
            reg_count += len(bloco.registros)

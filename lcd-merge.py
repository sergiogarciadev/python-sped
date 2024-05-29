# vim: set ft=python fileencoding=utf-8

import sys

from datetime import date
from pathlib import Path

from sped.lcdpr.arquivos import ArquivoDigital

fname1 = sys.argv[1]
fname2 = sys.argv[2]

if not Path(fname1).exists():
    print(f'File not found: {fname1}')

if not Path(fname2).exists():
    print(f'File not found: {fname2}')

arquivo1 = ArquivoDigital()
arquivo1.readfile(fname1)

arquivo2 = ArquivoDigital()
arquivo2.readfile(fname2)

bloco0=[]

for r in arquivo1._blocos['0'].registros:
    if isinstance(r, ArquivoDigital.registros.Registro0000):
        print(r.as_line())
        bloco0.append(r)
    if isinstance(r, ArquivoDigital.registros.Registro0010):
        print(r.as_line())
        bloco0.append(r)
    if isinstance(r, ArquivoDigital.registros.Registro0030):
        print(r.as_line())
        bloco0.append(r)

for r in (arquivo1._blocos['0'].registros + arquivo2._blocos['0'].registros):
    if isinstance(r, ArquivoDigital.registros.Registro0040):
        print(r.as_line())
        bloco0.append(r)
    if isinstance(r, ArquivoDigital.registros.Registro0045):
        print(r.as_line())
        bloco0.append(r)

for r in (arquivo1._blocos['0'].registros + arquivo2._blocos['0'].registros):
    if isinstance(r, ArquivoDigital.registros.Registro0050):
        print(r.as_line())
        bloco0.append(r)

arquivo1._blocos['0']._registros = bloco0

#
# Mesclar registro Q100 dos dois arquivos
#
regsQ100 = [r for r in arquivo1._blocos['Q'].registros if isinstance(r, arquivo1.registros.RegistroQ100)] + [r for r in arquivo2._blocos['Q'].registros if isinstance(r, arquivo1.registros.RegistroQ100)]
regsQ100 = sorted(regsQ100, key=lambda r: r.DATA)

#
# Define o bloco Q apenas com os registros Q100 (Q200 são gerados na sequencia)
#
arquivo1._blocos['Q']._registros = [r for r in regsQ100]

saldo=0

entradas_mes = 0
saidas_mes = 0
ultima_data = date.min

#
# Calcula dos registros Q200
#
for regQ100 in regsQ100:
    if ultima_data == date.min:
        ultima_data = regQ100.DATA

    if regQ100.DATA.month != ultima_data.month:
        #
        # Ao fim de cada mês, cria um Registro Q200 com o saldo final daqueles mês
        #
        regQ200 = arquivo1.registros.RegistroQ200()
        regQ200.MÊS = f'{ultima_data.month:02}{ultima_data.year:04}'
        regQ200.VL_ENTRADA = entradas_mes
        regQ200.VL_SAIDA = saidas_mes
        regQ200.SLD_FIN = abs(saldo)
        regQ200.NAT_SLD_FIN = 'P' if saldo >= 0 else 'N'
        
        arquivo1._blocos['Q'].add(regQ200)
        print(regQ200.as_line())

        entradas_mes = 0
        saidas_mes = 0

    ultima_data = regQ100.DATA

    saldo += regQ100.VL_ENTRADA - regQ100.VL_SAIDA
    regQ100.SLD_FIN = abs(saldo)
    regQ100.NAT_SLD_FIN = 'P' if saldo >= 0 else 'N'

    entradas_mes += regQ100.VL_ENTRADA
    saidas_mes += regQ100.VL_SAIDA

#
# Calcula mês de dezembro
#
regQ200 = arquivo1.registros.RegistroQ200()
regQ200.MÊS = f'{ultima_data.month:02}{ultima_data.year:04}'
arquivo1._blocos['Q'].add(regQ200)

regQ200.VL_ENTRADA = entradas_mes
regQ200.VL_SAIDA = saidas_mes
regQ200.SLD_FIN = abs(saldo)
regQ200.NAT_SLD_FIN = 'P' if saldo >= 0 else 'N'

with open(sys.argv[3], 'w', encoding='iso-8859-1') as f:
    arquivo1.write_to(f)

# vim: set ft=python fileencoding=utf-8

import sys

from datetime import date
from sped.lcdpr.arquivos import ArquivoDigital

fname = sys.argv[1]

arquivo = ArquivoDigital()
arquivo.readfile(fname)

with open(f'{fname}.fixed', 'w', encoding='iso-8859-1') as f:
    arquivo.write_to(f)

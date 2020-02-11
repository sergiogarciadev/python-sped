# -*- coding: utf-8 -*-

Autor = 'Claudio Fernandes de Souza Rodrigues (claudiofsr@yahoo.com)'
Data  = '11 de Fevereiro de 2020 (início: 10 de Janeiro de 2020)'

import os, csv, re, sys, itertools
from datetime import datetime
from time import time, sleep
from sped.efd.pis_cofins.arquivos import ArquivoDigital as ArquivoDigital_PIS_COFINS
from sped.efd.icms_ipi.arquivos   import ArquivoDigital as ArquivoDigital_ICMS_IPI
from sped.relatorios.efd_tabelas  import EFD_Tabelas
from sped.campos import CampoData, CampoCNPJ, CampoCPF, CampoCPFouCNPJ, CampoChaveEletronica, CampoNCM

# Versão mínima exigida: python 3.6.0
python_version = sys.version_info
if python_version < (3,6,0):
	print('versão mínima exigida do python é 3.6.0')
	print('versão atual', "%s.%s.%s" % (python_version[0],python_version[1],python_version[2]))
	exit()

# Python OOP: Atributos e Métodos (def, funções)
class SPED_EFD_Info:
	"""
	Imprimir informações da SPED EFD Contribuições em um arquivo.csv
	tal que em uma linha contenha todas as informações suficientes para
	verificar a correção dos lançamentos das contribuições de PIS/COFINS.
	"""
	
	# class or static variable
	
	# Python 3 Deep Dive (Part 4 - OOP)/03. Project 1/03. Project Solution - Transaction Numbers
	contador_de_linhas = itertools.count(2) # 2 é o valor inicial do contador
	
	### --- registros e colunas --- ###
	
	registros_de_data_emissao  = ['DT_DOC', 'DT_DOC_INI', 'DT_REF_INI', 'DT_OPER'] # 'Data da Emissão do Documento Fiscal'

	registros_de_data_execucao = ['DT_EXE_SERV', 'DT_E_S', 'DT_ENT', 'DT_A_P', 'DT_DOC_FIN', 'DT_REF_FIN'] # 'Data da Entrada/Aquisição/Execução ou da Saída/Prestação/Conclusão'

	registros_de_data = ['DT_INI', 'DT_FIN'] + registros_de_data_emissao + registros_de_data_execucao # merge/concatenating two lists in Python

	registros_de_identificacao_do_item = ['DESCR_ITEM', 'TIPO_ITEM', 'COD_NCM']

	registros_de_cadastro_do_participante = ['NOME_participante', 'CNPJ_participante', 'CPF_participante']

	registros_de_plano_de_contas = ['COD_NAT_CC', 'NOME_CTA']

	registros_de_codigo_cst = ['CST_PIS', 'CST_COFINS']

	registros_de_chave_eletronica = ['CHV_NFE', 'CHV_CTE', 'CHV_NFSE', 'CHV_DOCe', 'CHV_CFE', 'CHV_NFE_CTE']

	registros_de_base_de_calculo = ['VL_BC_PIS', 'VL_BC_COFINS']

	registros_de_valor = ['VL_DOC', 'VL_BRT', 'VL_OPER', 'VL_OPR', 'VL_OPER_DEP', 'VL_BC_CRED', 'VL_BC_EST', 'VL_TOT_REC', 'VL_REC_CAIXA', 'VL_REC_COMP', 'VL_REC', 'VL_ITEM'] # adicionado 'VL_OPR' para EFD ICMS_IPI
	
	registros_totais = registros_de_data + registros_de_identificacao_do_item + registros_de_plano_de_contas + registros_de_codigo_cst + registros_de_chave_eletronica + registros_de_base_de_calculo + registros_de_valor

	# Imprimir as informações desta coluna, nesta ordem
	colunas = ['Linhas', 'Arquivo da SPED EFD', 'Nº da Linha da EFD', 'CNPJ', 'NOME', 'Mês do Período de Apuração', 'Ano do Período de Apuração', 'Tipo de Operação', 'IND_ORIG_CRED', 'REG', 'CST Código da Situação Tributária', 
			   'NAT_BC_CRED', 'CFOP', 'COD_PART', *registros_de_cadastro_do_participante, 'CNPJ_CPF_PART', 'Data de Emissão', 'Data de Execução', 'COD_ITEM', *registros_de_identificacao_do_item, 
			   'Chave Eletrônica', 'COD_MOD', 'NUM_DOC', 'NUM_ITEM', 'COD_CTA', *registros_de_plano_de_contas, 'Valor do Item', 'Valor da Base de Cálculo', 'ALIQ_PIS', 'ALIQ_COFINS', 'CST_ICMS', 'VL_BC_ICMS', 'ALIQ_ICMS']

	# initialize the attributes of the class
	
	def __init__(self, file_path=None, encoding=None, efd_tipo=None, verbose=False):

		if file_path is None or not os.path.isfile(file_path):
			raise ValueError(f'O arquivo file_path = {file_path} não é válido!')
		else:
			self.file_path = file_path
				
		if encoding is None:
			self.encoding = 'UTF-8'
		else:
			self.encoding = encoding

		if efd_tipo is None or re.search(r'PIS|COFINS|Contrib', efd_tipo, flags=re.IGNORECASE):
			self.objeto_sped = ArquivoDigital_PIS_COFINS() # instanciar objeto sped_efd
			self.efd_tipo = 'efd_contribuicoes'
		elif re.search(r'ICMS|IPI', efd_tipo, flags=re.IGNORECASE):
			self.objeto_sped = ArquivoDigital_ICMS_IPI()   # instanciar objeto sped_efd
			self.efd_tipo = 'efd_icms_ipi'
		else:
			raise ValueError(f'efd_tipo = {efd_tipo} inválido!')
		
		if not isinstance(verbose, bool):
			raise ValueError(f'verbose deve ser uma variável boolean (True or False). verbose = {verbose} é inválido!')
		else:
			self.verbose = verbose
		
		self.basename = os.path.basename(self.file_path)
	
	@property
	def imprimir_informacoes(self):
				
		self.objeto_sped.readfile(self.file_path, codificacao=self.encoding, verbose=self.verbose)
		
		self.info_do_participante = self.cadastro_do_participante(self.objeto_sped)
		
		if self.verbose:
			print(f'self.info_do_participante = {self.info_do_participante} ; len(self.info_do_participante) = {len(self.info_do_participante)}\n')
		
		self.info_do_item = self.identificacao_do_item(self.objeto_sped)

		if self.verbose:
			print(f'self.info_do_item = {self.info_do_item} ; len(self.info_do_item) = {len(self.info_do_item)}\n')
		
		self.info_da_conta = self.plano_de_contas_contabeis(self.objeto_sped)

		if self.verbose:
			print(f'self.info_da_conta = {self.info_da_conta} ; len(self.info_da_conta) = {len(self.info_da_conta)}\n')
		
		self.info_de_abertura = self.obter_info_de_abertura(self.objeto_sped)
		
		filename, _ = os.path.splitext(self.file_path)
		arquivo_csv = filename + '.csv'
		
		# Função desabilitada
		# Funçao utilizada apenas para teste
		# self.imprimir_informacoes_linha_a_linha(self.objeto_sped, output_filename=arquivo_csv)
		
		self.imprimir_informacoes_da_efd(self.objeto_sped, output_filename=arquivo_csv)

	def __repr__(self):
		# https://stackoverflow.com/questions/25577578/access-class-variable-from-instance
    	# Devo substituir 'self.__class__.static_var' por 'type(self).static_var' ?
		return f'{type(self).__name__}(file_path={self.file_path!r}, encoding={self.encoding!r}, efd_tipo={self.efd_tipo!r}, verbose={self.verbose!r})'
		
	# https://radek.io/2011/07/21/static-variables-and-methods-in-python/
	@staticmethod
	def natureza_da_bc_dos_creditos(cfop):	
		"""
		http://sped.rfb.gov.br/arquivo/show/1681
		Tabela CFOP - Operações Geradoras de Créditos - Versão 1.0.0
		"""
		natureza_bc = None
		
		# Código 01 - CFOP de 'Aquisição de Bens para Revenda'
		if   cfop in ['1102','1113','1117','1118','1121','1251','1403','1652','2102','2113','2117','2118','2121','2251','2403','2652','3102','3251','3652']:
			natureza_bc = 1
		# Código 02 - CFOP de 'Aquisição de Bens Utilizados como Insumo'
		elif cfop in ['1101','1111','1116','1120','1122','1126','1128','1401','1407','1556','1651','1653','2101','2111','2116','2120','2122','2126','2128','2401','2407','2556','2651','2653','3101','3126','3128','3556','3651','3653']:
			natureza_bc = 2
		# Código 03 - CFOP de 'Aquisição de Serviços Utilizados como Insumos'
		elif cfop in ['1124','1125','1933','2124','2125','2933']:
			natureza_bc = 3
		# Código 12 - CFOP de 'Devolução de Vendas Sujeitas à Incidência Não-Cumulativa'
		elif cfop in ['1201','1202','1203','1204','1410','1411','1660','1661','1662','2201','2202','2410','2411','2660','2661','2662']:
			natureza_bc = 12
		# Código 13 - CFOP de 'Outras Operações com Direito a Crédito'
		elif cfop in ['1922','2922']:
			natureza_bc = 13
		
		return natureza_bc
	
	def identidade(chave):
		return chave

	def formatar_linhas(numero):
		return f'{int(numero):09d}'
	
	def formatar_cst_contrib(codigo_cst):
		try:
			codigo_cst = f'{int(codigo_cst):02d}'
			return f'{codigo_cst} - {EFD_Tabelas.tabela_cst_contrib[codigo_cst]}'
		except:
			return codigo_cst

	def formatar_cst_icms(codigo_cst):
		try:
			codigo_cst = f'{int(codigo_cst):03d}'
			return f'{codigo_cst} - {EFD_Tabelas.tabela_cst_icms[codigo_cst]}'
		except:
			return codigo_cst
	
	def formatar_nbc(natureza_bc):
		try:
			natureza_bc = f'{int(natureza_bc):02d}'
			return f'{natureza_bc} - {EFD_Tabelas.tabela_bc_do_credito[natureza_bc]}'
		except:
			return natureza_bc
	
	def formatar_tipo(tipo_do_item):
		try:
			tipo_do_item = f'{int(tipo_do_item):02d}'
			return f'{tipo_do_item} - {EFD_Tabelas.tabela_tipo_do_item[tipo_do_item]}'
		except:
			return tipo_do_item
	
	def formatar_mod(doc_fiscal):
		try:
			return f'{doc_fiscal} - {EFD_Tabelas.tabela_modelos_documentos_fiscais[doc_fiscal]}'
		except:
			return doc_fiscal
	
	# dict[key] = funtion_key(value) ; Definido apenas uma vez ; 
	# Ao escolher uma chave, o dicionário aplica uma função (que depende da chave) sobre o valor ; Ordem O(1)
	# Caso fossem utilizados vários if/then/else (ou select) a Ordem seria O(N), que é mais lento!
	myDict = {}
	for col in sorted(set(registros_totais + colunas)):
		
		match_linha = re.search(r'^Linhas', col, flags=re.IGNORECASE)
		match_data  = re.search(r'^DT_|Data', col, flags=re.IGNORECASE)
		match_chave = re.search(r'^CHV_|Chave Eletrônica', col, flags=re.IGNORECASE)
		match_ncm   = re.search(r'COD_NCM', col, flags=re.IGNORECASE)
		match_cnpj  = re.search(r'CNPJ', col, flags=re.IGNORECASE)
		match_cpf   = re.search(r'CPF',  col, flags=re.IGNORECASE)
		match_nbc   = re.search(r'NAT_BC_CRED', col, flags=re.IGNORECASE)
		match_tipo  = re.search(r'TIPO_ITEM', col, flags=re.IGNORECASE)
		match_mod   = re.search(r'COD_MOD', col, flags=re.IGNORECASE)

		match_cst_contib = re.search(r'^CST_(PIS|COFINS)|CST Código da Situação Tributária', col, flags=re.IGNORECASE)
		match_cst_icms   = re.search(r'^CST_ICMS', col, flags=re.IGNORECASE)
		
		myDict[col] = identidade
		
		# Estes vários if/elif/elif/... são executados apenas uma vez na definição da classe.
		if match_linha:
			myDict[col] = formatar_linhas		
		elif match_data:
			myDict[col] = CampoData.formatar
		elif match_chave:
			myDict[col] = CampoChaveEletronica.formatar
		elif match_ncm:
			myDict[col] = CampoNCM.formatar
		elif match_nbc:
			myDict[col] = formatar_nbc
		elif match_tipo:
			myDict[col] = formatar_tipo
		elif match_mod:
			myDict[col] = formatar_mod
		elif match_cst_contib:
			myDict[col] = formatar_cst_contrib
		elif match_cst_icms:
			myDict[col] = formatar_cst_icms
		
		if match_cnpj and match_cpf:
			myDict[col] = CampoCPFouCNPJ.formatar
		elif match_cnpj:
			myDict[col] = CampoCNPJ.formatar
		elif match_cpf:
			myDict[col] = CampoCPF.formatar
	
	if False:
		for idx, key in enumerate(myDict.keys(),1):
			print(f'{key:>40}: [{idx:>2}] {myDict[key]}')
	
	def formatar_valor(self,nome,val):
		"""
		Evitar n repetições de 'if condicao_j then A_j else B_j' tal que 1 <= j <= n, usar dicionário: myDict[key] = funtion_key(value)
		Better optimization technique using if/else or dictionary
		A series of if/else statement which receives the 'string' returns the appropriate function for it. (Around 40-50 if/else statements).
		A dictionary maintaining the key-value pair. key as strings, and values as the function objects, and one main function to search and return the function object.
		"""
		# https://stackoverflow.com/questions/11445226/better-optimization-technique-using-if-else-or-dictionary
		# https://softwareengineering.stackexchange.com/questions/182093/why-store-a-function-inside-a-python-dictionary/182095
		# https://stackoverflow.com/questions/9168340/using-a-dictionary-to-select-function-to-execute
		try:
			# https://stackoverflow.com/questions/25577578/access-class-variable-from-instance
			# val_formated = self.__class__.myDict[nome](val)
			val_formated = type(self).myDict[nome](val)
		except:
			val_formated = val
		#print(f'nome = {nome} ; val = {val} ; val_formated = {val_formated}')
		return val_formated
	
	# https://stackoverflow.com/questions/25577578/access-class-variable-from-instance
	def cadastro_do_participante(self,sped_efd):
		"""
		Registro 0150: Tabela de Cadastro do Participante
		Retorno desta função:
		info_do_participante[codigo_do_participante][campo] = descricao
		"""
		blocoZero = sped_efd._blocos['0'] # Ler apenas o bloco 0.
		info = {}
		for registro in blocoZero.registros:
			REG = registro.valores[1]
			if REG != '0150':
				continue
			codigo_do_participante = None
			for campo in registro.campos:
				valor = registro.valores[campo.indice]
				# Fazer distinção entre 'NOME' do Registro0000 e 'NOME' do Registro0150
				nome  = campo.nome + '_participante'
				if campo.nome == 'COD_PART':
					codigo_do_participante = valor
					info[codigo_do_participante] = {}
				if nome in type(self).registros_de_cadastro_do_participante and codigo_do_participante is not None:
					info[codigo_do_participante][nome] = valor
		return info

	def identificacao_do_item(self,sped_efd):
		"""
		Registro 0200: Tabela de Identificação do Item (Produtos e Serviços)
		Retorno desta função:
		info_do_item[codigo_do_item][campo] = descricao
		"""
		blocoZero = sped_efd._blocos['0'] # Ler apenas o bloco 0.
		info = {}
		for registro in blocoZero.registros:
			REG = registro.valores[1]
			if REG != '0200':
				continue
			codigo_do_item = None
			for campo in registro.campos:
				valor = registro.valores[campo.indice]
				if campo.nome == 'COD_ITEM':
					codigo_do_item = valor
					info[codigo_do_item] = {}
				if campo.nome in type(self).registros_de_identificacao_do_item and codigo_do_item is not None:
					info[codigo_do_item][campo.nome] = valor
		return info

	def plano_de_contas_contabeis(self,sped_efd):
		"""
		Registro 0500: Plano de Contas Contábeis
		Retorno desta função:
		info_do_item[codigo_do_item][campo] = descricao
		"""
		blocoZero = sped_efd._blocos['0'] # Ler apenas o bloco 0.
		info = {}
		for registro in blocoZero.registros:
			REG = registro.valores[1]
			if REG != '0500':
				continue
			codigo_do_item = None
			for campo in registro.campos:
				valor = registro.valores[campo.indice]
				if campo.nome == 'COD_CTA':
					codigo_do_item = valor
					info[codigo_do_item] = {}
			for campo in registro.campos:
				valor = registro.valores[campo.indice]
				if campo.nome in type(self).registros_de_plano_de_contas and codigo_do_item is not None:
					info[codigo_do_item][campo.nome] = valor
		return info


	def obter_info_de_abertura(self,sped_efd):
		registro = sped_efd._registro_abertura
		REG = registro.valores[1]
		nivel = registro.nivel
		codigo_cst = ''
		valor_item = ''
		valor_base = ''
		
		info_de_abertura = {}
		
		# https://www.geeksforgeeks.org/python-creating-multidimensional-dictionary/
		info_de_abertura.setdefault(nivel, {}).setdefault(codigo_cst, {}).setdefault(valor_item, {}).setdefault(valor_base, {})['Nível Hierárquico'] = nivel
		
		if self.verbose:
			print(f'registro.as_line() = {registro.as_line()} ; REG = {REG} ; nivel = {nivel}')
			print(f'info_de_abertura = {info_de_abertura}')
		
		for campo in registro.campos:
			
			valor = registro.valores[campo.indice]
			
			if campo.nome in type(self).colunas:
				info_de_abertura[nivel][codigo_cst][valor_item][valor_base][campo.nome] = valor	
			if campo.nome == 'DT_INI':
					ddmmaaaa = registro.valores[campo.indice]
					info_de_abertura[nivel][codigo_cst][valor_item][valor_base]['Data de Emissão'] = valor
					info_de_abertura[nivel][codigo_cst][valor_item][valor_base]['Mês do Período de Apuração'] = ddmmaaaa[2:4]
					info_de_abertura[nivel][codigo_cst][valor_item][valor_base]['Ano do Período de Apuração'] = ddmmaaaa[4:8]
			if campo.nome == 'DT_FIN':
					info_de_abertura[nivel][codigo_cst][valor_item][valor_base]['Data de Execução'] = valor
			if self.verbose:
				valor_formatado = self.formatar_valor(nome=campo.nome, val=valor)
				print(f'campo.indice = {campo.indice:>2} ; campo.nome = {campo.nome:>22} ; registro.valores[{campo.indice:>2}] = {valor:<50} ; valor_formatado = {valor_formatado}')		
		
		print() if self.verbose else 0
		
		return info_de_abertura
	
	def imprimir_informacoes_linha_a_linha(self,sped_efd,output_filename):
		"""
		Imprimir a título de aprendizagem
		Observar as sequências de informações dos registros dos blocos
		"""
		my_regex = r'^[A-Z]' # Ler os blocos da A a Z.

		# https://docs.python.org/3/library/csv.html
		with open(output_filename, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';')
			writer.writerow(type(self).colunas) # imprimir nomes das colunas
			
			for key in sped_efd._blocos.keys():
				
				match_bloco = re.search(my_regex, key, flags=re.IGNORECASE)
				if not match_bloco:
					continue
				
				bloco = sped_efd._blocos[key]
				count = 1
				
				for registro in bloco.registros:
					
					info = {}
					for coluna in type(self).colunas:
						info[coluna] = ''
						if coluna in self.info_de_abertura[0]['']['']:
							info[coluna] = self.info_de_abertura[0][''][''][coluna]
					
					for campo in registro.campos:
						
						valor = registro.valores[campo.indice]
						
						if campo.nome in type(self).colunas:
							info[campo.nome] = valor
						if campo.nome in type(self).registros_de_valor:
							info['Valor do Item'] = valor
						if campo.nome in type(self).registros_de_chave_eletronica:
							info['Chave Eletrônica'] = valor
						if campo.nome in type(self).registros_de_base_de_calculo:
							info['Valor da Base de Cálculo'] = valor
							
					writer.writerow( info.values() )
					
					# limitar tamanho do arquivo impresso
					# Imprimir apenas os 100 primeiros registro de cada Bloco
					count += 1
					if self.verbose and count > 100:
						break
	
	def adicionar_informacoes(self,dict_info):
		"""
		Adicionar informações em dict_info
		Formatar alguns de seus campos com o uso de tabelas ou funções
		"""
		dict_info['Arquivo da SPED EFD'] = self.basename
		dict_info['Linhas'] = next(type(self).contador_de_linhas)

		# re.search: find something anywhere in the string and return a match object.
		if re.search(r'\d{1,2}', dict_info['CST Código da Situação Tributária']): # em perl: if (cst =~ /\d{1,2}/)
			cst  = int(dict_info['CST Código da Situação Tributária'])
			if 1 <= cst <= 49:
				dict_info['Tipo de Operação'] = 'Saída'
			elif 50 <= cst <= 99:
				dict_info['Tipo de Operação'] = 'Entrada'
		
		# adicionar informação de NAT_BC_CRED para os créditos (50 <= cst <= 66) quando houver informação do CFOP e NAT_BC_CRED estiver vazio.
		if (len(dict_info['NAT_BC_CRED']) == 0 and re.search(r'\d{4}', dict_info['CFOP'])
			#and ( re.search(r'[1-9]', dict_info['ALIQ_PIS']) or re.search(r'[1-9]', dict_info['ALIQ_COFINS']) ) # aliq_cofins > 0
			and re.search(r'\d{1,2}', dict_info['CST Código da Situação Tributária'])):
			cfop = str(dict_info['CFOP'])
			cst  = int(dict_info['CST Código da Situação Tributária'])
			if 50 <= cst <= 66:
				dict_info['NAT_BC_CRED'] = type(self).natureza_da_bc_dos_creditos(cfop)
		
		# Índice de Origem do Crédito: Leia os comentários do 'Registro M100: Crédito de PIS/Pasep Relativo ao Período'.
		# Os códigos vinculados à importação (108, 208 e 308) são obtidos através da informação de CFOP iniciado em 3 (quando existente) ou pelo campo IND_ORIG_CRED nos demais casos.
		# O registro C100 possui o campo IND_OPER. IND_OPER igual a "0" (zero) indica operação de entrada. Veja os comentários do Registro C120.
		indicador_de_origem = 'Mercado Interno' # Default Value: 0 - Mercado Interno ; 1 - Mercado Externo (Importação).
		if len(dict_info['IND_ORIG_CRED']) == 0 and re.search(r'^3\d{3}', dict_info['CFOP']):
			indicador_de_origem = 'Mercado Externo (Importação)'
		dict_info['IND_ORIG_CRED'] = indicador_de_origem

		# adicionar informação de cadastro do participante obtido do Registro 0150
		# info_do_participante[codigo_do_participante][campo] = descricao
		codigo_do_participante = dict_info['COD_PART']
		if codigo_do_participante != '' and self.info_do_participante:
			for campo in self.info_do_participante[codigo_do_participante]:
				dict_info[campo] = self.info_do_participante[codigo_do_participante][campo]
		
		# adicionar informação de identificação do item obtido do Registro 0200
		# info_do_item[codigo_do_item][campo] = descricao
		codigo_do_item = dict_info['COD_ITEM']
		if codigo_do_item != '' and self.info_do_item:
			for campo in self.info_do_item[codigo_do_item]:
				dict_info[campo] = self.info_do_item[codigo_do_item][campo]
		
		# adicionar informação do plano de contas obtido do Registro 0500
		codigo_da_conta = dict_info['COD_CTA']
		# info_da_conta[codigo_da_conta][campo] = descricao
		if codigo_da_conta != '' and self.info_da_conta:
			for campo in self.info_da_conta[codigo_da_conta]:
				val = str(self.info_da_conta[codigo_da_conta][campo])
				if campo == 'COD_NAT_CC' and re.search(r'\d{1,2}', val):
					val = val.zfill(2) # val = f'{int(val):02d}'
					val = val + ' - ' + EFD_Tabelas.tabela_natureza_da_conta[val]
				dict_info[campo] = val
		
		# Ao final, formatar alguns valores dos campos
		for campo in dict_info.copy():
			valor_formatado  = self.formatar_valor(nome=campo, val=dict_info[campo])
			dict_info[campo] = valor_formatado
		
		return dict_info
	
	def imprimir_informacoes_da_efd(self,sped_efd,output_filename):
		
		my_regex = r'^[A-Z]' # Ler os blocos da A a Z.
		
		campos_necessarios = ['CST_PIS', 'CST_COFINS', 'VL_BC_PIS', 'VL_BC_COFINS']
		# Bastam os seguintes campos, desde que os registros de PIS/PASEP ocorram sempre anteriores aos registros de COFINS:
		# campos_necessarios = ['CST_COFINS', 'VL_BC_COFINS']

		if self.efd_tipo == 'efd_icms_ipi':
			campos_necessarios = ['CST_ICMS', 'VL_BC_ICMS']
		
		# https://docs.python.org/3/library/csv.html
		with open(output_filename, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter=';')
			writer.writerow(type(self).colunas) # imprimir nomes das colunas
			
			for key in sped_efd._blocos.keys():
				
				match_bloco = re.search(my_regex, key, flags=re.IGNORECASE)
				if not match_bloco:
					continue
				
				bloco = sped_efd._blocos[key]
				count = 1
				
				info = self.info_de_abertura
				
				for registro in bloco.registros:
					
					REG = registro.valores[1]
					        
					#print(f'efd_print_info: {registro = } ; {registro.nivel = } ; {registro.__dict__ = }')
					#sleep(0.1)
					
					try:
						nivel_anterior = nivel
						num_de_campos_anterior = num_de_campos
					except:
						nivel_anterior = registro.nivel + 1
						num_de_campos_anterior = len(registro.campos) + 1
					
					nivel = registro.nivel # nível atual
					num_de_campos = len(registro.campos)

					codigo_cst = ''
					valor_item = ''	
					valor_base = ''		
					
					for campo in registro.campos:
						if campo.nome in type(self).registros_de_codigo_cst:
							codigo_cst = registro.valores[campo.indice]
						if campo.nome in type(self).registros_de_base_de_calculo:
							valor_base = registro.valores[campo.indice]
						if campo.nome in type(self).registros_de_valor: 
							valor_item = registro.valores[campo.indice]
					
					if self.verbose:
						print(f'\ncount = {count:>2} ; key = {key} ; bloco = {bloco} ; REG = {REG} ; nivel_anterior = {nivel_anterior} ; nivel = {nivel} ; num_de_campos_anterior = {num_de_campos_anterior} ; num_de_campos = {num_de_campos} ; codigo_cst = {codigo_cst}')
						print(f'registro.as_line() = {registro.as_line()}')

					# As informações do pai e respectivos filhos devem ser apagadas quando o nivel hierárquico regride dos filhos para pais diferentes.
					if nivel < nivel_anterior or (nivel == nivel_anterior and num_de_campos < num_de_campos_anterior):
						if self.verbose and nivel < nivel_anterior:
							print(f'\n nivel atual: nivel = {nivel} < nivel_anterior = {nivel_anterior}; deletar informações em info a partir do nível {nivel} em diante:')
						if self.verbose and nivel == nivel_anterior and num_de_campos < num_de_campos_anterior:
							print(f'\n numero de campos atual: num_de_campos = {num_de_campos} < num_de_campos_anterior = {num_de_campos_anterior}; deletar informações em info a partir do nível {nivel} em diante:')
						# Delete items from dictionary while iterating: https://www.geeksforgeeks.org/python-delete-items-from-dictionary-while-iterating/
						for nv in list(info):
							if nv >= nivel:
								del info[nv]
								if self.verbose:
									print(f'\t *** deletar informações do nível {nv}: del info[{nv}] ***')
						print() if self.verbose else 0
					
					info.setdefault(nivel, {}).setdefault(codigo_cst, {}).setdefault(valor_item, {}).setdefault(valor_base, {})['Valor do Item'] = valor_item
					
					for campo in registro.campos:
						
						try:
							valor = registro.valores[campo.indice]
						except:
							valor = f'{REG}[{campo.indice}:{campo.nome}] sem valor definido'
							print(valor)
						
						if self.verbose:
							valor_formatado = self.formatar_valor(nome=campo.nome, val=valor)
							print(f'campo.indice = {campo.indice:>2} ; campo.nome = {campo.nome:>22} ; registro.valores[{campo.indice:>2}] = {valor:<50} ; valor_formatado = {valor_formatado}')
						
						if campo.nome in type(self).colunas:
							info[nivel][codigo_cst][valor_item][valor_base][campo.nome] = valor
						
						# Informar os campos em registros_de_data_emissao na coluna 'Data de Emissão'.
						if campo.nome in type(self).registros_de_data_emissao:
							info[nivel][codigo_cst][valor_item][valor_base]['Data de Emissão'] = valor
						# Informar os campos em registros_de_data_execucao na coluna 'Data de Execução'.
						if campo.nome in type(self).registros_de_data_execucao:
							info[nivel][codigo_cst][valor_item][valor_base]['Data de Execução'] = valor
						# Informar os campos de chave eletrônica de 44 dígitos na coluna 'Chave Eletrônica'.
						if campo.nome in type(self).registros_de_chave_eletronica:
							info[nivel][codigo_cst][valor_item][valor_base]['Chave Eletrônica'] = valor
						# Informar os campos CST_PIS e CST_COFINS na coluna 'CST Código da Situação Tributária'.
						if campo.nome in type(self).registros_de_codigo_cst:
							info[nivel][codigo_cst][valor_item][valor_base][campo.nome] = valor
							info[nivel][codigo_cst][valor_item][valor_base]['CST Código da Situação Tributária'] = valor
						# Informar os campos VL_BC_PIS e VL_BC_COFINS na coluna 'Valor da Base de Cálculo'.
						if campo.nome in type(self).registros_de_base_de_calculo:
							info[nivel][codigo_cst][valor_item][valor_base][campo.nome] = valor
							info[nivel][codigo_cst][valor_item][valor_base]['Valor da Base de Cálculo'] = valor				
					
					if self.verbose:
						print(f'\n-->info[nivel][codigo_cst][valor_item][valor_base] = info[{nivel}][{codigo_cst}][{valor_item}][{valor_base}] = {info[nivel][codigo_cst][valor_item][valor_base]}\n')
					
					#https://stackoverflow.com/questions/3931541/how-to-check-if-all-of-the-following-items-are-in-a-list
					# set(['a', 'c']).issubset(['a', 'b', 'c', 'd']) or set(lista1).issubset(lista2)
					
					if set(campos_necessarios).issubset( info[nivel][codigo_cst][valor_item][valor_base] ):
						
						# Zen of Python: Flat is better than nested.
						flattened_info = {} # eliminar os diversos niveis e trazer todas as informações para apenas uma dimensão.
						
						for coluna in type(self).colunas:
							flattened_info[coluna] = '' # atribuir valor inicial para todas as colunas
							
							if coluna in info[nivel][codigo_cst][valor_item][valor_base]:
								flattened_info[coluna] = info[nivel][codigo_cst][valor_item][valor_base][coluna]
								if self.verbose:
									print(f'nivel = {nivel:<10} ; codigo_cst = {codigo_cst:<2} ; valor_item = {valor_item:<15} ; coluna = {coluna:>35} = {info[nivel][codigo_cst][valor_item][valor_base][coluna]:<35} ; info[nivel][codigo_cst][valor_item][valor_base] = {info[nivel][codigo_cst][valor_item][valor_base]}')
								continue
							
							for nv in sorted(info,reverse=True): # nível em ordem decrescente
								if nv >= nivel:                  # informação já obtida acima
									continue
								if flattened_info[coluna] != '': # as informações obtidas do nível mais alto prevalecerá
									break
								for cst in info[nv]:
									for vl_item in info[nv][cst]:	
										for vl_base in info[nv][cst][vl_item]:
											if coluna in info[nv][cst][vl_item][vl_base]:
												flattened_info[coluna] = info[nv][cst][vl_item][vl_base][coluna]
												if self.verbose:
													print(f'nivel = {nivel} ; nv = {nv} ; codigo_cst = {cst:<2} ; valor_item = {vl_item:<15} ; coluna = {coluna:>35} = {info[nv][cst][vl_item][vl_base][coluna]:<35} ; info[nv][cst][vl_item][vl_base] = {info[nv][cst][vl_item][vl_base]}')
						
						print() if self.verbose else 0
						
						flattened_info['Nº da Linha da EFD'] = registro.numero_da_linha
						
						# Adicionar informações em flattened_info ou formatar alguns de seus campos com o uso de tabelas ou funções
						flattened_info = self.adicionar_informacoes(flattened_info)
						
						writer.writerow( flattened_info.values() )
					
					# Limitar tamanho do arquivo impresso
					# Imprimir apenas os 20 primeiros registro de cada Bloco
					count += 1
					if self.verbose and count > 20:
						break

		print(f"Gerado o arquivo csv: '{output_filename}'.")

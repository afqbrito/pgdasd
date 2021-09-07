# -*- coding: utf-8 -*-

import glob
import json
import os.path
import sys
from _io import open
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

# constantes
MODO_LEITURA = "r"
MODO_LEITURA_BINARIA = "rb"
MODO_ESCRITA = "w"
MODO_ADICAO = "a"

DELIMITADOR = "|"

REG_AAAAA = "AAAAA" + DELIMITADOR
REG_00000 = "00000" + DELIMITADOR
REG_99999 = "99999" + DELIMITADOR
REG_ZZZZZ = "ZZZZZ" + DELIMITADOR

INDICE_ID_DECLARACAO = 1
INDICE_DH_TRANSMISSAO = 4

def obtem_cabecalho_e_rodape(nome_arquivo, 
        inicio_cabecalho=None, max_linha_cab=2, 
        inicio_rodape=None, bytes_rodape=20):
    
    with open(nome_arquivo, MODO_LEITURA_BINARIA) as arquivo:
        
        cabecalho = le_linha(arquivo)
        leu_cabecalho = (cabecalho 
            and (not inicio_cabecalho or cabecalho.startswith(inicio_cabecalho)))

        linha_cab = 1
        while cabecalho and not leu_cabecalho and linha_cab < max_linha_cab: 
            cabecalho = le_linha(arquivo)
            linha_cab += 1 
            leu_cabecalho = cabecalho and cabecalho.startswith(inicio_cabecalho)
            
        arquivo.seek(-bytes_rodape, 2)
        
        leu_rodape = False
        rodape = le_linha(arquivo)
        
        if rodape:
            if inicio_rodape:
                leu_rodape = rodape.startswith(inicio_rodape)
                while rodape and not leu_rodape:
                    rodape = le_linha(arquivo)
                    leu_rodape = rodape.startswith(inicio_rodape)
                    
            else:
                leu_rodape = True
                novo_rodape = le_linha(arquivo)
                while novo_rodape:
                    rodape = novo_rodape
                    novo_rodape = le_linha(arquivo)
                    
    return (cabecalho if leu_cabecalho else None, 
            rodape if leu_rodape else None)

def le_linha(arquivo):
    return arquivo.readline().decode('ASCII').rstrip()

def descompacta_arquivo(nome_arq_zip, path_saida):
        
    with ZipFile(nome_arq_zip, 'r') as arq_zip:
        zip_info = arq_zip.filelist[0]
        return arq_zip.extract(zip_info, path_saida.absolute())

class DesmembraArquivosPgdasdPorUF:

    def __init__(self):
        
        self.padrao_nome_entrada = "*PGDASD*[.txt|.TXT|.zip|.ZIP]"
        
        self.path_entrada = None
        self.path_saida = None
        self.path_processados = None
        self.path_log = None
        self.path_temp = None
        self.path_erro = None
        
        self.uf = "PB"
        self.gerar_arquivo_unico = True
        self.saida_compactada = True
        
        self.nomes_entrada = None
        self.num_arq_entrada = 0
        
        self.entrada_tipo_zip = True
        self.nome_arq_entrada = None

        self.nome_saida_unica = None
        self.arq_processar = None
        self.reg_AAAAA = None
        self.reg_ZZZZZ = None

        self.num_linha_entrada = 0

        self.linhas_dec = None
        
        self.arq_saida = None
        self.num_linhas_saida_unica = 0
        self.nome_arq_dec = None 
        
        self.conta_dec_arquivo = 0
        self.conta_dec_desmembradas = 0

        self.tem_reg_uf = False
        
    def executar(self):
        self.configura()
        self.desmembra_arquivos()

    def configura(self):
        try:
            self.le_arquivo_de_configuracao()
            self.valida_configuracao()
         
        except Exception as e:
            raise (type(e)("Erro ao tentar configurar o demembramento. " + str(e))
                    .with_traceback(sys.exc_info()[2]))
     
    def le_arquivo_de_configuracao(self):
        nome_arq_config = sys.argv[0] + ".json"
    
        with open(nome_arq_config) as arq_config:
            config = json.loads(arq_config.read())
            
            self.path_entrada = Path(config["nome_path_entrada"])
            self.path_saida = Path(config["nome_path_saida"])
            self.path_processados = Path(config["nome_path_processados"])
            self.path_log = Path(config["nome_path_log"])
            self.path_temp = Path(config["nome_path_temp"])
            self.path_erro = Path(config["nome_path_erro"])
            
            self.uf = config["uf"]
            self.gerar_arquivo_unico = config["gerar_arquivo_unico"]
            self.saida_compactada = config["saida_compactada"]
            
            print(("\n----------" 
                   + "\nParametros de configuracao"
                   + "\n----------"
                    + "\nPadrao de nome de arquivo de entrada: '{}'"
                    + "\nDiretorio de entrada: '{}'"
                    + "\nDiretorio de saida: '{}'"
                    + "\nDiretorio de processados: '{}'"
                    + "\nDiretorio de log: '{}'"
                    + "\nDiretorio temporario: '{}'"
                    + "\nDiretorio de erro: '{}'"
                    + "\nUF: '{}'"
                    + "\nGerar arquivo unico: {}"
                    + "\nSaida compactada: {}")
                  .format(self.padrao_nome_entrada,
                          self.path_entrada.absolute(),
                          self.path_saida.absolute(),
                          self.path_processados.absolute(),
                          self.path_log.absolute(),
                          self.path_temp.absolute(),
                          self.path_erro.absolute(),
                          self.uf,
                          self.gerar_arquivo_unico,
                          self.saida_compactada
                      )
                  )
    
    def valida_configuracao(self):
        if not self.path_entrada.is_dir():
            raise FileNotFoundError("Diretorio de entrada nao localizado: '{}'"
                                    .format(self.path_entrada.absolute()))
    
    def desmembra_arquivos(self):
        print(("----------" 
               + "\nProcessando diretorio de entrada: '{}'"
               + "\n----------")
              .format(self.path_entrada.absolute()))

        try:
            self.num_arq_entrada = 0
            
            self.nomes_entrada = glob.glob(os.path.join(
                self.path_entrada.absolute(), self.padrao_nome_entrada))
            
            if len(self.nomes_entrada) == 0:
                print("--> Nenhum arquivo encontrado.")
            
            for self.nome_arq_entrada in self.nomes_entrada:
                self.num_arq_entrada += 1
                self.desmembra_arquivo()
         
        except Exception as e:
            raise (type(e)("Erro ao executar o demembramento. " + str(e))
                    .with_traceback(sys.exc_info()[2]))
    
    def desmembra_arquivo(self):
        print(("----------"
               + "\nDesmembrando arquivo {} de {}: '{}'"
               + "\n----------")
              .format(self.num_arq_entrada,
                      len(self.nomes_entrada),
                      self.nome_arq_entrada))
        
        self.conta_dec_desmembradas = 0
        
        self.ajusta_arquivo_processar()
        
        self.reg_AAAAA, self.reg_ZZZZZ = obtem_cabecalho_e_rodape(
            self.arq_processar.absolute(),
            inicio_cabecalho=REG_AAAAA, 
            inicio_rodape=REG_ZZZZZ)
        
        print("--> Cabecalho: '{}'\n--> Rodape: '{}'".format(self.reg_AAAAA, self.reg_ZZZZZ))

        if not self.gerar_arquivo_unico:
            self.nome_saida_unica = None
        else:
            self.inicializa_saida_unica()

        try:
            with self.arq_processar.open(mode=MODO_LEITURA, 
                                         encoding="cp1252", 
                                         errors="backslashreplace") as entrada:
                self.linhas_dec = None
                self.num_linha_entrada = 0
            
                for linha_entrada in entrada:
                    self.num_linha_entrada += 1
    
                    if linha_entrada.startswith(REG_00000):
                        self.inicializa_decalaracao(linha_entrada)
                        continue
                    
                    if self.linhas_dec:
                        self.linhas_dec.append(linha_entrada)
                    
                        if linha_entrada.find(DELIMITADOR + self.uf + DELIMITADOR) != -1:
                            self.tem_reg_uf = True        
                    
                        if linha_entrada.startswith(REG_99999):
                            self.encerra_declaracao()
                         
        except Exception as e:
            raise Exception("ERRO DE PROCESSAMENTO - Linha {}: {}. ".format(
                self.num_linha_entrada, linha_entrada.rstrip())) from e 

        self.encerra_saida_unica()
                     
        if self.entrada_tipo_zip:
            if self.arq_processar and self.arq_processar.is_file():
                os.remove(self.arq_processar)
                
        self.arq_processar = None
        
        os.rename(self.nome_arq_entrada, 
            self.path_processados.joinpath(os.path.basename(self.nome_arq_entrada)))

    def ajusta_arquivo_processar(self):    
        extensao = os.path.splitext(self.nome_arq_entrada.lower())[-1]
        
        self.entrada_tipo_zip = (extensao == ".zip")
        
        if not self.entrada_tipo_zip:
            self.arq_processar = Path(self.nome_arq_entrada)
        else:
            print("--> Descompactando arquivo zip")
            self.arq_processar = Path(descompacta_arquivo(self.nome_arq_entrada, self.path_temp))
    
    def inicializa_saida_unica(self):
        self.nome_saida_unica = "{}_{}.txt".format(
            os.path.splitext(os.path.basename(self.arq_processar.absolute()))[0],
            self.uf)
        
        self.arq_saida = Path(self.path_temp.absolute(), self.nome_saida_unica)
        
        with self.arq_saida.open(MODO_ESCRITA) as saida:
            saida.write(self.reg_AAAAA + "\n")
            
        self.num_linhas_saida_unica = 1
        
    def encerra_saida_unica(self):
        reg_ZZZZZ = REG_ZZZZZ + str(self.num_linhas_saida_unica + 1)
        
        with self.arq_saida.open(MODO_ADICAO) as saida:
            saida.write(reg_ZZZZZ + "\n") 
        
        os.rename(self.arq_saida.absolute(),
                  self.path_saida.joinpath(self.nome_saida_unica))
    
    def inicializa_decalaracao(self, linha_entrada):
        
        self.conta_dec_arquivo += 1

        #0     1                 2                 3                    4
        #00000|00140163201810001|01071831804082872|00279142190152163016|20181114174452|1.1.13|00140163000170|BONNET INDUSTRIA E COMERCIO DE CONFECCOES E BONE LTDA|6209|S|19940805|201810|296233,90||A|0||296233,90|0,00||
        
        valores_na_linha = linha_entrada.split(DELIMITADOR)
        
        # [1] 00140163201810001
        id_declaracao = valores_na_linha[INDICE_ID_DECLARACAO]
        
        # [4] 20181114174452
        str_dh_transmissao = datetime.strptime(valores_na_linha[INDICE_DH_TRANSMISSAO], 
            "%Y%m%d%H%M%S").strftime("%d-%m-%Y_%H%M%S")
        
        # PGDASD-00140163_2018-10_001_14-11-2018_174452.txt
        self.nome_arq_dec = "PGDASD-{}_{}_{}_{}.txt".format(
            id_declaracao[0:8],
            id_declaracao[8:12] + "-" + id_declaracao[12:14],
            id_declaracao[14:17],
            str_dh_transmissao)
            
        self.linhas_dec = [linha_entrada]
        self.tem_reg_uf = False
    
    def encerra_declaracao(self):
        if self.deve_gravar():
            self.grava_declaracao()
            
        self.linhas_dec = None
    
    def deve_gravar(self):
        return self.tem_reg_uf
    
    def grava_declaracao(self):
        
        self.conta_dec_desmembradas += 1
        print("--> Gravando a declaracao {} '{}'. Linha {}. {}"
              .format(self.conta_dec_desmembradas, self.nome_arq_dec.replace(".txt", ""), 
                      self.num_linha_entrada, self.reg_ZZZZZ.rsplit()))
        
        with self.arq_saida.open(MODO_ADICAO) as arq_saida:
            for linha in self.linhas_dec:
                arq_saida.write(linha)
                
        self.num_linhas_saida_unica += len(self.linhas_dec)
        self.linhas_dec = None 
    
if __name__ == "__main__":
    
    #locale.setlocale(locale.LC_ALL, "pt_BR")
    DesmembraArquivosPgdasdPorUF().executar()
    
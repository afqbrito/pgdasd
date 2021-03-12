# -*- coding: utf-8 -*-

import copy
import locale

# constantes
MODO_LEITURA = "r"
MODO_ESCRITA = "w"

FIM_DE_LINHA = "\n"

DELIMITADOR = "|"

INDICE_TIPO_REG = 0
INDICE_ID_DECLARACAO = 1

REG_00000 = "00000"
REG_03110 = "03110"
REG_03120 = "03120"
REG_03130 = "03130"
REG_99999 = "99999"

VIRGULA = ","

IMPOSTOS = ("IRPJ", "CSLL", "COFINS", "PIS", "INSS", "ICMS", "IPI", "ISS")
CAMPOS_REG_03110 = (26, 18, 16, 30, 22, 20, 24, 28)
CAMPOS_REG_03120_ou_03130 = (14, 6, 4, 18, 10, 8, 12, 16)

QTDE_IMPOSTOS = len(IMPOSTOS)

class AnalisaArquivoPgdasd2018:

    def __init__(self, nome_arq_entrada):
        self.arq_entrada = None
        self.arq_saida = None
        
        self.linha_entrada = None
        self.campos_dos_impostos = None
        
        self.valores_na_linha = None
        self.tipo_reg = None
        self.conta_dec_arquivo = 0
        
        self.tem_registro_03110 = False
        self.tem_registro_03120 = False
        self.tem_registro_03130 = False
        
        self.reg_00000 = None
        self.totais_dos_impostos = [0.0] * QTDE_IMPOSTOS
        
        self.nome_arq_entrada = nome_arq_entrada
        self.nome_saida = nome_arq_entrada + "-resumo.txt" 
        
        self.arq_entrada = None
        self.arq_saida = None

    # funcoes
    
    def deve_gravar(self) -> bool:
        return (self.tem_registro_03110 
                and (self.tem_registro_03120 or self.tem_registro_03130))
    
    def grava_declaracao(self):
        
        self.selecionadas += 1
        print("\t--> selecionada {}".format(self.selecionadas))
        
        self.arq_saida.write(self.reg_00000)
        self.arq_saida.write(self.id_declaracao)
        
        imposto_total = 0.0
        for i in range(QTDE_IMPOSTOS):
            imposto_total += self.totais_dos_impostos[i] 
            
            self.totais_dos_impostos[i] = IMPOSTOS[i] + ": " + locale.format_string(
                "%.2f", self.totais_dos_impostos[i], grouping=True, monetary=True) 
        
        imposto_total = (DELIMITADOR + "Total: " 
            + locale.format_string("%.2f", imposto_total, grouping=True, monetary=True))
        
        self.arq_saida.write(DELIMITADOR.join(self.totais_dos_impostos) 
                             + imposto_total + 2*FIM_DE_LINHA)
         
        return
    
    def coleta_impostos(self):
        
        for i in range(QTDE_IMPOSTOS):
            total = (self.totais_dos_impostos[i] 
                + locale.atof(self.valores_na_linha[self.campos_dos_impostos[i] - 1])) 
            
            self.totais_dos_impostos[i] = total 
        
        return
    
    def processa_registro(self):
        
        if self.tipo_reg == REG_03110:
            self.tem_registro_03110 = True
            self.campos_dos_impostos = CAMPOS_REG_03110
        
        else:
            if self.tipo_reg == REG_03120:
                self.tem_registro_03120 = True
            
            else:
                self.tem_registro_03130 = True
            
            self.campos_dos_impostos = CAMPOS_REG_03120_ou_03130
            
        self.coleta_impostos()
        
        return
    
    def inicializa_decalaracao(self):
        
        self.reg_00000 = copy.deepcopy(self.linha_entrada)
        
        self.conta_dec_arquivo += 1
        print("{:9d}:{:7d}: {:s}".format(self.num_linha_entrada, self.conta_dec_arquivo, self.reg_00000), end="")
        
        id_declaracao = self.valores_na_linha[INDICE_ID_DECLARACAO]
        
        self.id_declaracao = (id_declaracao[0:8] + DELIMITADOR
                              + id_declaracao[12:14] + "/" + id_declaracao[8:12] + DELIMITADOR
                              + id_declaracao[14:17]
                              + FIM_DE_LINHA)
                
        self.totais_dos_impostos = [0.0] * QTDE_IMPOSTOS
        
        self.tem_registro_03110 = False
        self.tem_registro_03120 = False
        self.tem_registro_03130 = False
        
        return
    
    def processa_declaracao(self):
        
        try:
            self.inicializa_decalaracao()
            
            for self.linha_entrada in self.arq_entrada:
                
                self.num_linha_entrada += 1
                
                self.valores_na_linha = self.linha_entrada.split(DELIMITADOR)
            
                self.tipo_reg = self.valores_na_linha[INDICE_TIPO_REG] 
            
                if self.tipo_reg in (REG_03110, REG_03120, REG_03130):
                    if self.linha_entrada.count(VIRGULA) > 0:
                        self.processa_registro() 
            
                elif self.tipo_reg == REG_99999:
                    break 
                     
            if self.deve_gravar():
                self.grava_declaracao()
                
        except:
            print("\t--> ERRO DE PROCESSAMENTO - Linha {}".format(self.num_linha_entrada), end="")
                 
        return
    
    def processa_arquivo(self):
    
        self.arq_entrada = open(self.nome_arq_entrada, mode=MODO_LEITURA)
        self.arq_saida = open(self.nome_saida, mode=MODO_ESCRITA, newline=FIM_DE_LINHA)
        
        self.num_linha_entrada = 0
        self.selecionadas = 0
        
        for self.linha_entrada in self.arq_entrada:
            
            self.num_linha_entrada += 1
            
            self.valores_na_linha = self.linha_entrada.split(DELIMITADOR)
            
            self.tipo_reg = self.valores_na_linha[INDICE_TIPO_REG]
            
            if self.tipo_reg == REG_00000:
                self.processa_declaracao()
        
        self.arq_saida.close()
        self.arq_entrada.close()

# inicializacao

locale.setlocale(locale.LC_ALL, "pt_BR")

ArquivoPgdasd2018("../../arquivos/90-0000-PUB-PGDASD2018-20181114-01.txt").processa_arquivo()

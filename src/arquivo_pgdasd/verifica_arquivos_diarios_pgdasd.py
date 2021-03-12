import glob

def verifica_arquivos_diarios(padrao_nome_zip, nome_dir_anos):
    
    diretorios_ano = glob.glob(nome_dir_anos, recursive=True)
    diretorios_ano.sort()
    
    qtde_anos = len(diretorios_ano)
    conta_anos = 0
    for subdir_ano in diretorios_ano:
        conta_anos += 1
        print("----------------------------------------")
        print("ano {:02d}/{:02d}: {}".format(conta_anos, qtde_anos, subdir_ano))
        print("----------------------------------------")
        print()
        
        diretorios_mes = glob.glob(subdir_ano + "\\*", recursive=True)
        diretorios_mes.sort()

        qtde_meses = len(diretorios_mes)
        conta_meses = 0
        for subdir_mes in diretorios_mes:
            conta_meses += 1
            print("----------------------------------------")
            print("mes {:02d}/{:02d}: {}".format(conta_meses, qtde_meses, subdir_mes))
            print("----------------------------------------")
            
            arquivos = glob.glob(subdir_mes + "\\**\\" + padrao_nome_zip,
                recursive=True)
            arquivos.sort()
            
            qtde_arquivos = len(arquivos)
            conta_arquivos = 0
            for arquivo in arquivos:
                conta_arquivos += 1
                print("arquivo {:02d}/{:02d}: {}".format(
                    conta_arquivos, qtde_arquivos, arquivo))
    
            print("----------------------------------------")
            print()

if __name__ == "__main__":

    verifica_arquivos_diarios("*-PGDASD2018-????????-??*.zip",
        ("S:\\GOIEF\\Nucleo do Simples Nacional\\ARQUIVOS BAIXADOS RFB"
            + "\\PGDAS-D\\PGDAS-D_2018\\*")
    )
    
    verifica_arquivos_diarios("*-PGDASD-????????-??*.zip",
        ("S:\\GOIEF\\Nucleo do Simples Nacional\\ARQUIVOS BAIXADOS RFB"
            + "\\PGDAS-D\\PGDAS-D\\*")
    )
    

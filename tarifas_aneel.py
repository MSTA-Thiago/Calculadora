#!/usr/bin/env python
#coding: utf-8
import pandas as pd
from datetime import datetime


# Carregar os arquivos CSV
parte1 = pd.read_csv('parte1.csv', sep=';', encoding='ISO-8859-1')
parte2 = pd.read_csv('parte2.csv', sep=';', encoding='ISO-8859-1')
parte3 = pd.read_csv('parte3.csv', sep=';', encoding='ISO-8859-1')

# Concatenar os DataFrames
tarifa = pd.concat([parte1, parte2, parte3])

# Salvar o DataFrame resultante em um único arquivo CSV
#df.to_csv('tarifa.csv', sep=';', index=False, encoding='ISO-8859-1')




#arquivo = 'tarifa.csv'

# url = 'https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv'
#tarifas = pd.read_csv(url, low_memory=False,encoding='latin-1',sep=';')
#tarifa = pd.read_csv(arquivo, low_memory=False, encoding='ISO-8859-1', sep=';')

distribuidoras =tarifa['SigAgente'].dropna().unique().tolist()

tarifa = tarifa[(tarifa['DscBaseTarifaria'] == "Tarifa de Aplicação")]
tarifa = tarifa[(tarifa['SigAgenteAcessante'] == "Não se aplica")]
tarifa = tarifa[(tarifa['DscDetalhe'] == "Não se aplica")]
tarifa = tarifa[(tarifa['DscModalidadeTarifaria'] == "Azul") | (tarifa['DscModalidadeTarifaria'] == "Verde")]
tarifa = tarifa[(tarifa['DscSubGrupo'] == "A2") | (tarifa['DscSubGrupo'] == "A3") | (tarifa['DscSubGrupo'] == "A3a") | (tarifa['DscSubGrupo'] == "A4") | (tarifa['DscSubGrupo'] == "AS")]
tarifa = tarifa.reset_index(drop=True)

tarifa['VlrTUSD']=tarifa['VlrTUSD'].str.replace(',', '.')
tarifa['VlrTE']=tarifa['VlrTE'].str.replace(',', '.')

for a in range(0, len(tarifa)):
    tarifa.loc[a, 'DatFimVigencia']=datetime.strptime(tarifa.loc[a, 'DatFimVigencia'], '%Y-%M-%d')
dict_types = {"DatFimVigencia":"datetime64[ns]"}
tarifa = tarifa.astype(dict_types)

for a in range(0, len(tarifa)):
    tarifa.loc[a, 'AnoVigencia']=tarifa.loc[a, 'DatFimVigencia'].year
tarifa = tarifa[(tarifa['AnoVigencia'] > 2023)]

tarifa = tarifa.reset_index(drop=True)
tarifa.set_index(['SigAgente', 'DscSubGrupo', 'DscModalidadeTarifaria', 'NomPostoTarifario', 'DscUnidadeTerciaria'], inplace=True)
tarifa.sort_index()

def tarifa_atual(distribuidora,subgrupo,modalidade):
    """
    Retorna as tarifas para simulação das contas no cativo e livre.
    Parametros:
    distribuidora
    subgrupo: A2, A3, A3a, A4, AS
    modalidade: Azul e Verde
    Uso:
    Para usar digite
    tarifa_atual(distribuidora,subgrupo,modalidade)
    """
    try:
        if (modalidade == 'Verde'):
            demanda_fp_kw = tarifa.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Não se aplica' and DscUnidadeTerciaria =='kW'")
            demanda_ponta_kw = 0
            TUSDd_P = 0
        elif (modalidade == 'Azul'):
            demanda_ponta_kw = tarifa.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='kW'")
            demanda_fp_kw = tarifa.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='kW'")
            TUSDd_P = float(demanda_ponta_kw.iloc[0,10])

        fora_ponta_mwh =  tarifa.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='MWh'")
        ponta_mwh =  tarifa.query("SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @modalidade and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='MWh'")
        TE_FP = float(fora_ponta_mwh.iloc[0,11])/1000
        TUSDe_FP = float(fora_ponta_mwh.iloc[0,10])/1000
        TE_P = float(ponta_mwh.iloc[0,11])/1000
        TUSDe_P = float(ponta_mwh.iloc[0,10])/1000
        TUSDd_FP = float(demanda_fp_kw.iloc[0,10])

        DscREH = fora_ponta_mwh.iloc[0,1]
        #print("TE_FP " + str(TE_FP))
        #print("TE_P " + str(TE_P))
        #print("TUSDd_FP " + str(TUSDd_FP))
        #print("TUSDd_P " + str(TUSDd_P))
        #print("TUSDe_P " + str(TUSDe_P))
        #print("TUSDe_FP " + str(TUSDe_FP))
        #print("DscREH " + DscREH)
        return TE_FP, TUSDe_FP, TE_P, TUSDe_P, TUSDd_P, TUSDd_FP, DscREH
    except:
        return 0,0,0,0,0,0,0

distribuidora = 'LIGHT'
subgrupo = 'A4'
modalidade = 'Azul'
print(tarifa_atual(distribuidora,subgrupo,modalidade)[6])

#print(tarifa)

import urllib
import pandas as pd
from datetime import datetime


# Definição das variáveis
distribuidora = 'EMS'
subgrupo = 'A2'
InputModal = 'Verde'

preco_pmt = 200
InputDemandaHP = 100
InputDemandaHFP = 100
InputConsumoHP = 5000
InputConsumoHFP = 20000
ICMS = 18
PASEP = 5

# Concatenar os DataFrames
url = 'https://dadosabertos.aneel.gov.br/dataset/5a583f3e-1646-4f67-bf0f-69db4203e89e/resource/fcf2906c-7c32-4b9b-a637-054e7a5234f4/download/tarifas-homologadas-distribuidoras-energia-eletrica.csv'
tarifas = pd.read_csv(url, low_memory=False,encoding='latin-1',sep=';')

distribuidoras = tarifas['SigAgente'].dropna().unique().tolist()

tarifas = tarifas[(tarifas['DscBaseTarifaria'] == "Tarifa de Aplicação")]
tarifas = tarifas[(tarifas['SigAgenteAcessante'] == "Não se aplica")]
tarifas = tarifas[(tarifas['DscDetalhe'] == "Não se aplica")]
tarifas = tarifas[(tarifas['DscModalidadeTarifaria'] == "Azul") | (tarifas['DscModalidadeTarifaria'] == "Verde")]
tarifas = tarifas[
    (tarifas['DscSubGrupo'] == "A2") | (tarifas['DscSubGrupo'] == "A3") | (tarifas['DscSubGrupo'] == "A3a") | (
            tarifas['DscSubGrupo'] == "A4") | (tarifas['DscSubGrupo'] == "AS")]
tarifas = tarifas.reset_index(drop=True)
tarifas['VlrTUSD'] = tarifas['VlrTUSD'].str.replace(',', '.')
tarifas['VlrTE'] = tarifas['VlrTE'].str.replace(',', '.')

for a in range(0, len(tarifas)):
    # Correção data
    tarifas.loc[a, 'DatFimVigencia'] = datetime.strptime(tarifas.loc[a, 'DatFimVigencia'], '%Y-%M-%d')
dict_types = {"DatFimVigencia": "datetime64[ns]"}
tarifas = tarifas.astype(dict_types)

for a in range(0, len(tarifas)):
    tarifas.loc[a, 'AnoVigencia'] = tarifas.loc[a, 'DatFimVigencia'].year
tarifas = tarifas[(tarifas['AnoVigencia'] > 2023)]
tarifas = tarifas.reset_index(drop=True)

tarifas.set_index(['SigAgente', 'DscSubGrupo', 'DscModalidadeTarifaria', 'NomPostoTarifario', 'DscUnidadeTerciaria'],
                  inplace=True)
tarifas.sort_index()

"""**Função para obtenção da tarifa atual**"""


def tarifa_atual(distribuidora, subgrupo, InputModal):
    try:
        if (InputModal == 'Verde'):
            demanda_fp_kw = tarifas.query(
                "SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @InputModal and NomPostoTarifario =='Não se aplica' and DscUnidadeTerciaria =='kW'")
            demanda_ponta_kw = 0
            TUSDd_P = 0
        elif (InputModal == 'Azul'):
            demanda_ponta_kw = tarifas.query(
                "SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @InputModal and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='kW'")
            demanda_fp_kw = tarifas.query(
                "SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @InputModal and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='kW'")
            TUSDd_P = float(demanda_ponta_kw.iloc[0, 10])

        fora_ponta_mwh = tarifas.query(
            "SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @InputModal and NomPostoTarifario =='Fora ponta' and DscUnidadeTerciaria =='MWh'")
        ponta_mwh = tarifas.query(
            "SigAgente == @distribuidora and DscSubGrupo == @subgrupo and DscModalidadeTarifaria == @InputModal and NomPostoTarifario =='Ponta' and DscUnidadeTerciaria =='MWh'")
        TE_FP = float(fora_ponta_mwh.iloc[0, 11]) / 1000
        TUSDe_FP = float(fora_ponta_mwh.iloc[0, 10]) / 1000
        TE_P = float(ponta_mwh.iloc[0, 11]) / 1000
        TUSDe_P = float(ponta_mwh.iloc[0, 10]) / 1000
        TUSDd_FP = float(demanda_fp_kw.iloc[0, 10])
        TUSDe = TUSDe_P - TUSDe_FP

        DscREH = fora_ponta_mwh.iloc[0, 1]
        print("TE_FP " + str(TE_FP))
        print("TE_P " + str(TE_P))
        print("TUSDd_FP " + str(TUSDd_FP))
        print("TUSDd_P " + str(TUSDd_P))
        print("TUSDe_P " + str(TUSDe_P))
        print("TUSDe_FP " + str(TUSDe_FP))
        print("DscREH " + DscREH)
        print("TUSDe " + str(TUSDe))
        return TE_FP, TUSDe_FP, TE_P, TUSDe_P, TUSDd_P, TUSDd_FP, DscREH, TUSDe
    except:
        return 0, 0, 0, 0, 0, 0, 0


"""**Função para cálculo**"""

t_atual = tarifa_atual(distribuidora, subgrupo, InputModal)

tarifa_atual(distribuidora, subgrupo, InputModal)

def do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP, preco_pmt,
                   InputModal):
    try:
        TE_FP = t_atual[0]
        TUSDe_FP = t_atual[1]
        TE_P = t_atual[2]
        TUSDe_P = t_atual[3]
        TUSDd_P = t_atual[4]
        TUSDd_FP = t_atual[5]
        TUSDe = t_atual[7]

        imposto = (1 / (1 - (ICMS / 100))) * (1 / (1 - (PASEP / 100)))
        # Cativo
        # Demanda
        if InputModal == 'Azul':
            demanda_ativa_unica = 0
            # Ponta
            demanda_ativa_p = TUSDd_P * InputDemandaHP * imposto
            # Fora Ponta
            demanda_ativa_fp = TUSDd_FP * InputDemandaHFP * imposto

        if InputModal == 'Verde':
            # Demanda ativa única
            demanda_ativa_p = 0
            demanda_ativa_fp = 0
            demanda_ativa_unica = TUSDd_FP * InputDemandaHFP * imposto

        # Energia
        energia_p = (TE_P + TUSDe_P) * InputConsumoHP * imposto
        energia_fp = (TE_FP + TUSDe_FP) * InputConsumoHFP * imposto

        # Resumo
        total_cativo = demanda_ativa_p + demanda_ativa_fp + energia_p + energia_fp + demanda_ativa_unica
        preco_medio_cativo = total_cativo / ((InputConsumoHP + InputConsumoHFP) / 1000)

        # Livre
        # Fatura Uso
        # Fio / TF: Demanda
        if InputModal == 'Azul':
            comp_fio_unica = 0
            # Ponta
            comp_fio_p = TUSDd_P * InputDemandaHP * imposto
            # Fora Ponta
            comp_fio_fp = TUSDd_FP * InputDemandaHFP * imposto

        if InputModal == 'Verde':
            # Demanda ativa única
            comp_fio_p = 0
            comp_fio_fp = 0
            comp_fio_unica = (TUSDd_FP) * InputDemandaHFP * imposto

        # Encargo
        comp_encargo_p = InputConsumoHP * TUSDe_P * imposto
        comp_encargo_fp = InputConsumoHFP * TUSDe_FP * imposto

        # Descontos
        if InputModal == 'Azul':
            desconto_fio_unico = 0
            # Ponta
            desconto_fio_fp = TUSDd_FP * InputDemandaHFP
            desconto_fio_p = TUSDd_P * InputDemandaHP

        if InputModal == 'Verde':
            # Demanda ativa única
            desconto_fio_fp = 0
            desconto_fio_unico = TUSDd_FP * InputDemandaHFP
            desconto_fio_p = TUSDe * InputConsumoHP

        desconto = (desconto_fio_unico + desconto_fio_fp + desconto_fio_p) * 0.5

        # Resumo Fatura Uso
        fatura_uso = comp_fio_p + comp_fio_fp + comp_fio_unica + comp_encargo_p + comp_encargo_fp - desconto

        # Fatura Energia
        fatura_energia = (InputConsumoHP + InputConsumoHFP) * preco_pmt / (0.82 * 1000)
        # Resumo
        total_livre = fatura_uso + fatura_energia
        preco_medio_livre = total_livre / ((InputConsumoHP + InputConsumoHFP) / 1000)

        desconto = (1 - total_livre / total_cativo) * 100
        # Adicionar desconto
        print(total_livre)
        print(total_cativo)
        print(desconto)
        print(preco_medio_livre)
        return total_livre, total_cativo, desconto, preco_medio_livre
    except:
        return 'error', 0, 0, 0


do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP, preco_pmt, InputModal)

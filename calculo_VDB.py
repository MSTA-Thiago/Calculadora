#!/usr/bin/env python
# coding: utf-8
#import pandas as pd
#from datetime import datetime
from tarifas_aneel import tarifa_atual

incentivada = 110
convencional = 75
swap = incentivada - convencional

def cal_VDB(distribuidora,subgrupo,modalidade,InputDemandaHP,InputDemandaHFP,InputConsumoHP,InputConsumoHFP):
    """
    Retorna o cálculo do VDB e a indicação de qual tipo de energia utilizar.
    Parametros:
    distribuidora
    subgrupo: A2, A3, A3a, A4, AS
    modalidade: Azul e Verde
    Uso:
    Para usar digite
    cal_VDB(distribuidora,subgrupo,modalidade)
    """

    t_atual = tarifa_atual(distribuidora,subgrupo,modalidade)
    TUSDe_FP = t_atual[1]
    TUSDe_P = t_atual[3]
    TUSDd_P = t_atual[4]
    TUSDd_FP = t_atual[5]

    try:
        if (modalidade == 'Azul'):
            VDB = (TUSDd_P * InputDemandaHP + TUSDd_FP * InputDemandaHFP)*0.5/(InputConsumoHP + InputConsumoHFP)
            fatorcarga_fp = InputConsumoHFP/(InputDemandaHFP*(730-65))
            fatorcarga_p = InputConsumoHP/(InputDemandaHP*65)
        elif (modalidade == 'Verde'):
            VDB = (InputConsumoHP * (TUSDe_P - TUSDe_FP) + InputDemandaHFP*TUSDd_FP)*0.5/(InputConsumoHP + InputConsumoHFP)
            fatorcarga_fp = InputConsumoHFP/(InputDemandaHFP*(730-65))
            fatorcarga_p = InputConsumoHP/(InputDemandaHFP*65)
        if (VDB > 2*swap):
            energia = 'i1'
        elif (VDB > swap):
            energia =  'i5'
        else:
            energia =  'conv'
        return VDB,energia,fatorcarga_p,fatorcarga_fp
    except:
        return 0,'erro',0

distribuidora = 'LIGHT'
subgrupo = 'A4'
modalidade = 'Azul'
print(tarifa_atual(distribuidora,subgrupo,modalidade)[6])


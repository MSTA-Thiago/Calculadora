from tarifas_aneel import tarifa_atual
from calculo_VDB import cal_VDB

# Inicializar
imposto = 1
demanda_ativa_p = 0
preco_pmt = 150

distribuidora = 'ELETROPAULO'
subgrupo = 'A4'
modalidade = 'Verde'
InputDemandaHP = 0
InputDemandaHFP = 500
InputConsumoHP = 4299
InputConsumoHFP = 36695

TE_FP = 0.26825
TE_P = 0.42317
TUSDd_FP = 17.95
TUSDd_P = 0
TUSDe_P = 0.80435
TUSDe_FP = 0.09001
t_atual = [TE_FP, TUSDe_FP, TE_P, TUSDe_P, TUSDd_P, TUSDd_FP,0]
energia = 'i5'

t_atual = tarifa_atual(distribuidora,subgrupo,modalidade)
energia = cal_VDB(distribuidora,subgrupo,modalidade,InputDemandaHP,InputDemandaHFP,InputConsumoHP,InputConsumoHFP)[1]

def do_calculation(t_atual,energia,InputDemandaHP,InputDemandaHFP,InputConsumoHP,InputConsumoHFP,imposto):
    try:
        TE_FP = t_atual[0]
        TUSDe_FP = t_atual[1]
        TE_P = t_atual[2]
        TUSDe_P = t_atual[3]
        TUSDd_P = t_atual[4]
        TUSDd_FP = t_atual[5]

        # Cativo
        # Demanda
        # Fora Ponta
        demanda_ativa_fp = TUSDd_FP * InputDemandaHFP * imposto
        if modalidade == 'Azul':
        # Ponta
            demanda_ativa_p = TUSDd_P * InputDemandaHP * imposto

        if modalidade == 'Verde':
        # Demanda ativa única
            demanda_ativa_p = 0

        # Energia
        energia_p = (TE_P + TUSDe_P) * InputConsumoHP * imposto
        energia_fp = (TE_FP + TUSDe_FP) * InputConsumoHFP * imposto

        # Resumo
        total_cativo = demanda_ativa_p + demanda_ativa_fp + energia_p + energia_fp
        preco_medio_cativo = total_cativo/((InputConsumoHP + InputConsumoHFP)/1000)

        #Livre
        # Fatura Uso
        # Fora Ponta
        comp_fio_fp = TUSDd_FP * InputDemandaHFP * imposto

            # Fio
        if modalidade == 'Azul':
                # Ponta
            comp_fio_p = TUSDd_P * InputDemandaHP * imposto

        if modalidade == 'Verde':
                # Demanda ativa única
            comp_fio_p = 0

            # Encargo
        comp_encargo_p = (InputConsumoHP + InputConsumoHFP)
        comp_encargo_fp = (InputConsumoHP + InputConsumoHFP)

            # Descontos
        desconto_fio_fp = InputDemandaHFP
        if modalidade == 'Azul':
                # Ponta
            desconto_fio_p = TUSDd_P * InputDemandaHP * imposto

        if modalidade == 'Verde':
                # Demanda ativa única
            desconto_fio_p = 0

        desconto_encargo = InputDemandaHFP

        #Resumo Fatura Uso
        fatura_uso = comp_fio_p + comp_fio_fp + comp_encargo_p + comp_encargo_fp + desconto_fio_fp + desconto_fio_p + desconto_encargo

        # Fatura Energia
        fatura_energia = (InputConsumoHP + InputConsumoHFP)*preco_pmt/(0.82*1000)
        # Resumo
        total_livre = fatura_uso + fatura_energia
        preco_medio_livre = total_livre/((InputConsumoHP + InputConsumoHFP)/1000)

        return demanda_ativa_p,demanda_ativa_fp,energia_p,energia_fp,total_cativo,preco_medio_cativo,comp_fio_p,comp_fio_fp,comp_encargo_p,comp_encargo_fp,desconto_fio_fp,desconto_fio_p,desconto_encargo,fatura_uso,fatura_energia,total_livre,preco_medio_livre
    except:
        return 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

do_calculation(t_atual,energia,InputDemandaHP,InputDemandaHFP,InputConsumoHP,InputConsumoHFP,imposto)
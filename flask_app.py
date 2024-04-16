# A very simple Flask Hello World app for you to get started with...
from flask import Flask, render_template, request

from tarifas_aneel import tarifa_atual
from calculo import InputConsumoHFP, InputConsumoHP, InputDemandaHFP, InputDemandaHP, do_calculation

# from InterfaceVisual import interface_visual
# from LogicaCalculadora import LogicaCalculadora
# from Grafico import Grafico
# from RelatorioPDF import RelatorioPDF

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=["GET", "POST"])
def teste():
    return render_template('teste.html')


@app.route('/simulacao-preco', methods=["GET", "POST"])
def home():
    print('log funcionando')
    errors = ""
    result = ""
    InputDemandaHP = None
    InputDemandaHFP = None
    InputConsumoHP = None
    InputConsumoHFP = None
    ICMS = None
    PASEP = None
    Inicio = None
    Fim = None
    Imposto = None
    dist = None
    subgrupo = None
    modalidade = None
    if request.method == "POST":
        try:
            dist = float(request.form["dist"])
            subgrupo = float(request.form["subgrupo"])
            modalidade = float(request.form["modalidade"])
            tarifas_usar = tarifa_atual(dist, subgrupo, modalidade)
            print(tarifas_usar)
            # TE_HFP, TUSD_HFP, TE_HP, TUSD_HP, Demanda_P, Demanda_FP, DscREH,distribuidoras
        except:
            errors += "Preencher o campo Distribuidora. \n\n"
        try:
            InputDemandaHP = float(request.form["InputDemandaHP"])
        except:
            # errors += "{!r} is not a number.\n".format(request.form["InputDemandaHP"])
            errors += "Preencher o campo InputDemandaHP.\n\n"
        try:
            InputDemandaHFP = float(request.form["InputDemandaHFP"])
        except:
            errors += "Preencher o campo InputDemandaHFP. \n\n"
        try:
            InputConsumoHP = float(request.form["InputConsumoHP"])
        except:
            errors += "Preencher o campo InputConsumoHP. \n\n"
        try:
            InputConsumoHFP = float(request.form["InputConsumoHFP"])
        except:
            errors += "Preencher o campo InputConsumoHFP. \n\n"
        try:
            ICMS = float(request.form["ICMS"])
        except:
            errors += "Preencher o campo ICMS. \n\n"
        try:
            PASEP = float(request.form["PASEP"])
        except:
            errors += "Preencher o campo PASEP. \n\n"
        # try:
        #    Inicio = request.form["Inicio"]
        # except:
        #    errors += "Preencher o campo Inicio. \n\n"
        # try:
        #    Fim = request.form["Fim"]
        # except:
        #    errors += "Preencher o campo Fim. \n\n"
        # try:
        #     lead = lead(content=request.form["email"])
        #     db.session.add(lead)
        #     db.session.commit()
        # except:
        #     errors += "Preencher o campo email. \n\n"
        if InputDemandaHP is not None and InputDemandaHFP is not None and InputConsumoHP is not None and InputConsumoHFP is not None and ICMS is not None and PASEP is not None:  # and Inicio is not None and Fim is not None:
            result1 = do_calculation(InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP)
            demanda_ativa_p = result1[0]
            demanda_ativa_fp = result1[1]
            energia_p = result1[2]
            energia_fp = result1[3]
            total_cativo = result1[4]
            preco_medio_cativo = result1[5]
            comp_fio_p = result1[6]
            comp_fio_fp = result1[7]
            comp_encargo_p = result1[8]
            comp_encargo_fp = result1[9]
            desconto_fio_fp = result1[10]
            desconto_fio_p = result1[11]
            desconto_encargo = result1[12]
            fatura_uso = result1[13]
            fatura_energia = result1[14]
            total_livre = result1[15]
            preco_medio_livre = result1[16]

            TE_HFP, TUSD_HFP, TE_HP, TUSD_HP, Demanda_P, Demanda_FP, DscREH, distribuidoras = tarifa_atual(dist, subgrupo,
                                                                                                   modalidade)

            assert isinstance(preco_medio_livre, object)
            print("O preço médio é:", preco_medio_livre)

    return render_template('cativo.html', errors=errors, result=result)


@app.route('/metodologia')
def metodologia_route():
    return render_template('metodologia.html')


@app.route('/contato')
def contato_route():
    return render_template('contato.html')


# @app.route('/cativo')
# def cativo_route():
#    return render_template("cativo.html")

@app.route('/livre')
def livre_route():
    return render_template('livre.html')


@app.route('/desconto')
def desconto_route():
    return render_template('desconto.html')


@app.route('/preco')
def preco_route():
    return render_template('preco.html')


if __name__ == '__main__':
    app.run(debug=True)

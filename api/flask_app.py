from flask import Flask, render_template, request, jsonify
from api.calculadora import tarifa_atual, do_calculation, t_atual, InputModal

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('home.html')



@app.route('/simulacao-preco', methods=["GET", "POST"])
def calculo():
    print('log funcionando')

    errors = {}
    result = {}
    if request.method == "POST":
        try:
            distribuidora = request.form["distribuidora"]
            subgrupo = request.form["subgrupo"]
            modalidade = request.form["InputModal"]
            # Chamar tarifa_atual com os novos valores dos formulários
            t_atual = tarifa_atual(distribuidora, subgrupo, modalidade)
            print(t_atual)
        except Exception as e:
            errors["tarifa"] = "Erro ao calcular as tarifas: {}".format(str(e))

        try:
            InputDemandaHP = float(request.form["InputDemandaHP"])
            InputDemandaHFP = float(request.form["InputDemandaHFP"])
            InputConsumoHP = float(request.form["InputConsumoHP"])
            InputConsumoHFP = float(request.form["InputConsumoHFP"])
            ICMS = float(request.form["ICMS"])
            PASEP = float(request.form["PASEP"])
            preco_pmt = float(request.form["preco_pmt"])
        except ValueError:
            errors["entrada"] = "Os campos devem ser números válidos."

        if not errors:
            # Chamar do_calculation com os novos valores dos formulários e t_atual atualizado
            result = do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP, preco_pmt, modalidade)
            total_livre, total_cativo, desconto, preco_medio_livre = result
            return jsonify({
                'resultado': {
                    'total_cativo': total_cativo,
                    'total_livre': total_livre,
                    'desconto': desconto,
                    'preco_medio_livre': preco_medio_livre
                }
            }), 200  # Código 200 indica sucesso
        else:
            return jsonify({'errors': errors}), 400  # Código 400 indica erro de requisição

    return render_template('calculo.html', errors=errors, result=result)


if __name__ == '__main__':
    app.run(debug=True)


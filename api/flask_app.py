from flask import Flask, render_template, request, send_file
from api.calculadora import tarifa_atual, do_calculation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
            try:
                razao_social = request.form["conta"]
                cnpj = request.form["cnpj"]
                # Chamar do_calculation com os novos valores dos formulários e t_atual atualizado
                result = do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP, preco_pmt, modalidade)
                total_livre, total_cativo, desconto, preco_medio_livre = result
                result_string1 = f"Total Livre: {total_livre}"
                result_string2 = f"Total Cativo: {total_cativo}"
                result_string3 = f"Desconto: {desconto}%"
                result_string4 = f"Preço Médio Livre: {preco_medio_livre}"
                # Gerar o PDF
                c = canvas.Canvas("calculation_results.pdf", pagesize=letter)
                c.drawString(100, 750, "Razão social: " + razao_social)
                c.drawString(100, 735, "CNPJ: " + cnpj)
                c.drawString(100, 720, result_string1)
                c.drawString(100, 705, result_string2)
                c.drawString(100, 690, result_string3)
                c.drawString(100, 675, result_string4)
                c.save()

                # Redirecionar o usuário para o PDF gerado
                return send_file("calculation_results.pdf", as_attachment=True, attachment_filename="calculation_results.pdf")

            except Exception as e:
                errors["pdf"] = "Erro ao gerar o PDF: {}".format(str(e))

    return render_template('calculo.html', errors=errors, result=result)


if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request, send_file
from api.calculadora import tarifa_atual, do_calculation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

app = Flask(__name__)
app.config["DEBUG"] = True

PDF_DIR = tempfile.gettempdir()

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
                    # Criar strings de resultados
                result_strings = [
                    f"Razão Social: {razao_social}",
                    f"CNPJ: {cnpj}",
                    f"Total Livre: {total_livre}",
                    f"Total Cativo: {total_cativo}",
                    f"Desconto: {desconto}%",
                    f"Preço Médio Livre: {preco_medio_livre}"
                ]
    
                # Gerar o PDF
                file_path = f"{PDF_DIR}/calculation_results.pdf"
                c = canvas.Canvas(file_path, pagesize=letter)
                for i, text in enumerate(result_strings):
                    c.drawString(100, 750 - (i * 15), text)
                c.save()

            # Redirecionar o usuário para o PDF gerado
            return send_file(file_path, as_attachment=False)

    return render_template('calculo.html', errors=errors, result=result)


if __name__ == '__main__':
    app.run(debug=True)


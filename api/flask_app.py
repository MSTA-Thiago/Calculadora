from flask import Flask, render_template, request, Response, send_file
from api.calculadora import tarifa_atual, do_calculation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.config["DEBUG"] = True

form_data = {}

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('calculo.html')


@app.route('/simulacao-preco', methods=['POST'])
def store_form_data():
    global form_data
    if request.method == 'POST':
        try:
            # Verificação dos campos do formulário
            distribuidora = request.form["distribuidora"]
            subgrupo = request.form["subgrupo"]
            modalidade = request.form["InputModal"]
            # Chamar tarifa_atual com os novos valores dos formulários
            t_atual = tarifa_atual(distribuidora, subgrupo, modalidade)
            print(t_atual)
        except Exception as e:
            return f'Erro ao calcular as tarifas: {str(e)}', 400

        try:
            InputDemandaHP = float(request.form["InputDemandaHP"])
            InputDemandaHFP = float(request.form["InputDemandaHFP"])
            InputConsumoHP = float(request.form["InputConsumoHP"])
            InputConsumoHFP = float(request.form["InputConsumoHFP"])
            ICMS = float(request.form["ICMS"])
            PASEP = float(request.form["PASEP"])
            preco_pmt = float(request.form["preco_pmt"])
        except ValueError:
            return 'Os campos devem ser números válidos.', 400

        # Se não houver erros, armazenar os dados do formulário no dicionário
        form_data = request.form.to_dict()
        return 'Dados do formulário armazenados com sucesso.'

@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    global form_data
    if request.method == "POST":
        try:
            distribuidora = form_data["distribuidora"]
            subgrupo = form_data["subgrupo"]
            modalidade = form_data["InputModal"]
            # Chamar tarifa_atual com os novos valores dos formulários
            t_atual = tarifa_atual(distribuidora, subgrupo, modalidade)
            InputDemandaHP = float(form_data["InputDemandaHP"])
            InputDemandaHFP = float(form_data["InputDemandaHFP"])
            InputConsumoHP = float(form_data["InputConsumoHP"])
            InputConsumoHFP = float(form_data["InputConsumoHFP"])
            ICMS = float(form_data["ICMS"])
            PASEP = float(form_data["PASEP"])
            preco_pmt = float(form_data["preco_pmt"])
            razao_social = form_data["conta"]
            cnpj = form_data["cnpj"]
            result = do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS, PASEP,
                                    preco_pmt, modalidade)
            total_livre, total_cativo, desconto, preco_medio_livre = result
            result_string1 = f"Total Livre: {total_livre}"
            result_string2 = f"Total Cativo: {total_cativo}"
            result_string3 = f"Desconto: {desconto}%"
            result_string4 = f"Preço Médio Livre: {preco_medio_livre}"
            buffer = BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 750, "Razão social: " + razao_social)
            c.drawString(100, 735, "CNPJ: " + cnpj)
            c.drawString(100, 720, result_string1)
            c.drawString(100, 705, result_string2)
            c.drawString(100, 690, result_string3)
            c.drawString(100, 675, result_string4)
            c.save()

            buffer.seek(0)
            return Response(buffer.read(), content_type='application/pdf')
        except Exception as e:
            return f'Erro ao gerar o PDF: {str(e)}', 400

if __name__ == "__main__":
    app.run(debug=True)

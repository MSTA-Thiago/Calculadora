from flask import Flask, render_template, request, Response
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from api.calculadora import tarifa_atual, do_calculation

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
            total_livre, total_cativo, desconto, total_desconto = result
            # Arredondando os valores para duas casas decimais
            total_livre = round(total_livre, 2)
            total_cativo = round(total_cativo, 2)
            desconto = round(desconto, 2)
            total_desconto = round(total_desconto, 2)

            result_string1 = f"Total Livre: {total_livre:.2f}"
            result_string2 = f"Total Cativo: {total_cativo:.2f}"
            result_string3 = f"Desconto: {desconto:.2f}%"
            result_string4 = f"Total do desconto: {total_desconto:.2f}"
            # Criação do buffer para armazenar o PDF
            buffer = BytesIO()

            # Criação do canvas para o PDF
            pagesize = landscape(A4)
            c = canvas.Canvas(buffer, pagesize=pagesize)

            buffer = BytesIO()


            # Criação do canvas para o PDF
            pagesize = landscape(A4)
            c = canvas.Canvas(buffer, pagesize=pagesize)

            # Título
            title_font = 'Helvetica-Bold'
            title_color = '#556B2F'
            title_text = "PROPOSTA PREÇO FIXO"
            c.setFont(title_font, 14)
            c.setFillColor(title_color)
            title_width = c.stringWidth(title_text)
            title_x = (pagesize[0] - title_width) / 2
            title_y = pagesize[1] - 50
            c.drawString(title_x, title_y, title_text)

            # Demais textos
            normal_font = 'Helvetica'
            normal_color = 'Black'
            normal_size = 12
            c.setFont(normal_font, normal_size)
            c.setFillColor(normal_color)
            c.drawString(100, title_y - 50, "Razão social: " + razao_social)
            c.drawString(100, title_y - 70, "CNPJ: " + cnpj)
            c.drawString(100, title_y - 90, result_string1)
            c.drawString(100, title_y - 110, result_string2)
            c.drawString(100, title_y - 130, result_string3)
            c.drawString(100, title_y - 150, result_string4)

            # Adicionando o gráfico de barras
            drawing = Drawing(400, 200)
            data = [total_cativo, total_livre, total_desconto]
            categories = ['Total Cativo', 'Total Livre', 'Total Desconto']
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 150
            bc.width = 300
            bc.data = [data]
            bc.strokeColor = colors.black
            bc.bars[0].fillColor = colors.blue
            bc.categoryAxis.categoryNames = categories
            bc.categoryAxis.labels.angle = 30
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max(data) * 1.1
            drawing.add(bc)
            drawing.drawOn(c, 100, 150)  # Posição ajustada para o gráfico

            # Salvar o canvas como PDF
            c.save()
            # Retorna o buffer
            buffer.seek(0)

            return Response(buffer.read(), content_type='application/pdf')
        except Exception as e:
            return f'Erro ao gerar o PDF: {str(e)}', 400

if __name__ == "__main__":
    app.run(debug=True)
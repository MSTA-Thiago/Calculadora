from io import BytesIO
from flask import Flask, render_template, request, Response
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tempfile
import os
import locale
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
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    if request.method == "POST":
        try:
            # Imputs:
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
            result = do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS,
                                    PASEP,
                                    preco_pmt, modalidade)
            total_livre, total_cativo, desconto, total_desconto = result
            # Gerar o grafico
            # Cria um array para o eixo X
            categorias = ['Total Cativo', 'Total Livre + Desconto']

            # Cria o gráfico de barras
            fig: object
            fig, ax = plt.subplots(figsize=(10, 8))

            # Adiciona as barras ao gráfico
            barra_cativo = ax.bar(categorias[0], total_cativo, color='green', label='Total Cativo')
            barra_livre = ax.bar(categorias[1], total_livre, color='orange', label='Total Livre')
            barra_desconto = ax.bar(categorias[1], total_desconto, bottom=total_livre, color='white', edgecolor='black',
                                    linestyle='--', linewidth=2, label='Total Desconto')

            # Função para adicionar os valores formatados dentro das barras
            def adicionar_valores_dentro_das_barras():
                # Adiciona o valor formatado dentro da barra de Total Cativo
                ax.text(barra_cativo[0].get_x() + barra_cativo[0].get_width() / 2, barra_cativo[0].get_height() / 2,
                        locale.currency(total_cativo, grouping=True), ha='center', va='center', color='black',
                        weight='bold')

                # Adiciona o valor formatado dentro da barra de Total Livre
                ax.text(barra_livre[0].get_x() + barra_livre[0].get_width() / 2, barra_livre[0].get_height() / 2,
                        locale.currency(total_livre, grouping=True), ha='center', va='center', color='black',
                        weight='bold')

                # Adiciona o valor formatado dentro da barra de Total Desconto
                ax.text(barra_desconto[0].get_x() + barra_desconto[0].get_width() / 2,
                        total_livre + barra_desconto[0].get_height() / 2,
                        locale.currency(total_desconto, grouping=True), ha='center', va='center', color='black',
                        weight='bold')

            # Chama a função para adicionar os valores formatados dentro das barras
            adicionar_valores_dentro_das_barras()

            # Adiciona rótulos dos eixos e título
            ax.set_xlabel('Categorias')
            ax.set_ylabel('Valor (R$)')
            ax.set_title('Comparação dos Totais')
            ax.legend()

            # Salva o gráfico em um arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                plt.savefig(tmpfile.name)
                tmpfile_path = tmpfile.name

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

            # Título
            title_font = 'Helvetica-Bold'
            title_color = '#556B2F'
            title_text = "PROPOSTA PREÇO FIXO"

            # Calcula a posição y para o título
            title_width = c.stringWidth(title_text, title_font)
            title_x = (pagesize[0] - title_width) / 2
            title_y = pagesize[1] - inch  # 1 inch (72 pixels) de espaçamento

            # Define o tamanho da fonte e a cor do título
            c.setFont(title_font, 14)
            c.setFillColor(title_color)
            c.drawString(title_x, title_y, title_text)

            # Define o estilo para os demais textos
            c.setFont('Helvetica', 12)
            c.setFillColor('Black')

            # Adiciona os rótulos como subtítulos
            c.setFont('Helvetica-Bold', 12)
            c.drawString(100, title_y - 50, "Razão social:")
            c.drawString(100, title_y - 70, "CNPJ:")
            c.drawString(100, title_y - 90, "Total Livre:")
            c.drawString(100, title_y - 110, "Total Cativo:")
            c.drawString(100, title_y - 130, "Desconto:")
            c.drawString(100, title_y - 150, "Total do desconto:")

            # Adiciona os valores correspondentes
            c.setFont('Helvetica', 12)
            c.drawString(182, title_y - 50, razao_social)
            c.drawString(140, title_y - 70, cnpj)
            c.drawString(170, title_y - 90, str(locale.currency(total_livre, grouping=True)))
            c.drawString(177, title_y - 110, str(locale.currency(total_cativo, grouping=True)))
            c.drawString(162, title_y - 130, f"{str(desconto)}%")
            c.drawString(213, title_y - 150, str(locale.currency(total_desconto, grouping=True)))

            # Insere o gráfico no PDF
            c.drawImage(tmpfile_path, 60, 40, width=400, height=332)

            c.showPage()
            c.save()
            # Retorna o buffer
            buffer.seek(0)
            os.remove(tmpfile_path)
            return Response(buffer.read(), content_type='application/pdf')
        except Exception as e:
            return f'Erro ao gerar o PDF: {str(e)}', 400


if __name__ == "__main__":
    app.run(debug=True)

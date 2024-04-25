from io import BytesIO
from flask import Flask, render_template, request, Response
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

            preco_pm = float(request.form["preco_pm"])
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
            COFINS = float(form_data["COFINS"])
            preco_pm = float(form_data["preco_pm"])
            certificadpR = float(form_data["certificadpR"])
            razao_social = form_data["conta"]
            cnpj = form_data["cnpj"]
            energia = form_data["energia"]
            result = do_calculation(t_atual, InputDemandaHP, InputDemandaHFP, InputConsumoHP, InputConsumoHFP, ICMS,
                                    PASEP, COFINS,
                                    preco_pm, certificadpR, energia, modalidade)
            total_livre, total_cativo, fatura_energia, fatura_uso, desconto, Benef_tusd, preco_medio_livre, desconto_tusd, Custo_global_ACR, Custo_global_ACL, Economia_reias, Equilibrio, total_desconto, preco_medio, Economia_anual = result
            # Variaeis
            # total_livre = round(total_livre, 2)
            # total_cativo = round(total_cativo, 2)
            # desconto = round(desconto, 2)
            # total_desconto = round(total_desconto, 2)
            # Economia_anual = round(Economia_anual, 2)
            # Custo_global_ACR = round(Custo_global_ACR, 2)
            # fatura_uso = round(fatura_uso, 2)
            # fatura_energia = round(fatura_energia, 2)

            # Gerar o grafico
            # Cria um array para o eixo X
            categorias = ['Fatura mercado cativo', 'Fatura mercado livre']

            # Cria o gráfico de barras
            fig, ax = plt.subplots(figsize=(10, 8))

            # Adiciona as barras ao gráfico
            barra_cativo = ax.bar(categorias[0], total_cativo, color='#097ade', label='Total Cativo')
            barra_livre = ax.bar(categorias[1], fatura_uso, color='orange', label='Fatura uso')
            barra_fatura_energia = ax.bar(categorias[1], fatura_energia, bottom=fatura_uso, color='green',
                                          label='Fatura Energia')
            barra_desconto = ax.bar(categorias[1], total_desconto, bottom=fatura_uso + fatura_energia, color='white',
                                    edgecolor='black',
                                    linestyle='--', linewidth=2, label='Total Desconto')

            # Função para adicionar os valores formatados dentro das barras
            def adicionar_valores_dentro_das_barras():
                # Adiciona o valor formatado dentro da barra de Total Cativo
                ax.text(barra_cativo[0].get_x() + barra_cativo[0].get_width() / 2, barra_cativo[0].get_height() / 2,
                        'R$ {:,.2f}'.format(total_cativo).replace(',', 'X').replace('.', ',').replace('X', '.'),
                        ha='center',
                        va='center', color='black', weight='bold')

                # Adiciona o valor formatado dentro da barra de Total Livre
                ax.text(barra_livre[0].get_x() + barra_livre[0].get_width() / 2, barra_livre[0].get_height() / 2,
                        'R$ {:,.2f}'.format(fatura_uso).replace(',', 'X').replace('.', ',').replace('X', '.'),
                        ha='center',
                        va='center', color='black', weight='bold')

                # Adiciona o valor formatado dentro da barra de Fatura Energia
                ax.text(barra_fatura_energia[0].get_x() + barra_fatura_energia[0].get_width() / 2,
                        fatura_uso + barra_fatura_energia[0].get_height() / 2,
                        'R$ {:,.2f}'.format(fatura_energia).replace(',', 'X').replace('.', ',').replace('X', '.'),
                        ha='center',
                        va='center', color='black', weight='bold')

                # Adiciona o valor formatado dentro da barra de Total Desconto
                ax.text(barra_desconto[0].get_x() + barra_desconto[0].get_width() / 2,
                        fatura_uso + fatura_energia + barra_desconto[0].get_height() / 2,
                        'R$ {:,.2f}'.format(total_desconto).replace(',', 'X').replace('.', ',').replace('X', '.'),
                        ha='center',
                        va='center',
                        color='black', weight='bold')

            # Chama a funcao para adicionar os valores formatados dentro das barras
            adicionar_valores_dentro_das_barras()

            # Adiciona rotulos dos eixos e titulo
            ax.set_xlabel('Categorias')
            ax.set_ylabel('Valor (R$)')
            ax.set_title('Comparação dos Totais')
            ax.legend()

            # Salva o grafico em um arquivo temporario
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                plt.savefig(tmpfile.name)
                tmpfile_path = tmpfile.name

            # Criação do buffer para armazenar o PDF
            buffer = BytesIO()

            titulo = 'PROPOSTA PREÇO FIXO'

            texto1 = f"Estudo de viabilidade cliente: {str(razao_social)}, {str(cnpj)}"

            texto2 = (
                f"Ao comprar {energia} considerando o perfil de consumo apresentado, ao preço médio de R$ "
                f"{str(format(preco_medio, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}/MWh (preço "
                f"da energia "
                f"considerando o valor do certificado de energia renovável, caso especificado), o cliente teve uma "
                f"economia mensal de {str(format(desconto, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}%, "
                f"o que representa R$ {str(format(total_desconto, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')} "
                f"de redução de custos com a energia mensal em relação ao ACR, e economia anual de "
                f"R$ {str(format(Economia_anual, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}, "
                f"conforme gráfico abaixo."
            )

            # legenda_grafico = 'Gráfico – Comparação e valor de economia entre os custos ACR e ACL, exemplo 1'
            # fonte_grafico = 'Fonte: o autor'

            texto3 = (
                f"No mês de referência da análise seu custo global com energia no ACR seria de R$ "
                f"{str(format(Custo_global_ACR, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}/MWh e no ACL "
                f"R$ {str(format(Custo_global_ACL, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}/MWh, ambos com valores com "
                f"impostos. Isso significa que a cada MWh consumido o cliente economizou "
                f"R$ {str(format(Economia_reias, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}."
            )
            texto4 = (
                f"Considerando o perfil de consumo informado, para preços de {energia} no ACL menores que o ponto de  "
                f"equilíbrio, R$ {str(format(Equilibrio, ',.2f').replace(',', 'X')).replace('.', ',').replace('X', '.')}, o "
                f"cliente garantirá um percentual de economia no ACL em relação ao ACR."
            )
            texto5 = (
                f"Referência de preço para análise de <i>swap</i> de energia: a {energia} contratada está "
                f"beneficiando o cliente em R$ "
                f"{str(format(Benef_tusd, ',.2f')).replace(',', 'X').replace('.', ',').replace('X', '.')}/MWh em relação ao "
                f"desconto na TUSD."
            )
            texto6 = (
                f"Caso haja despesas do comprador no ACL, que ele não teria no ACR, como por exemplo pagamento de gestão de "
                f"energia, custo com garantias financeiras, esses valores, com referência de custo mensal, deverão ser somados "
                f"ao custo ACL e reduzirão a economia indicada no estudo. Trata-se de um estudo de caráter estimativo."
            )

            textos = [texto2, texto3, texto4, texto5, texto6]

            # Crie um objeto PDF
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 2 * inch, id='normal')

            # Estilos de parágrafo
            styles = getSampleStyleSheet()

            # Titulo
            style_title = ParagraphStyle(name='Titulo', parent=styles['Normal'], alignment=TA_CENTER)
            style_title.fontName = 'Helvetica-Bold'
            style_title.fontSize = 14
            style_title.textColor = 'green'
            # style_title.fontWeight = 'bold'

            # Texto normal
            style_justified = ParagraphStyle(name="JustifiedStyle", parent=styles['Normal'], alignment=TA_JUSTIFY)
            style_justified.fontName = 'Times-Roman'  # Define a fonte para Times-Roman
            style_justified.fontSize = 12  # Define o tamanho da fonte para 12
            style_justified.firstLineIndent = 20
            style_justified.leading = 15

            # Texto 1
            style_paragrafo1 = ParagraphStyle(name="pasragrafo1", parent=styles['Normal'], alignment=TA_JUSTIFY)
            style_paragrafo1.fontName = 'Times-Roman'  # Define a fonte para Times-Roman
            style_paragrafo1.fontSize = 12  # Define o tamanho da fonte para 12
            style_paragrafo1.leading = 15

            # Legenda e fonte do grafico
            style_centered = ParagraphStyle(name='Centered', parent=styles['Normal'], alignment=TA_CENTER)
            style_centered.fontName = 'Times-Roman'
            style_centered.fontSize = 10

            content = []
            content = [Paragraph(titulo, style_title), Spacer(1, 0.5 * inch), Paragraph(texto1, style_paragrafo1),
                       Spacer(1, 12)]

            for texto in textos:
                if texto == texto2:
                    paragrafo = Paragraph(texto, style_justified)
                    content.append(paragrafo)
                    content.append(Image(tmpfile_path, width=312.5, height=250))  # Adiciona o grafico no pdf

                else:
                    paragrafo = Paragraph(texto, style_justified)
                    content.append(paragrafo)
                    content.append(Spacer(1, 12))

            # Construa o PDF
            doc.build(content)
            # Retorna o buffer
            buffer.seek(0)
            os.remove(tmpfile_path)
            if len(buffer.getvalue()) > 100:  # Um valor mínimo em bytes para um PDF não vazio
                return Response(buffer.read(), content_type='application/pdf')
            else:
                return 'O PDF gerado está vazio.', 400

            # return Response(buffer.read(), content_type='application/pdf',
            #                 headers={'Content-Disposition': 'attachment;filename=exemplo.pdf'})
        except Exception as e:
            return f'Erro ao gerar o PDF: {str(e)}', 400


@app.route('/contato', methods=["GET", "POST"])
def contato():
    return render_template('contato.html')


if __name__ == "__main__":
    app.run(debug=True)

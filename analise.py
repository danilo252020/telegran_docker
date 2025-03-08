import pandas as pd
import re
import nltk
import string
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import spacy
from wordcloud import WordCloud
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import argparse
import os
from pathlib import Path

# Configurações iniciais
nltk.download('stopwords')
stop_words_pt = nltk.corpus.stopwords.words('portuguese')
nlp = spacy.load("pt_core_news_sm")

class TelegramAnalyzer:
    def __init__(self, excel_path):
        self.df = pd.read_excel(excel_path)
        self._prepare_data()
        
    def _prepare_data(self):
        """Pré-processamento dos dados"""
        # Limpeza inicial
        self.df['Conteúdo Limpo'] = self.df['conteudo'].apply(self._limpar_mensagem)
        
        # Grupos de usuários
        self.grupos = {
            'Bolsonaro': ["JNA2021", "filipetrielli1", "lulajamais2", "ianmaldonado", "realpfigueiredo",
                         "allandossantos", "siteolavete", "DireitaChannel", "FlaviaFerronato", "FabianaBarroso",
                         "aazzibarreto", "isentaocast", "eduperez80", "ludmilalinsgrilo", "JulioVSchneider",
                         "conexaopoliticabr", "PHVox", "arthurweintraub", "diretoaosfatos", "opropriolavo",
                         "domesdras", "filgmartin", "vidadestra", "grupob38", "souzaslaughter"],
            
            'Lula': ["jornalistaslivres", "esquerdaonline", "progressistass", "+VPXlha9FZOcxOTgx", "voulula13",
                    "socialismos", "memesesquerdistas", "esquerdasunidascanal", "Andrejanonestelegram",
                    "lulaverso", "arsenaldolula"],
            
            'Neutros': ["avozdocerrado", "garoaclube", "bbcbrasil", "tramadora", "SputnikBrasil"]
        }

    @staticmethod
    def _limpar_mensagem(mensagem):
        """Limpeza do texto das mensagens"""
        if isinstance(mensagem, str):
            mensagem = mensagem.lower()
            mensagem = re.sub(r'\d+|http\S+|www\S+|https\S+', '', mensagem)
            mensagem = re.sub(r'\s+', ' ', mensagem).strip()
            palavras = [p for p in mensagem.split() if p not in stop_words_pt]
            return ' '.join(palavras)
        return ''

    def gerar_graficos_temporais(self, output_dir='output'):
        """Gera gráficos temporais e salva como HTML"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Gráfico geral
        fig = self._criar_grafico_mensagens_por_data()
        fig.write_html(f"{output_dir}/mensagens_por_data.html")
        
        # Gráfico por grupos
        fig_grupos = self._criar_grafico_grupos()
        fig_grupos.write_html(f"{output_dir}/mensagens_por_grupo.html")

    def _criar_grafico_mensagens_por_data(self):
        """Cria gráfico de mensagens por data"""
        mensagens_por_data = self.df.groupby(self.df['data'].dt.date).size().reset_index(name='Quantidade')
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mensagens_por_data['data'],
            y=mensagens_por_data['Quantidade'],
            mode='lines'
        ))
        fig.update_layout(
            title='Quantidade de Mensagens por Data',
            xaxis_title='Data',
            yaxis_title='Quantidade de Mensagens',
            hovermode='x unified'
        )
        return fig

    def _criar_grafico_grupos(self):
        """Cria gráfico comparativo entre grupos"""
        dfs = []
        for grupo, usuarios in self.grupos.items():
            df_grupo = self.df[self.df['username'].isin(usuarios)]
            contagem = df_grupo.groupby('data').size().reset_index(name='Quantidade')
            contagem['Grupo'] = grupo
            dfs.append(contagem)
            
        df_completo = pd.concat(dfs)
        fig = px.line(df_completo, x='data', y='Quantidade', color='Grupo',
                     title='Mensagens por Grupo ao Longo do Tempo')
        return fig

    def gerar_nuvens_palavras(self, output_dir='output'):
        """Gera e salva nuvens de palavras para cada grupo"""
        Path(output_dir).mkdir(exist_ok=True)
        
        for grupo, usuarios in self.grupos.items():
            textos = self.df[self.df['username'].isin(usuarios)]['Conteúdo Limpo'].str.cat(sep=' ')
            self._salvar_nuvem_palavras(textos, grupo, output_dir)

    @staticmethod
    def _salvar_nuvem_palavras(texto, grupo, output_dir):
        """Gera e salva imagem da nuvem de palavras"""
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Nuvem de Palavras - {grupo}')
        plt.savefig(f"{output_dir}/nuvem_palavras_{grupo}.png", bbox_inches='tight')
        plt.close()

    def gerar_relatorio_pdf(self, output_file='relatorio.pdf'):
        """Gera relatório consolidado em PDF"""
        doc = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4
        
        # Cabeçalho
        doc.setFont("Helvetica-Bold", 16)
        doc.drawString(50, height - 50, "Relatório de Análise do Telegram")
        doc.setFont("Helvetica", 12)
        doc.drawString(50, height - 80, f"Data de geração: {dt.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Adicionar gráficos
        y_position = height - 120
        for img in Path('output').glob('*.png'):
            doc.drawImage(str(img), 50, y_position - 200, width=500, height=200)
            y_position -= 250
            if y_position < 100:
                doc.showPage()
                y_position = height - 50
                
        doc.save()

def main():
    parser = argparse.ArgumentParser(description='Analisador de Dados do Telegram')
    parser.add_argument('--excel', required=True, help='Caminho do arquivo Excel de entrada')
    parser.add_argument('--output', default='output', help='Diretório de saída')
    args = parser.parse_args()

    analyzer = TelegramAnalyzer(args.excel)
    
    # Gerar saídas
    analyzer.gerar_graficos_temporais(args.output)
    analyzer.gerar_nuvens_palavras(args.output)
    analyzer.gerar_relatorio_pdf(os.path.join(args.output, 'relatorio.pdf'))

if __name__ == "__main__":
    main()
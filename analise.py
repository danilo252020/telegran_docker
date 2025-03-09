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
import tkinter as tk
from tkinter import ttk

# Configurações iniciais globais
nltk.download('stopwords')
stop_words_pt = nltk.corpus.stopwords.words('portuguese')
nlp = spacy.load("pt_core_news_sm")


class TelegramAnalyzer:
    """
    Classe para analisar e visualizar dados extraídos do Telegram.
    """
    def __init__(self, excel_path):
        """
        Carrega o DataFrame a partir do arquivo Excel e executa pré-processamento:
         - Limpeza do conteúdo (coluna 'conteudo')
         - Agrupamento do conteúdo limpo por data
         - Filtragem dos grupos de usuários
        """
        self.df = pd.read_excel(excel_path)
        
        # Aplicar a limpeza no conteúdo e criar uma coluna 'Conteúdo Limpo'
        self.df['Conteúdo Limpo'] = self.df['conteudo'].apply(self.limpar_mensagem)
        
        # Agrupar o conteúdo por data (concatenando as mensagens do mesmo dia)
        conteudo_por_data = self.df.groupby('data')['Conteúdo Limpo'].apply(' '.join).reset_index()
        conteudo_com_texto = conteudo_por_data[conteudo_por_data['Conteúdo Limpo'].str.strip() != '']
        conteudo_com_texto.loc[:, 'Dia'] = conteudo_com_texto['data'].dt.date
        self.conteudo_agrupado = conteudo_com_texto.groupby('Dia')['Conteúdo Limpo'].apply(' '.join).reset_index()
        
        # Definir os grupos de usuários
        self.bolsonaro_usernames = [
            "JNA2021", "filipetrielli1", "lulajamais2", "ianmaldonado", "realpfigueiredo",
            "allandossantos", "siteolavete", "DireitaChannel", "FlaviaFerronato", "FabianaBarroso",
            "aazzibarreto", "isentaocast", "eduperez80", "ludmilalinsgrilo", "JulioVSchneider",
            "conexaopoliticabr", "PHVox", "arthurweintraub", "diretoaosfatos", "opropriolavo",
            "domesdras", "filgmartin", "vidadestra", "grupob38", "souzaslaughter"
        ]
        self.lula_usernames = [
            "jornalistaslivres", "esquerdaonline", "progressistass", "+VPXlha9FZOcxOTgx", "voulula13",
            "socialismos", "memesesquerdistas", "esquerdasunidascanal", "Andrejanonestelegram",
            "lulaverso", "arsenaldolula"
        ]
        self.neutros_usernames = [
            "avozdocerrado", "garoaclube", "bbcbrasil", "tramadora", "SputnikBrasil"
        ]
        
        # Filtrar DataFrames por grupo
        self.df_jairbolsonarobrasil = self.df[self.df['username'] == 'jairbolsonarobrasil']
        self.df_lulanoTelegram = self.df[self.df['username'] == 'LulanoTelegram']
        self.df_bolsonaro_usernames = self.df[self.df['username'].isin(self.bolsonaro_usernames)]
        self.df_lula_usernames = self.df[self.df['username'].isin(self.lula_usernames)]
        self.df_neutros_usernames = self.df[self.df['username'].isin(self.neutros_usernames)]
        
        # Agregar o conteúdo limpo por grupo para uso na nuvem de palavras
        self.conteudo_jairbolsonarobrasil_agrupado = self.conteudo_agrupado[
            self.conteudo_agrupado['Dia'].isin(self.df_jairbolsonarobrasil['data'].dt.date)
        ]
        self.conteudo_lulanoTelegram_agrupado = self.conteudo_agrupado[
            self.conteudo_agrupado['Dia'].isin(self.df_lulanoTelegram['data'].dt.date)
        ]
        self.conteudo_bolsonaro_usernames_agrupado = self.conteudo_agrupado[
            self.conteudo_agrupado['Dia'].isin(self.df_bolsonaro_usernames['data'].dt.date)
        ]
        self.conteudo_lula_usernames_agrupado = self.conteudo_agrupado[
            self.conteudo_agrupado['Dia'].isin(self.df_lula_usernames['data'].dt.date)
        ]
        self.conteudo_neutros_usernames_agrupado = self.conteudo_agrupado[
            self.conteudo_agrupado['Dia'].isin(self.df_neutros_usernames['data'].dt.date)
        ]

    def grafico_mensagens_por_data(self):
        """Gera um gráfico interativo de quantidade de mensagens por data."""
        mensagens_por_data = self.df.groupby(self.df['data'].dt.date).size()
        mensagens_por_data_df = mensagens_por_data.reset_index(name='Quantidade de Mensagens')
        mensagens_por_data_df['data'] = mensagens_por_data_df['data'].apply(lambda x: x.strftime('%d-%m-%Y'))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mensagens_por_data_df['data'],
                                 y=mensagens_por_data_df['Quantidade de Mensagens'],
                                 mode='lines',
                                 name='Quantidade de Mensagens'))
        fig.update_layout(
            xaxis=dict(
                title='Data (Dia-Mês-Ano)',
                range=[mensagens_por_data_df['data'].iloc[0], mensagens_por_data_df['data'].iloc[29]],
                rangeslider=dict(
                    visible=True,
                    range=[mensagens_por_data_df['data'].iloc[0], mensagens_por_data_df['data'].iloc[-1]]
                ),
                tickformat='%d-%m-%Y',
            ),
            yaxis=dict(title='Quantidade de Mensagens'),
            title='Quantidade de Mensagens por Data',
            dragmode='zoom',
            hovermode='x unified'
        )
        fig.show()

    def grafico_mensagens_por_autor(self, autores_especificos):
        """
        Gera um gráfico interativo da quantidade de mensagens por autor (filtrado por uma lista)
        ao longo do tempo.
        """
        mensagens_por_autor_data_df = self.df.groupby(['data', 'username']).size().reset_index(name='Quantidade de Mensagens')
        filtro_df = mensagens_por_autor_data_df[mensagens_por_autor_data_df['username'].isin(autores_especificos)]
        fig1 = px.line(filtro_df,
                       x='data',
                       y='Quantidade de Mensagens',
                       color='username',
                       labels={"Data": "Data (Dia-Mês-Ano)", "Quantidade de Mensagens": "Quantidade de Mensagens"},
                       title='Quantidade de Mensagens por Autor e Data')
        fig1.update_layout(
            xaxis=dict(
                title='Data (Dia-Mês-Ano)',
                range=[filtro_df['data'].iloc[0], filtro_df['data'].iloc[29]],
                rangeslider=dict(
                    visible=True,
                    range=[filtro_df['data'].iloc[0], filtro_df['data'].iloc[-1]]
                ),
                tickformat='%d-%m-%Y',
            ),
            yaxis=dict(title='Quantidade de Mensagens'),
            dragmode='zoom',
            hovermode='x unified'
        )
        fig1.show()

    def criar_grafico_reacoes(self, username):
        """
        Gera um gráfico de barras mostrando a quantidade de reações (por emoji) para um usuário específico.
        """
        # Processar colunas de emojis e contagens
        self.df['emojis_list'] = self.df['emojis'].str.split(', ')
        self.df['counts_list'] = self.df['counts'].str.split(', ').apply(lambda x: list(map(int, x)))
        df_expanded = self.df.explode(['emojis_list', 'counts_list'])
        df_expanded = df_expanded.rename(columns={'emojis_list': 'emoji', 'counts_list': 'count'})
        df_user = df_expanded[df_expanded['username'] == username]
        df_grouped = df_user.groupby('emoji', as_index=False)['count'].sum()
        fig = px.bar(df_grouped,
                     x='emoji',
                     y='count',
                     labels={'emoji': 'Reação (Emoji)', 'count': 'Quantidade de Reações'},
                     title=f'Quantidade de Reações por Emoji - {username}')
        fig.show()

    def criar_grafico_reacoes_grupo(self, grupo_usernames, grupo_nome):
        """
        Cria um gráfico de barras com a quantidade de reações por emoji para um grupo de usuários.
        Retorna a figura (fig) para que o usuário possa exibi-la ou salvá-la.
        """
        df_grupo = self.df[self.df['username'].isin(grupo_usernames)].copy()
        # Processar as colunas de emojis e contagens
        df_grupo['emojis_list'] = df_grupo['emojis'].str.split(', ')
        df_grupo['counts_list'] = df_grupo['counts'].str.split(', ').apply(lambda x: list(map(int, x)))
        df_expanded = df_grupo.explode(['emojis_list', 'counts_list'])
        df_expanded = df_expanded.rename(columns={'emojis_list': 'emoji', 'counts_list': 'count'})
        df_grouped = df_expanded.groupby('emoji', as_index=False)['count'].sum()
        fig = px.bar(df_grouped,
                     x='emoji',
                     y='count',
                     labels={'emoji': 'Reação (Emoji)', 'count': 'Quantidade de Reações'},
                     title=f'Quantidade de Reações por Emoji - {grupo_nome}')
        return fig

    @staticmethod
    def limpar_mensagem(mensagem):
        """
        Limpa uma mensagem: converte para minúsculas, remove números, URLs, espaços extras e stop words.
        """
        if isinstance(mensagem, str):
            mensagem = mensagem.lower()
            mensagem = re.sub(r'\d+', '', mensagem)
            mensagem = re.sub(r'http\S+|www\S+|https\S+', '', mensagem, flags=re.MULTILINE)
            mensagem = mensagem.strip()
            mensagem = re.sub(r'\s+', ' ', mensagem)
            palavras = mensagem.split()
            mensagem = ' '.join([palavra for palavra in palavras if palavra not in stop_words_pt])
            return mensagem
        else:
            return ''

    @staticmethod
    def gerar_nuvem_palavras(texto, titulo="Nuvem de Palavras"):
        """
        Gera e exibe uma nuvem de palavras para o texto fornecido.
        """
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(titulo, fontsize=16)
        plt.show()

    def mostrar_nuvem_por_grupo(self, data_selecionada, grupo):
        """
        Exibe uma nuvem de palavras para um grupo específico em uma data selecionada.
        'grupo' deve ser uma string que indica qual grupo (ex.: 'jairbolsonarobrasil', 'lulanoTelegram', etc.)
        """
        data_formato = pd.to_datetime(data_selecionada, format='mixed').date()

        if grupo == 'jairbolsonarobrasil':
            filtro_data = self.conteudo_jairbolsonarobrasil_agrupado[
                self.conteudo_jairbolsonarobrasil_agrupado['Dia'] == data_formato
            ]['Conteúdo Limpo']
        elif grupo == 'lulanoTelegram':
            filtro_data = self.conteudo_lulanoTelegram_agrupado[
                self.conteudo_lulanoTelegram_agrupado['Dia'] == data_formato
            ]['Conteúdo Limpo']
        elif grupo == 'bolsonaro_usernames':
            filtro_data = self.conteudo_bolsonaro_usernames_agrupado[
                self.conteudo_bolsonaro_usernames_agrupado['Dia'] == data_formato
            ]['Conteúdo Limpo']
        elif grupo == 'lula_usernames':
            filtro_data = self.conteudo_lula_usernames_agrupado[
                self.conteudo_lula_usernames_agrupado['Dia'] == data_formato
            ]['Conteúdo Limpo']
        elif grupo == 'neutros_usernames':
            filtro_data = self.conteudo_neutros_usernames_agrupado[
                self.conteudo_neutros_usernames_agrupado['Dia'] == data_formato
            ]['Conteúdo Limpo']
        else:
            print(f"Grupo '{grupo}' não reconhecido.")
            return

        if not filtro_data.empty:
            texto = filtro_data.values[0]
            TelegramAnalyzer.gerar_nuvem_palavras(texto)
        else:
            print(f"Nenhum conteúdo encontrado para a data: {data_selecionada}")


# Exemplo de uso:
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analisar dados do Telegram.')
    parser.add_argument('--excel', type=str, default='Base_dados_Telegram.xlsx',
                        help='Caminho para o arquivo Excel com os dados.')
    args = parser.parse_args()

    analyzer = TelegramAnalyzer(args.excel)
    
    # Exemplo de execução dos métodos
    analyzer.grafico_mensagens_por_data()
    analyzer.grafico_mensagens_por_autor(['jairbolsonarobrasil', 'LulanoTelegram'])
    analyzer.criar_grafico_reacoes('jairbolsonarobrasil')
    analyzer.criar_grafico_reacoes('LulanoTelegram')
    
    # Chamar a função criar gráfico de reações por grupo e exibir os gráficos
    fig = analyzer.criar_grafico_reacoes_grupo(analyzer.bolsonaro_usernames, "Bolsonaro (Perfis Não Institucionais)")
    fig1 = analyzer.criar_grafico_reacoes_grupo(analyzer.lula_usernames, "Lula (Perfis Não Institucionais)")
    fig2 = analyzer.criar_grafico_reacoes_grupo(analyzer.neutros_usernames, "Neutros (Perfis Não Institucionais)")
    fig.show()
    fig1.show()
    fig2.show()

# Criando a janela principal
root = tk.Tk()
root.title("Seleção de Data e Grupo")

# Obtém as datas disponíveis (convertendo para string, se necessário)
available_dates = sorted(analyzer.conteudo_agrupado['Dia'].astype(str).unique())

# Define os grupos disponíveis
available_groups = ['jairbolsonarobrasil', 'lulanoTelegram', 'bolsonaro_usernames', 'lula_usernames', 'neutros_usernames']

# Variáveis para armazenar as seleções
selected_date = tk.StringVar()
selected_group = tk.StringVar()

# Função para chamar a nuvem de palavras
def gerar_nuvem():
    data = selected_date.get()
    grupo = selected_group.get()
    if data and grupo:
        analyzer.mostrar_nuvem_por_grupo(data, grupo)
    else:
        print("Selecione uma data e um grupo antes de continuar.")

# Criando widgets
tk.Label(root, text="Selecione a Data:").pack(pady=5)
date_menu = ttk.Combobox(root, textvariable=selected_date, values=available_dates, state="readonly")
date_menu.pack(pady=5)

tk.Label(root, text="Selecione o Grupo:").pack(pady=5)
group_menu = ttk.Combobox(root, textvariable=selected_group, values=available_groups, state="readonly")
group_menu.pack(pady=5)

btn_gerar = tk.Button(root, text="Gerar Nuvem de Palavras", command=gerar_nuvem)
btn_gerar.pack(pady=10)

# Executando a interface gráfica
root.mainloop()
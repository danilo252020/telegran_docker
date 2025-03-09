import os
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
import argparse
from pathlib import Path
import streamlit as st

# Desativa o file watcher do Streamlit (pode ajudar com erros relacionados ao torch)
os.environ["STREAMLIT_WATCH_FILES"] = "false"

# Configurações iniciais globais
nltk.download('stopwords')
stop_words_pt = nltk.corpus.stopwords.words('portuguese')
nlp = spacy.load("pt_core_news_sm")


class TelegramAnalyzer:
    """
    Classe para analisar e visualizar dados extraídos do Telegram.
    """
    def __init__(self, excel_path):
        # Carrega o DataFrame a partir do arquivo Excel e executa pré-processamento
        self.df = pd.read_excel(excel_path)
        
        # Aplicar a limpeza no conteúdo e criar uma coluna 'Conteúdo Limpo'
        self.df['Conteúdo Limpo'] = self.df['conteudo'].apply(self.limpar_mensagem)
        
        # Agrupar o conteúdo por data (concatenando as mensagens do mesmo dia)
        conteudo_por_data = self.df.groupby('data')['Conteúdo Limpo'].apply(' '.join).reset_index()
        conteudo_com_texto = conteudo_por_data[conteudo_por_data['Conteúdo Limpo'].str.strip() != '']
        # Para evitar o SettingWithCopyWarning, usamos .loc diretamente
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
        """Retorna um gráfico interativo de quantidade de mensagens por data."""
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
        return fig

    def grafico_mensagens_por_autor(self, autores_especificos):
        """Retorna um gráfico interativo da quantidade de mensagens por autor ao longo do tempo."""
        mensagens_por_autor_data_df = self.df.groupby(['data', 'username']).size().reset_index(name='Quantidade de Mensagens')
        filtro_df = mensagens_por_autor_data_df[mensagens_por_autor_data_df['username'].isin(autores_especificos)]
        fig = px.line(
            filtro_df,
            x='data',
            y='Quantidade de Mensagens',
            color='username',
            labels={"data": "Data (Dia-Mês-Ano)", "Quantidade de Mensagens": "Quantidade de Mensagens"},
            title='Quantidade de Mensagens por Autor e Data',
            color_discrete_sequence=["blue", "red"]  # Define as cores para os autores na ordem
        )
        fig.update_layout(
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
        return fig

    def criar_grafico_reacoes(self, username):
        """Retorna um gráfico de barras mostrando a quantidade de reações para um usuário específico."""
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
        return fig

    def criar_grafico_reacoes_grupo(self, grupo_usernames, grupo_nome):
        """Retorna um gráfico de barras com a quantidade de reações por emoji para um grupo de usuários."""
        df_grupo = self.df[self.df['username'].isin(grupo_usernames)].copy()
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
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(titulo, fontsize=16)
        return fig

    def mostrar_nuvem_por_grupo(self, data_selecionada, grupo):
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
            st.error(f"Grupo '{grupo}' não reconhecido.")
            return
        if not filtro_data.empty:
            texto = filtro_data.values[0]
            fig = TelegramAnalyzer.gerar_nuvem_palavras(texto)
            st.pyplot(fig)
        else:
            st.error(f"Nenhum conteúdo encontrado para a data: {data_selecionada}")


def main():
    parser = argparse.ArgumentParser(description='Analisar dados do Telegram.')
    parser.add_argument('--excel', type=str, default='Base_dados_Telegram.xlsx',
                        help='Caminho para o arquivo Excel com os dados.')
    args = parser.parse_args()
    analyzer = TelegramAnalyzer(args.excel)
    
    st.title("Análise de Dados do Telegram")
    
    st.header("Gráficos de Mensagens")
    if st.button("Gráfico de Mensagens por Data"):
        fig = analyzer.grafico_mensagens_por_data()
        st.plotly_chart(fig)
    if st.button("Gráfico de Mensagens por Autor"):
        fig = analyzer.grafico_mensagens_por_autor(['jairbolsonarobrasil', 'LulanoTelegram'])
        st.plotly_chart(fig)
    
    st.header("Gráficos de Reações")
    if st.button("Gráfico de Reações (jairbolsonarobrasil)"):
        fig = analyzer.criar_grafico_reacoes('jairbolsonarobrasil')
        st.plotly_chart(fig)
    if st.button("Gráfico de Reações (LulanoTelegram)"):
        fig = analyzer.criar_grafico_reacoes('LulanoTelegram')
        st.plotly_chart(fig)
    if st.button("Gráfico de Reações por Grupo (Bolsonaro)"):
        fig = analyzer.criar_grafico_reacoes_grupo(analyzer.bolsonaro_usernames, "Bolsonaro (Perfis Não Institucionais)")
        st.plotly_chart(fig)
    if st.button("Gráfico de Reações por Grupo (Lula)"):
        fig = analyzer.criar_grafico_reacoes_grupo(analyzer.lula_usernames, "Lula (Perfis Não Institucionais)")
        st.plotly_chart(fig)
    if st.button("Gráfico de Reações por Grupo (Neutros)"):
        fig = analyzer.criar_grafico_reacoes_grupo(analyzer.neutros_usernames, "Neutros (Perfis Não Institucionais)")
        st.plotly_chart(fig)
    
    st.header("Nuvem de Palavras")
    available_dates = sorted(analyzer.conteudo_agrupado['Dia'].astype(str).unique())
    available_groups = ['jairbolsonarobrasil', 'lulanoTelegram', 'bolsonaro_usernames', 'lula_usernames', 'neutros_usernames']
    
    data = st.selectbox("Selecione a Data:", available_dates)
    grupo = st.selectbox("Selecione o Grupo:", available_groups)
    
    if st.button("Gerar Nuvem de Palavras"):
        if data and grupo:
            analyzer.mostrar_nuvem_por_grupo(data, grupo)
        else:
            st.warning("Selecione uma data e um grupo antes de continuar.")


if __name__ == '__main__':
    main()
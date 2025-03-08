# Importações necessárias
import pandas as pd
import re
import nltk
import string 
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
from ipywidgets import interact, widgets
from IPython.display import display, clear_output
import datetime as dt
import spacy
#from bertopic import BERTopic
#from sklearn.feature_extraction.text import CountVectorizer
from groq import Groq
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
import datetime
import os
from textwrap import wrap
import time
import plotly.io as pio
import streamlit as st

nltk.download('stopwords')
stop_words_pt = stopwords.words('portuguese')

# Carregar o modelo em português
nlp = spacy.load("pt_core_news_sm")
 #Carregar o DataFrame a partir do arquivo Excel
df_final = pd.read_excel('Base_dados_Telegram.xlsx')
# 1. Gráfico interativo de quantidade de mensagens por data
def grafico_mensagens_por_data(df):
    mensagens_por_data = df.groupby(df['data'].dt.date).size()
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
    pio.renderers.default = "browser" 
    fig.show()
grafico_mensagens_por_data(df_final)
# 2. Gráfico interativo de quantidade de mensagens por autor e data
def grafico_mensagens_por_autor(df, autores_especificos):
    mensagens_por_autor_data_df = df.groupby(['data', 'username']).size().reset_index(name='Quantidade de Mensagens')
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
    pio.renderers.default = "browser" 
    fig1.show()
grafico_mensagens_por_autor(df_final, ['jairbolsonarobrasil', 'LulanoTelegram'])
# 3. Gráficos de barras para emojis por grupo
def criar_grafico_reacoes(df, username):
    df['emojis_list'] = df['emojis'].str.split(', ')
    df['counts_list'] = df['counts'].str.split(', ').apply(lambda x: list(map(int, x)))
    df_expanded = df.explode(['emojis_list', 'counts_list'])
    df_expanded = df_expanded.rename(columns={'emojis_list': 'emoji', 'counts_list': 'count'})
    
    df_user = df_expanded[df_expanded['username'] == username]
    df_grouped = df_user.groupby('emoji', as_index=False)['count'].sum()

    fig = px.bar(df_grouped,
                 x='emoji',
                 y='count',
                 labels={'emoji': 'Reação (Emoji)', 'count': 'Quantidade de Reações'},
                 title=f'Quantidade de Reações por Emoji - {username}')
    pio.renderers.default = "browser" 
    fig.show()
criar_grafico_reacoes(df_final, 'jairbolsonarobrasil')
criar_grafico_reacoes(df_final, 'LulanoTelegram')
# Filtrar os usernames de cada grupo
bolsonaro_usernames = ["JNA2021", "filipetrielli1", "lulajamais2", "ianmaldonado", "realpfigueiredo",
                       "allandossantos", "siteolavete", "DireitaChannel", "FlaviaFerronato", "FabianaBarroso",
                       "aazzibarreto", "isentaocast", "eduperez80", "ludmilalinsgrilo", "JulioVSchneider",
                       "conexaopoliticabr", "PHVox", "arthurweintraub", "diretoaosfatos", "opropriolavo",
                       "domesdras", "filgmartin", "vidadestra", "grupob38", "souzaslaughter"]

lula_usernames = ["jornalistaslivres", "esquerdaonline", "progressistass", "+VPXlha9FZOcxOTgx", "voulula13",
                  "socialismos", "memesesquerdistas", "esquerdasunidascanal", "Andrejanonestelegram",
                  "lulaverso", "arsenaldolula"]

neutros_usernames = ["avozdocerrado", "garoaclube", "bbcbrasil", "tramadora", "SputnikBrasil"]
 #Criar DataFrames filtrados por grupo
df_bolsonaro = df_final[df_final['username'].isin(bolsonaro_usernames)]

df_lula = df_final[df_final['username'].isin(lula_usernames)]
df_neutros = df_final[df_final['username'].isin(neutros_usernames)]
# Agrupar por data e contar a quantidade de mensagens
bolsonaro_por_data = df_bolsonaro.groupby('data').size().reset_index(name='Quantidade de Mensagens')
lula_por_data = df_lula.groupby('data').size().reset_index(name='Quantidade de Mensagens')
neutros_por_data = df_neutros.groupby('data').size().reset_index(name='Quantidade de Mensagens')
# Adicionar coluna para identificar o grupo
bolsonaro_por_data['Grupo'] = 'Bolsonaro'
lula_por_data['Grupo'] = 'Lula'
neutros_por_data['Grupo'] = 'Neutros'
# Concatenar os DataFrames
df_mensagens_por_data = pd.concat([bolsonaro_por_data, lula_por_data, neutros_por_data])
# Criar o gráfico de linhas
fig2 = px.line(df_mensagens_por_data,
              x='data',
              y='Quantidade de Mensagens',
              color='Grupo',
              labels={
                  "data": "Data",
                  "Quantidade de Mensagens": "Quantidade de Mensagens"
              },
              title='Quantidade de Mensagens por Data (Perfis Não Institucionais)')

# Ajustar a exibição inicial e adicionar funcionalidades de zoom e rolagem
fig2.update_layout(
    xaxis=dict(
        title='Data (Dia-Mês-Ano)',
        rangeslider=dict(
            visible=True,
            range=[df_mensagens_por_data['data'].min(), df_mensagens_por_data['data'].max()]  # Habilitar rolagem para o restante do período
        ),
        tickformat='%d-%m-%Y',  # Formato da data
    ),
    yaxis=dict(
        title='Quantidade de Mensagens'
    ),
    dragmode='zoom',  # Habilitar o modo de zoom
    hovermode='x unified'  # Exibir a informação da quantidade de mensagens ao passar o mouse
)

# Exibir o gráfico
fig2.show()
# Gráfico de Reações por Emoji para Perfis Não Institucionais

# Função para criar gráficos de barras de reações para cada grupo
def criar_grafico_reacoes_grupo(df, grupo_usernames, grupo_nome):
    df_grupo = df[df['username'].isin(grupo_usernames)]
    df_grouped = df_grupo.groupby('emoji', as_index=False)['count'].sum()

    fig = px.bar(df_grouped,
                 x='emoji',
                 y='count',
                 labels={
                     'emoji': 'Reação (Emoji)',
                     'count': 'Quantidade de Reações'
                 },
                 title=f'Quantidade de Reações por Emoji - {grupo_nome}')
    return fig
# Separar os emojis e as contagens em listas
df_final['emojis_list'] = df_final['emojis'].str.split(', ')
df_final['counts_list'] = df_final['counts'].str.split(', ').apply(lambda x: list(map(int, x)))
# Expandir as listas em várias linhas
df_expanded = df_final.explode(['emojis_list', 'counts_list'])
# Renomear as colunas expandidas
df_expanded = df_expanded.rename(columns={'emojis_list': 'emoji', 'counts_list': 'count'})
# Criar gráficos para os grupos
fig_reacoes_bolsonaro = criar_grafico_reacoes_grupo(df_expanded, bolsonaro_usernames, 'Bolsonaro (Perfis Não Institucionais)')
fig_reacoes_bolsonaro.show()
fig_reacoes_lula = criar_grafico_reacoes_grupo(df_expanded, lula_usernames, 'Lula (Perfis Não Institucionais)')
fig_reacoes_lula.show()
fig_reacoes_neutros = criar_grafico_reacoes_grupo(df_expanded, neutros_usernames, 'Neutros (Perfis Não Institucionais)')
fig_reacoes_neutros.show()
def limpar_mensagem(mensagem):
    if isinstance(mensagem, str):  # Verifica se a mensagem é uma string
        # Converter para minúsculas
        mensagem = mensagem.lower()

        # Remover números
        mensagem = re.sub(r'\d+', '', mensagem)

        # Remover URLs completamente
        mensagem = re.sub(r'http\S+|www\S+|https\S+', '', mensagem, flags=re.MULTILINE)

        # Remover espaços extras
        mensagem = mensagem.strip()
        mensagem = re.sub(r'\s+', ' ', mensagem)

        # Remover stop words
        palavras = mensagem.split()
        mensagem = ' '.join([palavra for palavra in palavras if palavra not in stop_words_pt])

        return mensagem
    else:
        return ''  # Retorna uma string vazia se não for uma string
# Aplicar a função de limpeza na coluna de conteúdo
df_final['Conteúdo Limpo'] = df_final['conteudo'].apply(limpar_mensagem)
# Agrupar o conteúdo por data e concatenar o conteúdo limpo
conteudo_por_data = df_final.groupby('data')['Conteúdo Limpo'].apply(' '.join).reset_index()
# Remover registros sem conteúdo e agrupar por dia
conteudo_com_texto = conteudo_por_data[conteudo_por_data['Conteúdo Limpo'].str.strip() != '']
conteudo_com_texto['Dia'] = conteudo_com_texto['data'].dt.date
conteudo_agrupado = conteudo_com_texto.groupby('Dia')['Conteúdo Limpo'].apply(' '.join).reset_index()
# Função para gerar nuvem de palavras
def gerar_nuvem_palavras(texto, titulo="Nuvem de Palavras"):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(titulo, fontsize=16)
    plt.show()
# Criar DataFrames para cada grupo específico
df_jairbolsonarobrasil = df_final[df_final['username'] == 'jairbolsonarobrasil']
df_lulanoTelegram = df_final[df_final['username'] == 'LulanoTelegram']
df_bolsonaro_usernames = df_final[df_final['username'].isin(bolsonaro_usernames)]
df_lula_usernames = df_final[df_final['username'].isin(lula_usernames)]
df_neutros_usernames = df_final[df_final['username'].isin(neutros_usernames)]
# Filtrar e agrupar o conteúdo limpo por data para cada grupo
conteudo_jairbolsonarobrasil_agrupado = conteudo_agrupado[conteudo_agrupado['Dia'].isin(df_jairbolsonarobrasil['data'].dt.date)]
conteudo_lulanoTelegram_agrupado = conteudo_agrupado[conteudo_agrupado['Dia'].isin(df_lulanoTelegram['data'].dt.date)]
conteudo_bolsonaro_usernames_agrupado = conteudo_agrupado[conteudo_agrupado['Dia'].isin(df_bolsonaro_usernames['data'].dt.date)]
conteudo_lula_usernames_agrupado = conteudo_agrupado[conteudo_agrupado['Dia'].isin(df_lula_usernames['data'].dt.date)]
conteudo_neutros_usernames_agrupado = conteudo_agrupado[conteudo_agrupado['Dia'].isin(df_neutros_usernames['data'].dt.date)]
# Função para gerar nuvem de palavras
def gerar_nuvem_palavras(texto):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(texto)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
# Converter a coluna 'Dia' para datetime, se necessário
if not pd.api.types.is_datetime64_any_dtype(conteudo_agrupado['Dia']):
    conteudo_agrupado['Dia'] = pd.to_datetime(conteudo_agrupado['Dia'])
# Criar um dropdown interativo com todas as datas disponíveis
datas_disponiveis = conteudo_agrupado['Dia'].dt.strftime('%d-%m-%Y').unique()
dropdown = widgets.Dropdown(
    options=datas_disponiveis,
    description='data:',
    disabled=False,
)
# Função para mostrar a nuvem de palavras para o dia selecionado em diferentes grupos
def mostrar_nuvem_por_grupo(data_selecionada, grupo):
    data_formato = pd.to_datetime(data_selecionada, format='%d-%m-%Y').date()

    if grupo == 'jairbolsonarobrasil':
        filtro_data = conteudo_jairbolsonarobrasil_agrupado[conteudo_jairbolsonarobrasil_agrupado['Dia'] == data_formato]['Conteúdo Limpo']
    elif grupo == 'lulanoTelegram':
        filtro_data = conteudo_lulanoTelegram_agrupado[conteudo_lulanoTelegram_agrupado['Dia'] == data_formato]['Conteúdo Limpo']
    elif grupo == 'bolsonaro_usernames':
        filtro_data = conteudo_bolsonaro_usernames_agrupado[conteudo_bolsonaro_usernames_agrupado['Dia'] == data_formato]['Conteúdo Limpo']
    elif grupo == 'lula_usernames':
        filtro_data = conteudo_lula_usernames_agrupado[conteudo_lula_usernames_agrupado['Dia'] == data_formato]['Conteúdo Limpo']
    elif grupo == 'neutros_usernames':
        filtro_data = conteudo_neutros_usernames_agrupado[conteudo_neutros_usernames_agrupado['Dia'] == data_formato]['Conteúdo Limpo']

    if not filtro_data.empty:
        texto = filtro_data.values[0]
        gerar_nuvem_palavras(texto)
    else:
        print(f"Nenhum conteúdo encontrado para a data: {data_selecionada}")
# Conectar a função de exibição da nuvem de palavras ao dropdown
#interact(mostrar_nuvem_por_grupo, data_selecionada=dropdown, grupo=['jairbolsonarobrasil', 'lulanoTelegram', 'bolsonaro_usernames', 'lula_usernames', 'neutros_usernames']) 

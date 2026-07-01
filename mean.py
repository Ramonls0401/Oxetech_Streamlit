import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        r"C:\Users\ResTIC16\Documents\streamlit_aula_15\dados\vendas_streamlit_loja.csv"
    )

    df.columns = df.columns.str.strip()

    df["data_venda"] = pd.to_datetime(df["data_venda"])

    # Criar a coluna de mês
    df["mes"] = df["data_venda"].dt.strftime("%m/%Y")

    return df

df = carregar_dados()

st.title("Dashboard de Vendas")
st.write("Este é um dashboard interativo de vendas, onde você pode explorar os dados de vendas da loja criado como aplicação Streamlit.")

# ----------------------------
# 3. Barra lateral com filtros
# ----------------------------

st.sidebar.header("Filtros")

cidades=sorted(df["cidade"].unique())
categorias=sorted(df["categoria"].unique())

cidade_selecionada = st.sidebar.multiselect(
    "Selecione a cidade", 
    options=cidades,
    default=cidades)
categoria_selecionada = st.sidebar.multiselect(
    "Selecione a categoria",
    options=categorias,
    default=categorias
)

# ----------------------------
# 4. Filtro de periodo
# ----------------------------

data_min=df["data_venda"].min()
data_max=df["data_venda"].max()

periodo=st.sidebar.date_input(
    "Selecione o período: ",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
    format="DD/MM/YYYY"
)

# ----------------------------
# 5. Tratamento de filtro data
# ----------------------------

if len(periodo) == 2 :
    data_inicio= pd.to_datetime(periodo[0])
    data_fim= pd.to_datetime(periodo[1])
else:
    data_inicio=data_min
    data_fim=data_max


# ----------------------------
# 6. Aplocação dos filtros no dataframe
# ----------------------------

df_filtrado=df[
    (df["cidade"].isin(cidade_selecionada)) &
    (df["categoria"].isin(categoria_selecionada)) &
    (df["data_venda"] >= data_inicio) &
    (df["data_venda"] <= data_fim)
]

# ----------------------------
# 7. Função para formatar moeda brasileira
# ----------------------------    

def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ----------------------------
# 8. calcular KPIs
# ----------------------------  

faturamento_total = df_filtrado["valor_total"].sum()
quantidade_total = df_filtrado["quantidade"].sum()
total_pedidos = len(df_filtrado)
ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Total", moeda_br(faturamento_total))
col2.metric("Quantidade Vendida", f"{quantidade_total:,}")
col3.metric("Total de Pedidos", f"{total_pedidos:,}")
col4.metric("Ticket Médio", moeda_br(ticket_medio))

# ----------------------------
# 9. Graficos de faturamento por produto
# ----------------------------  

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Faturamento por Produto")

    vendas_produto = (
        df_filtrado
        .groupby("produto")["valor_total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_produto = px.bar(
        vendas_produto,
        x="produto",
        y="valor_total",
        labels={
            "produto": "Produto", 
            "valor_total": "Faturamento"
        },
       
    )

    fig_produto.update_layout(
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=".2f",
        separators=",."
    )

    st.plotly_chart(fig_produto, width= "stretch")

with col_graf2:
    st.subheader("Faturamento por Cidade")

    vendas_cidade = (
        df_filtrado
        .groupby("cidade")["valor_total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


    fig_cidade = px.bar(
        vendas_cidade,
        x="cidade",
        y="valor_total",
        labels={
            "cidade": "Cidade", 
            "valor_total": "Faturamento"
        },
       
    )

    fig_cidade.update_layout(
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=".2f",
        separators=",."
    )

    st.plotly_chart(fig_cidade, width= "stretch")



#Grafico de evolução mensal

st.subheader("Evolução Mensal de Faturamento")

vendas_tempo=(
    df_filtrado
    .groupby("mes")["valor_total"]
    .sum()
)

vendas_tempo=vendas_tempo.reset_index()

fig_tempo=px.line(
    vendas_tempo,
    x="mes",
    y="valor_total",
    markers=True,
    labels={
        "mes": "Mês", 
        "valor_total": "Faturamento"      
    }
)


fig_tempo.update_layout(
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=".2f",
    separators=",."
)

st.plotly_chart(fig_tempo, width= "stretch")


st.subheader("Base de Dados Filtrada")
st.dataframe(df_filtrado, width="stretch")

csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Download dos dados filtrados em CSV",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv"
)
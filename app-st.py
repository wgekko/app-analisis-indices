import streamlit as st
import pandas as pd
import yfinance as yf
from io import BytesIO
from datetime import timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nasdaq100-DowJones-Portfolio", layout="wide", page_icon=":material/finance_mode:")

# Cargar CSS
with open("asset/styles.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#st.subheader("Análisis Técnico: Cruces Dorados, RSI y MACD")
st.button("Análisis Técnico (NASDAQ-DOW JONES- PORTFOLIO): Cruces Dorados, RSI y MACD" , key="pulse", use_container_width=True)

st.warning("IMPORTANTE, recuerde que las consultas a yahoo finance tienen un limite diario, una vez alcanzo ese liminte, la aplicación de un mensaje que no poder acceder a los precios")

with st.container(border=True):
    FAST, SLOW = 50, 200
    WINDOW_D = 15
    NDIAS = st.slider(":orange[Selecciona los días para análisis]", min_value=100, max_value=700, value=400, step=50)

# Listas de índices
tickers_nasdaq = [    "AAPL", "ABNB", "ADBE", "ADI", "ADP", "ADSK", "AEP", "AMAT", "AMD", "AMGN", "AMZN", "ANSS", "APP", "ARM", "ASML",
    "AVGO", "AXON", "AZN", "BIIB", "BKNG", "BKR", "CCEP", "CDNS", "CDW", "CEG", "CHTR", "CMCSA", "COST", "CPRT", "CRWD",
    "CSCO", "CSGP", "CSX", "CTAS", "CTSH", "DASH", "DDOG", "DXCM", "EA", "EXC", "FANG", "FAST", "FTNT", "GEHC", "GFS",
    "GILD", "GOOG", "GOOGL", "HON", "IDXX", "INTC", "INTU", "ISRG", "KDP", "KHC", "KLAC", "LIN", "LRCX", "LULU", "MAR",
    "MCHP", "MDLZ", "MELI", "META", "MNST", "MRVL", "MSFT", "MSTR", "MU", "NFLX", "NVDA", "NXPI", "ODFL", "ON", "ORLY",
    "PANW", "PAYX", "PCAR", "PDD", "PEP", "PLTR", "PYPL", "QCOM", "REGN", "ROP", "ROST", "SBUX", "SHOP", "SNPS", "TEAM",
    "TMUS", "TSLA", "TTD", "TTWO", "TXN", "VRSK", "VRTX", "WBD", "WDAY", "XEL"                 
    ]  
tickers_dowjones = [ "AAPL","AMGN","AMZN","AXP","BA","CAT","CRM","CSCO","CVX","DIS","GS","HD","HON","IBM","JNJ","JPM","KO",
                    "MCD","MMM","MRK","MSFT","NKE","NVDA","PG","SHW","TRV","UNH","V","VZ","WMT"                    
    ] 

#indice_seleccionado = st.selectbox(":orange[Selecciona ïndice/Portolio a analizar:]", [ "DOWJONES","NASDAQ100", "PORTFOLIO"],
#                                   index=None, placeholder="Seleccione índice/portfolio")

indice_seleccionado = st.radio(":orange[Selecciona ïndice/Portolio a analizar:]",key="visibility",
                               options=[ "Dow Jones","NASDAQ 100", "Portfolio"], horizontal=True  )


tickers = []
errores_tickers = []

if indice_seleccionado == "NASDAQ 100":
    tickers = tickers_nasdaq
elif indice_seleccionado == "Dow Jones":
    tickers = tickers_dowjones
else:
    entrada = st.text_input("Introduce símbolos separados por comas (ej: AAPL, MSFT, TSLA):", placeholder="AAPL, MSFT, TSLA")
    if entrada:
        posibles = [t.strip().upper() for t in entrada.split(",") if t.strip()]
        with st.spinner("Validando símbolos de forma eficiente..."):
            try:
                df_val = yf.download(posibles, period="1d", group_by="ticker", progress=False, threads=True)
                if isinstance(df_val.columns, pd.MultiIndex):
                    tickers = [sym for sym in posibles if sym in df_val.columns.get_level_values(0)]
                    errores_tickers = [sym for sym in posibles if sym not in df_val.columns.get_level_values(0)]
                else:
                    if df_val.empty:
                        st.error("No se pudo validar ningún símbolo. Intenta con otros." , icon=":material/warning:" )
                        st.stop()
                    else:
                        tickers = posibles
            except Exception as e:
                st.error(f"No se pudo validar los símbolos. Intenta más tarde. Error: {e}")
                st.stop()

        if errores_tickers:
            st.warning(f"Los siguientes símbolos no fueron reconocidos: {', '.join(errores_tickers)}")

        if not tickers:
            st.error("No se detectaron símbolos válidos. Corrige e intenta nuevamente.", icon=":material/warning:")
            st.stop()

# Funciones
def descargar_yahoo(ticker, ndias):
    try:
        df = yf.download(ticker, period=f"{ndias}d", interval="1d", progress=False)
        return df["Close"] if not df.empty else None
    except:
        return None

@st.cache_data(show_spinner=True)
def descargar_precios(tickers, ndias):
    precios = pd.DataFrame()
    fallidos = []
    progress_bar = st.progress(0)
    total = len(tickers)

    for i, ticker in enumerate(tickers):
        serie = descargar_yahoo(ticker, ndias)
        if serie is not None:
            serie.name = ticker
            precios = pd.concat([precios, serie], axis=1)
        else:
            fallidos.append(ticker)
        progress_bar.progress((i + 1) / total)

    progress_bar.empty()
    return precios.ffill(), fallidos

with st.spinner(":orange[Descargando precios desde Yahoo Finance...]"):
    precios, fallidos = descargar_precios(tickers, NDIAS)

if precios.empty:
    st.error("No se pudo descargar ningún precio.", icon=":material/error:")
    st.stop()

if fallidos:
    st.warning(f"No se pudieron descargar datos para: {', '.join(fallidos)}")

# Cálculo de cruces dorados
fast = precios.rolling(FAST).mean()
slow = precios.rolling(SLOW).mean()
cross = (fast.shift(1) < slow.shift(1)) & (fast >= slow)
last_cross = cross.apply(lambda c: c[c].index[-1] if c.any() else pd.NaT)
cutoff = precios.index.max() - timedelta(days=WINDOW_D - 1)
recent = last_cross >= cutoff

summary = pd.DataFrame({
    "symbol": last_cross.index,
    "Último cruce": last_cross.dt.strftime('%d-%m-%Y'),
    "Reciente": ["OK" if r else "" for r in recent]
})
summary["Fecha_orden"] = last_cross
summary = summary.sort_values("Fecha_orden", ascending=False, na_position="last").drop(columns="Fecha_orden")

st.subheader(f"Resumen de cruces dorados recientes - {indice_seleccionado}")
st.dataframe(summary, use_container_width=True)

# RSI
def calcular_rsi(series, periodo=14):
    delta = series.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    media_ganancia = ganancia.rolling(window=periodo).mean()
    media_perdida = perdida.rolling(window=periodo).mean()
    rs = media_ganancia / media_perdida
    return 100 - (100 / (1 + rs))

# MACD
def calcular_macd(series, rapida=10, lenta=30, señal=9):
    ema_rapida = series.ewm(span=rapida, adjust=False).mean()
    ema_lenta = series.ewm(span=lenta, adjust=False).mean()
    macd = ema_rapida - ema_lenta
    signal = macd.ewm(span=señal, adjust=False).mean()
    return macd, signal

# Backtest
def backtest(df, cruce_dorado, ticker_sel):
    if cruce_dorado.any():
        fecha_cruce = cruce_dorado[cruce_dorado].index[-1]
        precio_compra = df[ticker_sel].loc[fecha_cruce]
        precio_actual = df[ticker_sel].iloc[-1]
        rendimiento = (precio_actual - precio_compra) / precio_compra * 100
        return fecha_cruce, precio_compra, precio_actual, rendimiento
    return None, None, None, None

# Visualización
st.subheader("Visualización por símbolo")
ticker_sel = st.selectbox(":orange[Selecciona un símbolo:]", summary["symbol"].dropna())

if ticker_sel and ticker_sel in precios.columns:
    # Obtener la serie del símbolo seleccionado
    #serie = precios[ticker_sel]

    # Crear DataFrame con columnas adicionales
    #df = pd.DataFrame({
    #    ticker_sel: serie,
    #    "Fast MA": serie.rolling(FAST).mean(),
    #    "Slow MA": serie.rolling(SLOW).mean()
    #})
    # Verifica que la serie no sea vacía
    if isinstance(precios[ticker_sel], pd.Series):
        serie = precios[ticker_sel]
    else:
        st.error(f"No se pudo obtener datos válidos para {ticker_sel}.")
        st.stop()

    # Crear DataFrame con el índice correcto
    df = pd.DataFrame(index=serie.index)
    df[ticker_sel] = serie
    df["Fast MA"] = serie.rolling(FAST).mean()
    df["Slow MA"] = serie.rolling(SLOW).mean()

    # Visualización de precios y medias móviles
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df[ticker_sel], label="Precio Cierre")
    ax.plot(df.index, df["Fast MA"], label=f"Media {FAST}", linestyle="--")
    ax.plot(df.index, df["Slow MA"], label=f"Media {SLOW}", linestyle=":")
    ax.set_title(f"{ticker_sel} - Precio y Medias Móviles")
    ax.legend()
    st.pyplot(fig)

    # RSI
    df["RSI"] = calcular_rsi(df[ticker_sel])
    st.markdown(f"### RSI de 14 días: {df['RSI'].iloc[-1]:.2f}")
    st.line_chart(df["RSI"])

    # MACD
    df["MACD"], df["MACD_Signal"] = calcular_macd(df[ticker_sel])
    st.subheader("MACD y Señal")
    st.line_chart(df[["MACD", "MACD_Signal"]])

    # Detectar cruces MACD
    macd_cruce_alcista = (df["MACD"].shift(1) < df["MACD_Signal"].shift(1)) & (df["MACD"] >= df["MACD_Signal"])
    macd_cruce_bajista = (df["MACD"].shift(1) > df["MACD_Signal"].shift(1)) & (df["MACD"] <= df["MACD_Signal"])
    ultimo_indice_valido = df.dropna(subset=["MACD", "MACD_Signal"]).index[-1]

    if macd_cruce_alcista.loc[ultimo_indice_valido]:
        st.markdown("### - **Cruce alcista**: El MACD ha cruzado por encima de la señal.")
    elif macd_cruce_bajista.loc[ultimo_indice_valido]:
        st.markdown("### - **Cruce bajista**: El MACD ha cruzado por debajo de la señal.")
    else:
        st.markdown("### - No hay cruce reciente de MACD.")

    with st.container(border=True):
        # Backtest de cruce dorado
        cruces = (df["Fast MA"].shift(1) < df["Slow MA"].shift(1)) & (df["Fast MA"] >= df["Slow MA"])
        fecha_cruce, precio_compra, precio_actual, rendimiento = backtest(df, cruces, ticker_sel)
        if fecha_cruce:
            st.subheader(":orange[### Rendimiento desde el último cruce dorado]")
            st.subheader(f":orange[- **Fecha de cruce**: {fecha_cruce.strftime('%d-%m-%Y')}]")
            st.subheader(f":orange[- **Precio de compra**: ${precio_compra:.2f}]")
            st.subheader(f":orange[- **Precio actual**: ${precio_actual:.2f}]")
            st.subheader(f":orange[- **Rendimiento**: {rendimiento:.2f}%]")
        else:
            st.markdown(":orange[### No se encontró cruce dorado (media móvil 50/200) reciente.]")

# Exportar Excel
def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resumen")
    output.seek(0)
    return output

st.write("###")
st.write("---")
excel_data = exportar_excel(summary)
st.download_button(
    label="Descargar resumen en Excel",
    data=excel_data,
    file_name="resumen_cruces_dorados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    icon=":material/download:",
    key="download", 
    #use_container_width=True
)


# --------------- footer -----------------------------
st.write("---")
with st.container():
  #st.write("---")
  st.write("### &copy; - derechos reservados -  2025 -  Walter Gómez - FullStack Developer - Data Science - Business Intelligence")
  #st.write("##")
  left, right = st.columns(2, gap='medium', vertical_alignment="bottom")
  with left:
    #st.write('##')
    st.link_button("Mi LinkedIn", "https://www.linkedin.com/in/walter-gomez-fullstack-developer-datascience-businessintelligence-finanzas-python/",use_container_width=True)
  with right: 
     #st.write('##') 
    st.link_button("Mi Porfolio", "https://walter-portfolio-animado.netlify.app/", use_container_width=True)
      
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="💱 Conversión de Monedas", page_icon="💸", layout="centered")
st.title("💱 Conversión de Monedas y Análisis de Historial")
st.markdown("""
### Bienvenido 🌍  
Convierte entre **CLP** y las principales monedas del mundo.  
Visualiza también el historial de la tasa de cambio en diferentes periodos de tiempo.
""")

#API Key de TwelveData
API_KEY = "57065c233256483ea45ae840abb893e1"

# Lista de monedas importantes
monedas_importantes = ["USD", "EUR", "GBP", "JPY", "AUD"]

# Función para obtener el tipo de cambio
def obtener_tasa_cambio(par_divisa):
    url = "https://api.twelvedata.com/price"
    params = {
        "symbol": par_divisa,  # Par de divisas (Ejemplo: CLP/USD)
        "apikey": API_KEY
    }
    respuesta = requests.get(url, params=params)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        if "price" in datos:
            return float(datos["price"])
        else:
            return None
    else:
        return None

# Función para obtener el historial de tasas de cambio
def obtener_historial(moneda_base, moneda_destino, intervalo, cantidad):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": f"{moneda_base}/{moneda_destino}",  # Par de divisas
        "interval": intervalo,
        "apikey": API_KEY,
        "outputsize": cantidad
    }
    respuesta = requests.get(url, params=params)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        return None

# Configuración de la barra lateral
st.sidebar.title("⚙️ Configuración")
moneda_base = st.sidebar.selectbox("Selecciona la moneda base:", ["CLP"] + monedas_importantes)
moneda_destino = st.sidebar.selectbox("Selecciona la moneda destino:", monedas_importantes + ["CLP"])
monto = st.sidebar.number_input("💵 Monto a convertir:", min_value=0.0, value=10000.0, step=1000.0)

# Opciones para historial
opciones_historial = {
    "1 mes": ("1day", 30),
    "5 meses": ("1day", 150),
    "1 año": ("1month", 12),
}
opcion_intervalo = st.sidebar.selectbox("📅 Selecciona el periodo de historial:", list(opciones_historial.keys()))

# Línea divisora
st.markdown("---")

# Calcular conversión
if st.button("💸 Convertir"):
    par_divisa = f"{moneda_base}/{moneda_destino}"
    tasa_cambio = obtener_tasa_cambio(par_divisa)

    if tasa_cambio:
        monto_convertido = monto * tasa_cambio
        st.success(f"**{monto:,.2f} {moneda_base}** equivale a **{monto_convertido:,.2f} {moneda_destino}**")
    else:
        st.error(f"No se pudo obtener la tasa de cambio para el par {par_divisa}.")

# Mostrar historial de tasas de cambio
if st.button("📊 Mostrar Historial"):
    intervalo, cantidad = opciones_historial[opcion_intervalo]
    st.subheader(f"Historial de la tasa de cambio **{moneda_base}/{moneda_destino}** - {opcion_intervalo}")
    datos_historial = obtener_historial(moneda_base, moneda_destino, intervalo, cantidad)

    if datos_historial and "values" in datos_historial:
        try:
            # Convertir datos en DataFrame
            df = pd.DataFrame(datos_historial["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df = df.sort_values(by="datetime")

            if df.empty:
                st.warning("No hay datos disponibles para graficar.")
            else:
                # Graficar historial
                plt.figure(figsize=(10, 5))
                plt.plot(df["datetime"], df["close"], label=f"{moneda_base}/{moneda_destino}", color="blue")
                plt.xlabel("Fecha")
                plt.ylabel("Tasa de Cambio")
                plt.title(f"Historial de la Tasa de Cambio - {moneda_base}/{moneda_destino}")
                plt.legend()
                plt.grid()
                st.pyplot(plt)

                # Mostrar tabla de datos
                st.markdown("### 📋 Tabla de datos históricos")
                st.dataframe(df)
        except Exception as e:
            st.error(f"Error al procesar los datos del historial: {e}")
    else:
        st.warning(f"No se encontraron datos para {moneda_base}/{moneda_destino} en el intervalo seleccionado.")

# Línea divisora final
st.markdown("---")
st.info("👨‍💻 **Desarrollado por Ignacio Vera e Ignacio Catalán** con Streamlit y TwelveData API. 🚀")

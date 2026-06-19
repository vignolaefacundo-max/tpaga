import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import streamlit as st

# Configuración principal de la aplicación web
st.set_page_config(page_title="Optimizador de Producción", page_icon="📊", layout="wide")
st.title("📊 Optimizador de Producción de Placas Interactivo")
st.write("Modifica los parámetros del sistema en la barra lateral y presiona el botón para resolver el modelo.")

# ==========================================
# BARRA LATERAL: CONTROLES PARA EL USUARIO
# ==========================================
st.sidebar.header("⚙️ Parámetros del Sistema")

st.sidebar.subheader("⏳ Capacidades de Tiempo")
horas_smt = st.sidebar.slider("Horas disponibles Línea SMT", min_value=500, max_value=5000, value=2400, step=100)
horas_testing = st.sidebar.slider("Horas disponibles Estación Pruebas", min_value=500, max_value=3000, value=1200, step=100)

st.sidebar.subheader("📦 Disponibilidad de Chips")
chips_pro = st.sidebar.number_input("Stock máximo de Chips Pro", min_value=1000, max_value=10000, value=3500, step=100)

st.sidebar.subheader("📈 Compromisos y Techos de Mercado")
min_gama_media = st.sidebar.number_input("Compromiso Mínimo Gama Media", min_value=500, max_value=3000, value=1500, step=100)
max_tablets = st.sidebar.number_input("Demanda Máxima Tablets", min_value=500, max_value=3000, value=1200, step=100)
max_gama_baja = st.sidebar.number_input("Demanda Máxima Gama Baja", min_value=500, max_value=4000, value=2000, step=100)

# ==========================================
# PANTALLA PRINCIPAL: BOTÓN Y RESULTADOS
# ==========================================
st.subheader("🚀 Ejecutar el Modelo")
st.write("Haz clic en el botón de abajo para calcular la producción óptima con tus nuevos parámetros.")

# El botón de aceptar/resolver que solicitaste
if st.button("Resolver Optimización"):
    
    # 1. Coeficientes estáticos de la función objetivo (Ganancias en USD)
    c = [-45, -65, -25, -38, -15, -22, -30, -50]

    # 2. Matriz de restricciones con las variables x1 a x8
    A = [
        [0.4, 0.6, 0.3, 0.45, 0.2, 0.3, 0.5, 0.7],  # A. SMT
        [0.2, 0.4, 0.15, 0.25, 0.1, 0.15, 0.2, 0.35], # B. Testing
        [0.0, 1.0, 0.0,  1.0, 0.0, 1.0, 0.0, 1.0],  # C. Chips Pro
        [0.0, 0.0, 1.0,  1.0, 0.0, 0.0, 0.0, 0.0],  # D. Min Gama Media
        [0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 1.0, 1.0],  # E.1 Max Tablets
        [0.0, 0.0, 0.0,  0.0, 1.0, 1.0, 0.0, 0.0]   # E.2 Max Gama Baja
    ]

    # 3. Límites usando las variables que modificó el usuario
    bl = [-np.inf, -np.inf, -np.inf, min_gama_media, -np.inf, -np.inf]
    bu = [horas_smt, horas_testing, chips_pro, np.inf, max_tablets, max_gama_baja]

    # 4. Configuración interna del optimizador MILP
    constraints = LinearConstraint(A, bl, bu)
    bounds = Bounds([0] * 8, [np.inf] * 8)
    integridad_variables = [1] * 8  # Fuerza valores enteros completos

    # 5. Ejecución del cálculo matemático
    resultado = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integridad_variables
    )

    # 6. Despliegue de los resultados obtenidos
    st.markdown("---")
    st.subheader("📊 Resultados de la Simulación")
    st.info(f"**Mensaje del sistema:** {resultado.message}")
    
    if resultado.success:
        # Formato de dinero destacado
        ganancia_total = int(-resultado.fun)
        st.success(f"## 💰 Ganancia Máxima Mensual: USD {ganancia_total:,}")
        
        # Estructura visual en dos columnas para ordenar las 8 variables
        col1, col2 = st.columns(2)
        
        nombres = [
            "Celulares Gama Alta - Standard (x1)",
            "Celulares Gama Alta - Pro (x2)",
            "Celulares Gama Media - Standard (x3)",
            "Celulares Gama Media - Pro (x4)",
            "Celulares Gama Baja - Standard (x5)",
            "Celulares Gama Baja - Pro (x6)",
            "Tablets - Standard (x7)",
            "Tablets - Pro (x8)"
        ]
        
        with col1:
            st.write("### 📱 Smartphones")
            for i in range(6):
                st.metric(label=nombres[i], value=f"{int(resultado.x[i])} uds")
                
        with col2:
            st.write("### 📁 Tablets")
            for i in range(6, 8):
                st.metric(label=nombres[i], value=f"{int(resultado.x[i])} uds")
    else:
        st.error("❌ Los parámetros actuales no permiten encontrar una solución válida. Intenta flexibilizar las restricciones.")

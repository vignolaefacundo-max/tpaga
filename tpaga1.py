import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import streamlit as st

# Configuración principal de la aplicación web
st.set_page_config(page_title="Optimizador de Producción", page_icon="📊", layout="wide")
st.title("📊 Optimizador de Producción de Placas Interactivo")
st.write("Modifica los parámetros y mínimos individuales en la barra lateral y presiona el botón para resolver el modelo.")

# ==========================================
# BARRA LATERAL: CONTROLES PARA EL USUARIO
# ==========================================
st.sidebar.header("⚙️ Parámetros del Sistema")

# Sección de Capacidades y Recursos
with st.sidebar.expander("⏳ Recursos y Capacidades", expanded=True):
    horas_smt = st.slider("Horas disponibles Línea SMT", min_value=500, max_value=5000, value=2400, step=100)
    horas_testing = st.slider("Horas disponibles Estación Pruebas", min_value=500, max_value=3000, value=1200, step=100)
    chips_pro = st.number_input("Stock máximo de Chips Pro", min_value=1000, max_value=10000, value=3500, step=100)

# Sección de Límites de Mercado de Grupo
with st.sidebar.expander("📈 Techos y Compromisos de Grupo", expanded=False):
    min_gama_media = st.number_input("Compromiso Mínimo Gama Media (x3 + x4)", min_value=500, max_value=3000, value=1500, step=100)
    max_tablets = st.number_input("Demanda Máxima Tablets (x7 + x8)", min_value=500, max_value=3000, value=1200, step=100)
    max_gama_baja = st.number_input("Demanda Máxima Gama Baja (x5 + x6)", min_value=500, max_value=4000, value=2000, step=100)

# NUEVA SECCIÓN: Mínimos individuales para cada modelo
with st.sidebar.expander("🛡️ Producción Mínima por Modelo", expanded=True):
    st.write("Define el piso mínimo de fabricación para cada placa:")
    min_x1 = st.number_input("Gama Alta - Standard (x1)", min_value=0, max_value=1000, value=0, step=10)
    min_x2 = st.number_input("Gama Alta - Pro (x2)", min_value=0, max_value=1000, value=0, step=10)
    min_x3 = st.number_input("Gama Media - Standard (x3)", min_value=0, max_value=1000, value=0, step=10)
    min_x4 = st.number_input("Gama Media - Pro (x4)", min_value=0, max_value=1000, value=0, step=10)
    min_x5 = st.number_input("Gama Baja - Standard (x5)", min_value=0, max_value=1000, value=0, step=10)
    min_x6 = st.number_input("Gama Baja - Pro (x6)", min_value=0, max_value=1000, value=0, step=10)
    min_x7 = st.number_input("Tablets - Standard (x7)", min_value=0, max_value=1000, value=0, step=10)
    min_x8 = st.number_input("Tablets - Pro (x8)", min_value=0, max_value=1000, value=0, step=10)

# ==========================================
# PANTALLA PRINCIPAL: BOTÓN Y RESULTADOS
# ==========================================
st.subheader("🚀 Ejecutar el Modelo")
st.write("Haz clic en el botón de abajo para calcular la producción óptima.")

if st.button("Resolver Optimización"):
    
    # 1. Coeficientes de la función objetivo (Ganancias en USD)
    c = [-45, -65, -25, -38, -15, -22, -30, -50]

    # 2. Matriz de restricciones de grupo
    A = [
        [0.4, 0.6, 0.3, 0.45, 0.2, 0.3, 0.5, 0.7],  # A. SMT
        [0.2, 0.4, 0.15, 0.25, 0.1, 0.15, 0.2, 0.35], # B. Testing
        [0.0, 1.0, 0.0,  1.0, 0.0, 1.0, 0.0, 1.0],  # C. Chips Pro
        [0.0, 0.0, 1.0,  1.0, 0.0, 0.0, 0.0, 0.0],  # D. Min Gama Media
        [0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 1.0, 1.0],  # E.1 Max Tablets
        [0.0, 0.0, 0.0,  0.0, 1.0, 1.0, 0.0, 0.0]   # E.2 Max Gama Baja
    ]

    # 3. Límites de las restricciones de grupo
    bl = [-np.inf, -np.inf, -np.inf, min_gama_media, -np.inf, -np.inf]
    bu = [horas_smt, horas_testing, chips_pro, np.inf, max_tablets, max_gama_baja]

    # 4. CONFIGURACIÓN DE LÍMITES INDIVIDUALES (Bounds personalizados)
    # Se arma la lista con los 8 mínimos individuales ingresados por el usuario
    limite_inferior = [min_x1, min_x2, min_x3, min_x4, min_x5, min_x6, min_x7, min_x8]
    limite_superior = [np.inf] * 8
    
    constraints = LinearConstraint(A, bl, bu)
    bounds = Bounds(limite_inferior, limite_superior)
    integridad_variables = * 8  

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
        ganancia_total = int(-resultado.fun)
        st.success(f"## 💰 Ganancia Máxima Mensual: USD {ganancia_total:,}")
        
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
        st.error("❌ Los parámetros o mínimos individuales ingresados superan la capacidad física de la fábrica. Intenta reducir los mínimos obligatorios o aumentar las horas disponibles.")

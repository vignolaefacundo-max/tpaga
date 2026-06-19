import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import streamlit as st

# Configuración del título de la página web
st.set_page_config(page_title="Optimización de Producción", page_icon="📊")
st.title("📊 Optimizador de Producción de Placas")
st.write("Esta aplicación calcula la cantidad óptima de placas a fabricar para maximizar las ganancias.")

# Botón interactivo para ejecutar el cálculo
if st.button("🚀 Ejecutar Optimización"):
    
    # 1. COEFICIENTES DE LA FUNCIÓN OBJETIVO
    c = [-45, -65, -25, -38, -15, -22, -30, -50]

    # 2. MATRIZ DE RESTRICCIONES
    A = [
        [0.4, 0.6, 0.3, 0.45, 0.2, 0.3, 0.5, 0.7],  
        [0.2, 0.4, 0.15, 0.25, 0.1, 0.15, 0.2, 0.35], 
        [0.0, 1.0, 0.0,  1.0, 0.0, 1.0, 0.0, 1.0],  
        [0.0, 0.0, 1.0,  1.0, 0.0, 0.0, 0.0, 0.0],  
        [0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 1.0, 1.0],  
        [0.0, 0.0, 0.0,  0.0, 1.0, 1.0, 0.0, 0.0]   
    ]

    # 3. LÍMITES DE LAS RESTRICCIONES
    bl = [-np.inf, -np.inf, -np.inf, 1500, -np.inf, -np.inf]
    bu = [2400, 1200, 3500, np.inf, 1200, 2000]

    # 4. CONFIGURACIÓN DEL MODELO
    constraints = LinearConstraint(A, bl, bu)
    bounds = Bounds([0] * 8, [np.inf] * 8)
    integridad_variables = [1] * 8

    # 5. EJECUCIÓN DEL OPTIMIZADOR
    resultado = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integridad_variables
    )

    # 6. MOSTRAR RESULTADOS EN LA PÁGINA WEB
    st.subheader("Resultados del Sistema")
    st.info(f"Estado del optimizador: {resultado.message}")
    
    if resultado.success:
        # Mostrar la ganancia destacada en verde
        ganancia = int(-resultado.fun)
        st.success(f"### 💰 Ganancia Máxima Mensual: USD {ganancia:,}")
        
        st.subheader("📦 Cantidad Óptima a Fabricar")
        
        nombres_variables = [
            "Celulares Gama Alta - Standard",
            "Celulares Gama Alta - Pro",
            "Celulares Gama Media - Standard",
            "Celulares Gama Media - Pro",
            "Celulares Gama Baja - Standard",
            "Celulares Gama Baja - Pro",
            "Tablets - Standard",
            "Tablets - Pro"
        ]
        
        # Mostrar los resultados en una lista limpia
        for i in range(8):
            st.write(f"* **{nombres_variables[i]}:** {int(resultado.x[i])} unidades")
    else:
        st.error("No se encontró una solución óptima con las restricciones dadas.")

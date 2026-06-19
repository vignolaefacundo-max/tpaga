import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def optimizar_produccion_placas():
    """
    Optimiza la producción mensual de placas para smartphones y tablets.
    
    Variables de decisión:
    x1: Celulares Gama Alta - Standard    x2: Celulares Gama Alta - Pro
    x3: Celulares Gama Media - Standard   x4: Celulares Gama Media - Pro
    x5: Celulares Gama Baja - Standard    x6: Celulares Gama Baja - Pro
    x7: Tablets - Standard                x8: Tablets - Pro
    """
    
    # 1. COEFICIENTES DE LA FUNCIÓN OBJETIVO
    # Se ingresan con signo negativo porque la función 'milp' solo minimiza.
    # Maximizar Z = 45x1 + 65x2 + 25x3 + 38x4 + 15x5 + 22x6 + 30x7 + 50x8
    c = [-45, -65, -25, -38, -15, -22, -30, -50]

    # 2. MATRIZ DE RESTRICCIONES (Coeficientes de las variables)
    A = [
        # x1,  x2,  x3,   x4,  x5,  x6,  x7,  x8
        [0.4, 0.6, 0.3, 0.45, 0.2, 0.3, 0.5, 0.7],  # A. Capacidad Línea SMT (Horas)
        [0.2, 0.4, 0.15, 0.25, 0.1, 0.15, 0.2, 0.35], # B. Estación Pruebas y Calidad (Horas)
        [0.0, 1.0, 0.0,  1.0, 0.0, 1.0, 0.0, 1.0],  # C. Restricción de Chips Pro (Unidades)
        [0.0, 0.0, 1.0,  1.0, 0.0, 0.0, 0.0, 0.0],  # D. Compromisos Gama Media (Mínimo)
        [0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 1.0, 1.0],  # E.1 Techo Demanda Tablets (Máximo)
        [0.0, 0.0, 0.0,  0.0, 1.0, 1.0, 0.0, 0.0]   # E.2 Techo Demanda Gama Baja (Máximo)
    ]

    # 3. LÍMITES INFERIORES (bl) Y SUPERIORES (bu) DE LAS RESTRICCIONES
    bl = [-np.inf, -np.inf, -np.inf, 1500, -np.inf, -np.inf]
    bu = [2400, 1200, 3500, np.inf, 1200, 2000]

    # 4. CONFIGURACIÓN DEL MODELO
    constraints = LinearConstraint(A, bl, bu)
    
    # Restricción F: No negatividad (todas las variables deben ser mayores o iguales a 0)
    bounds = Bounds([0] * 8, [np.inf] * 8)

    # Integridad: Indicamos con un '1' que las 8 variables deben ser ENTERAS (unidades completas)
    integridad_variables = [1] * 8

    # 5. EJECUCIÓN DEL OPTIMIZADOR
    resultado = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integridad_variables
    )

    # 6. MOSTRAR RESULTADOS
    print("==================================================")
    print("        RESULTADOS DE LA OPTIMIZACIÓN             ")
    print("==================================================")
    print(f"Estado del sistema: {resultado.message}")
    
    if resultado.success:
        print(f"Ganancia Máxima Mensual (Z): USD {int(-resultado.fun):,}")
        print("\nCantidad óptima de placas a fabricar:")
        nombres_variables = [
            "x1 (Celulares Gama Alta - Standard) ",
            "x2 (Celulares Gama Alta - Pro)      ",
            "x3 (Celulares Gama Media - Standard)",
            "x4 (Celulares Gama Media - Pro)     ",
            "x5 (Celulares Gama Baja - Standard) ",
            "x6 (Celulares Gama Baja - Pro)      ",
            "x7 (Tablets - Standard)             ",
            "x8 (Tablets - Pro)                  "
        ]
        for i in range(8):
            print(f" -> {nombres_variables[i]}: {int(resultado.x[i])} unidades")
    print("==================================================")

if __name__ == "__main__":
    optimizar_produccion_placas()

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import hashlib
from datetime import datetime
from fpdf import FPDF  # REQUIERE: pip install fpdf

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
st.set_page_config(page_title="Comprobación de Lectura 2 - FSM", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main-title { color: #006B3F; font-family: 'Times New Roman', serif; font-size: 34px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .instrucciones-box { background-color: #f4f8f6; color: #000000; border-left: 5px solid #006B3F; padding: 15px; font-family: 'Times New Roman', serif; font-size: 12pt; margin-bottom: 30px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
    .q-title { color: #006B3F; font-family: 'Times New Roman', serif; font-size: 20px; font-weight: bold; margin-bottom: 10px; margin-top: 0; }
    .q-text { font-size: 15px; margin-bottom: 15px; line-height: 1.4; color: #333; }
    
    /* Configuración del Reporte y Rúbrica en Web */
    .section-header { color: #006B3F; font-family: 'Times New Roman', serif; font-size: 22px; font-weight: bold; border-bottom: 2px solid #006B3F; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    .watermark-container { position: relative; padding: 20px; background: white; border-radius: 10px; border-top: 8px solid #006B3F; z-index: 1; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .watermark { position: absolute; top: 30%; left: 15%; transform: rotate(-30deg); font-size: 60px; color: rgba(178, 34, 34, 0.08); font-weight: bold; z-index: -1; pointer-events: none; text-align: center; line-height: 1.2; white-space: nowrap; }
    .rubric-table { width: 100%; border-collapse: collapse; font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.4; margin-top: 15px; background: white; color: black; }
    .rubric-table th { background-color: #006B3F; color: white; font-weight: bold; text-align: center; padding: 8px; border: 1px solid #ddd; }
    .rubric-table td { padding: 8px; border: 1px solid #ddd; vertical-align: top; }
    .achieved-cell { background-color: #e6f4ea; border: 3px solid #006B3F !important; font-weight: bold; color: #137333; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS DE PREGUNTAS (10 REACTIVOS)
# ==========================================
preguntas = [
    {"id": "q1", "titulo": "Reactivo 1: Diagrama de Cuerpo Libre (DCL)", "texto": "Según Hibbeler, ¿cuál es el primer paso vital al crear un Diagrama de Cuerpo Libre (DCL) antes de aplicar las ecuaciones de equilibrio?", "opciones": ["Dibujar el elemento exactamente como se ve físicamente con las paredes.", "Aislar la partícula o elemento de su entorno y reemplazar los soportes por fuerzas.", "Graficar de inmediato las fuerzas cortantes.", "Dividir la estructura en secciones triangulares."], "correcta": "Aislar la partícula o elemento de su entorno y reemplazar los soportes por fuerzas."},
    {"id": "q2", "titulo": "Reactivo 2: Reacciones en Soportes", "texto": "Como regla general, si un soporte previene la traslación de un cuerpo en una dirección dada (por ejemplo, un pasador que bloquea el movimiento horizontal y vertical), ¿qué se desarrolla en el cuerpo?", "opciones": ["Una fuerza de reacción en esa dirección.", "Únicamente un momento de par.", "Una deformación plástica permanente.", "Una carga linealmente variable."], "correcta": "Una fuerza de reacción en esa dirección."},
    {"id": "q3", "titulo": "Reactivo 3: Estabilidad de Armaduras", "texto": "¿Cuál es la forma geométrica elemental que asegura la estabilidad estructural en la composición de una armadura simple?", "opciones": ["Un cuadrado de cuatro eslabones.", "Un arco de medio punto.", "Un triángulo formado por tres eslabones.", "Un rectángulo con soportes de rodillo."], "correcta": "Un triángulo formado por tres eslabones."},
    {"id": "q4", "titulo": "Reactivo 4: Método de Nudos (Limitante)", "texto": "Al utilizar el método de nudos para encontrar fuerzas internas en una armadura plana, ¿cuál es el número MÁXIMO de incógnitas que puede tener el nudo seleccionado para poder resolverse directamente?", "opciones": ["Una incógnita.", "Dos incógnitas.", "Tres incógnitas.", "Cuatro incógnitas."], "correcta": "Dos incógnitas."},
    {"id": "q5", "titulo": "Reactivo 5: Signos en el Método de Nudos", "texto": "Si al resolver el diagrama de un nudo, asumes que una fuerza desconocida sale del nudo (Tensión) y el resultado algebraico es negativo, esto significa que:", "opciones": ["El sistema no está en equilibrio estático.", "Debes usar el método de secciones forzosamente.", "La suposición fue incorrecta; la barra en realidad está en Compresión.", "La fuerza resultante es cero."], "correcta": "La suposición fue incorrecta; la barra en realidad está en Compresión."},
    {"id": "q6", "titulo": "Reactivo 6: Método de Secciones (Atajo)", "texto": "En el método de secciones, para encontrar el valor de una fuerza interna cortada de manera rápida, se recomienda hacer sumatoria de momentos ¿en qué punto específico?", "opciones": ["En el centroide exacto de la viga.", "En un apoyo de rodillo.", "En el punto donde las líneas de acción de las OTRAS fuerzas desconocidas se interceptan.", "Exclusivamente en el origen de coordenadas."], "correcta": "En el punto donde las líneas de acción de las OTRAS fuerzas desconocidas se interceptan."},
    {"id": "q7", "titulo": "Reactivo 7: Esfuerzo en Vigas", "texto": "Por definición mecánica, ¿cómo se aplican las cargas en los miembros estructurales conocidos como 'Vigas'?", "opciones": ["Axialmente a lo largo de su longitud.", "Perpendicularmente a su eje longitudinal.", "Mediante momentos de torsión pura en los extremos.", "En forma radial y centrífuga."], "correcta": "Perpendicularmente a su eje longitudinal."},
    {"id": "q8", "titulo": "Reactivo 8: Cargas Internas", "texto": "Al seccionar una viga imaginariamente para analizarla, surgen fuerzas reactivas internas. ¿Cuáles son estas dos reacciones principales que se deben graficar?", "opciones": ["Fuerza cortante (V) y Momento flexionante (M).", "Tensión (T) y Compresión (C).", "Fuerza normal (N) y Fuerza de fricción (Fr).", "Densidad de carga y Centroide."], "correcta": "Fuerza cortante (V) y Momento flexionante (M)."},
    {"id": "q9", "titulo": "Reactivo 9: Diagramas V y M", "texto": "Al graficar los diagramas de fuerza cortante y momento flexionante con respecto a 'x', si los valores calculados de las funciones son negativos, ¿dónde se deben graficar?", "opciones": ["Sobre el eje 'x'.", "En el plano 'z'.", "Se asumen como cero.", "Debajo del eje 'x'."], "correcta": "Debajo del eje 'x'."},
    {"id": "q10", "titulo": "Reactivo 10: Herramientas Tecnológicas", "texto": "¿Qué programa de software se recomienda explícitamente en el curso para generar cálculos inmediatos y diagramas de armaduras y vigas?", "opciones": ["AutoCAD 3D", "MDSolids 4.1.0", "MATLAB Simulink", "Python SciPy"], "correcta": "MDSolids 4.1.0"}
]

# ==========================================
# FUNCIONES DE FIGURAS INTERACTIVAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(aislar):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((0, 0), 4, 0.4, facecolor='#a9cce3', edgecolor='black'))
    
    if aislar == "Modelo Físico (Real)":
        # Paredes y suelo
        ax.add_patch(patches.Rectangle((-0.5, -0.5), 0.5, 1.5, facecolor='gray', hatch='//'))
        ax.add_patch(patches.Rectangle((3.5, -0.5), 1, 0.3, facecolor='gray', hatch='//'))
        ax.text(2, -1, "Múltiples elementos y soportes", ha='center', color='gray')
    else:
        # DCL (Solo fuerzas)
        ax.annotate('', xy=(0, 0), xytext=(0, -1), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
        ax.text(-0.3, -0.5, "Ay", color=TEC_GREEN, fontweight='bold')
        ax.annotate('', xy=(4, 0), xytext=(4, -1), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
        ax.text(4.2, -0.5, "By", color=TEC_GREEN, fontweight='bold')
        ax.text(2, -1, "Solo la pieza y los vectores", ha='center', color=TEC_GREEN, fontweight='bold')
        
    ax.annotate('', xy=(2, 0.4), xytext=(2, 1.5), arrowprops=dict(facecolor='red', width=3, headwidth=8))
    ax.set_xlim(-1, 5); ax.set_ylim(-1.5, 2); ax.axis('off')
    return fig

def plot_q2(soporte):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((1, 0), 2, 0.4, facecolor='lightgray', edgecolor='black'))
    
    if soporte == "Rodillo (1 restricción)":
        ax.add_patch(patches.Circle((2, -0.2), 0.2, facecolor='gray', edgecolor='black'))
        ax.annotate('', xy=(2, 0), xytext=(2, -1.2), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
        ax.text(2.2, -0.6, "Ry", color=TEC_GREEN, fontweight='bold')
    else:
        ax.add_patch(patches.Polygon([[2,0], [1.7,-0.5], [2.3,-0.5]], closed=True, facecolor='gray', edgecolor='black'))
        ax.annotate('', xy=(2, 0), xytext=(2, -1.2), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
        ax.annotate('', xy=(2, 0), xytext=(0.8, 0), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
        ax.text(2.2, -0.6, "Ry", color=TEC_GREEN, fontweight='bold')
        ax.text(1.2, 0.2, "Rx", color=TEC_GREEN, fontweight='bold')
        
    ax.set_xlim(0, 4); ax.set_ylim(-1.5, 1); ax.axis('off')
    return fig

def plot_q3(forma):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if forma == "Cuadrado (Inestable)":
        ax.add_patch(patches.Polygon([[0,0], [2,0], [2.5,2], [0.5,2]], closed=True, fill=False, edgecolor='red', linewidth=3, linestyle='--'))
        ax.plot([0,2,2,0,0], [0,0,2,2,0], color='gray', linewidth=1, alpha=0.5)
        ax.annotate('', xy=(0.5, 2), xytext=(-0.5, 2), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(1.5, -0.5, "Colapso Estructural", color='red', ha='center', fontweight='bold')
    else:
        ax.add_patch(patches.Polygon([[0,0], [2,0], [1,2]], closed=True, fill=False, edgecolor=TEC_GREEN, linewidth=3))
        ax.annotate('', xy=(1, 2), xytext=(0, 2), arrowprops=dict(facecolor='blue', width=3, headwidth=8))
        ax.text(1, -0.5, "Geometría Rígida", color=TEC_GREEN, ha='center', fontweight='bold')
        
    ax.set_xlim(-1, 3); ax.set_ylim(-1, 2.5); ax.axis('off')
    return fig

def plot_q4(num_incognitas):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([0], [0], marker='o', color='black', markersize=12)
    
    angles = [45, 135, 225, 315]
    for i in range(num_incognitas):
        rad = np.radians(angles[i])
        ax.annotate('', xy=(np.cos(rad)*1.5, np.sin(rad)*1.5), xytext=(0,0), arrowprops=dict(facecolor='blue', width=2, headwidth=8))
        
    ax.text(0, -1.8, r"Ecuaciones Disp: $\Sigma F_x=0$, $\Sigma F_y=0$", ha='center', color='gray')
    
    if num_incognitas <= 2:
        ax.text(0, 1.8, "✅ SOLUBLE", color='green', fontweight='bold', ha='center', fontsize=14)
    else:
        ax.text(0, 1.8, "❌ INSOLUBLE DIRECTAMENTE", color='red', fontweight='bold', ha='center', fontsize=14)
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.axis('off')
    return fig

def plot_q5(signo):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([-1.5, 1.5], [0, 0], color='gray', linewidth=8)
    
    if signo == "Resultado (+) : Tensión":
        ax.annotate('', xy=(2, 0), xytext=(0.5, 0), arrowprops=dict(facecolor='blue', width=4, headwidth=10))
        ax.annotate('', xy=(-2, 0), xytext=(-0.5, 0), arrowprops=dict(facecolor='blue', width=4, headwidth=10))
        ax.text(0, 0.5, "Tirando del nudo", color='blue', ha='center', fontweight='bold')
    else:
        ax.annotate('', xy=(0.5, 0), xytext=(2, 0), arrowprops=dict(facecolor='red', width=4, headwidth=10))
        ax.annotate('', xy=(-0.5, 0), xytext=(-2, 0), arrowprops=dict(facecolor='red', width=4, headwidth=10))
        ax.text(0, 0.5, "Empujando al nudo", color='red', ha='center', fontweight='bold')
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.5, 1.5); ax.axis('off')
    return fig

def plot_q6(pivote):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    # Corte de armadura
    ax.plot([0, 1.5], [0, 0], color='gray', linewidth=3)
    ax.plot([0, 1.5], [2, 2], color='gray', linewidth=3)
    ax.plot([1.5, 1.5], [0, 2], color='gray', linewidth=3)
    ax.plot([0, 1.5], [0, 2], color='gray', linewidth=3)
    
    # Fuerzas internas expuestas
    ax.annotate('', xy=(3, 2), xytext=(1.5, 2), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
    ax.annotate('', xy=(3, 0), xytext=(1.5, 0), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
    ax.annotate('', xy=(3, 2), xytext=(1.5, 0), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
    
    # Proyecciones
    ax.plot([3, 3], [0, 2], 'k--')
    ax.plot([3], [2], marker='o', color='red', markersize=8)
    
    if pivote == "En la intersección":
        ax.text(3, 2.5, "Pivote virtual", color='green', ha='center', fontweight='bold')
        ax.text(1.5, -0.8, "2 incógnitas se anulan (d=0)", color='green', ha='center')
    else:
        ax.plot([0], [0], marker='o', color='red', markersize=8)
        ax.text(0, -0.5, "Pivote pobre", color='red', ha='center', fontweight='bold')
        ax.text(1.5, -0.8, "Ecuación muy compleja", color='red', ha='center')

    ax.set_xlim(-1, 4); ax.set_ylim(-1.5, 3); ax.axis('off')
    return fig

def plot_q7(angulo):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((-2, -0.2), 4, 0.4, facecolor='lightgray', edgecolor='black'))
    
    rad = np.radians(angulo)
    x, y = 1.5 * np.cos(rad), 1.5 * np.sin(rad)
    ax.annotate('', xy=(0, 0), xytext=(x, y), arrowprops=dict(facecolor='red', width=3, headwidth=8))
    
    if angulo == 90:
        ax.text(0, -0.8, "Carga Perpendicular\n(Viga trabaja a Flexión)", color='green', ha='center', fontweight='bold')
    else:
        ax.text(0, -0.8, "Componente Axial Presente\n(Riesgo de Pandeo)", color='orange', ha='center', fontweight='bold')
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.5, 2); ax.axis('off')
    return fig

def plot_q8(vista):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    if vista == "Viga Completa":
        ax.add_patch(patches.Rectangle((0, 0), 4, 0.5, facecolor='gray'))
        ax.text(2, 0.25, "Fuerzas ocultas en el interior", color='white', ha='center', va='center')
    else:
        ax.add_patch(patches.Rectangle((0, 0), 2, 0.5, facecolor='gray'))
        ax.annotate('', xy=(2, -0.8), xytext=(2, 0.25), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(2.2, -0.4, "V", color='red', fontweight='bold', fontsize=14)
        ax.annotate('', xy=(2.6, 0.8), xytext=(2.1, 0.8), arrowprops=dict(facecolor='blue', width=3, headwidth=8, connectionstyle="arc3,rad=-0.5"))
        ax.text(2.8, 0.6, "M", color='blue', fontweight='bold', fontsize=14)
        ax.text(1, -1.2, "Sección cortada", color='black', ha='center')

    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1.5, 1.5); ax.axis('off')
    return fig

def plot_q9(valor):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([0, 4], [0, 0], color='black', linewidth=2) # Eje X
    ax.text(4.2, 0, "x", fontsize=12)
    
    if valor == "Positivo (+V / +M)":
        ax.add_patch(patches.Rectangle((1, 0), 2, 1.5, facecolor='green', alpha=0.3, edgecolor='green', linewidth=2))
        ax.text(2, 0.75, "Área Positiva", color='green', ha='center', va='center', fontweight='bold')
    else:
        ax.add_patch(patches.Rectangle((1, 0), 2, -1.5, facecolor='red', alpha=0.3, edgecolor='red', linewidth=2))
        ax.text(2, -0.75, "Área Negativa", color='red', ha='center', va='center', fontweight='bold')
        
    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-2, 2); ax.axis('off')
    return fig

def plot_q10(modulo):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((-2, -1.5), 4, 3, facecolor='#2C3E50', edgecolor='black', linewidth=2))
    ax.add_patch(patches.Rectangle((-1.8, -1.3), 3.6, 2.2, facecolor='white'))
    ax.text(0, 1.1, "MDSolids 4.1.0", color='white', ha='center', fontweight='bold', fontsize=14)
    
    if modulo == "Truss Analysis Module":
        ax.plot([-1, 0, 1, -1], [-0.5, 0.5, -0.5, -0.5], color='black', linewidth=2)
        ax.text(0, -1, "Cálculo de Armaduras", ha='center', color='blue')
    else:
        ax.add_patch(patches.Rectangle((-1.2, -0.1), 2.4, 0.2, facecolor='gray'))
        ax.annotate('', xy=(0, -0.5), xytext=(0, 0.8), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(0, -1, "Diagramas V y M", ha='center', color='red')
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2, 2); ax.axis('off')
    return fig

funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.radio("Aislar sistema:", ["Modelo Físico (Real)", "DCL Matemático"], horizontal=True, key='sim_q1'),
    lambda: st.radio("Tipo de Apoyo:", ["Rodillo (1 restricción)", "Pasador Fijo (2 restricciones)"], horizontal=True, key='sim_q2'),
    lambda: st.radio("Configuración Estructural:", ["Cuadrado (Inestable)", "Triángulo (Estable)"], horizontal=True, key='sim_q3'),
    lambda: st.slider("Número de barras desconocidas (Incógnitas):", 1, 4, 2, key='sim_q4'),
    lambda: st.radio("Signo Algebraico Obtenido:", ["Resultado (+) : Tensión", "Resultado (-) : Compresión"], horizontal=True, key='sim_q5'),
    lambda: st.radio("Elegir Pivote de Momentos:", ["En la intersección", "En otro punto al azar"], horizontal=True, key='sim_q6'),
    lambda: st.slider("Ángulo de la Carga (Grados):", 30, 90, 90, step=15, key='sim_q7'),
    lambda: st.radio("Vista de la Viga:", ["Viga Completa", "Corte Transversal"], horizontal=True, key='sim_q8'),
    lambda: st.radio("Valor calculado de la función:", ["Positivo (+V / +M)", "Negativo (-V / -M)"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Módulo del Software:", ["Truss Analysis Module", "Determinate Beam Module"], horizontal=True, key='sim_q10')
]

# ==========================================
# GENERADOR DE PDF NATIVO ENRIQUECIDO (FPDF)
# ==========================================
def generar_pdf_descarga(nombre, matricula, token, puntaje, detalles):
    pdf = FPDF()
    pdf.add_page()
    
    def clean_text(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, clean_text("Certificado de Resultados - Fundamentos de Sistemas Mecánicos"), ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 2: Temas 3, 4 y 5"), ln=True, align='C')
    pdf.ln(5)
    
    # Datos de Estudiante
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, clean_text(f"Estudiante: {nombre} | Matrícula: {matricula}"), ln=True)
    pdf.cell(0, 8, clean_text(f"Token de Autenticidad: {token}"), ln=True)
    pdf.cell(0, 8, clean_text(f"Fecha de Cierre: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), ln=True)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text(f"Calificación Final: {puntaje} / 100"), ln=True)
    pdf.ln(5)
    
    # -----------------------------------------------------
    # DIAGNÓSTICO TAXONÓMICO Y RÚBRICA
    # -----------------------------------------------------
    pdf.set_fill_color(240, 248, 246) 
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Diagnóstico Taxonómico (Marzano)"), ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    
    if puntaje >= 80:
        nivel_marzano = "Nivel 3/4: Análisis y Utilización"
        desc_marzano = "El estudiante abstrae modelos estructurales, domina el DCL y evalúa matemáticamente cargas internas."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante identifica convenciones de signos y reglas de apoyos, pero requiere reforzar el método de secciones."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante asimila definiciones básicas de estática. Requiere acompañamiento analítico."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    # Criterios actualizados para Temas 3, 4 y 5
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Diagramas de Cuerpo Libre (DCL) y Soportes:"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Aísla correctamente la partícula e identifica restricciones espaciales (rodillos vs pasadores)." if puntaje >= 80 else ("Confunde ocasionalmente la cantidad de restricciones por tipo de apoyo." if puntaje >= 60 else "No logra abstraer el modelo matemático del modelo físico.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Análisis de Armaduras (Nudos y Secciones):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Interpreta signos algebraicos de Tensión/Compresión y aplica el atajo de momentos en cortes." if puntaje >= 80 else ("Entiende el método de nudos, pero desconoce la aplicación eficiente del método de secciones." if puntaje >= 60 else "Desconoce los principios de fuerzas internas bidimensionales en armaduras.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Cargas Internas en Vigas (Cortante y Momento):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Domina la convención de signos V y M, y comprende su representación gráfica por debajo y encima del eje." if puntaje >= 80 else ("Reconoce las reacciones internas pero confunde las convenciones de ploteo espacial." if puntaje >= 60 else "No identifica la relación entre cargas externas perpendiculares y reacciones internas (V/M).")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c3_txt}"))
    pdf.ln(5)
    
    # Desglose de preguntas
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Desglose por Reactivo:"), ln=True, fill=True)
    pdf.ln(2)
    
    for det in detalles:
        estado = "CORRECTO" if det['es_correcta'] else "INCORRECTO"
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 6, clean_text(f"{det['titulo']} [{estado}]"), ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, clean_text(f"Tu respuesta: {det['elegida']}"))
        if not det['es_correcta']:
            pdf.multi_cell(0, 6, clean_text(f"Respuesta correcta: {det['correcta']}"))
        pdf.ln(3)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# MANEJO DE ESTADO
# ==========================================
if 'examen_terminado' not in st.session_state:
    st.session_state.examen_terminado = False

# ==========================================
# PANTALLA 1: ENTORNO LANDSCAPE DE EXAMEN
# ==========================================
if not st.session_state.examen_terminado:
    st.markdown('<p class="main-title">Comprobación de Lectura 2: Temas 3, 4 y 5</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para observar el comportamiento físico/matemático del concepto estructural. Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
    </div>
    """, unsafe_allow_html=True)

    col_id1, col_id2 = st.columns(2)
    nombre_alumno = col_id1.text_input("Nombre Completo:", placeholder="Ej. Ana García")
    matricula = col_id2.text_input("Matrícula Institucional:", placeholder="Ej. 2670193")
    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

    respuestas_temporales = {}

    for i, q in enumerate(preguntas):
        col_fig, col_text = st.columns([1.2, 1])
        
        with col_fig:
            param = controles[i]()
            st.pyplot(funciones_graficas[i](param), use_container_width=True)
            
        with col_text:
            st.markdown(f'<p class="q-title">{q["titulo"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="q-text">{q["texto"]}</p>', unsafe_allow_html=True)
            respuestas_temporales[q['id']] = st.radio("Respuesta:", q['opciones'], key=f'r_{q["id"]}', index=None, label_visibility="collapsed")
            
        st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)

    if st.button("Finalizar y Emitir Reporte Oficial", type="primary", use_container_width=True):
        if not nombre_alumno or not matricula:
            st.error("⚠️ Por favor, ingresa tu nombre y matrícula en la parte superior antes de enviar.")
        else:
            puntaje = 0
            detalles = []
            for q in preguntas:
                resp = respuestas_temporales[q['id']]
                es_correcta = (resp == q['correcta'])
                if es_correcta: puntaje += 10
                detalles.append({"titulo": q['titulo'], "elegida": resp if resp else "Sin responder", "correcta": q['correcta'], "es_correcta": es_correcta})
                
            token_str = f"{matricula}-{puntaje}-{datetime.now().strftime('%Y%m%d%H%M')}"
            st.session_state.nombre_alumno = nombre_alumno
            st.session_state.matricula = matricula
            st.session_state.hash = hashlib.sha256(token_str.encode()).hexdigest()[:12].upper()
            st.session_state.puntaje = puntaje
            st.session_state.detalles = detalles
            st.session_state.examen_terminado = True
            st.rerun()

# ==========================================
# PANTALLA 2: REPORTE, RÚBRICA Y TAXONOMÍA
# ==========================================
else:
    st.markdown('<p class="main-title">Reporte Institucional de Evaluación</p>', unsafe_allow_html=True)
    
    col_meta, col_tax = st.columns([1.3, 1])

    with col_meta:
        st.markdown(f"""
        <div class="watermark-container">
            <div class="watermark">{st.session_state.hash}<br>{st.session_state.matricula}</div>
            <h2 style="color:#006B3F; margin-top: 0;">Certificado de Resultados</h2>
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 2</p>
            <p style="font-size: 15px;"><b>Estudiante:</b> {st.session_state.nombre_alumno}</p>
            <p style="font-size: 15px;"><b>Matrícula:</b> {st.session_state.matricula}</p>
            <p style="font-size: 15px;"><b>Token de Autenticidad:</b> <code>{st.session_state.hash}</code></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.puntaje >= 70:
            st.success(f"### Calificación Final: {st.session_state.puntaje} / 100")
        else:
            st.error(f"### Calificación Final: {st.session_state.puntaje} / 100")

    with col_tax:
        st.markdown('<p class="section-header">Diagnóstico Taxonómico (Marzano)</p>', unsafe_allow_html=True)
        fig_pyramid, ax_p = plt.subplots(figsize=(5, 4))
        colores_piramide = ['#FF9999', '#FFCC99', '#FFFF99', '#66BB6A', '#92A8D1']
        textos_piramide = [
            '1. Recuperación\n(Recuerda Definiciones)',
            '2. Comprensión\n(Interpreta Soportes)',
            '3. Análisis\n(Evalúa Armaduras)',
            '4. Utilización\n(Grafica V y M)',
            '5. Metacognición\n(Evaluación Crítica)'
        ]
        
        nivel_alcanzado = 3 if st.session_state.puntaje >= 80 else (2 if st.session_state.puntaje >= 60 else 0)

        for i in range(5):
            y_base, y_top = i * 2, (i + 1) * 2
            ancho_base, ancho_top = 10 - y_base, 10 - y_top
            poligono = patches.Polygon([
                [5 - (ancho_base / 2), y_base], [5 + (ancho_base / 2), y_base], 
                [5 + (ancho_top / 2), y_top], [5 - (ancho_top / 2), y_top]
            ], closed=True, facecolor=colores_piramide[i], edgecolor='black', linewidth=1)
            
            if i == nivel_alcanzado:
                poligono.set_edgecolor(TEC_GREEN)
                poligono.set_linewidth(3.5)
                ax_p.annotate('← NIVEL DEL ESTUDIANTE', xy=(5 + (ancho_base / 2), y_base + 1), xytext=(5 + (ancho_base / 2) + 0.5, y_base + 1),
                              arrowprops=dict(facecolor=TEC_GREEN, shrink=0.05, width=3, headwidth=8), 
                              fontsize=10, color=TEC_GREEN, fontweight='bold', va='center')
            
            ax_p.add_patch(poligono)
            ax_p.text(5, y_base + 1, textos_piramide[i], ha='center', va='center', fontsize=9, fontweight='bold')
            
        ax_p.set_xlim(0, 14); ax_p.set_ylim(0, 10.5); ax_p.axis('off'); fig_pyramid.tight_layout()
        st.pyplot(fig_pyramid)

    st.markdown('<p class="section-header">Rúbrica de Competencias Evaluadas</p>', unsafe_allow_html=True)
    
    c_level = "achieved-cell" if st.session_state.puntaje >= 80 else ""
    a_level = "achieved-cell" if 60 <= st.session_state.puntaje < 80 else ""
    b_level = "achieved-cell" if st.session_state.puntaje < 60 else ""

    rubric_html = f"""
    <table class="rubric-table">
        <thead>
            <tr>
                <th style="width: 25%;">Criterio Evaluado</th>
                <th style="width: 25%;">Altamente Competente<br>(100 - 80 pts)</th>
                <th style="width: 25%;">Competente<br>(70 - 60 pts)</th>
                <th style="width: 25%;">Aún en Desarrollo<br>(< 60 pts)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>DCL y Soportes</b><br>(Abstracción del modelo físico)</td>
                <td class="{c_level}">✓ Aísla correctamente la partícula e identifica restricciones espaciales (rodillos vs pasadores).</td>
                <td class="{a_level}">✓ Realiza el DCL pero confunde ocasionalmente la cantidad de restricciones por tipo de apoyo.</td>
                <td class="{b_level}">✓ No logra abstraer el modelo matemático del modelo físico.</td>
            </tr>
            <tr>
                <td><b>Análisis de Armaduras</b><br>(Métodos de Nudos y Secciones)</td>
                <td class="{c_level}">✓ Interpreta signos algebraicos de Tensión/Compresión y aplica el atajo de momentos en cortes.</td>
                <td class="{a_level}">✓ Entiende el método de nudos, pero desconoce la aplicación eficiente del método de secciones.</td>
                <td class="{b_level}">✓ Desconoce los principios de fuerzas internas bidimensionales en armaduras.</td>
            </tr>
            <tr>
                <td><b>Cargas Internas en Vigas</b><br>(Cortante y Momento)</td>
                <td class="{c_level}">✓ Domina la convención de signos V y M, y comprende su representación gráfica respecto al eje x.</td>
                <td class="{a_level}">✓ Reconoce las reacciones internas pero confunde las convenciones de ploteo espacial.</td>
                <td class="{b_level}">✓ No identifica la relación entre cargas externas perpendiculares y reacciones internas.</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(rubric_html, unsafe_allow_html=True)

    st.markdown('<p class="section-header">Desglose por Reactivo</p>', unsafe_allow_html=True)
    
    for det in st.session_state.detalles:
        if det['es_correcta']:
            st.markdown(f"**{det['titulo']}** ✅")
            st.markdown(f"<span style='color:#137333;'>Tu respuesta: {det['elegida']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{det['titulo']}** ❌")
            st.markdown(f"<span style='color:#B22222;'>Tu respuesta: {det['elegida']}</span>", unsafe_allow_html=True)
            st.caption(f"Respuesta correcta: {det['correcta']}")
        st.divider()

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial y súbelo a Canvas como evidencia de tu Comprobación de Lectura 2.")

    pdf_bytes = generar_pdf_descarga(
        st.session_state.nombre_alumno, 
        st.session_state.matricula, 
        st.session_state.hash, 
        st.session_state.puntaje, 
        st.session_state.detalles
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.download_button(
            label="⬇️ Descargar Certificado Oficial en PDF",
            data=pdf_bytes,
            file_name=f"Certificado_Lectura2_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
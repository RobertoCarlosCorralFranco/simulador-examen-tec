import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import hashlib
from datetime import datetime
from fpdf import FPDF  # REQUIERE: pip install fpdf

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
st.set_page_config(page_title="Comprobación de Lectura 1 - FSM", layout="wide")

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
    {"id": "q1", "titulo": "Reactivo 1: Producto Cruz", "texto": "Para encontrar el momento mediante vectores, aplicamos el producto cruz entre el brazo de palanca y la fuerza. ¿Qué característica geométrica define al vector resultante?", "opciones": ["Escalar de magnitud de giro.", "Vector paralelo a la fuerza.", "Vector perpendicular al plano del brazo y la fuerza.", "Vector que apunta al origen."], "correcta": "Vector perpendicular al plano del brazo y la fuerza."},
    {"id": "q2", "titulo": "Reactivo 2: Regla de la Mano Derecha", "texto": "Si los dedos de la mano derecha indican un giro y el pulgar señala hacia el eje negativo de las Z (-Z), ¿qué nos indica esto sobre el momento?", "opciones": ["Tiene un valor positivo (+).", "Tiene un valor negativo (-).", "Existe equilibrio de traslación.", "La fuerza aplicada es nula."], "correcta": "Tiene un valor negativo (-)."},
    {"id": "q3", "titulo": "Reactivo 3: Momento de Par", "texto": "¿Cuál de las siguientes descripciones define correctamente a un 'momento de par'?", "opciones": ["Fuerzas de magnitudes diferentes que se cruzan.", "Una sola fuerza en el centro de gravedad.", "Dos fuerzas de la misma magnitud, paralelas y con sentidos opuestos.", "Fuerza de desplazamiento lineal continuo."], "correcta": "Dos fuerzas de la misma magnitud, paralelas y con sentidos opuestos."},
    {"id": "q4", "titulo": "Reactivo 4: Equilibrio Bidimensional", "texto": "Según la Primera Ley de Newton, para asegurar que una partícula en 2D se mantenga en reposo absoluto, ¿qué condiciones deben cumplirse?", "opciones": ["Solo la suma de fuerzas en Y igual a cero.", "Fuerza neta y momento neto iguales a cero.", "Fuerzas anuladas, sin importar el momento.", "Fuerza resultante igual al peso."], "correcta": "Fuerza neta y momento neto iguales a cero."},
    {"id": "q5", "titulo": "Reactivo 5: Sistema Equivalente (Resultante)", "texto": "Si un cuerpo rígido está sometido a múltiples fuerzas y momentos, puede ser simplificado a un punto referencial obteniendo:", "opciones": ["La anulación total de las fuerzas.", "Solo un momento de par.", "Una sola fuerza resultante y un momento de par resultante.", "Un conjunto infinito de fuerzas."], "correcta": "Una sola fuerza resultante y un momento de par resultante."},
    {"id": "q6", "titulo": "Reactivo 6: Brazo de Palanca", "texto": "Al calcular un momento escalar (M = F * r), ¿qué representa exactamente la variable 'r' (brazo de palanca)?", "opciones": ["La longitud total del cuerpo rígido.", "La distancia perpendicular desde el punto de referencia a la línea de acción de la fuerza.", "La distancia paralela a la fuerza.", "La magnitud del vector fuerza."], "correcta": "La distancia perpendicular desde el punto de referencia a la línea de acción de la fuerza."},
    {"id": "q7", "titulo": "Reactivo 7: Equilibrio Tridimensional", "texto": "Al aplicar el procedimiento de equilibrio para sistemas tridimensionales (3D), ¿cuántas ecuaciones de equilibrio escalar se generan en total?", "opciones": ["2 ecuaciones.", "3 ecuaciones.", "4 ecuaciones.", "6 ecuaciones."], "correcta": "6 ecuaciones."},
    {"id": "q8", "titulo": "Reactivo 8: Primera Ley de Newton", "texto": "Si la fuerza resultante que actúa sobre una partícula es cero y originalmente estaba en reposo, ¿qué sucederá con la partícula?", "opciones": ["Se acelerará gradualmente.", "Permanecerá en reposo.", "Se moverá en círculos.", "Colapsará por compresión."], "correcta": "Permanecerá en reposo."},
    {"id": "q9", "titulo": "Reactivo 9: Independencia del Momento de un Par", "texto": "Si calculamos la suma de los momentos generados por un 'par de fuerzas' respecto a distintos puntos de referencia, el momento de par resultante:", "opciones": ["Depende completamente del punto elegido.", "Es equivalente y da el mismo valor sin importar el punto.", "Se anula si el punto está fuera del cuerpo.", "Aumenta proporcionalmente con la distancia."], "correcta": "Es equivalente y da el mismo valor sin importar el punto."},
    {"id": "q10", "titulo": "Reactivo 10: Análisis Vectorial Cartesiano", "texto": "Para resolver problemas complejos de fuerzas en el espacio tridimensional, es conveniente expresar cada fuerza y brazo de palanca como:", "opciones": ["Vectores con componentes i, j, k.", "Escalares absolutos sin signo.", "Polígonos de fuerzas 2D.", "Sistemas de poleas ideales."], "correcta": "Vectores con componentes i, j, k."}
]

# ==========================================
# FUNCIONES DE FIGURAS ALINEADAS Y CENTRADAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(angulo):
    fig = plt.figure(figsize=(5, 3.5))
    ax = fig.add_subplot(111, projection='3d')
    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
    rad = np.radians(angulo)
    fx, fy = np.cos(rad), np.sin(rad)
    ax.quiver(0,0,0, 1,0,0, color='blue', linewidth=2)
    ax.quiver(0,0,0, fx,fy,0, color='red', linewidth=2)
    ax.quiver(0,0,0, 0,0,fy, color='green', linewidth=4)
    ax.text(1.1,0,0, 'r', color='blue', fontsize=12)
    ax.text(fx*1.1, fy*1.1, 0, 'F', color='red', fontsize=12)
    ax.text(0,0,fy*1.1, 'M', color='green', fontweight='bold', fontsize=12)
    ax.set_xlim([-1, 1]); ax.set_ylim([-1, 1]); ax.set_zlim([-1, 1])
    ax.view_init(elev=20., azim=45) 
    ax.axis('off')
    fig.tight_layout()
    return fig

def plot_q2(giro):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    if giro == "Giro Horario":
        ax.annotate('', xy=(0, -1.2), xytext=(0, 0), arrowprops=dict(facecolor='red', width=4, headwidth=10))
        ax.text(0, -1.5, 'Pulgar en -Z (Negativo)', color='red', ha='center', fontweight='bold', fontsize=12)
    else:
        ax.annotate('', xy=(0, 1.2), xytext=(0, 0), arrowprops=dict(facecolor='green', width=4, headwidth=10))
        ax.text(0, 1.5, 'Pulgar en +Z (Positivo)', color='green', ha='center', fontweight='bold', fontsize=12)
    arc = patches.Arc((0,0), 2, 1, angle=0, theta1=180 if giro=="Giro Horario" else 0, theta2=360 if giro=="Giro Horario" else 180, color='orange', linewidth=3)
    ax.add_patch(arc)
    ax.text(0, 0, 'Dedos', color='orange', ha='center', fontsize=12)
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.axis('off')
    return fig

def plot_q3(distancia):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    d = distancia / 2
    ax.plot([0, 0], [-d, d], color='gray', linewidth=3, linestyle='--')
    ax.annotate('', xy=(1, d), xytext=(0, d), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
    ax.annotate('', xy=(-1, -d), xytext=(0, -d), arrowprops=dict(facecolor=TEC_GREEN, width=3, headwidth=8))
    ax.text(1.2, d, 'F', color=TEC_GREEN, fontweight='bold', fontsize=14)
    ax.text(-1.2, -d, '-F', color=TEC_GREEN, fontweight='bold', fontsize=14)
    ax.text(0, 0, f"M = F * {distancia}m", color='blue', ha='center', fontweight='bold')
    ax.set_xlim(-2, 2); ax.set_ylim(-2.5, 2.5); ax.axis('off')
    return fig

def plot_q4(estado):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((-0.8, -0.8), 1.6, 1.6, facecolor='lightgray', edgecolor='black', linewidth=2))
    if estado == "Fuerzas=0 y Momentos=0":
        ax.text(0, 0, "REPOSO\nABSOLUTO", color='green', ha='center', va='center', fontweight='bold', fontsize=14)
    elif estado == "Solo Fuerzas=0":
        ax.text(0, 0, "GIRANDO", color='red', ha='center', va='center', fontweight='bold', fontsize=14)
        ax.add_patch(patches.Arc((0,0), 2.2, 2.2, angle=0, theta1=0, theta2=180, color='red', linewidth=3))
    elif estado == "Solo Momentos=0":
        ax.text(0, 0, "TRASLADANDO", color='red', ha='center', va='center', fontweight='bold', fontsize=14)
        ax.annotate('', xy=(2, 0), xytext=(0.9, 0), arrowprops=dict(facecolor='red', width=4, headwidth=10))
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-1.5, 1.5); ax.axis('off')
    return fig

def plot_q5(simplificar):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Circle((0,0), 1, color='lightblue', alpha=0.4))
    if not simplificar:
        ax.annotate('', xy=(0.5, 1.2), xytext=(0, 0.5), arrowprops=dict(facecolor='gray', width=1, headwidth=5))
        ax.annotate('', xy=(-1.2, -0.5), xytext=(-0.5, 0), arrowprops=dict(facecolor='gray', width=1, headwidth=5))
        ax.text(0, -1.5, "Múltiples Fuerzas y Momentos", ha='center', fontsize=11)
    else:
        ax.annotate('', xy=(1.5, 1.5), xytext=(0, 0), arrowprops=dict(facecolor='blue', width=3, headwidth=8))
        ax.add_patch(patches.Arc((0,0), 1, 1, angle=0, theta1=45, theta2=315, color='purple', linewidth=3))
        ax.text(1.5, 1.6, 'R', color='blue', fontweight='bold', fontsize=12)
        ax.text(0, -1.5, "Resultante 1 Fuerza + 1 Momento", ha='center', fontsize=11, color='green')
    ax.set_xlim(-2, 2); ax.set_ylim(-1.8, 1.8); ax.axis('off')
    return fig

def plot_q6(posicion):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([0], [0], marker='^', color='green', markersize=15)
    ax.plot([-2, 2], [posicion, posicion], color='red', linewidth=2, linestyle=':') 
    ax.annotate('', xy=(1, posicion), xytext=(-1, posicion), arrowprops=dict(facecolor='red', width=2, headwidth=6))
    ax.plot([0, 0], [0, posicion], color='blue', linewidth=3)
    ax.text(0.1, posicion/2, f'r={posicion}', color='blue', fontweight='bold')
    ax.text(-1, posicion+0.3, 'Línea de acción', color='red')
    ax.set_xlim(-2, 2); ax.set_ylim(-0.5, 3.5); ax.axis('off')
    return fig

def plot_q7(dim):
    fig = plt.figure(figsize=(5, 3.5))
    if dim == "2D":
        ax = fig.add_subplot(111); fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        ax.plot([-1,1],[0,0], 'k-', [0,0],[-1,1], 'k-')
        ax.text(0.5, 0.5, r'$\Sigma F_x=0$   $\Sigma F_y=0$', fontsize=12, color='blue')
        ax.text(0.5, -0.5, r'$\Sigma M_z=0$', fontsize=12, color='red')
        ax.text(-0.5, 0.8, '3 Ecuaciones', fontsize=14, fontweight='bold', color='green')
        ax.axis('off'); fig.tight_layout()
    else:
        ax = fig.add_subplot(111, projection='3d')
        fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        ax.plot([-1,1],[0,0],[0,0], 'k-'); ax.plot([0,0],[-1,1],[0,0], 'k-'); ax.plot([0,0],[0,0],[-1,1], 'k-')
        ax.text(0.5,0,0.5, r'$\Sigma F_x, y, z = 0$', fontsize=12, color='blue')
        ax.text(0.5,0,-0.5, r'$\Sigma M_x, y, z = 0$', fontsize=12, color='red')
        ax.set_title('6 Ecuaciones (3D)', fontsize=14, color='green', fontweight='bold')
        ax.axis('off'); fig.tight_layout()
    return fig

def plot_q8(fuerza):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((-0.5, -0.5), 1, 1, facecolor='#FFCC99', edgecolor='black'))
    if fuerza == 0:
        ax.text(0, 0, "V=0\n(Reposo)", ha='center', va='center', fontweight='bold')
        ax.text(0, -1.2, r'$\Sigma F = 0$', color='green', ha='center', fontsize=14)
    else:
        ax.annotate('', xy=(1.5, 0), xytext=(0.5, 0), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(0, 0, "ACELERANDO", ha='center', va='center', fontweight='bold', color='red')
        ax.text(0, -1.2, r'$\Sigma F \neq 0$', color='red', ha='center', fontsize=14)
    ax.set_xlim(-2, 2); ax.set_ylim(-1.5, 1.5); ax.axis('off')
    return fig

def plot_q9(punto):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([-1, 1], [1, -1], color='gray', linewidth=3)
    ax.annotate('', xy=(-1, 1.5), xytext=(-1, 0.5), arrowprops=dict(facecolor='green', width=2, headwidth=6))
    ax.annotate('', xy=(1, -1.5), xytext=(1, -0.5), arrowprops=dict(facecolor='green', width=2, headwidth=6))
    if punto == "Punto A (Centro)":
        ax.plot([0], [0], marker='o', color='red', markersize=10)
        ax.text(0, 0.3, "M = 100 Nm", color='red', fontweight='bold', ha='center')
    else:
        ax.plot([-1.5], [1.5], marker='o', color='blue', markersize=10)
        ax.text(-1.5, 1.8, "M = 100 Nm", color='blue', fontweight='bold', ha='center')
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2, 2.5); ax.axis('off')
    return fig

def plot_q10(formato):
    fig = plt.figure(figsize=(5, 3.5))
    if formato == "Escalar":
        ax = fig.add_subplot(111); fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        ax.annotate('', xy=(1,1), xytext=(0,0), arrowprops=dict(facecolor='black', width=2, headwidth=6))
        ax.text(0.5, 0.7, "F = 50 N", fontsize=14, fontweight='bold')
        ax.axis('off'); fig.tight_layout()
    else:
        ax = fig.add_subplot(111, projection='3d')
        fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
        ax.quiver(0,0,0, 1,1,1, color='purple', linewidth=3)
        ax.text(1.1,1.1,1.1, r'$\vec{F} = 30\hat{i} + 20\hat{j} + 40\hat{k}$', color='purple', fontweight='bold', fontsize=12)
        ax.set_xlim([0, 1.5]); ax.set_ylim([0, 1.5]); ax.set_zlim([0, 1.5])
        ax.axis('off'); fig.tight_layout()
    return fig

funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.slider("Gira la fuerza F (Grados):", 0, 180, 45, key='sim_q1'),
    lambda: st.radio("Simulador de Rotación:", ["Giro Antihorario", "Giro Horario"], horizontal=True, key='sim_q2'),
    lambda: st.slider("Aumenta la distancia (m):", 1, 4, 1, key='sim_q3'),
    lambda: st.radio("Prueba los estados:", ["Solo Fuerzas=0", "Solo Momentos=0", "Fuerzas=0 y Momentos=0"], key='sim_q4'),
    lambda: st.checkbox("⚙️ Calcular Resultante", key='sim_q5'),
    lambda: st.slider("Mueve la línea de acción (r):", 1.0, 3.0, 1.0, step=0.5, key='sim_q6'),
    lambda: st.radio("Dimensión Espacial:", ["2D", "3D"], horizontal=True, key='sim_q7'),
    lambda: st.slider("Fuerza Neta Aplicada (N):", 0, 100, 0, step=50, key='sim_q8'),
    lambda: st.radio("Cambiar Punto de Referencia:", ["Punto A (Centro)", "Punto B (Borde)"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Formato de Análisis:", ["Escalar", "Vectorial Cartesiano"], horizontal=True, key='sim_q10')
]

# ==========================================
# GENERADOR DE PDF NATIVO ENRIQUECIDO (FPDF)
# ==========================================
def generar_pdf_descarga(nombre, matricula, token, puntaje, detalles):
    pdf = FPDF()
    pdf.add_page()
    
    # Manejo de codificación para símbolos latinos en FPDF
    def clean_text(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    # Encabezado General
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, clean_text("Certificado de Resultados - Fundamentos de Sistemas Mecánicos"), ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 1: Temas 1 y 2"), ln=True, align='C')
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
    # DIAGNÓSTICO TAXONÓMICO Y RÚBRICA INTEGRADOS AL PDF
    # -----------------------------------------------------
    pdf.set_fill_color(240, 248, 246) # Verde institucional ultra claro
    
    # Taxonomía
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Diagnóstico Taxonómico (Marzano)"), ln=True, fill=True)
    pdf.set_font("Arial", size=10)
    
    if puntaje >= 80:
        nivel_marzano = "Nivel 3: Análisis"
        desc_marzano = "El estudiante abstrae conceptos, evalúa el equilibrio tridimensional y toma decisiones analíticas."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante interpreta vectores y comprende los fundamentos teóricos del equilibrio."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante se encuentra en fase de asimilación de conceptos básicos. Requiere reforzamiento."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    # Rúbrica de Evaluación Dinámica
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    # Criterio 1
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Interpretación Vectorial (Producto Cruz y Brazo de Palanca):"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Comprende la perpendicularidad del vector resultante y establece correctamente el signo." if puntaje >= 80 else ("Identifica el vector resultante pero comete errores al aplicar la regla del signo." if puntaje >= 60 else "Desconoce la naturaleza tridimensional del producto cruz.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    # Criterio 2
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Momento y Resultante (Momento Par y Simplificación):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Identifica el efecto de un momento par y abstrae la simplificación a sistemas equivalentes." if puntaje >= 80 else ("Identifica el momento de par adecuadamente, pero omite la independencia del punto referencial." if puntaje >= 60 else "No distingue un momento de par de un sistema de fuerzas de traslación.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    # Criterio 3
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Equilibrio Bidimensional y Tridimensional (1ra Ley de Newton):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Establece que fuerzas y momentos netos deben ser cero simultáneamente; conoce ecuaciones 3D." if puntaje >= 80 else ("Maneja la sumatoria de fuerzas pero presenta lagunas respecto al equilibrio rotacional." if puntaje >= 60 else "Incapacidad para interpretar el equilibrio rígido de un sistema.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c3_txt}"))
    pdf.ln(5)
    
    # -----------------------------------------------------
    # DESGLOSE DE PREGUNTAS
    # -----------------------------------------------------
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
    st.markdown('<p class="main-title">Comprobación de Lectura 1: Temas 1 y 2</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para observar el comportamiento físico del concepto. Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
    </div>
    """, unsafe_allow_html=True)

    col_id1, col_id2 = st.columns(2)
    nombre_alumno = col_id1.text_input("Nombre Completo:", placeholder="Ej. Juan Pérez")
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
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 1</p>
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
            '2. Comprensión\n(Interpreta Vectores)',
            '3. Análisis\n(Evalúa Equilibrio)',
            '4. Utilización\n(Toma Decisiones)',
            '5. Metacognición\n(Evaluación Crítica)'
        ]
        
        nivel_alcanzado = 2 if st.session_state.puntaje >= 80 else (1 if st.session_state.puntaje >= 60 else 0)

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
                <td><b>Interpretación Vectorial</b><br>(Producto Cruz, Brazo de Palanca y Regla del Pulgar)</td>
                <td class="{c_level}">✓ Comprende la perpendicularidad del vector resultante y establece correctamente el signo del momento usando la regla espacial de la mano derecha.</td>
                <td class="{a_level}">✓ Identifica el vector resultante pero comete errores ocasionales al aplicar la regla del signo o definir la distancia perpendicular.</td>
                <td class="{b_level}">✓ Desconoce la naturaleza tridimensional del producto cruz y los vectores.</td>
            </tr>
            <tr>
                <td><b>Momento y Resultante</b><br>(Momento Par y Simplificación de Sistemas)</td>
                <td class="{c_level}">✓ Identifica de inmediato el efecto de un momento par y logra abstraer la simplificación a sistemas equivalentes en un punto.</td>
                <td class="{a_level}">✓ Identifica el momento de par adecuadamente, pero omite la independencia del punto de referencia.</td>
                <td class="{b_level}">✓ No puede distinguir un momento de par de un sistema de fuerzas de traslación.</td>
            </tr>
            <tr>
                <td><b>Equilibrio Bidimensional y Tridimensional</b><br>(Primera Ley de Newton)</td>
                <td class="{c_level}">✓ Establece con exactitud que las fuerzas y los momentos netos deben ser cero simultáneamente y conoce las ecuaciones aplicables en 3D.</td>
                <td class="{a_level}">✓ Maneja la sumatoria de fuerzas pero presenta lagunas teóricas respecto al equilibrio rotacional.</td>
                <td class="{b_level}">✓ Incapacidad para interpretar el equilibrio rígido de un sistema mecánico.</td>
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

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial (que incluye el diagnóstico pedagógico) y súbelo a Canvas como evidencia.")

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
            file_name=f"Certificado_Lectura1_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
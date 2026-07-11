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
st.set_page_config(page_title="Comprobación de Lectura 4 - FSM", layout="wide")

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
    {"id": "q1", "titulo": "Reactivo 1: Aceleración en rotación", "texto": "Cuando un cuerpo gira alrededor de un punto O, el centro de masa G experimenta dos componentes de aceleración que forman 90° entre sí. ¿Cuáles son estas componentes?", "opciones": ["Aceleración elástica y plástica.", "Aceleración normal y tangencial.", "Aceleración de traslación y de inercia.", "Aceleración estática y dinámica."], "correcta": "Aceleración normal y tangencial."},
    {"id": "q2", "titulo": "Reactivo 2: Momentos respecto al centro de masa", "texto": "Si se calcula la sumatoria de momentos puramente con respecto al centro de masa G de un cuerpo rígido en rotación, ¿a qué es equivalente dicho momento?", "opciones": ["A la suma de las fuerzas en el eje X e Y.", "Al peso del cuerpo por la gravedad.", "Al momento de inercia (IG) por la aceleración angular (α).", "A cero, ya que en el centro de gravedad no hay momento."], "correcta": "Al momento de inercia (IG) por la aceleración angular (α)."},
    {"id": "q3", "titulo": "Reactivo 3: Momento respecto a un punto de apoyo O", "texto": "Al tomar momentos respecto a un eje de rotación O que NO es el centro de gravedad, ¿qué componente de la aceleración del centro de masa G es la única que genera momento cinético respecto a O?", "opciones": ["La aceleración normal ($a_n$).", "La aceleración tangencial ($a_t$).", "La aceleración angular ($a_c$).", "La aceleración de gravedad ($g$)."], "correcta": "La aceleración tangencial ($a_t$)."},
    {"id": "q4", "titulo": "Reactivo 4: Definición de Momento de Inercia", "texto": "Físicamente, ¿qué representa el 'momento de inercia de masa' ($I$) para un cuerpo rígido?", "opciones": ["La resistencia del cuerpo a trasladarse en línea recta.", "La tendencia del material a deformarse plásticamente.", "La fuerza necesaria para detener completamente su avance longitudinal.", "La resistencia que experimenta el cuerpo a cambiar su velocidad o aceleración angular."], "correcta": "La resistencia que experimenta el cuerpo a cambiar su velocidad o aceleración angular."},
    {"id": "q5", "titulo": "Reactivo 5: Teorema de Ejes Paralelos", "texto": "Si conoces el momento de inercia respecto al centro de masa ($I_G$), ¿qué teorema usas para calcular el momento de inercia respecto a un eje Z distinto y desplazado?", "opciones": ["Teorema de los ejes paralelos ($I = I_G + md^2$).", "Teorema de Pitágoras.", "Ley de Senos de Inercia.", "Principio del Movimiento del Centro de Masa."], "correcta": "Teorema de los ejes paralelos ($I = I_G + md^2$)."},
    {"id": "q6", "titulo": "Reactivo 6: Radio de giro", "texto": "Es un concepto usado en los manuales de ingeniería que expresa cómo se distribuye la masa de un cuerpo alrededor del eje en el que se encuentra su centroide ($k = \\sqrt{I/m}$).", "opciones": ["Diferencial de volumen.", "Radio de inercia rotacional.", "Módulo elástico radial.", "Radio de giro."], "correcta": "Radio de giro."},
    {"id": "q7", "titulo": "Reactivo 7: Traslación y sumatoria de fuerzas", "texto": "En un movimiento de traslación pura, las fuerzas magnéticas, de gravedad, resortes, etc., se denominan fuerzas externas. ¿A qué es igual la sumatoria de todas estas fuerzas externas?", "opciones": ["Al momento flexionante interno del cuerpo.", "A la masa del cuerpo multiplicada por la aceleración de su centro de masa ($m \\cdot a_G$).", "Al momento de inercia por la aceleración angular ($I_G \\cdot \\alpha$).", "A cero, ya que el sistema debe estar en equilibrio estático."], "correcta": "A la masa del cuerpo multiplicada por la aceleración de su centro de masa ($m \\cdot a_G$)."},
    {"id": "q8", "titulo": "Reactivo 8: Ecuación General de Momentos", "texto": "Durante el movimiento general plano de un cuerpo rígido, si realizamos una sumatoria de momentos con respecto a un punto arbitrario P ($\\Sigma M_P$), esta sumatoria debe ser igual a:", "opciones": ["La masa del cuerpo multiplicada por la gravedad.", "La suma de los momentos cinéticos con respecto al punto P ($\\Sigma (M_k)_P$).", "El vector de aceleración normal.", "Cero, asumiendo un cuerpo simétrico."], "correcta": "La suma de los momentos cinéticos con respecto al punto P ($\\Sigma (M_k)_P$)."},
    {"id": "q9", "titulo": "Reactivo 9: DCL vs. Diagrama Cinético", "texto": "¿Cuál es la principal diferencia entre un Diagrama de Cuerpo Libre (DCL) y un Diagrama Cinético?", "opciones": ["El DCL muestra las aceleraciones; el Diagrama Cinético muestra las dimensiones.", "No hay diferencia, son el mismo diagrama.", "El DCL se usa en 3D y el Cinético en 2D.", "El DCL muestra las 'causas' (fuerzas externas y reacciones), mientras que el Diagrama Cinético muestra los 'efectos' inerciales ($ma_x, ma_y, I_G\\alpha$)."], "correcta": "El DCL muestra las 'causas' (fuerzas externas y reacciones), mientras que el Diagrama Cinético muestra los 'efectos' inerciales ($ma_x, ma_y, I_G\\alpha$)."},
    {"id": "q10", "titulo": "Reactivo 10: Metodología Cinética", "texto": "Según las lecturas, ¿cuál es el procedimiento lógico y ordenado para resolver un problema de cinética plana de cuerpos rígidos?", "opciones": ["1) Diagrama Cinético, 2) Ecuaciones de Movimiento, 3) DCL.", "1) Hacer un DCL, 2) Hacer el Diagrama Cinético, 3) Aplicar las fórmulas.", "1) Aplicar fórmulas de inmediato, 2) Dibujar DCL como comprobación.", "1) Calcular inercias, 2) Resolver fuerzas, 3) Omitir diagramas."], "correcta": "1) Hacer un DCL, 2) Hacer el Diagrama Cinético, 3) Aplicar las fórmulas."}
]

# ==========================================
# FUNCIONES DE FIGURAS INTERACTIVAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(componente):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot(0, 0, marker='o', color='black', markersize=8)
    ax.text(-0.3, -0.3, "O", fontweight='bold')
    
    rad = np.radians(45)
    gx, gy = 2*np.cos(rad), 2*np.sin(rad)
    
    ax.plot([0, gx], [0, gy], color='gray', lw=4)
    ax.add_patch(patches.Circle((gx, gy), 0.3, facecolor='lightblue', edgecolor='black'))
    ax.text(gx+0.1, gy+0.3, "G", fontweight='bold')
    
    if componente == "Aceleración Normal ($a_n$)":
        ax.annotate('', xy=(gx - 1*np.cos(rad), gy - 1*np.sin(rad)), xytext=(gx, gy), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(gx - 0.8*np.cos(rad) - 0.2, gy - 0.8*np.sin(rad) + 0.2, r"$a_n = \omega^2 r_G$", color='red', fontweight='bold')
    else:
        ax.annotate('', xy=(gx - 1*np.sin(rad), gy + 1*np.cos(rad)), xytext=(gx, gy), arrowprops=dict(facecolor='blue', width=3, headwidth=8))
        ax.text(gx - 1.2*np.sin(rad), gy + 1.2*np.cos(rad), r"$a_t = \alpha r_G$", color='blue', fontweight='bold')
        
    ax.set_xlim(-1, 3); ax.set_ylim(-1, 3); ax.axis('off')
    return fig

def plot_q2(fuerza):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Circle((0, 0), 1.5, facecolor='#E8DAEF', edgecolor='black'))
    ax.plot(0, 0, marker='x', color='black', markersize=8)
    ax.text(0.1, 0.1, "G", fontweight='bold')
    
    if fuerza == "Efecto (Momento de Inercia)":
        ax.annotate('', xy=(-0.8, 1), xytext=(-0.5, 1.2), arrowprops=dict(facecolor='blue', width=2, headwidth=6, connectionstyle="arc3,rad=-0.3"))
        ax.text(-1, 1.4, r"$I_G \cdot \alpha$", color='blue', fontweight='bold', fontsize=14)
        ax.text(0, -2, "Resistencia Rotacional Pura", ha='center')
    else:
        ax.annotate('', xy=(1.5, 0), xytext=(1.5, 1), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(1.7, 0.5, "Fuerza F", color='red')
        ax.annotate('', xy=(-0.8, 1), xytext=(-0.5, 1.2), arrowprops=dict(facecolor='green', width=1, headwidth=4, connectionstyle="arc3,rad=-0.3"))
        ax.text(-1, 1.4, r"$\Sigma M_G$", color='green', fontweight='bold', fontsize=14)
        ax.text(0, -2, "Causa Externa", ha='center')
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.axis('off')
    return fig

def plot_q3(momento):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot(0, 0, marker='^', color='black', markersize=10)
    ax.text(-0.5, 0, "O", fontweight='bold')
    ax.plot([0, 2], [0, 0], color='gray', lw=5)
    ax.add_patch(patches.Circle((2, 0), 0.4, facecolor='lightblue', edgecolor='black'))
    ax.text(2, 0.5, "G", fontweight='bold')
    
    ax.annotate('', xy=(1.2, 0), xytext=(2, 0), arrowprops=dict(facecolor='red', width=2, headwidth=6))
    ax.text(1, -0.3, "$ma_n$", color='red')
    
    ax.annotate('', xy=(2, 1), xytext=(2, 0), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
    ax.text(2.2, 0.5, "$ma_t$", color='blue')
    
    if momento == "Genera Momento en O":
        ax.plot([0, 2], [0, 0], color='blue', lw=2, linestyle='--')
        ax.text(1, 0.2, "Brazo de palanca (r)", color='blue')
        ax.text(1, 1.5, r"$(ma_t \cdot r)$ SÍ genera momento", color='blue', fontweight='bold', ha='center')
    else:
        ax.plot([-1, 3], [0, 0], color='red', lw=1, linestyle='--')
        ax.text(1, 1.5, r"$ma_n$ cruza por O. Brazo = 0", color='red', fontweight='bold', ha='center')
        
    ax.set_xlim(-1, 4); ax.set_ylim(-1, 2); ax.axis('off')
    return fig

def plot_q4(inercia):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if inercia == "Alta Inercia (Masa alejada)":
        ax.add_patch(patches.Circle((0, 0), 1.5, facecolor='none', edgecolor='black', lw=4))
        ax.add_patch(patches.Circle((0, 0), 0.2, facecolor='gray', edgecolor='black'))
        ax.plot([0, 1.5], [0, 0], 'k--')
        ax.text(0.7, 0.1, "r grande")
        ax.text(0, -2, r"$I = \int r^2 dm$ (Alta Resistencia)", ha='center', color='red', fontweight='bold')
    else:
        ax.add_patch(patches.Circle((0, 0), 0.8, facecolor='gray', edgecolor='black'))
        ax.plot([0, 0.8], [0, 0], 'k--')
        ax.text(0.3, 0.1, "r peq.")
        ax.text(0, -2, "Baja Resistencia a Girar", ha='center', color='green', fontweight='bold')
        
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.axis('off')
    return fig

def plot_q5(teorema):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    # Corregido: Se elimina smooth=True
    ax.add_patch(patches.Polygon([[0,0], [2,-1], [3,1], [1,2]], facecolor='#A9DFBF', edgecolor='black'))
    ax.plot(1.5, 0.5, marker='o', color='black')
    ax.text(1.2, 0.5, "G")
    ax.plot([1.5, 1.5], [-1.5, 2.5], 'b-', lw=2)
    ax.text(1.3, 2.3, "Eje G", color='blue')
    
    if teorema == "Teorema de Ejes Paralelos":
        ax.plot([3.5, 3.5], [-1.5, 2.5], 'r-', lw=2)
        ax.text(3.6, 2.3, "Eje Z", color='red')
        ax.annotate('', xy=(3.5, 0), xytext=(1.5, 0), arrowprops=dict(facecolor='black', arrowstyle='<->'))
        ax.text(2.5, 0.2, "d", fontweight='bold')
        ax.text(2.5, -2, r"$I_Z = I_G + md^2$", ha='center', color='red', fontweight='bold', fontsize=12)
    else:
        ax.text(2.5, -2, r"$I_G$ (Inercia centroidal)", ha='center', color='blue', fontweight='bold', fontsize=12)
        
    ax.set_xlim(-1, 5); ax.set_ylim(-2.5, 3); ax.axis('off')
    return fig

def plot_q6(radio):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if radio == "Cuerpo Real":
        ax.add_patch(patches.Rectangle((-1, -1), 2, 2, facecolor='gray', edgecolor='black'))
        ax.plot([0, 0], [-2, 2], 'k-.')
        ax.text(0, -2.5, "Masa Distribuida (I)", ha='center', fontweight='bold')
    else:
        ax.plot([0, 0], [-2, 2], 'k-.')
        ax.plot(1.5, 0, marker='o', color='red', markersize=15)
        ax.annotate('', xy=(1.5, 0), xytext=(0, 0), arrowprops=dict(facecolor='blue', arrowstyle='<->'))
        ax.text(0.7, 0.2, "k (Radio de giro)", color='blue', fontweight='bold')
        ax.text(0, -2.5, r"Toda la masa $m$ a distancia $k$", ha='center', fontweight='bold')
        
    ax.set_xlim(-2, 3); ax.set_ylim(-3, 3); ax.axis('off')
    return fig

def plot_q7(fuerzas):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((0, 0), 2, 1, facecolor='#AED6F1', edgecolor='black'))
    
    if fuerzas == "Fuerzas Externas (Causas)":
        ax.annotate('', xy=(2.5, 0.8), xytext=(2, 0.8), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(2.5, 0.2), xytext=(2, 0.2), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(-0.5, 0.5), xytext=(0, 0.5), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(1, -0.5, r"$\Sigma F_x, \Sigma F_y$", color='red', fontweight='bold', ha='center', fontsize=14)
    else:
        ax.plot(1, 0.5, marker='o', color='blue')
        ax.annotate('', xy=(2.5, 0.5), xytext=(1, 0.5), arrowprops=dict(facecolor='blue', width=4, headwidth=8))
        ax.text(1.7, 0.7, r"$m \cdot a_G$", color='blue', fontweight='bold', fontsize=14)
        ax.text(1, -0.5, "Efecto Cinético", color='blue', fontweight='bold', ha='center')
        
    ax.set_xlim(-1, 3.5); ax.set_ylim(-1, 2); ax.axis('off')
    return fig

def plot_q8(momento):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Circle((2, 1), 1, facecolor='lightgray', edgecolor='black'))
    ax.plot(2, 1, marker='o', color='black') # G
    ax.text(2, 1.2, "G")
    ax.plot(0.5, 0.5, marker='x', color='red', markersize=8) # P
    ax.text(0.5, 0.7, "P", color='red', fontweight='bold')
    
    if momento == "Momentos Cinéticos (Efectos)":
        ax.annotate('', xy=(3, 1), xytext=(2, 1), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
        ax.text(2.5, 1.2, "$m(a_G)_x$", color='blue')
        ax.annotate('', xy=(1.5, 1.8), xytext=(1.8, 1.5), arrowprops=dict(facecolor='blue', width=2, headwidth=6, connectionstyle="arc3,rad=-0.3"))
        ax.text(1.2, 1.9, "$I_G\\alpha$", color='blue')
        ax.plot([0.5, 2], [0.5, 1], 'r--')
        ax.text(1.5, -0.5, r"$\Sigma (M_k)_P$", color='blue', fontweight='bold', ha='center', fontsize=12)
    else:
        ax.annotate('', xy=(3.5, 1.5), xytext=(2.5, 1.5), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(3, 1.7, "$F_1$", color='red')
        ax.plot([0.5, 2.5], [0.5, 1.5], 'r--')
        ax.text(1.5, -0.5, r"$\Sigma M_P$", color='red', fontweight='bold', ha='center', fontsize=12)

    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1, 2.5); ax.axis('off')
    return fig

def plot_q9(diagrama):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((0, 0), 2, 1, facecolor='#FAD7A1', edgecolor='black'))
    
    if diagrama == "Diagrama de Cuerpo Libre (Causas)":
        ax.annotate('', xy=(2.5, 0.8), xytext=(2, 0.8), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(1, 1.5), xytext=(1, 1), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(0.5, 1.5), xytext=(0.8, 1.2), arrowprops=dict(facecolor='red', width=2, headwidth=6, connectionstyle="arc3,rad=0.3"))
        ax.text(1, -0.5, "Muestra Fuerzas y Momentos Externos", color='red', fontweight='bold', ha='center')
    else:
        ax.plot(1, 0.5, marker='o', color='blue')
        ax.text(0.8, 0.5, "G")
        ax.annotate('', xy=(2, 0.5), xytext=(1, 0.5), arrowprops=dict(facecolor='blue', width=3, headwidth=8))
        ax.text(1.5, 0.2, "$ma_G$", color='blue', fontweight='bold')
        ax.annotate('', xy=(0.5, 1.2), xytext=(0.8, 0.9), arrowprops=dict(facecolor='blue', width=2, headwidth=6, connectionstyle="arc3,rad=0.3"))
        ax.text(0.5, 1.4, "$I_G\\alpha$", color='blue', fontweight='bold')
        ax.text(1, -0.5, "Muestra Vectores Inerciales", color='blue', fontweight='bold', ha='center')

    ax.set_xlim(-1, 3.5); ax.set_ylim(-1, 2); ax.axis('off')
    return fig

def plot_q10(paso):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    c1, c2, c3 = 'gray', 'gray', 'gray'
    if paso == "Paso 1: DCL": c1 = 'red'
    elif paso == "Paso 2: Diagrama Cinético": c2 = 'blue'
    else: c3 = 'green'
    
    ax.add_patch(patches.Rectangle((0, 2), 4, 0.8, facecolor=c1, edgecolor='black', alpha=0.7))
    ax.text(2, 2.4, "1. Diagrama de Cuerpo Libre", ha='center', fontweight='bold')
    
    ax.add_patch(patches.Rectangle((0, 1), 4, 0.8, facecolor=c2, edgecolor='black', alpha=0.7))
    ax.text(2, 1.4, "2. Diagrama Cinético", ha='center', fontweight='bold')
    
    ax.add_patch(patches.Rectangle((0, 0), 4, 0.8, facecolor=c3, edgecolor='black', alpha=0.7))
    ax.text(2, 0.4, "3. Ecuaciones de Movimiento", ha='center', fontweight='bold')
    
    ax.annotate('', xy=(2, 1.8), xytext=(2, 2), arrowprops=dict(arrowstyle="->", lw=2))
    ax.annotate('', xy=(2, 0.8), xytext=(2, 1), arrowprops=dict(arrowstyle="->", lw=2))

    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 3.5); ax.axis('off')
    return fig

funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.radio("Componente de la aceleración:", ["Aceleración Normal ($a_n$)", "Aceleración Tangencial ($a_t$)"], horizontal=True, key='sim_q1'),
    lambda: st.radio("Análisis en G:", ["Causa Externa", "Efecto (Momento de Inercia)"], horizontal=True, key='sim_q2'),
    lambda: st.radio("Brazo de Palanca respecto a O:", ["Pasa por el Origen", "Genera Momento en O"], horizontal=True, key='sim_q3'),
    lambda: st.radio("Distribución de la Masa:", ["Alta Inercia (Masa alejada)", "Baja Inercia (Masa concentrada)"], horizontal=True, key='sim_q4'),
    lambda: st.radio("Desplazamiento del Eje:", ["Eje Original (Centroide)", "Teorema de Ejes Paralelos"], horizontal=True, key='sim_q5'),
    lambda: st.radio("Representación de Masa:", ["Cuerpo Real", "Masa puntual a radio k"], horizontal=True, key='sim_q6'),
    lambda: st.radio("Ecuación de Traslación:", ["Fuerzas Externas (Causas)", "Vector Masa-Aceleración (Efecto)"], horizontal=True, key='sim_q7'),
    lambda: st.radio("Sumatoria de Momentos en P:", ["Momentos Externos (Causas)", "Momentos Cinéticos (Efectos)"], horizontal=True, key='sim_q8'),
    lambda: st.radio("Tipo de Diagrama:", ["Diagrama de Cuerpo Libre (Causas)", "Diagrama Cinético (Efectos)"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Secuencia Metodológica:", ["Paso 1: DCL", "Paso 2: Diagrama Cinético", "Paso 3: Fórmulas Matemáticas"], horizontal=True, key='sim_q10')
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
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 4: Temas 8, 9 y 10"), ln=True, align='C')
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
        desc_marzano = "El estudiante abstrae relaciones cinéticas, domina el momento de inercia y formula ecuaciones de movimiento."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante diferencia DCL de Diagrama Cinético y reconoce componentes de aceleración angular."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante requiere afianzar las bases de la Segunda Ley de Newton aplicada a la rotación."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Rotación y Aceleración (Tema 8):"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Domina las componentes normal/tangencial y su relación con el momento cinético." if puntaje >= 80 else ("Entiende la rotación pero confunde brazos de palanca cinéticos." if puntaje >= 60 else "No identifica el efecto rotacional de la aceleración tangencial.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Momento de Inercia de Masa (Tema 9):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Comprende la inercia rotacional, el radio de giro y el teorema de ejes paralelos." if puntaje >= 80 else ("Distingue la inercia de la masa, pero confunde los traslados de eje." if puntaje >= 60 else "Desconoce el concepto físico del momento de inercia de masa.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Ecuaciones de Movimiento y Diagramas (Tema 10):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Integra rigurosamente el DCL con el Diagrama Cinético mediante ecuaciones de movimiento." if puntaje >= 80 else ("Conoce las fórmulas pero falla en el procedimiento estructurado DCL/Cinético." if puntaje >= 60 else "No relaciona las fuerzas externas con las aceleraciones cinéticas del cuerpo.")
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
    st.markdown('<p class="main-title">Comprobación de Lectura 4: Temas 8, 9 y 10</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para observar el comportamiento cinético y dinámico de los cuerpos rígidos. Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
    </div>
    """, unsafe_allow_html=True)

    col_id1, col_id2 = st.columns(2)
    nombre_alumno = col_id1.text_input("Nombre Completo:", placeholder="Ej. Carlos Mendoza")
    matricula = col_id2.text_input("Matrícula Institucional:", placeholder="Ej. 3087876")
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
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 4 (Temas 8, 9 y 10)</p>
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
            '2. Comprensión\n(Identifica Vectores)',
            '3. Análisis\n(Relaciona Inercia y Masa)',
            '4. Utilización\n(Plantea Ecuaciones Cinemáticas)',
            '5. Metacognición\n(Evalúa Metodología)'
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
                <td><b>Rotación y Aceleración</b><br>(Tema 8)</td>
                <td class="{c_level}">✓ Domina las componentes normal/tangencial y su relación con el momento cinético.</td>
                <td class="{a_level}">✓ Entiende la rotación pero confunde brazos de palanca cinéticos.</td>
                <td class="{b_level}">✓ No identifica el efecto rotacional de la aceleración tangencial.</td>
            </tr>
            <tr>
                <td><b>Momento de Inercia de Masa</b><br>(Tema 9)</td>
                <td class="{c_level}">✓ Comprende la inercia rotacional, el radio de giro y el teorema de ejes paralelos.</td>
                <td class="{a_level}">✓ Distingue la inercia de la masa, pero confunde los traslados de eje.</td>
                <td class="{b_level}">✓ Desconoce el concepto físico del momento de inercia de masa.</td>
            </tr>
            <tr>
                <td><b>Ecuaciones y Diagramas</b><br>(Tema 10)</td>
                <td class="{c_level}">✓ Integra rigurosamente el DCL con el Diagrama Cinético mediante ecuaciones de movimiento.</td>
                <td class="{a_level}">✓ Conoce las fórmulas pero falla en el procedimiento estructurado DCL/Cinético.</td>
                <td class="{b_level}">✓ No relaciona las fuerzas externas con las aceleraciones cinéticas del cuerpo.</td>
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

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial y súbelo a Canvas como evidencia de tu Comprobación de Lectura 4.")

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
            file_name=f"Certificado_Lectura4_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
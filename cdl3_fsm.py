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
st.set_page_config(page_title="Comprobación de Lectura 3 - FSM", layout="wide")

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
    {"id": "q1", "titulo": "Reactivo 1: Centro de gravedad", "texto": "¿Qué condición mecánica debe cumplirse para que un objeto (como un cuchillo sobre el dedo índice) se mantenga en equilibrio estable?", "opciones": ["Su centroide debe estar fuera de su volumen.", "Su centro de gravedad debe estar directamente sobre el punto de apoyo.", "La aceleración tangencial debe ser cero.", "Debe estar sometido a un movimiento plano general."], "correcta": "Su centro de gravedad debe estar directamente sobre el punto de apoyo."},
    {"id": "q2", "titulo": "Reactivo 2: Centroide vs. Centro de Gravedad", "texto": "El centroide representa el centro geométrico de un cuerpo. ¿Bajo qué condición única el centroide coincide exactamente con el centro de masa y el centro de gravedad?", "opciones": ["Solo cuando el cuerpo tiene movimiento de traslación rectilínea.", "Cuando el cuerpo experimenta una aceleración angular constante.", "Solo si el material que compone al cuerpo es uniforme u homogéneo (densidad constante).", "Cuando el objeto tiene forma circular exclusivamente."], "correcta": "Solo si el material que compone al cuerpo es uniforme u homogéneo (densidad constante)."},
    {"id": "q3", "titulo": "Reactivo 3: Ubicación del Centroide", "texto": "Mecánicamente, ¿es posible que el centroide o centro de gravedad se ubique en un punto físico fuera del material del objeto?", "opciones": ["No, siempre debe estar dentro de la masa del objeto.", "Sí, un ejemplo clásico es un anillo, donde el centroide está en el espacio vacío central.", "Solo si el cuerpo está experimentando rotación en un eje fijo.", "Depende enteramente de la aceleración gravitacional del entorno."], "correcta": "Sí, un ejemplo clásico es un anillo, donde el centroide está en el espacio vacío central."},
    {"id": "q4", "titulo": "Reactivo 4: Cuerpos compuestos", "texto": "Para encontrar el centroide de un 'cuerpo compuesto', ¿cuál es el procedimiento analítico recomendado?", "opciones": ["Dividirlo en cuerpos más simples, hallar el centroide de cada uno y aplicar un balance de momentos (suma ponderada).", "Calcular el momento de inercia polar de la figura completa.", "Aplicar la derivada de la posición angular con respecto al tiempo.", "Asumir que el centroide se ubica en el extremo más pesado."], "correcta": "Dividirlo en cuerpos más simples, hallar el centroide de cada uno y aplicar un balance de momentos (suma ponderada)."},
    {"id": "q5", "titulo": "Reactivo 5: Cargas distribuidas", "texto": "Al analizar una carga distribuida sobre una viga, la magnitud de la fuerza resultante es igual a...", "opciones": ["El perímetro del área de carga.", "El área o volumen total bajo el diagrama de la carga distribuida.", "La integral de la aceleración angular.", "La densidad del material multiplicada por su longitud."], "correcta": "El área o volumen total bajo el diagrama de la carga distribuida."},
    {"id": "q6", "titulo": "Reactivo 6: Tipos de Movimiento", "texto": "Si al moverse un cuerpo rígido, las líneas de trayectorias de dos de sus puntos se mantienen paralelas durante el movimiento, ¿cómo se le llama a este fenómeno?", "opciones": ["Rotación sobre eje fijo.", "Movimiento plano general.", "Traslación rectilínea.", "Cinemática de cuerpo deformante."], "correcta": "Traslación rectilínea."},
    {"id": "q7", "titulo": "Reactivo 7: Rotación con respecto a eje fijo", "texto": "En la rotación con respecto a un eje fijo, todas las partículas que forman el cuerpo experimentan un movimiento circular. ¿Cuál es la única excepción?", "opciones": ["Las partículas ubicadas en el perímetro exterior.", "Las partículas que forman parte del eje fijo alrededor del cual gira el cuerpo.", "Las partículas con mayor densidad.", "Ninguna, todas las partículas sin excepción se mueven."], "correcta": "Las partículas que forman parte del eje fijo alrededor del cual gira el cuerpo."},
    {"id": "q8", "titulo": "Reactivo 8: Movimiento Plano General", "texto": "¿A qué nos referimos cuando decimos que un cuerpo rígido experimenta un 'movimiento plano general' (como una llanta rodando)?", "opciones": ["A un movimiento tridimensional unido a un punto fijo.", "Al movimiento estático donde la velocidad y aceleración son cero.", "Cuando experimenta simultáneamente un movimiento de traslación y un movimiento de rotación.", "A la traslación curvilínea pura."], "correcta": "Cuando experimenta simultáneamente un movimiento de traslación y un movimiento de rotación."},
    {"id": "q9", "titulo": "Reactivo 9: Mecanismo Biela - Manivela", "texto": "En el mecanismo biela-corredera-manivela de un motor, la 'corredera' (pistón) realiza traslación y la 'manivela' rotación pura. ¿Qué movimiento describe la 'biela' (eslabón intermedio)?", "opciones": ["Rotación pura sobre un eje fijo.", "Traslación rectilínea únicamente.", "Movimiento tridimensional fijo.", "Movimiento plano general (traslación y rotación simultánea)."], "correcta": "Movimiento plano general (traslación y rotación simultánea)."},
    {"id": "q10", "titulo": "Reactivo 10: Componentes de Aceleración", "texto": "Al analizar un punto P en rotación, la aceleración tangencial se asocia con el cambio de magnitud de la velocidad. ¿Qué fórmula define la aceleración tangencial ($a_t$)?", "opciones": ["$a_t = \\alpha \\cdot r$ (aceleración angular por radio)", "$a_t = \\omega^2 \\cdot r$ (velocidad angular al cuadrado por radio)", "$a_t = v / r$", "$a_t = \\theta \\cdot t$"], "correcta": "$a_t = \\alpha \\cdot r$ (aceleración angular por radio)"}
]

# ==========================================
# FUNCIONES DE FIGURAS INTERACTIVAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(estado):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    # Dedo
    ax.add_patch(patches.Polygon([[1.8,0], [2.2,0], [2,1]], facecolor='#F5CBA7', edgecolor='black'))
    
    if estado == "En Equilibrio (CG alineado)":
        # Cuchillo centrado
        ax.add_patch(patches.Rectangle((0.5, 1), 3, 0.3, facecolor='gray', edgecolor='black'))
        ax.plot(2, 1.15, marker='o', color='red', markersize=6)
        ax.annotate('', xy=(2, 0.5), xytext=(2, 1.15), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(2.1, 1.3, "CG y Peso", color='red', fontweight='bold')
        ax.text(2, -0.4, "Estable", color='green', ha='center', fontweight='bold')
    else:
        # Cuchillo desalineado y cayendo
        ax.add_patch(patches.Rectangle((1.5, 0.8), 3, 0.3, angle=-15, facecolor='gray', edgecolor='black'))
        ax.plot(3, 0.55, marker='o', color='red', markersize=6)
        ax.annotate('', xy=(3, -0.1), xytext=(3, 0.55), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(3.1, 0.6, "CG y Peso", color='red', fontweight='bold')
        ax.text(2, -0.4, "Genera un Momento -> Cae", color='red', ha='center', fontweight='bold')
        
    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 2); ax.axis('off')
    return fig

def plot_q2(material):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if material == "Homogéneo (Uniforme)":
        ax.add_patch(patches.Rectangle((1, 0), 2, 1, facecolor='lightblue', edgecolor='black'))
        ax.plot(2, 0.5, marker='o', color='blue', markersize=8)
        ax.text(2, 0.7, "Centroide = CG", color='blue', ha='center', fontweight='bold')
    else:
        # Densidad variable (mitad plomo, mitad madera)
        ax.add_patch(patches.Rectangle((1, 0), 1, 1, facecolor='darkgray', edgecolor='black'))
        ax.add_patch(patches.Rectangle((2, 0), 1, 1, facecolor='#DEB887', edgecolor='black'))
        ax.text(1.5, 0.2, "Alta Densidad", ha='center', fontsize=8)
        ax.text(2.5, 0.2, "Baja Densidad", ha='center', fontsize=8)
        
        ax.plot(2, 0.5, marker='x', color='black', markersize=8) # Centroide geométrico
        ax.plot(1.6, 0.5, marker='o', color='red', markersize=8) # CG desplazado
        
        ax.text(2, 0.7, "Centroide", color='black', ha='center', fontsize=9)
        ax.text(1.3, 0.7, "CG", color='red', ha='center', fontweight='bold')
        
    ax.set_xlim(0.5, 3.5); ax.set_ylim(-0.5, 1.5); ax.axis('off')
    return fig

def plot_q3(forma):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if forma == "Disco Sólido":
        ax.add_patch(patches.Circle((2, 1), 0.8, facecolor='lightgray', edgecolor='black'))
        ax.plot(2, 1, marker='o', color='red', markersize=8)
        ax.text(2, 0, "Centroide DENTRO de la masa", color='green', ha='center', fontweight='bold')
    else:
        ax.add_patch(patches.Circle((2, 1), 0.8, facecolor='lightgray', edgecolor='black', linewidth=4, fill=False))
        ax.plot(2, 1, marker='o', color='red', markersize=8)
        ax.text(2, 0, "Centroide FUERA de la masa (Vacío)", color='red', ha='center', fontweight='bold')
        
    ax.set_xlim(0, 4); ax.set_ylim(-0.2, 2.2); ax.axis('off')
    return fig

def plot_q4(desglose):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if desglose == "Cuerpo Compuesto Unido":
        ax.add_patch(patches.Polygon([[1,0], [3,0], [3,0.5], [1.5,0.5], [1.5,2], [1,2]], facecolor='gray', edgecolor='black'))
        ax.plot(1.6, 0.6, marker='o', color='blue', markersize=8) # CG compuesto aprox
        ax.text(1.6, 0.8, r"$\bar{x} = \frac{\sum \tilde{x} W}{\sum W}$", color='blue', fontweight='bold')
    else:
        # Pieza 1
        ax.add_patch(patches.Rectangle((1, 0), 0.5, 2, facecolor='lightblue', edgecolor='black', alpha=0.7))
        ax.plot(1.25, 1, marker='o', color='red', markersize=6)
        ax.text(1.25, 1.2, "$G_1$", color='red', ha='center')
        
        # Pieza 2
        ax.add_patch(patches.Rectangle((1.5, 0), 1.5, 0.5, facecolor='lightgreen', edgecolor='black', alpha=0.7))
        ax.plot(2.25, 0.25, marker='o', color='red', markersize=6)
        ax.text(2.25, 0.45, "$G_2$", color='red', ha='center')
        ax.text(2, 2, "Separación en formas simples", color='black', ha='center', fontweight='bold')

    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 2.5); ax.axis('off')
    return fig

def plot_q5(distribucion):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([0, 4], [0, 0], color='black', linewidth=3) # Viga
    
    if distribucion == "Carga Rectangular Uniforme":
        ax.add_patch(patches.Rectangle((0, 0), 4, 1.5, facecolor='lightblue', edgecolor='blue', alpha=0.5))
        ax.annotate('', xy=(2, 0), xytext=(2, 1.5), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(2.2, 0.7, r"$F_R$ en $L/2$", color='red', fontweight='bold')
    else:
        ax.add_patch(patches.Polygon([[0,0], [4,0], [4,1.5]], facecolor='lightblue', edgecolor='blue', alpha=0.5))
        ax.annotate('', xy=(2.66, 0), xytext=(2.66, 1), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(2.8, 0.5, r"$F_R$ en $2L/3$", color='red', fontweight='bold')

    ax.text(2, -0.5, r"Magnitud = $\int w(x) dx$ (Área)", color='blue', ha='center')
    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-1, 2); ax.axis('off')
    return fig

def plot_q6(trayectoria):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if trayectoria == "Traslación Rectilínea":
        ax.plot([0, 3], [0, 1], 'k--') # Path
        # Caja 1
        ax.add_patch(patches.Rectangle((0, 0), 1, 0.5, facecolor='gray', edgecolor='black'))
        ax.plot([0,1], [0.5,0.5], 'r-', lw=2)
        # Caja 2
        ax.add_patch(patches.Rectangle((2, 0.66), 1, 0.5, facecolor='gray', edgecolor='black'))
        ax.plot([2,3], [1.16, 1.16], 'r-', lw=2)
        ax.text(1.5, -0.5, "Orientación constante en línea recta", ha='center', color='blue')
    else:
        x = np.linspace(0, 3, 50)
        y = np.sin(x)
        ax.plot(x, y, 'k--')
        # Caja 1
        ax.add_patch(patches.Rectangle((0, 0), 1, 0.5, facecolor='gray', edgecolor='black'))
        ax.plot([0,1], [0.5,0.5], 'r-', lw=2)
        # Caja 2
        ax.add_patch(patches.Rectangle((2.5, np.sin(2.5)), 1, 0.5, facecolor='gray', edgecolor='black'))
        ax.plot([2.5, 3.5], [np.sin(2.5)+0.5, np.sin(2.5)+0.5], 'r-', lw=2)
        ax.text(1.5, -1.2, "Orientación constante en curva", ha='center', color='blue')

    ax.set_xlim(-0.5, 4); ax.set_ylim(-1.5, 2); ax.axis('off')
    return fig

def plot_q7(visibilidad):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Circle((2, 1), 1, facecolor='lightgray', edgecolor='black'))
    
    # Eje fijo
    ax.plot(2, 1, marker='x', color='red', markersize=12, markeredgewidth=3)
    ax.text(2.2, 1, "Eje fijo\n(Velocidad cero)", color='red')
    
    if visibilidad == "Mostrar partículas en el radio":
        rad = np.radians(45)
        px, py = 2 + np.cos(rad)*0.8, 1 + np.sin(rad)*0.8
        ax.plot(px, py, marker='o', color='blue')
        ax.annotate('', xy=(px-0.3, py+0.3), xytext=(px, py), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
        ax.text(px-0.5, py+0.4, "$v = \omega r$", color='blue')
        
    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 2.5); ax.axis('off')
    return fig

def plot_q8(componentes):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.plot([0, 4], [0, 0], color='black', lw=2)
    
    if componentes == "Movimiento Plano General":
        ax.add_patch(patches.Circle((2, 1), 1, facecolor='lightgray', edgecolor='black'))
        ax.annotate('', xy=(3, 1), xytext=(2, 1), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(3, 2), xytext=(2, 2), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
        ax.plot(2, 0, marker='o', color='green')
        ax.text(2, -0.5, "Traslación + Rotación (Rodadura)", ha='center', fontweight='bold')
    else:
        ax.add_patch(patches.Circle((1, 1), 0.5, facecolor='lightgray', edgecolor='black'))
        ax.annotate('', xy=(2, 1), xytext=(1, 1), arrowprops=dict(facecolor='red', width=1, headwidth=4))
        ax.text(2.5, 1, "+", fontsize=20)
        ax.add_patch(patches.Circle((3.5, 1), 0.5, facecolor='lightgray', edgecolor='black'))
        ax.annotate('', xy=(3.5, 1.7), xytext=(3.5, 1.5), arrowprops=dict(facecolor='blue', width=1, headwidth=4))
        ax.text(1.5, 0.2, "Traslación pura", ha='center', color='red')
        ax.text(3.5, 0.2, "Rotación pura", ha='center', color='blue')
        
    ax.set_xlim(0, 4.5); ax.set_ylim(-1, 2.5); ax.axis('off')
    return fig

def plot_q9(eslabon):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    # Ejes
    ax.plot([-1, 4], [0, 0], 'k--', lw=1)
    
    # Coordenadas
    O2 = (0, 0)
    A = (0.5, 1)
    B = (3, 0)
    
    # Dibujar partes
    c_manivela = 'gray'
    c_biela = 'gray'
    c_corredera = 'gray'
    
    if eslabon == "Manivela (2)": c_manivela = 'red'
    elif eslabon == "Biela (3)": c_biela = 'blue'
    else: c_corredera = 'green'
    
    ax.plot([O2[0], A[0]], [O2[1], A[1]], color=c_manivela, lw=5) # Manivela
    ax.plot([A[0], B[0]], [A[1], B[1]], color=c_biela, lw=5) # Biela
    ax.add_patch(patches.Rectangle((B[0]-0.4, B[1]-0.2), 0.8, 0.4, facecolor=c_corredera, edgecolor='black')) # Corredera
    
    ax.plot(0, 0, marker='o', color='black')
    
    if eslabon == "Manivela (2)": ax.text(0, 1.2, "Rotación pura (Eje fijo)", color='red')
    elif eslabon == "Biela (3)": ax.text(1.5, 1.2, "Movimiento Plano General", color='blue', fontweight='bold')
    else: ax.text(3, 0.5, "Traslación", color='green')

    ax.set_xlim(-1, 4); ax.set_ylim(-1, 2); ax.axis('off')
    return fig

def plot_q10(variacion):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Circle((0, 0), 1.5, facecolor='none', edgecolor='lightgray', linestyle='--'))
    ax.plot(0, 0, marker='+', color='black')
    
    # Punto P a 45 grados
    rad = np.radians(45)
    px, py = 1.5*np.cos(rad), 1.5*np.sin(rad)
    ax.plot(px, py, marker='o', color='black')
    
    if variacion == "Aceleración Angular constante (Aumenta an)":
        # at pequeño, an grande
        ax.annotate('', xy=(px - 0.5*np.sin(rad), py + 0.5*np.cos(rad)), xytext=(px, py), arrowprops=dict(facecolor='blue', width=1, headwidth=4))
        ax.annotate('', xy=(0, 0), xytext=(px, py), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(px-0.3, py+0.5, r"$a_t = \alpha r$", color='blue')
        ax.text(0.5, 0.5, r"$a_n = \omega^2 r$", color='red', fontweight='bold')
    else:
        # at grande (fuerte aceleración angular)
        ax.annotate('', xy=(px - 1.5*np.sin(rad), py + 1.5*np.cos(rad)), xytext=(px, py), arrowprops=dict(facecolor='blue', width=3, headwidth=8))
        ax.annotate('', xy=(0.5*np.cos(rad), 0.5*np.sin(rad)), xytext=(px, py), arrowprops=dict(facecolor='red', width=1, headwidth=4))
        ax.text(px-1, py+1.5, r"$a_t = \alpha r$", color='blue', fontweight='bold')
        ax.text(1, 1, r"$a_n$", color='red')
        
    ax.set_xlim(-2, 2); ax.set_ylim(-0.5, 2.5); ax.axis('off')
    return fig

funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.radio("Posición del objeto:", ["En Equilibrio (CG alineado)", "Desalineado"], horizontal=True, key='sim_q1'),
    lambda: st.radio("Distribución de masa:", ["Homogéneo (Uniforme)", "Material mixto (Densidad variable)"], horizontal=True, key='sim_q2'),
    lambda: st.radio("Geometría del cuerpo:", ["Disco Sólido", "Anillo (Hueco)"], horizontal=True, key='sim_q3'),
    lambda: st.radio("Análisis:", ["Cuerpo Compuesto Unido", "Desglose por partes"], horizontal=True, key='sim_q4'),
    lambda: st.radio("Perfil de Carga:", ["Carga Rectangular Uniforme", "Carga Triangular"], horizontal=True, key='sim_q5'),
    lambda: st.radio("Trayectoria:", ["Traslación Rectilínea", "Traslación Curvilínea"], horizontal=True, key='sim_q6'),
    lambda: st.radio("Visualización:", ["Solo el Eje Fijo", "Mostrar partículas en el radio"], horizontal=True, key='sim_q7'),
    lambda: st.radio("Descomposición de movimiento:", ["Movimiento Plano General", "Suma de Traslación + Rotación"], horizontal=True, key='sim_q8'),
    lambda: st.radio("Resaltar eslabón:", ["Manivela (2)", "Biela (3)", "Corredera (Pistón)"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Cambio en el tiempo:", ["Aceleración Angular constante (Aumenta an)", "Fuerte aceleración angular (Aumenta at)"], horizontal=True, key='sim_q10')
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
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 3: Temas 6 y 7"), ln=True, align='C')
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
        desc_marzano = "El estudiante abstrae geometrías para cálculo de centroides, distribuciones de carga y modelado de cinemática de cuerpo rígido."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante comprende los conceptos básicos de centro de gravedad y distingue los tipos elementales de movimiento plano."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante identifica conceptos de manera aislada. Requiere refuerzo en integración de ecuaciones cinemáticas."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Centroides y Cargas Distribuidas (Tema 6):"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Domina el concepto de CG vs centroide y deduce fuerzas resultantes bajo curvas de carga." if puntaje >= 80 else ("Entiende el centro geométrico pero confunde el tratamiento de cuerpos de densidad variable." if puntaje >= 60 else "Presenta fallas en identificar la relación de fuerzas con integrales de volumen/área.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Tipos de Movimiento Plano (Tema 7):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Clasifica con precisión la traslación, rotación y el movimiento plano general en mecanismos complejos." if puntaje >= 80 else ("Distingue traslación y rotación básica, pero se confunde en los eslabones con movimiento combinado." if puntaje >= 60 else "No diferencia la traslación de la rotación en el análisis mecánico.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Cinemática de Rotación y Aceleración (Tema 7):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Aplica correctamente las ecuaciones escalares para componentes tangenciales (alfa*r) y normales." if puntaje >= 80 else ("Reconoce las fórmulas angulares pero confunde la función de la aceleración tangencial." if puntaje >= 60 else "Desconoce el comportamiento de los vectores de velocidad y aceleración en rotación.")
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
    st.markdown('<p class="main-title">Comprobación de Lectura 3: Temas 6 y 7</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para observar el comportamiento físico/matemático del concepto (Centroides y Movimiento). Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
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
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 3 (Temas 6 y 7)</p>
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
            '2. Comprensión\n(Diferencia Movimientos)',
            '3. Análisis\n(Ubicación de Centroides)',
            '4. Utilización\n(Ecuaciones Cinemáticas)',
            '5. Metacognición\n(Evaluación de Mecanismos)'
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
                <td><b>Centroides y Cargas Distribuidas</b><br>(Tema 6)</td>
                <td class="{c_level}">✓ Domina el concepto de CG vs centroide y deduce las fuerzas resultantes y su ubicación bajo curvas.</td>
                <td class="{a_level}">✓ Entiende el centro geométrico pero confunde el tratamiento de cuerpos de densidad variable.</td>
                <td class="{b_level}">✓ Presenta fallas en identificar la relación de fuerzas resultantes con el volumen/área.</td>
            </tr>
            <tr>
                <td><b>Tipos de Movimiento Plano</b><br>(Tema 7)</td>
                <td class="{c_level}">✓ Clasifica con precisión la traslación, rotación y el movimiento general en mecanismos complejos.</td>
                <td class="{a_level}">✓ Distingue traslación y rotación básica, pero se confunde en eslabones con movimiento combinado.</td>
                <td class="{b_level}">✓ No diferencia la traslación pura de la rotación en el análisis mecánico y de eslabones.</td>
            </tr>
            <tr>
                <td><b>Cinemática de Rotación y Ecuaciones</b><br>(Tema 7)</td>
                <td class="{c_level}">✓ Aplica correctamente las ecuaciones escalares para los componentes de aceleración (tangencial y normal).</td>
                <td class="{a_level}">✓ Reconoce las fórmulas angulares pero confunde la función de la aceleración tangencial.</td>
                <td class="{b_level}">✓ Desconoce el comportamiento de los vectores de velocidad y aceleración en un cuerpo girando.</td>
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

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial y súbelo a Canvas como evidencia de tu Comprobación de Lectura 3.")

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
            file_name=f"Certificado_Lectura3_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
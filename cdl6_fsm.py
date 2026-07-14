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
st.set_page_config(page_title="Comprobación de Lectura 6 - FSM", layout="wide")

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
    {"id": "q1", "titulo": "Reactivo 1: Fases del Hierro", "texto": "¿Cuál es la estructura cristalina y la característica principal de la Ferrita (Fe-$\\alpha$) a temperatura ambiente antes de fundir?", "opciones": ["Estructura FCC; es muy dura y frágil.", "Estructura BCC; es el constituyente más blando y dúctil de los aceros.", "Estructura HC; contiene 6.7% de carbono puro.", "No tiene estructura cristalina, es un material amorfo."], "correcta": "Estructura BCC; es el constituyente más blando y dúctil de los aceros."},
    {"id": "q2", "titulo": "Reactivo 2: Cementita", "texto": "En el diagrama de fase hierro-carbono, ¿a qué porcentaje máximo de carbono se forma el compuesto duro conocido como cementita ($Fe_3C$)?", "opciones": ["Al 0.008%", "Al 2.1%", "Al 6.7%", "Al 100% (Grafito puro)"], "correcta": "Al 6.7%"},
    {"id": "q3", "titulo": "Reactivo 3: Ensayo de Tracción", "texto": "¿Qué cambio físico experimenta paulatinamente la geometría de una probeta de metal al someterla a un ensayo de tracción hasta su rotura?", "opciones": ["Su longitud se reduce y su diámetro se expande constantemente.", "Su diámetro se va reduciendo y su longitud se va incrementando (formando un cuello).", "Mantiene su volumen geométrico intacto hasta fracturarse repentinamente.", "Se fragmenta en múltiples pedazos sin deformarse."], "correcta": "Su diámetro se va reduciendo y su longitud se va incrementando (formando un cuello)."},
    {"id": "q4", "titulo": "Reactivo 4: Curva Esfuerzo-Deformación", "texto": "En el diagrama esfuerzo-deformación, ¿cómo se le llama al límite crítico o resistencia que define la transición y el inicio de la deformación permanente del material?", "opciones": ["Resistencia a la tensión (Esfuerzo Último).", "Resistencia a la cedencia (fluencia).", "Módulo de elasticidad.", "Energía de impacto."], "correcta": "Resistencia a la cedencia (fluencia)."},
    {"id": "q5", "titulo": "Reactivo 5: Fatiga Estática en Cerámicos", "texto": "De acuerdo con el texto, ¿qué causa el fenómeno de 'fatiga estática' que reduce la tenacidad en los materiales cerámicos y vidrios alrededor de la temperatura ambiente?", "opciones": ["El ataque químico provocado por la humedad atmosférica.", "Las cargas cíclicas mecánicas de alta frecuencia.", "Las desigualdades de expansión por choque térmico.", "La deformación viscosa interna."], "correcta": "El ataque químico provocado por la humedad atmosférica."},
    {"id": "q6", "titulo": "Reactivo 6: Propiedades Ópticas", "texto": "¿Qué propiedad óptica de los vidrios y diamantes relaciona matemáticamente la velocidad de la luz en el vacío con la velocidad de la luz en el material transparente?", "opciones": ["Translucidez.", "Reflectancia (R).", "Opacidad por iones de metal.", "Índice de refracción (n)."], "correcta": "Índice de refracción (n)."},
    {"id": "q7", "titulo": "Reactivo 7: Propiedades de los Polímeros", "texto": "Según la lectura, ¿cuáles son los mecanismos principales de deformación mecánica que caracterizan a los polímeros?", "opciones": ["Fractura por fragilidad y choque térmico.", "Ductilidad extrema y endurecimiento por trabajo en frío.", "Deformación viscoelástica y elastomérica (con relajación de esfuerzo).", "Comportamiento puramente lineal según la ley de Hooke sin cedencia."], "correcta": "Deformación viscoelástica y elastomérica (con relajación de esfuerzo)."},
    {"id": "q8", "titulo": "Reactivo 8: Características de los Metales", "texto": "A nivel atómico, ¿qué característica intrínseca de los metales les otorga su excelente conductividad térmica y eléctrica, además de hacerlos opacos a la luz?", "opciones": ["Su alta resistencia a la compresión.", "La presencia de muchos electrones libres.", "Su estructura exclusivamente amorfa.", "Su fuerte enlace covalente direccional."], "correcta": "La presencia de muchos electrones libres."},
    {"id": "q9", "titulo": "Reactivo 9: Clasificación de Materiales Sólidos", "texto": "De acuerdo con su composición química y estructura atómica, ¿cuáles son los tres grupos primarios puros en los que se clasifican los materiales sólidos estructurales?", "opciones": ["Semiconductores, dieléctricos y magnéticos.", "Aceros, fundiciones y grafitos.", "Metales, cerámicas y polímeros.", "Estructurales, electromagnéticos y compuestos."], "correcta": "Metales, cerámicas y polímeros."},
    {"id": "q10", "titulo": "Reactivo 10: Selección de Materiales", "texto": "En la ingeniería, en ocasiones es difícil decidir qué material utilizar en una aplicación determinada. ¿Cuáles son los cuatro criterios o parámetros de diseño principales mencionados para realizar esta selección?", "opciones": ["Resistencia, ductilidad, costo y densidad.", "Color, índice de refracción, reflectancia y transparencia.", "Temperatura, presión, entropía y fase.", "Viscosidad, tenacidad a la fractura, límite elástico y tamaño de celdilla."], "correcta": "Resistencia, ductilidad, costo y densidad."}
]

# ==========================================
# FUNCIONES DE FIGURAS INTERACTIVAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(fase):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    ax.add_patch(patches.Rectangle((1, 0.5), 2, 2, fill=False, edgecolor='black', lw=2))
    corners = [(1, 0.5), (3, 0.5), (1, 2.5), (3, 2.5)]
    
    if fase == "Ferrita ($\\alpha$) - Temperatura Ambiente":
        for c in corners: ax.add_patch(patches.Circle(c, 0.3, color='blue', alpha=0.5, ec='black'))
        # Atomo central (BCC)
        ax.add_patch(patches.Circle((2, 1.5), 0.3, color='darkblue', alpha=0.8, ec='black'))
        ax.text(2, -0.2, "BCC: Cúbica Centrada en el Cuerpo", ha='center', fontweight='bold', color='darkblue')
        ax.text(2, -0.6, "Blando y dúctil", ha='center')
    else:
        for c in corners: ax.add_patch(patches.Circle(c, 0.3, color='red', alpha=0.5, ec='black'))
        # Atomo en las caras (FCC)
        ax.add_patch(patches.Circle((2, 1.5), 0.3, color='darkred', alpha=0.8, ec='black'))
        ax.text(2, -0.2, "FCC: Cúbica Centrada en las Caras", ha='center', fontweight='bold', color='darkred')
        ax.text(2, -0.6, "Mayor capacidad de disolver carbono", ha='center')

    ax.set_xlim(0, 4); ax.set_ylim(-1, 3); ax.axis('off')
    return fig

def plot_q2(porcentaje):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    # Ejes diagrama
    ax.plot([0, 7], [0, 0], 'k-', lw=2)
    ax.text(3.5, -0.5, "Porcentaje de Carbono (%)", ha='center')
    ax.text(-0.5, 0.5, "Temperatura", rotation=90, va='center')
    
    ax.plot([0, 0], [0, 3], 'k-', lw=1)
    ax.plot([6.7, 6.7], [0, 3], 'k--', lw=2, color='red')
    
    if porcentaje == "Aceros (Bajo carbono)":
        ax.add_patch(patches.Rectangle((0, 0), 2.1, 2.5, facecolor='lightblue', alpha=0.6))
        ax.text(1, 1.2, "Aceros\n(0 a 2.1%)", ha='center', fontweight='bold')
    else:
        ax.annotate('', xy=(6.7, 1.5), xytext=(4.5, 1.5), arrowprops=dict(facecolor='red', width=3, headwidth=8))
        ax.text(3, 1.5, "Límite del Diagrama:", color='red')
        ax.text(5.5, 1.9, "Cementita\n(6.7% C)", color='red', fontweight='bold', ha='center')
        ax.text(6.7, -0.3, "6.7", color='red', ha='center')

    ax.set_xlim(-1, 8); ax.set_ylim(-1, 3.5); ax.axis('off')
    return fig

def plot_q3(etapa):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if etapa == "Estado Inicial":
        ax.add_patch(patches.Rectangle((1, 0.5), 2, 1, facecolor='gray', edgecolor='black'))
        ax.annotate('', xy=(0.5, 1), xytext=(1, 1), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
        ax.annotate('', xy=(3.5, 1), xytext=(3, 1), arrowprops=dict(facecolor='blue', width=2, headwidth=6))
        ax.text(2, 0.2, "Diámetro Original $D_0$", ha='center')
    else:
        # Dibujar probeta con estricción (cuello)
        ax.add_patch(patches.Polygon([[0.5, 0.5], [1.5, 0.5], [2, 0.8], [2.5, 0.5], [3.5, 0.5], 
                                      [3.5, 1.5], [2.5, 1.5], [2, 1.2], [1.5, 1.5], [0.5, 1.5]], 
                                     facecolor='#C0C0C0', edgecolor='black'))
        ax.annotate('', xy=(0, 1), xytext=(0.5, 1), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.annotate('', xy=(4, 1), xytext=(3.5, 1), arrowprops=dict(facecolor='red', width=2, headwidth=6))
        ax.text(2, 1.8, "Estricción (Cuello)", color='red', fontweight='bold', ha='center')
        ax.text(2, -0.2, "Longitud mayor, Diámetro menor", ha='center', fontweight='bold')

    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5); ax.axis('off')
    return fig

def plot_q4(zona):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    # Ejes
    ax.plot([0, 4], [0, 0], 'k-', lw=1)
    ax.plot([0, 0], [0, 3], 'k-', lw=1)
    ax.text(2, -0.4, "Deformación ($\\epsilon$)", ha='center')
    ax.text(-0.3, 1.5, "Esfuerzo ($\\sigma$)", rotation=90, va='center')
    
    # Curva
    x_el = np.linspace(0, 1, 10)
    y_el = x_el * 1.5
    x_pl = np.linspace(1, 3.5, 30)
    y_pl = 1.5 + np.sin((x_pl-1)*1.2) * 1
    
    ax.plot(x_el, y_el, 'b-', lw=3)
    ax.plot(x_pl, y_pl, 'r-', lw=3)
    
    # Punto de Fluencia
    ax.plot(1, 1.5, marker='o', color='black', markersize=8)
    
    if zona == "Zona Elástica":
        ax.fill_between(x_el, 0, y_el, color='blue', alpha=0.2)
        ax.text(0.5, 1.2, "Ley de Hooke\n(Lineal)", color='blue', ha='right')
    else:
        ax.annotate('Límite de Cedencia\n(Fluencia)', xy=(1, 1.5), xytext=(0.5, 2.5), 
                    arrowprops=dict(facecolor='black', width=2, headwidth=6), fontweight='bold')
        ax.fill_between(x_pl, 0, y_pl, color='red', alpha=0.2)
        ax.text(2.5, 1, "Deformación Plástica\nPermanente", color='red', ha='center')

    ax.set_xlim(-0.5, 4); ax.set_ylim(-0.5, 3.5); ax.axis('off')
    return fig

def plot_q5(ambiente):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.add_patch(patches.Rectangle((0, 0), 3, 2, facecolor='#D3D3D3', edgecolor='black'))
    
    # Dibujar grieta
    ax.plot([0, 1.5], [1, 1], 'k-', lw=3)
    ax.plot(1.5, 1, marker='<', color='black', markersize=10)
    
    if ambiente == "Humedad Atmosférica":
        ax.text(0.5, 1.2, "$H_2O$", color='blue', fontweight='bold')
        ax.text(1.2, 1.2, "$H_2O$", color='blue', fontweight='bold')
        ax.annotate('Ataque químico', xy=(1.5, 1), xytext=(2.5, 1.5), arrowprops=dict(facecolor='red', width=2, headwidth=6), color='red', fontweight='bold')
        ax.text(1.5, -0.5, "Fatiga Estática: Ruptura lenta", ha='center', fontweight='bold')
    else:
        ax.text(1.5, -0.5, "Ambiente Seco / Vacío", ha='center', color='gray')
        ax.text(2.5, 1.5, "Material estable", color='green', fontweight='bold')

    ax.set_xlim(-0.5, 3.5); ax.set_ylim(-1, 2.5); ax.axis('off')
    return fig

def plot_q6(indice):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.plot([0, 4], [1.5, 1.5], 'k-', lw=2) # Frontera
    ax.text(2, 1.7, "Vacío ($v = c$)", ha='center')
    ax.text(0.5, 0.5, "Material transparente", color='blue')
    
    ax.plot([2, 2], [0, 3], 'k--', lw=1) # Normal
    
    # Rayo incidente
    ax.annotate('', xy=(2, 1.5), xytext=(1, 3), arrowprops=dict(arrowstyle="-", color='orange', lw=3))
    
    if indice == "Alto Índice (Diamante)":
        # Rayo muy desviado
        ax.annotate('', xy=(2.4, 0), xytext=(2, 1.5), arrowprops=dict(arrowstyle="-", color='orange', lw=3))
        ax.text(3, 0.5, "$n = 2.42$", color='red', fontweight='bold')
        ax.text(2, -0.5, "La luz disminuye drásticamente su velocidad", ha='center', color='red')
    else:
        # Rayo poco desviado
        ax.annotate('', xy=(2.8, 0), xytext=(2, 1.5), arrowprops=dict(arrowstyle="-", color='orange', lw=3))
        ax.text(3, 0.5, "$n = 1.5$", color='blue', fontweight='bold')
        ax.text(2, -0.5, "$n = c / v$", ha='center', fontweight='bold')

    ax.set_xlim(0, 4); ax.set_ylim(-1, 3); ax.axis('off')
    return fig

def plot_q7(comportamiento):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if comportamiento == "Viscoelástico (Polímeros)":
        # Modelo muelle-amortiguador
        ax.plot([1, 1], [2, 1.5], 'k-', lw=2) # Tallo resorte
        x_res = np.linspace(1.5, 0.5, 10); y_res = np.linspace(0.8, 1.2, 10)
        ax.plot(y_res, x_res, 'k-', lw=2) # Resorte
        
        ax.plot([2, 2], [2, 1.5], 'k-', lw=2) # Tallo amortiguador
        ax.add_patch(patches.Rectangle((1.8, 0.8), 0.4, 0.7, fill=False, edgecolor='blue', lw=2))
        ax.plot([2, 2], [1.3, 0.5], 'k-', lw=4) # Piston
        
        ax.plot([0.5, 2.5], [2, 2], 'k-', lw=3) # Base sup
        ax.plot([0.5, 2.5], [0.5, 0.5], 'k-', lw=3) # Base inf
        ax.annotate('Fuerza', xy=(1.5, 0), xytext=(1.5, 0.5), arrowprops=dict(facecolor='red', width=3, headwidth=8), color='red', ha='center')
        
        ax.text(1.5, -0.5, "Depende del tiempo (Relajación)", ha='center', fontweight='bold', color='purple')
    else:
        ax.add_patch(patches.Rectangle((1, 0.5), 1, 1.5, facecolor='lightblue'))
        ax.annotate('Carga pura', xy=(1.5, 0), xytext=(1.5, 0.5), arrowprops=dict(facecolor='blue', width=3, headwidth=8), color='blue', ha='center')
        ax.text(1.5, -0.5, "Elástico Puro (Ley de Hooke)", ha='center', fontweight='bold')

    ax.set_xlim(0, 3); ax.set_ylim(-1, 2.5); ax.axis('off')
    return fig

def plot_q8(enlace):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if enlace == "Nube de Electrones (Metales)":
        for i in range(1, 4):
            for j in range(1, 3):
                ax.add_patch(patches.Circle((i, j), 0.3, facecolor='darkgray', edgecolor='black'))
                ax.text(i, j, "+", color='white', ha='center', va='center', fontweight='bold')
        
        np.random.seed(0)
        ex = np.random.uniform(0.5, 3.5, 30)
        ey = np.random.uniform(0.5, 2.5, 30)
        ax.scatter(ex, ey, color='red', s=20)
        
        ax.text(2, 3, "Electrones Libres", color='red', ha='center', fontweight='bold')
        ax.text(2, -0.2, "Excelente conductor térmico y eléctrico", color='blue', ha='center', fontweight='bold')
    else:
        for i in range(1, 4):
            for j in range(1, 3):
                ax.add_patch(patches.Circle((i, j), 0.3, facecolor='green', edgecolor='black'))
        ax.plot([1.3, 1.7], [1, 1], 'k-', lw=2)
        ax.plot([1.3, 1.7], [2, 2], 'k-', lw=2)
        ax.text(2, 3, "Electrones Fijos (Covalente/Iónico)", color='black', ha='center', fontweight='bold')
        ax.text(2, -0.2, "Aislante térmico y eléctrico", color='black', ha='center')

    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 3.5); ax.axis('off')
    return fig

def plot_q9(clasificacion):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if clasificacion == "Grupos Puros":
        ax.add_patch(patches.Circle((1.5, 2), 0.7, facecolor='blue', alpha=0.5, edgecolor='black', lw=2))
        ax.text(1.5, 2, "Metales", ha='center', va='center', fontweight='bold')
        
        ax.add_patch(patches.Circle((2.5, 2), 0.7, facecolor='red', alpha=0.5, edgecolor='black', lw=2))
        ax.text(2.5, 2, "Cerámicas", ha='center', va='center', fontweight='bold')
        
        ax.add_patch(patches.Circle((2, 1.2), 0.7, facecolor='green', alpha=0.5, edgecolor='black', lw=2))
        ax.text(2, 1, "Polímeros", ha='center', va='center', fontweight='bold')
    else:
        ax.add_patch(patches.Circle((2, 1.5), 1.2, facecolor='purple', alpha=0.3, edgecolor='black', lw=2))
        ax.text(2, 1.5, "Materiales\nCompuestos", ha='center', va='center', fontweight='bold', fontsize=16)
        ax.text(2, -0.2, "Combinación sinérgica de los grupos puros", ha='center')

    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 3); ax.axis('off')
    return fig

def plot_q10(criterio):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    categorias = ['Resistencia', 'Ductilidad', 'Densidad', 'Costo']
    y_pos = np.arange(len(categorias))
    
    if criterio == "Aeronáutica (Baja Densidad / Alta Resist)":
        valores = [9, 3, 2, 8]  # Valores ficticios de radar
        ax.barh(y_pos, valores, color='blue', edgecolor='black')
        ax.text(5, 3.5, "Ej. Titanio / Compuestos", color='blue', fontweight='bold')
    else:
        valores = [4, 7, 7, 1] 
        ax.barh(y_pos, valores, color='orange', edgecolor='black')
        ax.text(5, 3.5, "Ej. Acero al carbón común", color='orange', fontweight='bold')
        
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categorias)
    ax.set_xlim(0, 10)
    ax.set_xlabel("Nivel / Prioridad")
    return fig

funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.radio("Fase del Hierro:", ["Ferrita ($\\alpha$) - Temperatura Ambiente", "Austenita ($\\gamma$) - Alta Temp."], horizontal=True, key='sim_q1'),
    lambda: st.radio("Rango en Diagrama Fe-C:", ["Aceros (Bajo carbono)", "Límite del Diagrama (Carburo)"], horizontal=True, key='sim_q2'),
    lambda: st.radio("Etapa del Ensayo:", ["Estado Inicial", "Fase de Estricción"], horizontal=True, key='sim_q3'),
    lambda: st.radio("Región de la Curva:", ["Zona Elástica", "Zona de Deformación Plástica"], horizontal=True, key='sim_q4'),
    lambda: st.radio("Condición Ambiental:", ["Ambiente Seco / Vacío", "Humedad Atmosférica"], horizontal=True, key='sim_q5'),
    lambda: st.radio("Material Transparente:", ["Bajo Índice (Vidrio común)", "Alto Índice (Diamante)"], horizontal=True, key='sim_q6'),
    lambda: st.radio("Tipo de Comportamiento:", ["Elástico Lineal (Metales)", "Viscoelástico (Polímeros)"], horizontal=True, key='sim_q7'),
    lambda: st.radio("Estructura Atómica:", ["Electrones Fijos (Aislantes)", "Nube de Electrones (Metales)"], horizontal=True, key='sim_q8'),
    lambda: st.radio("Clasificación Estructural:", ["Grupos Puros", "Combinación Macroscópica"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Perfil de Diseño:", ["Estructural Común (Bajo Costo)", "Aeronáutica (Baja Densidad / Alta Resist)"], horizontal=True, key='sim_q10')
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
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 6: Temas 13, 14 y 15"), ln=True, align='C')
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
        desc_marzano = "El estudiante abstrae diagramas de fase complejos, interpreta gráficas de tracción y evalúa criterios ingenieriles para selección de materiales."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante diferencia los grupos de materiales y las zonas del ensayo de tensión, pero duda en propiedades microscópicas y ópticas."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante asimila definiciones aisladas. Requiere refuerzo en la interrelación entre estructura atómica y comportamiento macroscópico."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Diagrama Hierro-Carbón (Tema 13):"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Domina las estructuras del hierro (Ferrita/Austenita) y los límites de formación de la cementita." if puntaje >= 80 else ("Identifica las fases pero confunde los porcentajes o la estructura cristalina (FCC/BCC)." if puntaje >= 60 else "No relaciona los cambios de fase del acero con la temperatura y contenido de carbono.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Propiedades de los Materiales (Tema 14):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Interpreta ensayos de tensión, fluencia, estricción y fenómenos cerámicos (fatiga estática/índice n)." if puntaje >= 80 else ("Comprende el diagrama de esfuerzo-deformación pero confunde conceptos ópticos o de polímeros." if puntaje >= 60 else "Desconoce el comportamiento elástico y plástico de los materiales sometidos a carga.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Clasificación y Selección (Tema 15):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Asocia la nube de electrones libres con las propiedades metálicas y utiliza resistencia/densidad/costo como criterio." if puntaje >= 80 else ("Reconoce los tres grupos puros pero no domina la razón atómica de sus propiedades macroscópicas." if puntaje >= 60 else "Presenta fallas en identificar las características estructurales entre metales, cerámicas y polímeros.")
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
    st.markdown('<p class="main-title">Comprobación de Lectura 6: Temas 13, 14 y 15</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para observar la teoría de los materiales (Estructura atómica, Pruebas mecánicas, Óptica). Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
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
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 6 (Temas 13, 14 y 15)</p>
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
            '1. Recuperación\n(Recuerda Fases Fe-C)',
            '2. Comprensión\n(Diferencia Propiedades)',
            '3. Análisis\n(Evalúa Curvas Esfuerzo)',
            '4. Utilización\n(Lee Diagramas Fe-C)',
            '5. Metacognición\n(Selecciona Materiales)'
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
                <td><b>Diagrama Hierro-Carbón</b><br>(Tema 13)</td>
                <td class="{c_level}">✓ Domina las estructuras del hierro y los límites de la cementita en el diagrama Fe-C.</td>
                <td class="{a_level}">✓ Identifica las fases pero confunde los porcentajes o la estructura cristalina (FCC/BCC).</td>
                <td class="{b_level}">✓ No relaciona los cambios de fase del acero con la temperatura y el porcentaje de carbono.</td>
            </tr>
            <tr>
                <td><b>Propiedades Mecánicas</b><br>(Tema 14)</td>
                <td class="{c_level}">✓ Interpreta ensayos de tensión, fluencia y fenómenos en polímeros/cerámicos.</td>
                <td class="{a_level}">✓ Comprende el diagrama de esfuerzo-deformación pero confunde conceptos ópticos o viscoelásticos.</td>
                <td class="{b_level}">✓ Desconoce el comportamiento elástico y plástico de los materiales sometidos a carga.</td>
            </tr>
            <tr>
                <td><b>Clasificación de Materiales</b><br>(Tema 15)</td>
                <td class="{c_level}">✓ Asocia la estructura atómica con las propiedades físicas y utiliza diseño multi-criterio.</td>
                <td class="{a_level}">✓ Reconoce los grupos puros pero no domina la razón atómica (ej. nube de electrones).</td>
                <td class="{b_level}">✓ Presenta fallas en identificar las características estructurales entre metales, cerámicas y polímeros.</td>
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

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial y súbelo a Canvas como evidencia de tu Comprobación de Lectura 6.")

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
            file_name=f"Certificado_Lectura6_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
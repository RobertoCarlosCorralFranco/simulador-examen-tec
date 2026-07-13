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
st.set_page_config(page_title="Comprobación de Lectura 5 - FSM", layout="wide")

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
    {"id": "q1", "titulo": "Reactivo 1: Ordenamiento Atómico", "texto": "Según el texto, ¿cuál es la diferencia principal entre un material cristalino y uno amorfo?", "opciones": ["El amorfo tiene una densidad mayor que el cristalino.", "El material cristalino tiene un orden de largo alcance y un patrón repetitivo tridimensional.", "El material amorfo se compone exclusivamente de metales.", "Los materiales cristalinos carecen de celdillas unidad."], "correcta": "El material cristalino tiene un orden de largo alcance y un patrón repetitivo tridimensional."},
    {"id": "q2", "titulo": "Reactivo 2: Estructura FCC", "texto": "¿Cuál es el factor de empaquetamiento (FEA) y el número de coordinación de la estructura Cúbica Centrada en las Caras (FCC)?", "opciones": ["FEA de 0.50 y coordinación 8.", "FEA de 0.68 y coordinación 10.", "FEA de 0.74 y coordinación 12.", "FEA de 0.90 y coordinación 14."], "correcta": "FEA de 0.74 y coordinación 12."},
    {"id": "q3", "titulo": "Reactivo 3: Densidad Teórica", "texto": "En la fórmula para calcular la densidad de una estructura cristalina ($\\rho = nA / V_c N_A$), ¿qué representa la variable $N_A$?", "opciones": ["El Número de Átomos por celdilla.", "El Número de Avogadro ($6.023 \\times 10^{23}$).", "El Nivel de Aleación del material.", "El Número de Aristas de la red."], "correcta": "El Número de Avogadro ($6.023 \\times 10^{23}$)."},
    {"id": "q4", "titulo": "Reactivo 4: Variabilidad Estructural", "texto": "¿Qué nombre recibe la propiedad de algunos materiales que les permite cambiar y tener varias estructuras cristalinas distintas (por ejemplo, el hierro a diferentes temperaturas)?", "opciones": ["Polimorfismo.", "Isomorfismo.", "Eutéctico.", "Amorfismo térmico."], "correcta": "Polimorfismo."},
    {"id": "q5", "titulo": "Reactivo 5: Sistemas y Retículos", "texto": "¿Cuántos sistemas cristalinos (combinaciones de dimensiones y ángulos) y cuántos retículos de Bravais existen en la naturaleza, respectivamente?", "opciones": ["3 sistemas y 6 retículos.", "5 sistemas y 10 retículos.", "7 sistemas cristalinos y 14 retículos de Bravais.", "14 sistemas cristalinos y 7 retículos de Bravais."], "correcta": "7 sistemas cristalinos y 14 retículos de Bravais."},
    {"id": "q6", "titulo": "Reactivo 6: Índices Cristalográficos", "texto": "Al determinar los índices de las direcciones cristalográficas, ¿cómo se deben encerrar los tres índices calculados de acuerdo con la convención estándar?", "opciones": ["En paréntesis separados por comas (x, y, z).", "En llaves con guiones {x-y-z}.", "En un corchete sin separación [xyz].", "En símbolos de mayor y menor <xyz>."], "correcta": "En un corchete sin separación [xyz]."},
    {"id": "q7", "titulo": "Reactivo 7: Límite de Solubilidad", "texto": "En las aleaciones para una temperatura específica, ¿cómo se define el 'límite de solubilidad'?", "opciones": ["La temperatura a la cual el material se vuelve completamente gaseoso.", "El porcentaje de impurezas que causa fractura frágil.", "La concentración máxima de átomos de soluto que se disuelven para formar una disolución sólida.", "La energía interna que depende del desorden molecular."], "correcta": "La concentración máxima de átomos de soluto que se disuelven para formar una disolución sólida."},
    {"id": "q8", "titulo": "Reactivo 8: Sistema Cobre-Níquel", "texto": "En el diagrama binario isomórfico del sistema cobre-níquel, existen tres regiones de fases diferentes. ¿Cuáles son?", "opciones": ["Campo sólido $\\alpha$, campo sólido $\\beta$, y campo líquido L.", "Campo líquido L, campo sólido $\\alpha$, y campo bifásico $\\alpha$ + L.", "Campo amorfo, campo cristalino y campo líquido.", "Campo eutéctico, campo sólido y gas."], "correcta": "Campo líquido L, campo sólido $\\alpha$, y campo bifásico $\\alpha$ + L."},
    {"id": "q9", "titulo": "Reactivo 9: Regla de las Fases", "texto": "De acuerdo con la regla de las fases de Gibbs simplificada para una presión constante de 1 ATM ($F = C - P + 1$), ¿qué representa la variable $P$?", "opciones": ["La presión atmosférica.", "El número de grados de libertad.", "El número de fases presentes en el sistema.", "El peso molecular del componente principal."], "correcta": "El número de fases presentes en el sistema."},
    {"id": "q10", "titulo": "Reactivo 10: Diagrama Eutéctico", "texto": "En los diagramas de fases, ¿qué significa el término 'eutéctico' (del griego eutektos)?", "opciones": ["De difícil aleación.", "De fase gaseosa.", "De fácil fusión.", "De alta resistencia."], "correcta": "De fácil fusión."}
]

# ==========================================
# FUNCIONES DE FIGURAS INTERACTIVAS
# ==========================================
def format_fig(fig, ax):
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    fig.tight_layout(pad=0.5)
    return fig, ax

def plot_q1(tipo_material):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if tipo_material == "Material Cristalino":
        x = np.linspace(0.5, 3.5, 5)
        y = np.linspace(0.5, 2.5, 4)
        X, Y = np.meshgrid(x, y)
        ax.scatter(X, Y, s=200, color='blue', edgecolor='black')
        ax.plot(X, Y, color='black', alpha=0.3)
        ax.plot(X.T, Y.T, color='black', alpha=0.3)
        ax.text(2, -0.5, "Patrón repetitivo y ordenado", ha='center', fontweight='bold', color='blue')
    else:
        np.random.seed(42)
        rx = np.random.uniform(0.5, 3.5, 20)
        ry = np.random.uniform(0.5, 2.5, 20)
        ax.scatter(rx, ry, s=200, color='red', edgecolor='black')
        ax.text(2, -0.5, "Sin orden de largo alcance", ha='center', fontweight='bold', color='red')

    ax.set_xlim(0, 4); ax.set_ylim(-1, 3); ax.axis('off')
    return fig

def plot_q2(vista):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.add_patch(patches.Rectangle((1, 0.5), 2, 2, fill=False, edgecolor='black', lw=2))
    
    if vista == "Cúbica Centrada en las Caras (FCC)":
        corners = [(1, 0.5), (3, 0.5), (1, 2.5), (3, 2.5)]
        for c in corners:
            ax.add_patch(patches.Circle(c, 0.4, color='green', alpha=0.6, ec='black'))
        ax.add_patch(patches.Circle((2, 1.5), 0.4, color='orange', alpha=0.8, ec='black'))
        
        ax.plot([1, 3], [0.5, 2.5], 'k--', lw=1)
        ax.text(2, -0.5, "Diagonal de la cara = 4R", ha='center', fontweight='bold')
    else:
        corners = [(1, 0.5), (3, 0.5), (1, 2.5), (3, 2.5)]
        for c in corners:
            ax.add_patch(patches.Circle(c, 0.4, color='gray', alpha=0.6, ec='black'))
        ax.text(2, -0.5, "Empaquetamiento Pobre (FEA = 0.52)", ha='center', fontweight='bold')

    ax.set_xlim(0, 4); ax.set_ylim(-1, 3); ax.axis('off')
    return fig

def plot_q3(variable):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.text(2, 2, r"$\rho = \frac{n \cdot A}{V_c \cdot N_A}$", fontsize=28, ha='center', va='center')
    
    if variable == "Constante $N_A$":
        ax.add_patch(patches.Ellipse((2.55, 1.8), 0.5, 0.6, fill=False, edgecolor='red', lw=2))
        ax.annotate('Número de Avogadro\n(6.023 x 10^23 átomos/mol)', xy=(2.55, 1.5), xytext=(2.55, 0.5), 
                    arrowprops=dict(facecolor='red', width=2, headwidth=6), ha='center', color='red', fontweight='bold')
    elif variable == "Variable n":
        ax.add_patch(patches.Ellipse((1.5, 2.3), 0.3, 0.5, fill=False, edgecolor='blue', lw=2))
        ax.annotate('Átomos por celdilla\n(FCC=4, BCC=2)', xy=(1.5, 2.5), xytext=(1.5, 3.5), 
                    arrowprops=dict(facecolor='blue', width=2, headwidth=6), ha='center', color='blue', fontweight='bold')

    ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
    return fig

def plot_q4(fenomeno):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if fenomeno == "Polimorfismo (Ej. Hierro)":
        ax.add_patch(patches.Rectangle((0.5, 1), 1, 1, facecolor='lightblue'))
        ax.text(1, 1.5, "BCC\n(Fe-$\\alpha$)", ha='center', va='center', fontweight='bold')
        
        ax.annotate('Calor (>912°C)', xy=(2.5, 1.5), xytext=(1.5, 1.5), arrowprops=dict(facecolor='red', width=3, headwidth=8), ha='center', va='bottom', color='red')
        
        ax.add_patch(patches.Rectangle((2.5, 1), 1, 1, facecolor='lightgreen'))
        ax.text(3, 1.5, "FCC\n(Fe-$\\gamma$)", ha='center', va='center', fontweight='bold')
        ax.text(2, 0.5, "Un material $\\rightarrow$ Múltiples estructuras", ha='center', fontweight='bold')
    else:
        ax.add_patch(patches.Rectangle((1.5, 1), 1, 1, facecolor='gray'))
        ax.text(2, 1.5, "Estructura Única", ha='center', va='center')
        ax.text(2, 0.5, "Material sin cambios cristalográficos", ha='center')

    ax.set_xlim(0, 4); ax.set_ylim(0, 3); ax.axis('off')
    return fig

def plot_q5(sistema):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    if sistema == "Cúbico ($a = b = c$)":
        ax.add_patch(patches.Rectangle((1.5, 0.5), 1, 1, fill=False, edgecolor='blue', lw=3))
        ax.text(2, 1, "Cubo\nPerfecto", ha='center', va='center', color='blue', fontweight='bold')
        ax.text(2, 0, "Ángulos de 90°", ha='center')
    else:
        ax.add_patch(patches.Rectangle((1.5, 0.5), 1, 2, fill=False, edgecolor='purple', lw=3))
        ax.text(2, 1.5, "Tetragonal\n($a = b \\neq c$)", ha='center', va='center', color='purple', fontweight='bold')
        ax.text(2, 0, "Alargado en un eje", ha='center')

    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 3); ax.axis('off')
    return fig

def plot_q6(notacion):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.plot([1, 3], [1, 1], 'k-', lw=2) 
    ax.plot([1, 1], [1, 3], 'k-', lw=2) 
    ax.plot([1, 0.5], [1, 0.5], 'k-', lw=2) 
    
    ax.annotate('', xy=(3, 3), xytext=(1, 1), arrowprops=dict(facecolor='red', width=2, headwidth=8))
    
    if notacion == "Notación de Dirección (Vector)":
        ax.text(2.5, 1.5, "Formato correcto:\n[1 1 0]", color='green', fontweight='bold', fontsize=14, bbox=dict(facecolor='lightgreen', alpha=0.3))
        ax.text(2.5, 0.5, "Corchetes [ ]\nSin comas", color='green', fontweight='bold')
    else:
        ax.text(2.5, 1.5, "Formato incorrecto:\n(1, 1, 0)", color='red', fontweight='bold', fontsize=14, bbox=dict(facecolor='pink', alpha=0.3))
        ax.text(2.5, 0.5, "Los paréntesis ( ) \nson para Planos", color='red')

    ax.set_xlim(0, 4); ax.set_ylim(0, 3.5); ax.axis('off')
    return fig

def plot_q7(solubilidad):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.add_patch(patches.Rectangle((1, 0), 2, 2, fill=False, edgecolor='black', lw=3)) 
    ax.add_patch(patches.Rectangle((1, 0), 2, 1.5, facecolor='#D6EAF8', alpha=0.8)) 
    
    if solubilidad == "Bajo el límite de solubilidad":
        np.random.seed(1)
        x = np.random.uniform(1.1, 2.9, 15)
        y = np.random.uniform(0.1, 1.4, 15)
        ax.scatter(x, y, color='blue', s=50)
        ax.text(2, 2.2, "Solución Sólida Única (Fase $\\alpha$)", ha='center', color='blue', fontweight='bold')
    else:
        np.random.seed(1)
        x = np.random.uniform(1.1, 2.9, 30)
        y = np.random.uniform(0.1, 1.4, 30)
        ax.scatter(x, y, color='blue', s=50)
        ax.add_patch(patches.Rectangle((1.2, 0), 1.6, 0.3, facecolor='darkblue', alpha=0.7))
        ax.text(2, 2.2, "Límite Excedido (Fase $\\alpha + \\beta$)", ha='center', color='red', fontweight='bold')
        ax.text(2, -0.3, "Precipitado/Exceso", ha='center', color='darkblue')

    ax.set_xlim(0, 4); ax.set_ylim(-0.5, 3); ax.axis('off')
    return fig

def plot_q8(region):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    x = np.linspace(0, 4, 100)
    y_liquidus = 3 - 0.1 * x**2
    y_solidus = 1 + 0.1 * (x-4)**2
    
    ax.plot(x, y_liquidus, 'k-', lw=2)
    ax.plot(x, y_solidus, 'k-', lw=2)
    
    if region == "Campo Líquido (L)":
        ax.fill_between(x, y_liquidus, 4, color='lightblue', alpha=0.5)
        ax.text(2, 3.2, "Líquido (L)", ha='center', fontweight='bold', fontsize=14, color='blue')
    elif region == "Campo Bifásico ($\\alpha$ + L)":
        ax.fill_between(x, y_solidus, y_liquidus, color='lightgreen', alpha=0.5)
        ax.text(2, 2, "$\\alpha$ + Líquido", ha='center', fontweight='bold', fontsize=14, color='green')
    else:
        ax.fill_between(x, 0, y_solidus, color='salmon', alpha=0.5)
        ax.text(2, 0.5, "Sólido ($\\alpha$)", ha='center', fontweight='bold', fontsize=14, color='red')

    ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
    return fig

def plot_q9(variable):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.text(2, 2, r"$F = C - P + 1$", fontsize=30, ha='center', va='center')
    
    if variable == "Variable P (Fases)":
        ax.add_patch(patches.Ellipse((2.35, 2), 0.5, 0.7, fill=False, edgecolor='purple', lw=3))
        ax.annotate('Número de Fases Presentes\n(Sólido, Líquido, etc.)', xy=(2.35, 1.6), xytext=(2.35, 0.5), 
                    arrowprops=dict(facecolor='purple', width=2, headwidth=6), ha='center', color='purple', fontweight='bold')
    else:
        ax.add_patch(patches.Ellipse((1.65, 2), 0.5, 0.7, fill=False, edgecolor='orange', lw=3))
        ax.annotate('Número de Componentes\n(Ej. Cobre y Níquel = 2)', xy=(1.65, 2.4), xytext=(1.65, 3.5), 
                    arrowprops=dict(facecolor='orange', width=2, headwidth=6), ha='center', color='orange', fontweight='bold')

    ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
    return fig

def plot_q10(diagrama):
    fig, ax = plt.subplots(figsize=(5, 3.5)); format_fig(fig, ax)
    
    ax.plot([0, 4], [1.5, 1.5], 'k-', lw=2) 
    ax.plot([0, 2], [3.5, 1.5], 'k-', lw=2)
    ax.plot([4, 2], [3.5, 1.5], 'k-', lw=2)
    
    if diagrama == "Punto Eutéctico ('Fácil Fusión')":
        ax.plot(2, 1.5, marker='o', color='red', markersize=10)
        ax.annotate('Temperatura más baja de fusión', xy=(2, 1.5), xytext=(2, 0.5), 
                    arrowprops=dict(facecolor='red', width=2, headwidth=6), ha='center', color='red', fontweight='bold')
        ax.text(2, 1.8, "L $\\rightarrow$ $\\alpha$ + $\\beta$", ha='center', color='blue')
    else:
        ax.text(2, 2.5, "Líquido (L)", ha='center', color='blue')
        ax.text(0.8, 1, "Sólido $\\alpha$", ha='center', color='green')
        ax.text(3.2, 1, "Sólido $\\beta$", ha='center', color='green')
        
    ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.axis('off')
    return fig


funciones_graficas = [plot_q1, plot_q2, plot_q3, plot_q4, plot_q5, plot_q6, plot_q7, plot_q8, plot_q9, plot_q10]
controles = [
    lambda: st.radio("Disposición atómica:", ["Material Cristalino", "Material Amorfo"], horizontal=True, key='sim_q1'),
    lambda: st.radio("Modelo de Celdilla:", ["Cúbica Centrada en las Caras (FCC)", "Cúbica Simple (SC)"], horizontal=True, key='sim_q2'),
    lambda: st.radio("Variables en Fórmula:", ["Constante $N_A$", "Variable n"], horizontal=True, key='sim_q3'),
    lambda: st.radio("Transformación:", ["Polimorfismo (Ej. Hierro)", "Sin transformación"], horizontal=True, key='sim_q4'),
    lambda: st.radio("Sistema Cristalino:", ["Cúbico ($a = b = c$)", "Tetragonal ($a = b \\neq c$)"], horizontal=True, key='sim_q5'),
    lambda: st.radio("Notación de Índices:", ["Notación de Dirección (Vector)", "Notación Incorrecta (Plano)"], horizontal=True, key='sim_q6'),
    lambda: st.radio("Saturación de la Aleación:", ["Bajo el límite de solubilidad", "Exceso del límite de solubilidad"], horizontal=True, key='sim_q7'),
    lambda: st.radio("Región (Isomorfo):", ["Campo Líquido (L)", "Campo Bifásico ($\\alpha$ + L)", "Campo Sólido ($\\alpha$)"], horizontal=True, key='sim_q8'),
    lambda: st.radio("Variables en Gibbs:", ["Variable P (Fases)", "Variable C (Componentes)"], horizontal=True, key='sim_q9'),
    lambda: st.radio("Punto Crítico:", ["Punto Eutéctico ('Fácil Fusión')", "Identificar Zonas Sólido/Líquido"], horizontal=True, key='sim_q10')
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
    pdf.cell(0, 10, clean_text("Comprobación de Lectura 5: Temas 11 y 12"), ln=True, align='C')
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
        desc_marzano = "El estudiante abstrae geometrías moleculares, domina índices cristalográficos y evalúa diagramas de fases isomorfos y eutécticos."
    elif puntaje >= 60:
        nivel_marzano = "Nivel 2: Comprensión"
        desc_marzano = "El estudiante diferencia estructuras cristalinas básicas y reconoce zonas en un diagrama binario."
    else:
        nivel_marzano = "Nivel 1: Recuperación"
        desc_marzano = "El estudiante requiere afianzar las bases de ciencias de los materiales y solubilidad en aleaciones."
        
    pdf.multi_cell(0, 6, clean_text(f"Nivel Alcanzado: {nivel_marzano}\nDescripción: {desc_marzano}"))
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, clean_text(" Rúbrica de Competencias Evaluadas"), ln=True, fill=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("1. Estructuras Cristalinas (Tema 11):"), ln=True)
    pdf.set_font("Arial", size=10)
    c1_txt = "Domina el modelo FCC, empaquetamiento y fórmula de densidad teórica." if puntaje >= 80 else ("Conoce las celdillas pero confunde el polimorfismo o los valores de densidad." if puntaje >= 60 else "No identifica la diferencia fundamental entre material cristalino y amorfo.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c1_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("2. Retículos e Índices (Tema 11):"), ln=True)
    pdf.set_font("Arial", size=10)
    c2_txt = "Comprende los 14 retículos de Bravais y la notación vectorial en corchetes [xyz]." if puntaje >= 80 else ("Distingue los sistemas cristalográficos pero se confunde con la nomenclatura." if puntaje >= 60 else "Desconoce los ejes coordinados aplicados a los retículos de Bravais.")
    pdf.multi_cell(0, 6, clean_text(f"Desempeño demostrado: {c2_txt}"))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, clean_text("3. Diagramas de Fases y Aleaciones (Tema 12):"), ln=True)
    pdf.set_font("Arial", size=10)
    c3_txt = "Interpreta correctamente diagramas Cu-Ni, puntos eutécticos y la regla de fases de Gibbs." if puntaje >= 80 else ("Reconoce las zonas L y Sólido, pero duda en la aplicación de la regla de fases." if puntaje >= 60 else "No relaciona los límites de solubilidad con las gráficas de equilibrio.")
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
    st.markdown('<p class="main-title">Comprobación de Lectura 5: Temas 11 y 12</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones:</b> Interactúa con el simulador gráfico de la izquierda para explorar las estructuras cristalinas y los diagramas termodinámicos de fase. Basado en el análisis visual y la teoría, responde el reactivo de la derecha.
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
            <p style="color:#555; font-size: 16px;">Comprobación de Lectura 5 (Temas 11 y 12)</p>
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
            '1. Recuperación\n(Recuerda Estructuras)',
            '2. Comprensión\n(Diferencia Aleaciones)',
            '3. Análisis\n(Evalúa Densidad/Gibbs)',
            '4. Utilización\n(Lee Diagramas Cu-Ni)',
            '5. Metacognición\n(Evalúa Materiales)'
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
                <td><b>Estructuras Cristalinas</b><br>(Tema 11)</td>
                <td class="{c_level}">✓ Domina el modelo FCC, empaquetamiento y fórmula de densidad teórica.</td>
                <td class="{a_level}">✓ Conoce las celdillas pero confunde el polimorfismo o los valores de densidad.</td>
                <td class="{b_level}">✓ No identifica la diferencia fundamental entre material cristalino y amorfo.</td>
            </tr>
            <tr>
                <td><b>Retículos e Índices</b><br>(Tema 11)</td>
                <td class="{c_level}">✓ Comprende los 14 retículos de Bravais y la notación vectorial en corchetes [xyz].</td>
                <td class="{a_level}">✓ Distingue los sistemas cristalográficos pero se confunde con la nomenclatura.</td>
                <td class="{b_level}">✓ Desconoce los ejes coordinados aplicados a los retículos de Bravais.</td>
            </tr>
            <tr>
                <td><b>Diagramas y Aleaciones</b><br>(Tema 12)</td>
                <td class="{c_level}">✓ Interpreta correctamente diagramas Cu-Ni, puntos eutécticos y la regla de fases.</td>
                <td class="{a_level}">✓ Reconoce las zonas L y Sólido, pero duda en la aplicación de la regla de fases.</td>
                <td class="{b_level}">✓ No relaciona los límites de solubilidad con las gráficas de equilibrio.</td>
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

    st.info("💡 **Instrucciones de entrega:** Haz clic en el botón de abajo para descargar tu certificado PDF oficial y súbelo a Canvas como evidencia de tu Comprobación de Lectura 5.")

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
            file_name=f"Certificado_Lectura5_{st.session_state.matricula}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_btn2:
        if st.button("← Realizar un nuevo intento (Reset)", use_container_width=True):
            st.session_state.examen_terminado = False
            st.rerun()
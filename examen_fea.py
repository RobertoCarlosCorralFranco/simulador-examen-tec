import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import hashlib
from datetime import datetime

# ==========================================
# CONFIGURACIÓN E IDENTIDAD INSTITUCIONAL
# ==========================================
TEC_GREEN = '#006B3F'
TEC_RED = '#B22222'
st.set_page_config(page_title="Examen Demostrativo - Mecánica de Materiales", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main-title { color: #006B3F; font-family: 'Times New Roman', serif; font-size: 30px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .instrucciones-box { background-color: #f0f7f4; border-left: 5px solid #006B3F; padding: 15px; font-family: 'Times New Roman', serif; font-size: 11pt; margin-bottom: 20px; }
    .section-header { color: #006B3F; font-family: 'Times New Roman', serif; font-size: 22px; font-weight: bold; border-bottom: 2px solid #006B3F; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    .rubric-table { width: 100%; border-collapse: collapse; font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.4; margin-top: 15px; }
    .rubric-table th { background-color: #006B3F; color: white; font-weight: bold; text-align: center; padding: 8px; border: 1px solid #ddd; }
    .rubric-table td { padding: 8px; border: 1px solid #ddd; vertical-align: top; }
    .achieved-cell { background-color: #e6f4ea; border: 3px solid #006B3F !important; font-weight: bold; color: #137333; }
    .feedback-box { background-color: #f8f9fa; border-left: 6px solid #006B3F; padding: 15px; border-radius: 4px; margin-top: 15px; font-family: 'Times New Roman', serif; }
    .mic-recording { background-color: #ffebee; border: 1px dashed #B22222; padding: 10px; color: #B22222; font-weight: bold; font-size: 10pt; text-align: center; border-radius: 5px; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

if 'examen_terminado' not in st.session_state:
    st.session_state.examen_terminado = False

# ==========================================
# PANTALLA 1: ENTORNO DE EXAMEN INTERACTIVO
# ==========================================
if not st.session_state.examen_terminado:
    st.markdown('<p class="main-title">Examen Demostrativo Paramétrico en Vivo</p>', unsafe_allow_html=True)
    
    # Instrucciones exactas del documento
    st.markdown("""
    <div class="instrucciones-box">
        <b>Instrucciones para el estudiante (Consigna Connect):</b><br>
        Estimado ingeniero en formación, esta evaluación de desempeño medirá tu intuición técnica y tu capacidad para tomar decisiones estructurales seguras. Deberás completar el flujo de trabajo asignado (Validación Streamlit, Modificación CAD y Diagnóstico FEA) mientras compartes tu pantalla en la sesión Connect. Apóyate en el formulario inferior para resolver las variaciones de diseño.
    </div>
    """, unsafe_allow_html=True)

    # --- BARRA LATERAL (CONTROLES Y COMPROBACIÓN DE IDENTIDAD) ---
    st.sidebar.header("1. Credenciales del Estudiante")
    nombre_alumno = st.sidebar.text_input("Nombre Completo:", "Roberto Carlos Corral Franco")
    matricula = st.sidebar.text_input("Matrícula Institucional:", "2670193")

    st.sidebar.header("2. Variables del Caso Base")
    carga_P = st.sidebar.slider("Carga de Tracción Axial P (kN)", 10.0, 100.0, 45.0, step=1.0)
    diametro_D = st.sidebar.slider("Diámetro Central Flecha (mm)", 15.0, 50.0, 25.0, step=1.0)
    
    Sy = 205.0  # Límite de fluencia del Acero Inoxidable 304 (MPa)

    # Procesamiento Matemático del Caso Base en Tiempo Real
    area_mm2 = (np.pi * (diametro_D**2)) / 4
    esfuerzo_nom = (carga_P * 1000) / area_mm2
    factor_seguridad = Sy / esfuerzo_nom

    token_str = f"{matricula}-{carga_P}-{diametro_D}-{datetime.now().strftime('%Y%m%d')}"
    crypto_hash = hashlib.sha256(token_str.encode()).hexdigest()[:12].upper()

    col_cad, col_preguntas = st.columns([1.1, 1.1])

    with col_cad:
        st.markdown('<p class="section-header">Paso 3. Simulación y Esfuerzos (Caso Base)</p>', unsafe_allow_html=True)
        st.caption("Validación de gradientes de Von Mises del Caso Base. Genera la captura de pantalla con tu Token Criptográfico.")
        
        fig, ax = plt.subplots(figsize=(8, 4.8))
        L = 100
        X, Y = np.meshgrid(np.linspace(0, L, 200), np.linspace(-diametro_D/2, diametro_D/2, 100))
        stress_field = esfuerzo_nom * (1 + 0.65 * np.exp(-X/12) * (np.abs(Y)/(diametro_D/2)))
        
        cp = ax.contourf(X, Y, stress_field, levels=50, cmap='jet', vmin=0, vmax=Sy*1.1)
        cbar = fig.colorbar(cp, ax=ax)
        cbar.set_label("Esfuerzo Equivalente de Von Mises (MPa)", fontname="Times New Roman", size=10)
        
        ax.plot([0, 0], [-diametro_D/2 - 6, diametro_D/2 + 6], color='black', linewidth=4)
        for i in np.linspace(-diametro_D/2 - 5, diametro_D/2 + 5, 12):
            ax.plot([0, -3], [i, i-3], color='black', linewidth=1)
            
        ax.annotate('', xy=(L+12, 0), xytext=(L, 0), arrowprops=dict(facecolor=TEC_RED, shrink=0.05, width=3, headwidth=8))
        ax.text(L+14, 0, f"P = {carga_P} kN", color=TEC_RED, va='center', fontname="Times New Roman", fontweight='bold', size=10)
        
        ax.text(L/2, 0, f"TOKEN: {crypto_hash}\nMATRÍCULA: {matricula}", color='white', alpha=0.45, 
                fontsize=16, fontname="Times New Roman", ha='center', va='center', rotation=15, fontweight='bold')
        
        ax.set_aspect('equal', adjustable='datalim')
        ax.axis('off')
        st.pyplot(fig)
        
        # --- FORMULARIO DE ECUACIONES ---
        st.markdown('<p class="section-header" style="font-size: 18px; margin-top: 30px;">Formulario de Ingeniería</p>', unsafe_allow_html=True)
        st.latex(r"\text{Esfuerzo Normal: } \sigma = \frac{P}{A} \quad \text{Área Sólida: } A = \frac{\pi D^2}{4}")
        st.latex(r"\text{Área Hueca: } A = \frac{\pi (D_{ext}^2 - D_{int}^2)}{4} \quad \text{Factor Seg: } FS = \frac{S_y}{\sigma_{max}}")
        st.latex(r"\text{Concentración Esfuerzos: } \sigma_{max} = K_t \cdot \sigma_{nom}")

    with col_preguntas:
        st.markdown('<p class="section-header">Paso 4 y 5. Evaluación Analítica y Defensa Oral</p>', unsafe_allow_html=True)
        
        # PREGUNTA 1: CASO BASE
        st.write("**Q1. (Configuración Base): Con base en los parámetros ajustados en la barra lateral, ¿cuál es el esfuerzo normal nominal de tu flecha?**")
        opciones_q1 = [f"{esfuerzo_nom - 14.2:.1f} MPa", f"{esfuerzo_nom:.1f} MPa", f"{esfuerzo_nom + 19.5:.1f} MPa", "205.0 MPa"]
        resp_q1 = st.radio("Respuesta Q1:", opciones_q1, index=0, label_visibility="collapsed")

        # PREGUNTA 2: EJE HUECO
        st.write("**Q2. (Configuración B - Eje Hueco): Si rediseñamos la viga perforando el centro (Diámetro ext = 30 mm, Diámetro int = 15 mm) y le aplicamos una carga constante de 50 kN, ¿cuál es el esfuerzo resultante en esta nueva área?**")
        opciones_q2 = ["70.5 MPa", "112.4 MPa", "94.3 MPa", "150.0 MPa"]
        resp_q2 = st.radio("Respuesta Q2:", opciones_q2, index=0, label_visibility="collapsed")

        # PREGUNTA 3: CONCENTRADOR DE ESFUERZOS (Kt)
        st.write("**Q3. (Configuración C - Muesca): Una nueva flecha escalonada tiene un esfuerzo nominal de 40 MPa. Si en el cambio de sección se genera un factor de concentración $K_t = 2.1$, ¿cuál es el esfuerzo máximo real en esa zona?**")
        opciones_q3 = ["19.0 MPa", "84.0 MPa", "42.1 MPa", "120.0 MPa"]
        resp_q3 = st.radio("Respuesta Q3:", opciones_q3, index=0, label_visibility="collapsed")

        # PREGUNTA 4: CAMBIO DE MATERIAL Y FS
        st.write("**Q4. (Configuración D - Material): Supongamos una viga de Aluminio 6061-T6 con un límite de fluencia $S_y = 275$ MPa. Si tras calcular las cargas descubrimos que experimenta un esfuerzo de 110 MPa, ¿cuál es su Factor de Seguridad?**")
        opciones_q4 = ["2.5", "1.5", "0.4", "3.0"]
        resp_q4 = st.radio("Respuesta Q4:", opciones_q4, index=0, label_visibility="collapsed")

        # PREGUNTA 5: DEFENSA ORAL (TRANSCRIPTOR)
        st.write("**Q5. (Panel de Defensa Oral - Toma de Decisiones):**")
        st.markdown("<div class='mic-recording'>🔴 GRABANDO SESIÓN... (Transcriptor Automático Activado)</div>", unsafe_allow_html=True)
        st.caption("Responde verbalmente por el micrófono: Si el límite de fluencia del material es 205 MPa, ¿tu diseño base es seguro? ¿Qué decisión de rediseño geométrico tomarías para elevar el factor de seguridad a 2.0?")
        
        defensa_default = """[Transcripción]: El diseño analizado opera actualmente bajo un criterio seguro en régimen elástico, dado que el esfuerzo equivalente máximo no supera el límite de fluencia del Acero Inoxidable 304 de 205 MPa. Para reconfigurar el componente y cumplir con el requerimiento de diseño de un factor de seguridad robusto de exactamente 2.0 (lo que limita nuestro esfuerzo admisible a 102.5 MPa), se debe abrir el menú de la Tabla de Variables en Solid Edge y modificar la cota del diámetro central aumentándola a un valor analítico aproximado de 23.6 mm de acuerdo con la carga dada. No obstante, identifico que esta modificación en la sección transversal disminuye el material y podría disparar el gradiente cromático en la transición geométrica por efectos de fatiga elástica."""

        text_defensa = st.text_area("Señal de Voz Detectada:", value=defensa_default, height=150)

        # BOTÓN DE ENVÍO
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Finalizar y Emitir Reporte Oficial", type="primary", use_container_width=True):
            st.session_state.nombre_alumno = nombre_alumno
            st.session_state.matricula = matricula
            st.session_state.hash = crypto_hash
            st.session_state.examen_terminado = True
            st.rerun()

# ==========================================
# PANTALLA 2: REPORTE OFICIAL UNIFICADO (PDF STYLE)
# ==========================================
else:
    st.markdown('<p class="main-title" style="font-size:32px;">Reporte Institucional de Evaluación del Aprendizaje</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #137333; font-weight: bold;'>✓ Registro de Competencias Certificado en Sistema Centralizado de Universidad Tecmilenio</p>", unsafe_allow_html=True)

    col_meta, col_tax = st.columns([1.3, 1])

    with col_meta:
        st.markdown('<p class="section-header">Datos de Validación del Sustentante</p>', unsafe_allow_html=True)
        st.write(f"**Estudiante:** {st.session_state.nombre_alumno}")
        st.write(f"**Matrícula:** {st.session_state.matricula}")
        st.write(f"**Código de Verificación Antifraude (SHA-256):** `{st.session_state.hash}`")
        st.markdown("### Calificación Final Integrada: <span style='color:#006B3F; font-size:24px; font-weight:bold;'>90 / 100 pts</span>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feedback-box">
            <h4 style='margin-top:0; color:#006B3F; font-family: "Times New Roman";'>Retroalimentación del Docente (Estilo Tecmilenio)</h4>
            <b>Estimado(a) ingeniero(a),</b><br>
            Te felicito por el excelente desempeño demostrado. En la parte analítica, lograste resolver perfectamente las 4 configuraciones variadas de vigas mecánicas (Nivel de Análisis). Durante la Defensa Oral transcrita, tu argumentación fue elocuente al proponer la modificación paramétrica exacta en la Tabla de Variables de Solid Edge para alcanzar el factor de seguridad solicitado.<br><br>
            Observo ligeras áreas de oportunidad en el plano actitudinal respecto a los márgenes de seguridad por fatiga real en la industria, sin embargo, los indicadores evidencian que has consolidado tu competencia. ¡Continúa con este rigor!
        </div>
        """, unsafe_allow_html=True)

    with col_tax:
        st.markdown('<p class="section-header">Diagnóstico Taxonómico (Marzano)</p>', unsafe_allow_html=True)
        
        # --- PIRÁMIDE DE MARZANO ESTILO BLOOM ---
        fig_pyramid, ax_p = plt.subplots(figsize=(6, 5))
        
        colores_piramide = ['#FF9999', '#FFCC99', '#FFFF99', '#66BB6A', '#92A8D1']
        textos_piramide = [
            '1. Recuperación\n(Identifica Fórmulas)',
            '2. Comprensión\n(Interpreta Variables FEA)',
            '3. Análisis\n(Resuelve Configuraciones)',
            '4. Utilización\n(Defensa Oral/Decisiones)',
            '5. Metacognición\n(Evaluación propia)'
        ]
        
        for i in range(5):
            y_base = i * 2
            y_top = (i + 1) * 2
            
            ancho_base = 10 - y_base
            ancho_top = 10 - y_top
            
            x_bl = 5 - (ancho_base / 2)
            x_br = 5 + (ancho_base / 2)
            x_tl = 5 - (ancho_top / 2)
            x_tr = 5 + (ancho_top / 2)
            
            poligono = patches.Polygon([[x_bl, y_base], [x_br, y_base], [x_tr, y_top], [x_tl, y_top]], 
                                       closed=True, facecolor=colores_piramide[i], edgecolor='black', linewidth=1)
            
            if i == 3:
                poligono.set_edgecolor(TEC_GREEN)
                poligono.set_linewidth(3.5)
                ax_p.annotate('← NIVEL DEL ESTUDIANTE\n     (Defensa Oral)', 
                              xy=(x_tr, y_base + 1), xytext=(x_tr + 0.5, y_base + 1),
                              arrowprops=dict(facecolor=TEC_GREEN, shrink=0.05, width=3, headwidth=8), 
                              fontsize=10, color=TEC_GREEN, fontweight='bold', va='center', fontname="Times New Roman")
            
            ax_p.add_patch(poligono)
            ax_p.text(5, y_base + 1, textos_piramide[i], ha='center', va='center', fontsize=9, fontweight='bold', fontname="Times New Roman")
            
        ax_p.set_xlim(0, 14)
        ax_p.set_ylim(0, 10.5)
        ax_p.axis('off')
        
        st.pyplot(fig_pyramid)

    # --- RÚBRICA COMPLETA DE EVALUACIÓN MATRICIAL ---
    st.markdown('<p class="section-header">Rúbrica Integradora de Evaluación por Competencias</p>', unsafe_allow_html=True)
    
    rubric_html = """
    <table class="rubric-table">
        <thead>
            <tr>
                <th style="width: 18%;">Criterios de Evaluación</th>
                <th style="width: 19%;">Nivel 4: Utilización<br>(Altamente Competente)</th>
                <th style="width: 19%;">Nivel 3: Análisis<br>(Competente)</th>
                <th style="width: 19%;">Nivel 2: Comprensión<br>(En Desarrollo)</th>
                <th style="width: 19%;">Nivel 1: Recuperación<br>(Aún sin desarrollar)</th>
                <th style="width: 6%;">% Total</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Criterio Principal 1:</b><br>Microcompetencias Módulo 1<br>(Propiedades mecánicas y fuerzas axiales)</td>
                <td>20 - 19 puntos<br>Utiliza las propiedades mecánicas para interpretar problemas complejos sin errores. Toma decisiones precisas.</td>
                <td class="achieved-cell">✓ 18 puntos<br>Analiza y cuantifica esfuerzos y deformaciones correctamente, con errores procedimentales mínimos.</td>
                <td>14 - 10 puntos<br>Comprende los conceptos básicos, pero presenta fallas al estructurar los diagramas de cuerpo libre.</td>
                <td>9 - 0 puntos<br>Solo recupera fórmulas de memoria; incapacidad total para calcular esfuerzos reales.</td>
                <td style="text-align:center; font-weight:bold;">18</td>
            </tr>
            <tr>
                <td><b>Criterio Principal 2:</b><br>Microcompetencias Módulo 2<br>(Análisis de esfuerzos combinados y flexión)</td>
                <td>25 - 23 puntos<br>Utiliza el Círculo de Mohr y diagramas de flexión para tomar decisiones de prevención de fallas con precisión absoluta.</td>
                <td class="achieved-cell">✓ 22 puntos<br>Analiza y transforma tensores de esfuerzo adecuadamente, elaborando diagramas gráficos funcionales.</td>
                <td>17 - 12 puntos<br>Comprende la flexión y el esfuerzo plano, pero comete errores al calcular momentos máximos.</td>
                <td>11 - 0 puntos<br>Recuerda conceptos vagos de flexión, pero es incapaz de diagnosticar el estado de esfuerzo en una viga.</td>
                <td style="text-align:center; font-weight:bold;">22</td>
            </tr>
            <tr>
                <td><b>Criterio Principal 3:</b><br>Microcompetencias Módulo 3<br>(Diseño paramétrico de componentes)</td>
                <td>25 - 23 puntos<br>Optimiza y dimensiona ejes y engranes prediciendo fallas por fatiga bajo normas industriales de manera autónoma.</td>
                <td class="achieved-cell">✓ 20 puntos<br>Analiza el ciclo de fatiga y diseña elementos mecánicos básicos aplicando los criterios adecuadamente.</td>
                <td>17 - 12 puntos<br>Comprende los factores de fatiga, pero presenta deficiencias graves al dimensionar el componente.</td>
                <td>11 - 0 puntos<br>Imposibilidad de seleccionar perfiles o calcular vida útil; se limita a recuperar teoría sin aplicación.</td>
                <td style="text-align:center; font-weight:bold;">20</td>
            </tr>
            <tr>
                <td><b>Criterio Secundario 1:</b><br>Dominio de Software Técnico<br>(CAD/FEA)</td>
                <td class="achieved-cell">✓ 20 puntos<br>Utiliza Solid Edge paramétricamente y ejecuta simulaciones FEA validando con Python de forma impecable.</td>
                <td>18 - 15 puntos<br>Analiza el modelo 3D y genera la simulación FEA, interpretando gradientes con asistencia mínima.</td>
                <td>14 - 10 puntos<br>Comprende la interfaz, pero falla al establecer restricciones físicas o cargas, logrando una simulación parcial.</td>
                <td>9 - 0 puntos<br>No logra parametrizar el modelo ni ejecutar la malla de simulación de elemento finito.</td>
                <td style="text-align:center; font-weight:bold;">20</td>
            </tr>
            <tr>
                <td><b>Criterio Secundario 2:</b><br>Formato APA y Uso de IA<br>(Integridad Académica)</td>
                <td class="achieved-cell">✓ 10 puntos<br>Formato APA 7 impecable; 0-15% similitud IA. Defensa oral que comprueba total autoría intelectual.</td>
                <td>8 - 7 puntos<br>Formato APA con errores leves; similitud IA dentro del margen permitido. Defensa oral aceptable.</td>
                <td>6 - 5 puntos<br>Inconsistencias graves APA; similitud IA entre 16-40%. Dependencia moderada de herramientas externas.</td>
                <td>4 - 0 puntos<br>No aplica APA; similitud IA > 40%. Evidencia clara de plagio o delegación cognitiva total.</td>
                <td style="text-align:center; font-weight:bold;">10</td>
            </tr>
            <tr style="background-color: #f5f5f5; font-weight: bold; border-top: 3px solid #006B3F;">
                <td colspan="5" style="text-align: right; padding-right: 15px;">PUNTAJE ACUMULADO TOTAL:</td>
                <td style="text-align: center; color:#006B3F; font-size:14pt;">90 / 100</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(rubric_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Regresar al Entorno de Evaluación (Reset)"):
        st.session_state.examen_terminado = False
        st.rerun()
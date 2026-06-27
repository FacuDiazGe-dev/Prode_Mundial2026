import streamlit as st

from styles_config import mostrar_decalogo
from styles_shared import css_panel_base, css_panel_header, css_section_title


def render_reglas():
    # ============================================================
    # ESTILOS — REGLAS DEL JUEGO
    # ============================================================

    css_reglas = (
        """
<style>
"""
        + css_section_title("reglas-title")
        + """

/* ============================================================
   PANEL BASE — REGLAS
   ============================================================ */

"""
        + css_panel_base("reglas-panel")
        + css_panel_header("reglas")
        + """

/* ============================================================
   FAQ — SOBRIO Y CLARO
   ============================================================ */

.faq-panel {
    display: grid;
    gap: 10px;
}

.faq-item {
    background: rgba(248,250,252,0.86);
    border: 1px solid rgba(226,232,240,0.88);
    border-radius: 15px;
    padding: 12px 13px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.55),
        0 6px 14px rgba(15,23,42,0.035);
}

.faq-question {
    display: flex;
    align-items: center;
    gap: 9px;

    color: #0f172a;
    font-family: 'Montserrat', sans-serif;
    font-size: 13.5px;
    font-weight: 900;
    line-height: 1.18;

    margin-bottom: 7px;
}

.faq-question-icon {
    width: 24px;
    height: 24px;
    min-width: 24px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 999px;
    background: rgba(7,17,31,0.96);
    border: 1px solid rgba(244,197,66,0.24);

    color: #F4C542;
    font-size: 11px;
    font-weight: 900;
}

.faq-list {
    margin: 0;
    padding-left: 33px;

    color: #334155;
    font-size: 12.5px;
    font-weight: 600;
    line-height: 1.42;
}

.faq-list li {
    margin-bottom: 5px;
}

.faq-list li:last-child {
    margin-bottom: 0;
}

/* ============================================================
   AJUSTES DECÁLOGO DENTRO DE REGLAS DEL JUEGO
   ============================================================ */

/* Centrado real de números */
.decalogo-number,
.decalogo-rule-number,
.decalogo-item-number {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    line-height: 1 !important;
    margin: 0 !important;
}

/* Si el número está dentro de span/div, también lo centra */
.decalogo-number *,
.decalogo-rule-number *,
.decalogo-item-number * {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

/* Reduce aire entre título y descripción */
.decalogo-rule-title,
.decalogo-content h3,
.decalogo-item h3 {
    margin-top: 0 !important;
    margin-bottom: 1px !important;
    line-height: 1.16 !important;
}

/* Descripción más cercana al título */
.decalogo-rule-text,
.decalogo-content p,
.decalogo-item p {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: 1.36 !important;
}

/* Compacta cada regla */
.decalogo-item,
.decalogo-rule {
    gap: 9px !important;
    margin-bottom: 8px !important;
}

/* Compacta el bloque interno de texto */
.decalogo-content,
.decalogo-rule-content {
    display: flex !important;
    flex-direction: column !important;
    gap: 1px !important;
}

/* Si el decálogo usa listas, reduce separación */
.decalogo-list {
    gap: 8px !important;
}

.decalogo-card {
    padding: 18px 16px !important;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {
    .faq-question {
        font-size: 13px;
    }

    .faq-list {
        font-size: 12px;
        padding-left: 30px;
    }

    .faq-item {
        padding: 11px 12px;
    }

    .decalogo-card {
        padding: 16px 13px !important;
    }

    .decalogo-item,
    .decalogo-rule {
        gap: 8px !important;
        margin-bottom: 7px !important;
    }

    .decalogo-rule-title,
    .decalogo-content h3,
    .decalogo-item h3 {
        margin-bottom: 1px !important;
    }

    .decalogo-rule-text,
    .decalogo-content p,
    .decalogo-item p {
        line-height: 1.34 !important;
    }
}
</style>
"""
    )

    st.markdown(css_reglas, unsafe_allow_html=True)

    # ============================================================
    # TÍTULO
    # ============================================================

    st.markdown("""
<div class="reglas-title">
<h1>📜 Reglas del Juego</h1>
<p>El reglamento, el decálogo y las respuestas importantes del Prode.</p>
</div>
""", unsafe_allow_html=True)

    # ============================================================
    # LAYOUT EN DOS COLUMNAS
    # ============================================================

    col_decalogo, col_faq = st.columns(
        [1, 1],
        gap="large"
    )

    # ============================================================
    # COLUMNA IZQUIERDA — DECÁLOGO
    # ============================================================

    with col_decalogo:

        mostrar_decalogo()

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================================
    # COLUMNA DERECHA — FAQ
    # ============================================================

    with col_faq:

        st.markdown("""
<div class="reglas-panel">
<div class="reglas-panel-header">
<div class="reglas-panel-icon">📘</div>
<div>
<div class="reglas-panel-title">Reglas y preguntas frecuentes</div>
<div class="reglas-panel-subtitle">Cómo se juega, cómo se puntúa y qué cosas no se negocian</div>
</div>
</div>

<div class="faq-panel">

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">1</div>
<div>¿Cómo se suman puntos?</div>
</div>
<ul class="faq-list">
<li><strong>Fase de grupos:</strong> 1 punto por acertar la tendencia general (gana equipo 1, empate o gana equipo 2) y 2 puntos extra por acertar el resultado exacto.</li>
<li><strong>Máximo fase de grupos:</strong> 3 puntos por partido.</li>
<li><strong>⚽ Fase eliminatoria:</strong> se pronostica el resultado de los 90 minutos. También suma 1 punto por tendencia y 2 puntos extra por resultado exacto.</li>
<li><strong>Clasificado:</strong> en eliminatorias se suma 1 punto extra por acertar qué equipo avanza. Si pronosticás empate, tenés que elegir el clasificado por alargue o penales.</li>
<li><strong>Máximo fase eliminatoria:</strong> 4 puntos por partido.</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">2</div>
<div>¿Hasta cuándo puedo cargar mis pronósticos?</div>
</div>
<ul class="faq-list">
<li>Hasta la fecha límite indicada en la sección "Mi Prode".</li>
<li>Pasada esa hora, la edición se bloquea automáticamente. Es una falta de respeto total pedirle al Admin que te lo cargue.</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">3</div>
<div>¿Cómo se determina el ganador?</div>
</div>
<ul class="faq-list">
<li>El GANADOR será el jugador que sume la mayor cantidad de puntos al finalizar la fase de grupos.</li>
<li>En caso de EMPATE TÉCNICO, define quien tenga más resultados exactos. Si persiste, define quien tenga más resultados generales.</li>
<li>Si el empate sigue, siguiendo, se define a Piedra, Papel o Tijera en un duelo a mejor de 3 rondas, con al menos 3 participantes del PRODE como testigos. ¡He dicho!</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">4</div>
<div>¿Cuánto hay que poner?</div>
</div>
<ul class="faq-list">
<li>La tarasca, la guita, la biyuya... El monto final lo decidirá el Comité Organizador mediante votación en el grupo de WhatsApp.</li>
<li>Definido el Aporte, se comunicará el alias y la fecha límite para transferir..</li>
<li>Si pasa la fecha límite y no pusiste un peso, se elimina tu cuenta y tus pronósticos quedan sin efecto. A llorar al campito.</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">5</div>
<div>¿Puedo modificar mis pronósticos?¿donde?</div>
</div>
<ul class="faq-list">
<li>Sí, mientras la edición esté abierta. en la seccion Mi Prode.</li>
<li>Una vez bloqueados, ya no se pueden editar.</li>
<li>Opción analógica: Si la tecnología te supera, pedile al Admin la plantilla de Excel para que el Comité lo cargue por vos. Somos inclusivos.</li>
<li>Opción prehistórica: Si el Excel tampoco es lo tuyo, podés mandar tu predicción escrita a mano en un papelito.</li>
<li>Aviso importante: Lo que carga la administración lo hace un ser humano más distraído de lo que imaginás. Revisá tus datos a tiempo. La organización no se responsabiliza por sus propios errores. Besis.</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">6</div>
<div>¿Qué pasa si no cargo un partido?</div>
</div>
<ul class="faq-list">
<li>Nada. Queda sin pronóstico o con el valor por defecto que defina la Organizacion.</li>
</ul>
</div>

<div class="faq-item">
<div class="faq-question">
<div class="faq-question-icon">7</div>
<div>¿Puedo ser eliminado o expulsado?</div>
</div>
<ul class="faq-list">
<li>¿Me pueden descalificar? ¡Sí, sin dudarlo! En este juego familiar prima la buena onda. Cualquier comportamiento inapropiado, exceso, trampa o falta de respeto hacia otro miembro del grupo te dejará fuera de competencia. Esto significa la eliminación total de tu cuenta y de tus pronósticos guardados. No hay lola..</li>
</ul>
</div>

</div>
</div>
""", unsafe_allow_html=True)

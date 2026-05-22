import streamlit as st

from styles_config import mostrar_decalogo


def render_reglas():
    # ============================================================
    # ESTILOS — REGLAS DEL JUEGO
    # ============================================================

    st.markdown("""
<style>
.reglas-title {
    margin-bottom: 22px;
}

.reglas-title h1 {
    font-family: 'Montserrat', sans-serif;
    font-size: 34px;
    font-weight: 900;
    color: #07111F;
    margin: 0;
    letter-spacing: -0.04em;
}

.reglas-title p {
    margin: 6px 0 0 0;
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
}

.reglas-panel {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,0.06);
    margin-bottom: 18px;
}

.reglas-panel-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(226,232,240,0.75);
}

.reglas-panel-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;

    flex-shrink: 0;
}

.reglas-panel-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
}

.reglas-panel-subtitle {
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    margin-top: 2px;
}

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
    padding: 13px 14px;

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
    font-size: 14px;
    font-weight: 900;
    line-height: 1.2;

    margin-bottom: 8px;
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
    font-size: 13px;
    font-weight: 650;
    line-height: 1.48;
}

.faq-list li {
    margin-bottom: 6px;
}

.faq-list li:last-child {
    margin-bottom: 0;
}

/* ============================================================
   AJUSTES DECÁLOGO DENTRO DE REGLAS DEL JUEGO
   ============================================================ */

.decalogo-number,
.decalogo-rule-number {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

.decalogo-rule-title,
.decalogo-content h3 {
    margin-bottom: 2px !important;
}

.decalogo-rule-text,
.decalogo-content p {
    margin-top: 0 !important;
    line-height: 1.42 !important;
}

.decalogo-item,
.decalogo-rule {
    gap: 10px !important;
}

@media (max-width: 768px) {
    .reglas-title h1 {
        font-size: 28px;
    }

    .reglas-title p {
        font-size: 12px;
    }

    .reglas-panel {
        padding: 13px;
        border-radius: 16px;
    }

    .reglas-panel-title {
        font-size: 16px;
    }

    .reglas-panel-subtitle {
        font-size: 11px;
    }

    .faq-question {
        font-size: 13px;
    }

    .faq-list {
        font-size: 12px;
        padding-left: 30px;
    }
}
</style>
""", unsafe_allow_html=True)

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

        st.markdown("""
<div class="reglas-panel">
<div class="reglas-panel-header">
<div class="reglas-panel-icon">📜</div>
<div>
<div class="reglas-panel-title">Decálogo del Prode</div>
<div class="reglas-panel-subtitle">Las reglas sagradas del grupo</div>
</div>
</div>
""", unsafe_allow_html=True)

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
<li>0 puntos: Si no acertás el resultado.</li>
<li>1 punto: Por acertar el resultado general (Ganador o Empate).</li>
<li>2 puntos adicionales: Por acertar el resultado exacto.</li>
<li>3 puntos: Es la cantidad máxima por partido.</li>
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

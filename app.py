import streamlit as st
import folium
import math
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Rastreador de Forrageamento",
    page_icon="🐝",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown("""
<style>

    /* Fundo geral */
    .stApp {
        background-color: #fafaf7;
    }

    /* Limita um pouco a largura para manter aparência elegante */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Título principal */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #3d3d32;
        margin-bottom: 0.2rem;
        line-height: 1.15;
    }

    .main-subtitle {
        font-size: 1.05rem;
        color: #73736a;
        margin-bottom: 1.8rem;
    }

    /* Cabeçalhos de seção */
    .section-title {
        font-size: 1.25rem;
        font-weight: 750;
        color: #44443a;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    /* Card da espécie */
    .bee-card {
        background: white;
        border: 1px solid #e7e5d9;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0 20px 0;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .bee-name {
        font-size: 1.45rem;
        font-weight: 800;
        color: #3d3d32;
        margin-bottom: 2px;
    }

    .bee-scientific {
        font-size: 0.95rem;
        color: #7b7b70;
        font-style: italic;
    }

    /* Cards dos indicadores */
    .metric-card {
        background: white;
        border: 1px solid #e7e5d9;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.035);
    }

    .metric-icon {
        font-size: 1.45rem;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #85857a;
        margin-top: 5px;
    }

    .metric-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: #3d3d32;
        margin-top: 2px;
    }

    /* Caixa de informação */
    .info-box {
        background: #f4f8ee;
        border-left: 5px solid #7c9a45;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 15px 0;
        color: #4b5540;
    }

    /* Caixa de contribuição */
    .support-box {
        background: linear-gradient(135deg, #fffdf4, #fff8df);
        border: 1px solid #eadca8;
        border-radius: 16px;
        padding: 22px;
        margin-top: 25px;
    }

    /* Legenda do mapa */
    .map-legend {
        background: white;
        border: 1px solid #deded6;
        border-radius: 10px;
        padding: 10px 13px;
        font-size: 0.82rem;
        color: #55554c;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Rodapé */
    .footer {
        text-align: center;
        color: #8a8a80;
        font-size: 0.8rem;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #e5e4dc;
    }

    /* Botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 42px;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DADOS DAS ABELHAS
# ============================================================

especies_abelhas = {
    "Arapuá/Irapuã (Trigona spinipes)": 1000,
    "Boca-de-Sapo (Partamona helleri)": 700,
    "Boiassu (Melipona interrupta)": 1500,
    "Borá (Tetragona clavipes)": 1500,
    "Bugia (Melipona mondury)": 1000,
    "Canudo (Scaptotrigona depilis)": 1500,
    "Guaraipo (Melipona bicolor)": 1000,
    "Guiruçu (Schwarziana quadripunctata)": 1000,
    "Iraí (Nannotrigona testaceicornis)": 500,
    "Jandaíra (Melipona subnitida)": 1000,
    "Jandaira-preta (Melipona mandacaia)": 1500,
    "Jataí (Tetragonisca angustula)": 500,
    "Jataí-Acriana (Tetragonisca weyrauchi)": 500,
    "Jataí-da-Terra (Paratrigona subnuda e Paratrigona lineata)": 500,
    "Lambe-olhos (Leurotrigona muelleri)": 300,
    "Limão (Lestrimelitta limao)": 1000,
    "Mandaçaia (Melipona quadrifasciata)": 1500,
    "Mandaguari Amarela (Scaptotrigona xanthotricha)": 1500,
    "Mandaguari Preta (Scaptotrigona postica)": 1500,
    "Mano-Pé (Scaptotrigona bipunctata)": 1500,
    "Marmelada (Frieseomelitta varia)": 500,
    "Mirim-droryana (Plebeia droryana)": 400,
    "Mirim-emerina (Plebeia emerina)": 500,
    "Mirim-guaçu (Plebeia remota)": 700,
    "Mirim-preguiça (Frieseomelitta varia)": 500,
    "Mirim-saitá (Plebeia moureana)": 500,
    "Mombucão (Cephalotrigona capitata)": 1000,
    "Rabo-de-tatu (Nannotrigona punctata)": 500,
    "Tiúba (Melipona fasciculata)": 1500,
    "Tubuna (Scaptotrigona bipunctata)": 1500,
    "Uruçu-amarela (Melipona rufiventris)": 1500,
    "Uruçu-caboclo (Melipona fuscopilosa)": 1700,
    "Uruçu-cinzenta (Melipona fasciculata)": 1500,
    "Uruçu-do-chão (Melipona capixaba)": 1500,
    "Uruçu-grandis / Uruçu-grande (Melipona grandis)": 2700,
    "Uruçu-nordestina (Melipona scutellaris)": 1500,
    "Uruçu-True / Amarela (Melipona flavolineata)": 1500,
}


# ============================================================
# FUNÇÕES
# ============================================================

def extrair_nome_cientifico(nome):
    """
    Extrai a parte entre parênteses.
    """
    if "(" in nome and ")" in nome:
        return nome.split("(")[-1].replace(")", "")
    return ""


def extrair_nome_popular(nome):
    """
    Remove o nome científico para exibir apenas o nome popular.
    """
    if "(" in nome:
        return nome.split("(")[0].strip()
    return nome


def calcular_area_km2(raio_metros):
    """
    Calcula a área aproximada de um círculo em km².
    """
    raio_km = raio_metros / 1000
    return math.pi * (raio_km ** 2)


def formatar_area(area):
    if area < 1:
        return f"{area:.2f} km²"
    return f"{area:.2f} km²"


# ============================================================
# INICIALIZAÇÃO DO ESTADO
# ============================================================

if "lat" not in st.session_state:
    st.session_state.lat = -22.9068

if "lon" not in st.session_state:
    st.session_state.lon = -43.1729

if "last_gps_lat" not in st.session_state:
    st.session_state.last_gps_lat = None

if "last_gps_lon" not in st.session_state:
    st.session_state.last_gps_lon = None


# ============================================================
# GEOCODER
# ============================================================

geolocator = Nominatim(
    user_agent="rastreador_forrageamento_abelhas"
)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="main-title">🐝 Rastreador de Forrageamento</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Estime a área potencial de forrageamento das abelhas nativas '
    'a partir da localização da colônia.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SELEÇÃO DA ABELHA
# ============================================================

st.markdown(
    '<div class="section-title">🐝 1. Escolha a espécie</div>',
    unsafe_allow_html=True
)

especie_escolhida = st.selectbox(
    "Selecione a espécie da sua colônia",
    sorted(especies_abelhas.keys()),
    label_visibility="collapsed"
)

raio_metros = especies_abelhas[especie_escolhida]

nome_popular = extrair_nome_popular(especie_escolhida)
nome_cientifico = extrair_nome_cientifico(especie_escolhida)

area_km2 = calcular_area_km2(raio_metros)


# ============================================================
# CARD DA ESPÉCIE
# ============================================================

st.markdown(
    f"""
    <div class="bee-card">
        <div class="bee-name">🐝 {nome_popular}</div>
        <div class="bee-scientific">{nome_cientifico}</div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INDICADORES
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📏</div>
            <div class="metric-label">RAIO ESTIMADO</div>
            <div class="metric-value">{raio_metros:,} m</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🌿</div>
            <div class="metric-label">ÁREA CIRCULAR</div>
            <div class="metric-value">{formatar_area(area_km2)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-icon">📍</div>
            <div class="metric-label">REFERÊNCIA</div>
            <div class="metric-value">Ninho</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# AVISO CIENTÍFICO
# ============================================================

st.markdown(
    f"""
    <div class="info-box">
        <b>🌿 Como interpretar o mapa</b><br>
        O círculo representa uma <b>estimativa de alcance de forrageamento</b>
        para a espécie selecionada. Ele não significa que as abelhas utilizem
        toda a área ou que exista recurso floral em todos os pontos.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOCALIZAÇÃO
# ============================================================

st.markdown(
    '<div class="section-title">📍 2. Localização do ninho</div>',
    unsafe_allow_html=True
)

st.write(
    "Escolha uma das opções abaixo para posicionar o ninho no mapa."
)


# ============================================================
# GPS
# ============================================================

loc_gps = streamlit_geolocation()

if (
    loc_gps
    and loc_gps.get("latitude") is not None
    and loc_gps.get("longitude") is not None
):

    g_lat = loc_gps["latitude"]
    g_lon = loc_gps["longitude"]

    if (
        g_lat != st.session_state.last_gps_lat
        or g_lon != st.session_state.last_gps_lon
    ):

        st.session_state.last_gps_lat = g_lat
        st.session_state.last_gps_lon = g_lon

        st.session_state.lat = g_lat
        st.session_state.lon = g_lon

        st.success("📍 Localização obtida com sucesso!")


# ============================================================
# BUSCA POR ENDEREÇO
# ============================================================

with st.form("form_busca_endereco"):

    endereco_busca = st.text_input(
        "🔍 Buscar endereço ou cidade",
        placeholder="Ex.: Seropédica, RJ"
    )

    buscar = st.form_submit_button(
        "🔎 Localizar no mapa",
        use_container_width=True
    )

    if buscar:

        if not endereco_busca.strip():

            st.warning("Digite um endereço ou cidade para pesquisar.")

        else:

            try:

                with st.spinner("Localizando..."):

                    loc = geolocator.geocode(
                        endereco_busca,
                        timeout=10
                    )

                if loc:

                    st.session_state.lat = loc.latitude
                    st.session_state.lon = loc.longitude

                    st.success(
                        f"📍 Local encontrado: {loc.address}"
                    )

                else:

                    st.error(
                        "Não encontrei esse endereço. "
                        "Tente informar também a cidade ou o estado."
                    )

            except Exception:

                st.error(
                    "Não foi possível realizar a busca agora. "
                    "Tente novamente em alguns segundos."
                )


# ============================================================
# COORDENADAS AVANÇADAS
# ============================================================

with st.expander("⚙️ Opções avançadas — coordenadas"):

    st.caption(
        "Você também pode informar manualmente as coordenadas "
        "geográficas do ninho."
    )

    col_lat, col_lon = st.columns(2)

    with col_lat:

        lat_inicial = st.number_input(
            "Latitude",
            value=float(st.session_state.lat),
            format="%.6f"
        )

    with col_lon:

        lon_inicial = st.number_input(
            "Longitude",
            value=float(st.session_state.lon),
            format="%.6f"
        )

    if (
        lat_inicial != st.session_state.lat
        or lon_inicial != st.session_state.lon
    ):

        st.session_state.lat = lat_inicial
        st.session_state.lon = lon_inicial


# ============================================================
# MAPA
# ============================================================

st.markdown(
    '<div class="section-title">🗺️ 3. Área de forrageamento</div>',
    unsafe_allow_html=True
)

st.caption(
    "Toque ou clique em qualquer ponto do mapa para reposicionar o ninho."
)


centro_mapa = [
    st.session_state.lat,
    st.session_state.lon
]


# ============================================================
# MAPA FOLIUM
# ============================================================

m = folium.Map(
    location=centro_mapa,
    zoom_start=15,
    tiles="CartoDB positron",
    control_scale=True
)


# ------------------------------------------------------------
# SATÉLITE
# ------------------------------------------------------------

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/World_Imagery/"
        "MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri",
    name="🛰️ Satélite",
    overlay=False,
    control=True
).add_to(m)


# ------------------------------------------------------------
# MAPA PADRÃO
# ------------------------------------------------------------

folium.TileLayer(
    "CartoDB positron",
    name="🗺️ Mapa",
    overlay=False,
    control=True
).add_to(m)


# ------------------------------------------------------------
# MARCADOR DO NINHO
# ------------------------------------------------------------

folium.Marker(
    location=centro_mapa,
    tooltip="📍 Ninho",
    popup=folium.Popup(
        f"""
        <b>🐝 Localização do ninho</b><br><br>
        {nome_popular}<br>
        Raio estimado: {raio_metros} m
        """,
        max_width=250
    ),
    icon=folium.Icon(
        color="green",
        icon="home",
        prefix="fa"
    )
).add_to(m)


# ------------------------------------------------------------
# CÍRCULO DE FORRAGEAMENTO
# ------------------------------------------------------------

folium.Circle(
    location=centro_mapa,
    radius=raio_metros,
    color="#d8a900",
    weight=3,
    fill=True,
    fill_color="#f4c430",
    fill_opacity=0.22,
    popup=folium.Popup(
        f"""
        <b>🌿 Área potencial de forrageamento</b><br><br>
        <b>Espécie:</b> {nome_popular}<br>
        <b>Raio:</b> {raio_metros:,} m<br>
        <b>Área circular:</b> {formatar_area(area_km2)}
        """,
        max_width=280
    )
).add_to(m)


# ------------------------------------------------------------
# CÍRCULO EXTERNO DISCRETO
# ------------------------------------------------------------

folium.Circle(
    location=centro_mapa,
    radius=raio_metros,
    color="#ffffff",
    weight=1,
    fill=False,
    opacity=0.8
).add_to(m)


# ------------------------------------------------------------
# LEGENDA
# ------------------------------------------------------------

legend_html = f"""
<div style="
    position: fixed;
    bottom: 25px;
    left: 25px;
    z-index: 9999;
    background: white;
    padding: 10px 13px;
    border-radius: 10px;
    border: 1px solid #ddd;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    font-size: 12px;
">
    <b>Legenda</b><br>
    📍 Ninho<br>
    <span style="color:#d8a900;">●</span>
    Área potencial de forrageamento<br>
    <small>Raio: {raio_metros:,} m</small>
</div>
"""

m.get_root().html.add_child(
    folium.Element(legend_html)
)


# ------------------------------------------------------------
# CONTROLE DE CAMADAS
# ------------------------------------------------------------

folium.LayerControl(
    position="topright",
    collapsed=True
).add_to(m)


# ============================================================
# EXIBIÇÃO
# ============================================================

output = st_folium(
    m,
    width=None,
    height=580,
    key="meu_mapa_abelhas"
)


# ============================================================
# CLIQUE NO MAPA
# ============================================================

if output and output.get("last_clicked"):

    clicked_lat = output["last_clicked"]["lat"]
    clicked_lon = output["last_clicked"]["lng"]

    if (
        clicked_lat != st.session_state.lat
        or clicked_lon != st.session_state.lon
    ):

        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lon

        st.rerun()


# ============================================================
# INFORMAÇÕES DA ÁREA
# ============================================================

st.markdown(
    '<div class="section-title">🌿 Sobre esta área</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"""
        **🐝 Espécie**

        {nome_popular}

        **🔬 Nome científico**

        *{nome_cientifico}*
        """
    )

with col2:

    st.markdown(
        f"""
        **📏 Raio estimado**

        {raio_metros:,} metros

        **🌿 Área circular aproximada**

        {formatar_area(area_km2)}
        """
    )


st.info(
    "💡 Para planejamento de paisagismo, observe dentro da área "
    "demarcada a presença de árvores, arbustos, plantas cultivadas "
    "e vegetação nativa que possam oferecer recursos florais."
)


# ============================================================
# ABELHA NÃO ENCONTRADA
# ============================================================

with st.expander("🐝 Não encontrou sua espécie?"):

    st.write(
        "Se uma espécie de abelha nativa não estiver cadastrada, "
        "você pode enviar uma sugestão para inclusão na ferramenta."
    )

    st.markdown(
        "📧 **E-mail:** "
        "[paulo_eduardo_cb@hotmail.com]"
        "(mailto:paulo_eduardo_cb@hotmail.com)"
    )


# ============================================================
# APOIO AO PROJETO
# ============================================================

st.markdown(
    '<div class="support-box">',
    unsafe_allow_html=True
)

st.markdown("### ☕ Apoie este projeto")

st.write(
    "Este aplicativo é gratuito e foi desenvolvido para apoiar "
    "a meliponicultura, a pesquisa e o planejamento de áreas "
    "favoráveis às nossas abelhas nativas."
)

st.write(
    "Se a ferramenta foi útil para você e quiser colaborar "
    "com a manutenção do projeto, qualquer contribuição via "
    "Pix é muito bem-vinda. ❤️"
)

st.markdown("**Dados para contribuição via Pix**")

st.write(
    "**👤 Favorecido:** Paulo Eduardo Castelo Branco Geraldo"
)

st.write(
    "**🏦 Banco:** Nubank"
)

st.write("**🔑 Chave Pix:**")

st.code(
    "02450e96-4a41-4b62-8275-0b741c23a42b",
    language="text"
)

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="footer">
        🐝 Rastreador de Forrageamento<br>
        Desenvolvido para apoiar a meliponicultura e a
        conservação das abelhas nativas.
        <br><br>
        © 2026
    </div>
    """,
    unsafe_allow_html=True
)

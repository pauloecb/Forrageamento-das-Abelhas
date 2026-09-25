import streamlit as st
import folium
from folium.plugins import LocateControl
from branca.element import Element
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import math
import re


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Rastreador de Abelhas",
    page_icon="🐝",
    layout="centered"
)


# ============================================================
# ESTILO VISUAL
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #fafaf7;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* TÍTULO PRINCIPAL */

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #263238;
    margin-bottom: 0.2rem;
}

.main-subtitle {
    color: #607d8b;
    font-size: 1.05rem;
    margin-bottom: 1.8rem;
}


/* TÍTULOS DE SEÇÃO */

.section-title {
    font-size: 1.35rem;
    font-weight: 750;
    color: #37474f;
    margin-top: 1rem;
    margin-bottom: 1rem;
}


/* CARD DA ABELHA */

.bee-card {
    background: linear-gradient(135deg, #fffdf3, #fff8d9);
    border: 1px solid #f0df91;
    border-radius: 16px;
    padding: 20px;
    margin-top: 12px;
    margin-bottom: 18px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}

.bee-name {
    font-size: 1.45rem;
    font-weight: 800;
    color: #4e342e;
}

.bee-scientific {
    font-size: 0.95rem;
    color: #795548;
    margin-top: 3px;
}


/* MÉTRICAS */

.metric-card {
    background-color: white;
    border-radius: 14px;
    padding: 17px;
    border: 1px solid #e5e5e5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    min-height: 105px;
}

.metric-icon {
    font-size: 1.4rem;
}

.metric-label {
    color: #78909c;
    font-size: 0.82rem;
    margin-top: 5px;
}

.metric-value {
    font-size: 1.25rem;
    font-weight: 800;
    color: #37474f;
    margin-top: 3px;
}


/* CAIXAS INFORMATIVAS */

.info-box {
    background-color: #eef7ff;
    border-left: 5px solid #2196f3;
    padding: 14px 16px;
    border-radius: 10px;
    margin: 15px 0;
    color: #37474f;
}

.support-box {
    background: linear-gradient(135deg, #fff8e1, #fffdf4);
    border: 1px solid #f0d77a;
    padding: 18px;
    border-radius: 14px;
    margin-top: 25px;
}


/* LEGENDA DO MAPA */

.map-legend {
    background: white;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #dddddd;
    margin-top: 10px;
    font-size: 0.88rem;
    color: #455a64;
}


/* RODAPÉ */

.footer {
    text-align: center;
    color: #90a4ae;
    font-size: 0.82rem;
    margin-top: 35px;
    padding-top: 15px;
    border-top: 1px solid #eeeeee;
}


/* BOTÕES */

.stButton > button {
    border-radius: 10px;
    font-weight: 650;
}


/* SELECTBOX */

div[data-baseweb="select"] > div {
    border-radius: 10px;
}


/* INPUTS */

.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
}


/* CONTROLE DE LOCALIZAÇÃO DO FOLIUM */

.leaflet-control-locate a {
    background-color: white !important;
    color: #37474f !important;
    font-size: 19px !important;
}

.leaflet-control-locate a:hover {
    background-color: #f5f5f5 !important;
}


/* MELHORA VISUAL DOS CONTROLES DO MAPA */

.leaflet-control-zoom a,
.leaflet-control-layers {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="main-title">🌿 Rastreador de Forrageamento</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">'
    'Descubra o raio de alcance estimado das abelhas nativas '
    'a partir da localização do seu ninho.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# BANCO DE ESPÉCIES
# ============================================================

especies_abelhas = {

    "Arapuá/Irapuã (Trigona spinipes)": 1000,

    "Boca-de-Sapo (Partamona helleri)": 700,

    "Borá (Tetragona clavipes)": 1500,

    "Jataí-da-Terra (Paratrigona subnuda e Paratrigona lineata)": 500,

    "Jataí-Acriana (Tetragonisca weyrauchi)": 500,

    "Boiassu (Melipona interrupta)": 1500,

    "Bugia (Melipona mondury)": 1000,

    "Canudo (Scaptotrigona depilis)": 1500,

    "Guaraipo (Melipona bicolor)": 1000,

    "Guiruçu (Schwarziana quadripunctata)": 1000,

    "Iraí (Nannotrigona testaceicornis)": 500,

    "Jandaíra (Melipona subnitida)": 1000,

    "Jandaira-preta (Melipona mandacaia)": 1500,

    "Jataí (Tetragonisca angustula)": 500,

    "Lambe-olhos (Leurotrigona muelleri)": 300,

    "Mandaçaia (Melipona quadrifasciata)": 1500,

    "Mandaguari Amarela (Scaptotrigona xanthotricha)": 1500,

    "Mandaguari Preta (Scaptotrigona postica)": 1500,

    "Mano-Pé (Scaptotrigona bipunctata)": 1500,

    "Marmelada (Frieseomelitta varia)": 500,

    "Mirim-droryana (Plebeia droryana)": 400,

    "Mirim-emerina (Plebeia emerina)": 500,

    "Mirim-preguiça (Frieseomelitta varia)": 500,

    "Mirim-guaçu (Plebeia remota)": 700,

    "Mirim-saitá (Plebeia moureana)": 500,

    "Mombucão (Cephalotrigona capitata)": 1000,

    "Limão (Lestrimelitta limao)": 1000,

    "Rabo-de-tatu (Nannotrigona punctata)": 500,

    "Tiúba (Melipona fasciculata)": 1500,

    "Tubuna (Scaptotrigona bipunctata)": 1500,

    "Uruçu-amarela (Melipona rufiventris)": 1500,

    "Uruçu-cinzenta (Melipona fasciculata)": 1500,

    "Uruçu-caboclo (Melipona fuscopilosa)": 1700,

    "Uruçu-do-chão (Melipona capixaba)": 1500,

    "Uruçu-grandis / Uruçu-grande (Melipona grandis)": 2700,

    "Uruçu-nordestina (Melipona scutellaris)": 1500,

    "Uruçu-True / Amarela (Melipona flavolineata)": 1500
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def extrair_nome_cientifico(nome):
    """
    Extrai o conteúdo entre parênteses.
    """
    resultado = re.search(r"\((.*?)\)", nome)

    if resultado:
        return resultado.group(1)

    return ""


def extrair_nome_popular(nome):
    """
    Extrai o nome popular antes dos parênteses.
    """
    resultado = re.search(r"^(.*?)\s*\(", nome)

    if resultado:
        return resultado.group(1).strip()

    return nome


def calcular_area_km2(raio_metros):
    raio_km = raio_metros / 1000
    return math.pi * (raio_km ** 2)


def formatar_area(area):
    if area < 1:
        return f"{area:.2f} km²"

    return f"{area:.1f} km²"


# ============================================================
# 1 — ESCOLHA DA ABELHA
# ============================================================

st.markdown(
    '<div class="section-title">🐝 1. Escolha da abelha</div>',
    unsafe_allow_html=True
)

especie_escolhida = st.selectbox(
    "Selecione a espécie:",
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

        <div class="bee-name">
            🐝 {nome_popular}
        </div>

        <div class="bee-scientific">
            {nome_cientifico}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MÉTRICAS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-label">Raio estimado</div>
            <div class="metric-value">{raio_metros:,} m</div>
        </div>
        """.replace(",", "."),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🌿</div>
            <div class="metric-label">Área circular</div>
            <div class="metric-value">{formatar_area(area_km2)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-icon">🏠</div>
            <div class="metric-label">Referência</div>
            <div class="metric-value">Ninho</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# AVISO CIENTÍFICO
# ============================================================

st.markdown(
    """
    <div class="info-box">
        🧭 <b>Importante:</b> o raio apresentado é uma estimativa
        de referência. O alcance real pode variar conforme a espécie,
        disponibilidade de recursos, clima, relevo e características
        da colônia.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOCALIZAÇÃO INICIAL
# ============================================================

if "lat" not in st.session_state:
    st.session_state.lat = -22.9068

if "lon" not in st.session_state:
    st.session_state.lon = -43.1729


# ============================================================
# 2 — LOCALIZAÇÃO DO NINHO
# ============================================================

st.markdown(
    '<div class="section-title">📍 2. Localização do ninho</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
        🗺️ <b>Você pode escolher a localização de três formas:</b><br><br>
        • pesquisar um endereço ou cidade;<br>
        • tocar diretamente no mapa;<br>
        • usar o botão ⦿ no canto superior direito do mapa para usar o GPS.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BUSCA POR ENDEREÇO
# ============================================================

geolocator = Nominatim(
    user_agent="rastreador_abelhas_app"
)

with st.form("form_busca_endereco"):

    endereco_busca = st.text_input(
        "🔍 Pesquisar endereço ou cidade",
        placeholder="Ex.: Seropédica, RJ"
    )

    buscar = st.form_submit_button(
        "🔎 Encontrar localização",
        use_container_width=True
    )


if buscar:

    if endereco_busca.strip():

        try:

            loc = geolocator.geocode(endereco_busca)

            if loc:

                st.session_state.lat = loc.latitude
                st.session_state.lon = loc.longitude

                st.success(
                    f"📍 Localização encontrada: {loc.address}"
                )

                st.rerun()

            else:

                st.error(
                    "Não encontrei esse endereço. "
                    "Tente informar também a cidade ou o estado."
                )

        except Exception:

            st.error(
                "Não foi possível realizar a busca agora."
            )

    else:

        st.warning(
            "Digite um endereço ou cidade para pesquisar."
        )


# ============================================================
# OPÇÕES AVANÇADAS
# ============================================================

with st.expander("⚙️ Opções avançadas — coordenadas"):

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

        st.rerun()


# ============================================================
# 3 — MAPA
# ============================================================

st.markdown(
    '<div class="section-title">🗺️ 3. Área de forrageamento</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        color:#607d8b;
        margin-bottom:10px;
        font-size:0.95rem;
    ">
        💡 Toque em qualquer ponto do mapa para posicionar o ninho.
        O botão ⦿ usa a localização atual do seu dispositivo.
    </div>
    """,
    unsafe_allow_html=True
)


centro_mapa = [
    st.session_state.lat,
    st.session_state.lon
]


# ============================================================
# CRIAÇÃO DO MAPA
# ============================================================

m = folium.Map(
    location=centro_mapa,
    zoom_start=15,
    tiles="CartoDB positron",
    control_scale=True
)


# ============================================================
# CAMADA DE SATÉLITE
# ============================================================

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


# ============================================================
# CAMADA MAPA CLARO
# ============================================================

folium.TileLayer(
    tiles="CartoDB positron",
    name="🗺️ Mapa",
    overlay=False,
    control=True
).add_to(m)


# ============================================================
# MARCADOR DO NINHO
# ============================================================

folium.Marker(
    location=centro_mapa,
    popup=folium.Popup(
        f"""
        <div style="text-align:center;">
            <b>🏠 Ninho</b><br>
            {nome_popular}
        </div>
        """,
        max_width=250
    ),
    tooltip="🏠 Localização do ninho",
    icon=folium.Icon(
        color="green",
        icon="home",
        prefix="fa"
    )
).add_to(m)


# ============================================================
# CÍRCULO DE FORRAGEAMENTO
# ============================================================

folium.Circle(
    location=centro_mapa,
    radius=raio_metros,
    color="#f4c20d",
    weight=3,
    fill=True,
    fill_color="#ff9800",
    fill_opacity=0.25,
    popup=folium.Popup(
        f"""
        <b>{nome_popular}</b><br>
        Raio estimado: {raio_metros} metros<br>
        Área aproximada: {formatar_area(area_km2)}
        """,
        max_width=280
    )
).add_to(m)


# ============================================================
# CONTROLE DE GPS
# ============================================================

LocateControl(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    drawCircle=False,
    showPopup=False,
    locateOptions={
        "enableHighAccuracy": True,
        "maximumAge": 0,
        "timeout": 10000
    }
).add_to(m)


# ============================================================
# INTEGRAÇÃO GPS → LOCALIZAÇÃO DO NINHO
# ============================================================
#
# O LocateControl encontra a localização do dispositivo.
#
# Quando a localização é encontrada, este código dispara
# artificialmente um "clique" no mapa exatamente naquele ponto.
#
# O st_folium já sabe capturar cliques no mapa através de
# "last_clicked". Dessa forma aproveitamos a mesma lógica
# utilizada para posicionar manualmente o ninho.
# ============================================================

map_name = m.get_name()

gps_bridge = Element(
    f"""
    <script>

    (function() {{

        var map = {map_name};

        map.on('locationfound', function(e) {{

            if (!e || !e.latlng) {{
                return;
            }}

            // Centraliza o mapa na localização encontrada
            map.setView(
                [e.latlng.lat, e.latlng.lng],
                17,
                {{
                    animate: true
                }}
            );

            // Envia a localização para o mesmo sistema
            // usado quando o usuário toca manualmente no mapa.
            setTimeout(function() {{

                map.fire('click', {{
                    latlng: e.latlng
                }});

            }}, 250);

        }});

        map.on('locationerror', function(e) {{

            console.warn(
                'Não foi possível obter a localização:',
                e.message
            );

        }});

    }})();

    </script>
    """
)

m.get_root().html.add_child(gps_bridge)


# ============================================================
# CONTROLE DE CAMADAS
# ============================================================

folium.LayerControl(
    position="topright",
    collapsed=True
).add_to(m)


# ============================================================
# LEGENDA
# ============================================================

st.markdown(
    """
    <div class="map-legend">
        🏠 <b>Marcador:</b> localização do ninho
        &nbsp;&nbsp;•&nbsp;&nbsp;
        🟡 <b>Círculo:</b> raio estimado de forrageamento
        &nbsp;&nbsp;•&nbsp;&nbsp;
        ⦿ <b>GPS:</b> localização atual do dispositivo
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EXIBIÇÃO DO MAPA
# ============================================================

output = st_folium(
    m,
    width=700,
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
# INFORMAÇÕES SOBRE A ÁREA
# ============================================================

st.markdown(
    '<div class="section-title">🌿 Sobre esta área</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="info-box">

        A área representada possui aproximadamente
        <b>{formatar_area(area_km2)}</b> em torno do ninho,
        considerando um raio de <b>{raio_metros} metros</b>.

        <br><br>

        Essa representação pode ajudar o meliponicultor a
        visualizar quais áreas do entorno do meliponário podem
        fazer parte da região potencialmente explorada pela
        colônia em busca de néctar, pólen, resinas e outros recursos.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ESPÉCIE NÃO ENCONTRADA
# ============================================================

with st.expander("🐝 Não encontrou sua espécie?"):

    st.markdown(
        """
        Se você conhece uma espécie de abelha nativa que ainda
        não aparece na lista, pode enviar a sugestão para que
        ela seja analisada e eventualmente adicionada ao banco
        de dados.
        """
    )

    st.markdown(
        """
        📧 **E-mail:**
        [paulo_eduardo_cb@hotmail.com](mailto:paulo_eduardo_cb@hotmail.com)
        """
    )


# ============================================================
# APOIO AO PROJETO
# ============================================================

st.markdown(
    """
    <div class="support-box">

        <b>🐝 Ajude a melhorar o projeto</b>

        <br><br>

        Este projeto foi criado para auxiliar meliponicultores
        a visualizar o potencial de forrageamento das abelhas
        nativas e entender melhor a paisagem ao redor dos ninhos.

        <br><br>

        Quanto mais espécies, nomes populares e informações
        forem adicionados, mais útil a ferramenta poderá se tornar.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="footer">
        🌿 Rastreador de Forrageamento de Abelhas Nativas<br>
        Ferramenta de referência para meliponicultura
    </div>
    """,
    unsafe_allow_html=True
)

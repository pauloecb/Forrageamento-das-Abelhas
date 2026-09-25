import streamlit as st
import folium
from folium.plugins import LocateControl
from branca.element import Element
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import math


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Rastreador de Abelhas",
    page_icon="🐝",
    layout="centered"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7f8fa;
    }

    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #202124;
        margin-bottom: 0.2rem;
    }

    .main-subtitle {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 1.8rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 750;
        color: #202124;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem;
        min-height: 105px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-icon {
        font-size: 1.3rem;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.82rem;
        color: #6b7280;
    }

    .metric-value {
        font-size: 1.25rem;
        font-weight: 750;
        color: #202124;
        margin-top: 0.15rem;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.8rem;
        margin-top: 2.5rem;
    }

    /* Botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 10px;
    }

    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    /* GPS / controles do Leaflet */
    .leaflet-control-locate {
        margin-top: 10px !important;
    }

    .leaflet-control-layers {
        margin-top: 10px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="main-title">🐝 Rastreador de Abelhas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-subtitle">Visualize a área potencial de forrageamento ao redor do seu meliponário.</div>',
    unsafe_allow_html=True
)


# ============================================================
# ESPÉCIES
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
# SELEÇÃO DA ABELHA
# ============================================================

st.markdown(
    '<div class="section-title">🐝 Escolha a espécie</div>',
    unsafe_allow_html=True
)

especie_selecionada = st.selectbox(
    "Espécie da abelha",
    list(especies_abelhas.keys()),
    index=list(especies_abelhas.keys()).index(
        "Jataí (Tetragonisca angustula)"
    )
)

raio_metros = especies_abelhas[especie_selecionada]


# ============================================================
# INFORMAÇÕES DA ESPÉCIE
# ============================================================

partes = especie_selecionada.split("(", 1)

nome_popular = partes[0].strip()

if len(partes) > 1:
    nome_cientifico = "(" + partes[1].strip()
else:
    nome_cientifico = ""


st.markdown(
    f"""
    **{nome_popular}**

    *{nome_cientifico}*
    """
)


# ============================================================
# CÁLCULO DA ÁREA
# ============================================================

area_km2 = math.pi * (raio_metros / 1000) ** 2


def formatar_area(area):
    if area < 10:
        return f"{area:.2f} km²"
    else:
        return f"{area:.1f} km²"


# ============================================================
# MÉTRICAS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📏</div>
            <div class="metric-label">Raio estimado</div>
            <div class="metric-value">{raio_metros:,} m</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">⭕</div>
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
            <div class="metric-icon">🏡</div>
            <div class="metric-label">Referência</div>
            <div class="metric-value">Ninho</div>
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
# LOCALIZAÇÃO DO NINHO
# ============================================================

st.markdown(
    '<div class="section-title">📍 Localização do ninho</div>',
    unsafe_allow_html=True
)

st.caption(
    "Você pode pesquisar um endereço, usar o GPS dentro do mapa "
    "ou simplesmente clicar diretamente no local do ninho."
)


# ============================================================
# BUSCA POR ENDEREÇO
# ============================================================

with st.form("form_endereco"):
    endereco = st.text_input(
        "Pesquisar endereço",
        placeholder="Digite rua, bairro, cidade ou ponto de referência"
    )

    pesquisar = st.form_submit_button(
        "🔎 Localizar endereço",
        use_container_width=True
    )

if pesquisar and endereco:

    try:
        geolocator = Nominatim(
            user_agent="rastreador_abelhas"
        )

        local = geolocator.geocode(
            endereco,
            timeout=10
        )

        if local:

            st.session_state.lat = local.latitude
            st.session_state.lon = local.longitude

            st.success(
                f"Local encontrado: {local.address}"
            )

            st.rerun()

        else:

            st.warning(
                "Não foi possível localizar esse endereço."
            )

    except Exception as e:

        st.error(
            "Não foi possível realizar a busca do endereço."
        )


# ============================================================
# COORDENADAS MANUAIS
# ============================================================

with st.expander("⚙️ Inserir coordenadas manualmente"):

    col1, col2 = st.columns(2)

    with col1:
        nova_lat = st.number_input(
            "Latitude",
            value=float(st.session_state.lat),
            format="%.6f"
        )

    with col2:
        nova_lon = st.number_input(
            "Longitude",
            value=float(st.session_state.lon),
            format="%.6f"
        )

    if st.button(
        "📍 Aplicar coordenadas",
        use_container_width=True
    ):

        st.session_state.lat = nova_lat
        st.session_state.lon = nova_lon

        st.rerun()


# ============================================================
# MAPA
# ============================================================

st.markdown(
    '<div class="section-title">🗺️ Área de forrageamento</div>',
    unsafe_allow_html=True
)


m = folium.Map(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    zoom_start=14,
    tiles=None,
    control_scale=True
)


# ============================================================
# CAMADA DE SATÉLITE — PADRÃO
# ============================================================

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="🛰️ Satélite",
    overlay=False,
    control=True,
    show=True
).add_to(m)


# ============================================================
# CAMADA DE MAPA
# ============================================================

folium.TileLayer(
    tiles="CartoDB positron",
    name="🗺️ Mapa",
    overlay=False,
    control=True,
    show=False
).add_to(m)


# ============================================================
# MARCADOR DO NINHO
# ============================================================

folium.Marker(
    [
        st.session_state.lat,
        st.session_state.lon
    ],
    tooltip="🐝 Local do ninho",
    popup=f"""
    <b>🐝 Ninho</b><br>
    {nome_popular}<br>
    Raio estimado: {raio_metros} metros
    """,
    icon=folium.Icon(
        color="orange",
        icon="home"
    )
).add_to(m)


# ============================================================
# CÍRCULO DE FORRAGEAMENTO
# ============================================================

folium.Circle(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    radius=raio_metros,
    color="#e0a100",
    fill=True,
    fill_color="#f5c542",
    fill_opacity=0.18,
    weight=2,
    tooltip=f"Raio estimado: {raio_metros} metros"
).add_to(m)


# ============================================================
# GPS DENTRO DO MAPA
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
# PONTE ENTRE GPS E STREAMLIT
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

            map.setView(
                [e.latlng.lat, e.latlng.lng],
                17,
                {{ animate: true }}
            );

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
    position="topright"
).add_to(m)


# ============================================================
# EXIBIÇÃO DO MAPA
# ============================================================

map_data = st_folium(
    m,
    width=700,
    height=580,
    key="meu_mapa_abelhas"
)


# ============================================================
# CLIQUE NO MAPA
# ============================================================

if map_data:

    clicked = map_data.get("last_clicked")

    if clicked:

        nova_lat = clicked.get("lat")
        nova_lon = clicked.get("lng")

        if nova_lat is not None and nova_lon is not None:

            if (
                abs(nova_lat - st.session_state.lat) > 0.000001
                or
                abs(nova_lon - st.session_state.lon) > 0.000001
            ):

                st.session_state.lat = nova_lat
                st.session_state.lon = nova_lon

                st.rerun()


# ============================================================
# SOBRE ESTA ÁREA
# ============================================================

st.markdown(
    '<div class="section-title">🌿 Sobre esta área</div>',
    unsafe_allow_html=True
)

st.info(
    f"""
A área representada possui aproximadamente **{formatar_area(area_km2)}**
em torno do ninho, considerando um raio estimado de **{raio_metros} metros**.

Essa representação pode ajudar o meliponicultor a visualizar o entorno
do meliponário e identificar áreas que podem fazer parte da região
potencialmente explorada pela colônia em busca de néctar, pólen,
resinas e outros recursos.

**Importante:** o círculo é uma representação geométrica baseada no
raio estimado da espécie. Ele não significa que a colônia encontrará
recursos em toda essa área nem que o voo real será perfeitamente
circular.
"""
)


# ============================================================
# AJUDE A MELHORAR
# ============================================================

st.markdown(
    '<div class="section-title">🐝 Ajude a melhorar o projeto</div>',
    unsafe_allow_html=True
)

st.success(
    """
Este projeto foi criado para auxiliar meliponicultores a visualizar
o potencial de forrageamento das abelhas nativas e entender melhor
a paisagem ao redor dos ninhos.

Quanto mais espécies, nomes populares e informações forem adicionados,
mais útil a ferramenta poderá se tornar.
"""
)


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="footer">
        Rastreador de Abelhas 🐝 · Ferramenta experimental para meliponicultura
    </div>
    """,
    unsafe_allow_html=True
)

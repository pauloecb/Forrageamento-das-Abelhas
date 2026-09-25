import streamlit as st
import folium

from folium.plugins import LocateControl
from streamlit_folium import st_folium

from branca.element import Element
from geopy.geocoders import Nominatim

import math


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Rastreador de Abelhas",
    page_icon="🐝",
    layout="wide"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #f4f4f4;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .titulo {
        font-size: 2.2rem;
        font-weight: 700;
        color: #222;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .pix-card {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-top: 20px;
    }

    .rodape {
        text-align: center;
        color: #888;
        font-size: 0.85rem;
        margin-top: 30px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo">🐝 Rastreador de Abelhas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Estime a área de forrageamento da sua abelha sem ferrão.'
    '</div>',
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
# ESCOLHA DA ABELHA
# ============================================================

especie = st.selectbox(
    "Escolha a espécie de abelha:",
    list(especies_abelhas.keys()),
    index=list(especies_abelhas.keys()).index(
        "Jataí (Tetragonisca angustula)"
    )
)

raio_metros = especies_abelhas[especie]

area_km2 = math.pi * (raio_metros / 1000) ** 2


# ============================================================
# POSIÇÃO DO NINHO
# ============================================================

if "lat" not in st.session_state:
    st.session_state.lat = -22.9068

if "lon" not in st.session_state:
    st.session_state.lon = -43.1729


# ============================================================
# BUSCA POR ENDEREÇO
# ============================================================

st.markdown("### 📍 Localização do ninho")

endereco = st.text_input(
    "Pesquisar endereço",
    placeholder="Digite uma rua, bairro, cidade..."
)

if st.button("🔎 Buscar endereço"):

    if endereco.strip():

        try:

            geolocator = Nominatim(
                user_agent="rastreador_abelhas"
            )

            local = geolocator.geocode(endereco)

            if local:

                st.session_state.lat = local.latitude
                st.session_state.lon = local.longitude

                st.success(
                    f"Local encontrado: {local.address}"
                )

                st.rerun()

            else:

                st.warning(
                    "Não encontrei esse endereço."
                )

        except Exception:

            st.error(
                "Não foi possível pesquisar o endereço."
            )


# ============================================================
# COORDENADAS MANUAIS
# ============================================================

with st.expander("✏️ Informar coordenadas manualmente"):

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

    if st.button("📍 Usar estas coordenadas"):

        st.session_state.lat = nova_lat
        st.session_state.lon = nova_lon

        st.rerun()


# ============================================================
# MAPA
# ============================================================

m = folium.Map(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    zoom_start=15,
    control_scale=True
)


# ============================================================
# CAMADA SATÉLITE
# ============================================================

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri",
    name="Satélite",
    overlay=False,
    control=True
).add_to(m)


# ============================================================
# CAMADA MAPA NORMAL
# ============================================================

folium.TileLayer(
    tiles="CartoDB positron",
    name="Mapa",
    overlay=False,
    control=True
).add_to(m)


# ============================================================
# MARCADOR DO NINHO
# ============================================================

marcador_ninho = folium.Marker(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    tooltip="Local do ninho",
    popup=f"""
    <b>🐝 Ninho</b><br>
    {especie}<br>
    Raio estimado: {raio_metros} m
    """,
    icon=folium.Icon(
        color="green",
        icon="home"
    )
)

marcador_ninho.add_to(m)


# ============================================================
# CÍRCULO DE FORRAGEAMENTO
# ============================================================

circulo_ninho = folium.Circle(
    location=[
        st.session_state.lat,
        st.session_state.lon
    ],
    radius=raio_metros,
    color="#f1c40f",
    fill=True,
    fill_color="#f1c40f",
    fill_opacity=0.20,
    weight=2,
    tooltip=f"Raio estimado: {raio_metros} metros"
)

circulo_ninho.add_to(m)


# ============================================================
# CONTROLE GPS DENTRO DO MAPA
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
# CONTROLE DE CAMADAS
# ============================================================

folium.LayerControl().add_to(m)


# ============================================================
# JAVASCRIPT DO GPS
# ============================================================

map_name = m.get_name()
marker_name = marcador_ninho.get_name()
circle_name = circulo_ninho.get_name()

gps_script = f"""
<script>

(function() {{

    var mapa = {map_name};
    var marcador = {marker_name};
    var circulo = {circle_name};

    if (!mapa) {{
        return;
    }}

    /*
     * O evento "locationfound" é disparado pelo LocateControl
     * quando o navegador encontra a posição do dispositivo.
     *
     * IMPORTANTE:
     * Não usamos o "center" do mapa.
     *
     * Assim, arrastar o mapa não altera o ninho.
     */

    mapa.off('locationfound');

    mapa.on('locationfound', function(e) {{

        var latitude = e.latlng.lat;
        var longitude = e.latlng.lng;

        /*
         * Move o marcador do ninho.
         */

        if (marcador) {{
            marcador.setLatLng([
                latitude,
                longitude
            ]);
        }}

        /*
         * Move o círculo amarelo.
         */

        if (circulo) {{
            circulo.setLatLng([
                latitude,
                longitude
            ]);
        }}

        /*
         * Mantém o mapa centralizado na localização encontrada.
         */

        mapa.setView(
            [latitude, longitude],
            mapa.getZoom()
        );

    }});

}})();

</script>
"""

m.get_root().html.add_child(
    Element(gps_script)
)


# ============================================================
# EXIBIÇÃO DO MAPA
# ============================================================

map_data = st_folium(
    m,
    width=700,
    height=580,
    key="meu_mapa_abelhas",
    returned_objects=["last_clicked"]
)


# ============================================================
# CLIQUE NO MAPA
# ============================================================

if map_data and map_data.get("last_clicked"):

    clicado = map_data["last_clicked"]

    nova_lat = float(clicado["lat"])
    nova_lon = float(clicado["lng"])

    diferenca_lat = abs(
        nova_lat - st.session_state.lat
    )

    diferenca_lon = abs(
        nova_lon - st.session_state.lon
    )

    if diferenca_lat > 0.000001 or diferenca_lon > 0.000001:

        st.session_state.lat = nova_lat
        st.session_state.lon = nova_lon

        st.rerun()


# ============================================================
# INFORMAÇÕES
# ============================================================

st.markdown("### 🐝 Informações do forrageamento")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Espécie",
        especie.split(" (")[0]
    )

with col2:

    st.metric(
        "Raio estimado",
        f"{raio_metros} m"
    )

with col3:

    st.metric(
        "Área aproximada",
        f"{area_km2:.2f} km²"
    )


st.info(
    """
    O círculo representa uma estimativa geométrica do raio de
    forrageamento da espécie selecionada.

    Ele não significa que a abelha necessariamente utilizará
    todos os pontos dentro do círculo. A disponibilidade de
    flores, água, obstáculos, clima, competição e outros fatores
    podem influenciar o deslocamento real das abelhas.
    """
)


# ============================================================
# COMO USAR
# ============================================================

st.success(
    """
    **Como usar:**

    📍 Use o botão GPS dentro do mapa para localizar o dispositivo.

    🖱️ Clique diretamente no mapa para escolher manualmente
    o local do ninho.

    🔎 Pesquise um endereço para posicionar o ninho.

    ✏️ Ou informe latitude e longitude manualmente.

    🗺️ Arraste o mapa livremente para explorar a região.
    O ninho não será alterado ao movimentar o mapa.
    """
)


# ============================================================
# APOIE O PROJETO
# ============================================================

st.markdown(
    """
    <div class="pix-card">

    <h3>💚 Apoie o projeto</h3>

    Se esta ferramenta for útil para você e quiser ajudar
    na continuidade do projeto:

    <br><br>

    <b>Favorecido:</b><br>
    Paulo Eduardo Castelo Branco Geraldo

    <br><br>

    <b>Banco:</b><br>
    Nubank

    <br><br>

    <b>Chave Pix:</b><br>
    02450e96-4a41-4b62-8275-0b741c23a42b

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AGRADECIMENTO
# ============================================================

st.success(
    "Maria Alice R. M. Castelo Branco e Paulo Eduardo Castelo Branco"
)


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="rodape">
    Ferramenta experimental desenvolvida para auxiliar
    meliponicultores na observação da área de forrageamento.
    </div>
    """,
    unsafe_allow_html=True
)

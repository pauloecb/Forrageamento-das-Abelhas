import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation

# Configuração da página do app
st.set_page_config(page_title="Rastreador de Abelhas", page_icon="🐝", layout="centered")

# Injetando metadados de PWA para forçar o nome correto no celular
st.markdown(
    """
    <head>
        <meta name="apple-mobile-web-app-title" content="Rastreador de Abelhas">
        <meta name="application-name" content="Rastreador de Abelhas">
        <link rel="manifest" href="data:application/manifest+json;charset=utf-8,{
            'name': 'Rastreador de Abelhas',
            'short_name': 'Abelhas',
            'start_url': '.',
            'display': 'standalone',
            'background_color': '#ffffff',
            'theme_color': '#FF4B4B'
        }">
    </head>
    """,
    unsafe_allow_html=True
)

st.title("🌿 Rastreador de Forrageamento")
st.markdown("Descubra o raio de alcance das abelhas nativas a partir da sua localização.")

# Dicionário completo de espécies e raios em ordem alfabética
especies_abelhas = {
    "Jataí-Acriana (Tetragonisca weyrauchi)":500,
    "Boiassu (Melipona interrupta)": 1500,
    "Bugia (Melipona bicolor)": 1000,
    "Canudo (Scaptotrigona depilis)": 1500,
    "Guaraipo (Melipona bicolor schencki)": 1000,
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
    "Mirim-droryana (Plebeia droryana)": 400,
    "Mirim-preguiça (Frieseomelitta varia)": 500,
    "Mombucão (Cephalotrigona capitata)": 1000,
    "Mosquito / Abelha-cachorro (Lestrimelitta limao)": 1000,
    "Rabo-de-tatu (Nannotrigona punctata)": 500,
    "Tiúba (Melipona fasciculata)": 1500,
    "Tubuna (Scaptotrigona bipunctata)": 1500,
    "Uruçu-amarela (Melipona rufiventris)": 1500,
    "Uruçu-cinzenta (Melipona fasciculata)": 1500,
    "Uruçu-do-chão (Melipona capixaba)": 1500,
    "Uruçu-nordestina (Melipona scutellaris)": 1500,
    "Uruçu-True / Amarela (Melipona flavolineata)": 1500
}

# Inicializador do Geopy
geolocator = Nominatim(user_agent="raio_abelhas_app")

# Seção principal bem visível
st.subheader("1️⃣ Escolha a Espécie de Abelha")
especie_escolhida = st.selectbox(
    "Selecione na lista abaixo:", 
    sorted(list(especies_abelhas.keys())),
    label_visibility="collapsed"
)
raio_metros = especies_abelhas[especie_escolhida]

st.info(f"🎯 Raio de alcance estimado para a **{especie_escolhida}**: **{raio_metros} metros**.")

st.markdown("---")
st.subheader("2️⃣ Localização do Ninho")

# Botão de GPS do dispositivo
st.markdown("**Opção A: Usar GPS do celular/computador**")
loc_gps = streamlit_geolocation()

# Coordenadas padrão iniciais (Rio de Janeiro)
lat_padrao, lon_padrao = -22.9068, -43.1729

# Se o GPS retornou coordenadas válidas
if loc_gps and loc_gps.get('latitude') and loc_gps.get('longitude'):
    lat_padrao = loc_gps['latitude']
    lon_padrao = loc_gps['longitude']
    st.success("📍 Localização obtida via GPS com sucesso!")

# Opção de busca por endereço
endereco_busca = st.text_input("🔍 **Opção B: Ou digite o endereço / cidade:**")

if endereco_busca:
    try:
        loc = geolocator.geocode(endereco_busca)
        if loc:
            lat_padrao = loc.latitude
            lon_padrao = loc.longitude
            st.success(f"Encontrado: {loc.address[:50]}...")
        else:
            st.error("Endereço não encontrado.")
    except Exception:
        st.error("Erro ao buscar endereço.")

# Inputs manuais diretos e limpos
lat_inicial = st.number_input("Latitude", value=lat_padrao, format="%.6f")
lon_inicial = st.number_input("Longitude", value=lon_padrao, format="%.6f")

# Inicializando estado da sessão
if 'lat' not in st.session_state:
    st.session_state.lat = lat_inicial
    st.session_state.lon = lon_inicial

# Atualiza se houver mudança relevante
if st.session_state.lat != lat_inicial or st.session_state.lon != lon_inicial:
    st.session_state.lat = lat_inicial
    st.session_state.lon = lon_inicial

st.markdown("### 🗺️ Mapa de Forrageamento")
st.markdown("💡 *Toque no mapa para reposicionar o ninho.*")

# Criando o mapa base
m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15, tiles="CartoDB positron")

# Camada de satélite
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Visão de Satélite'
).add_to(m)

# Marcador que se move conforme o clique
folium.Marker(
    location=[st.session_state.lat, st.session_state.lon],
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# Círculo de forrageamento
folium.Circle(
    location=[st.session_state.lat, st.session_state.lon],
    radius=raio_metros,
    color='yellow',
    fill=True,
    fill_color='orange',
    fill_opacity=0.3
).add_to(m)

# Captura o clique
output = st_folium(m, width=700, height=450)

if output and output.get("last_clicked"):
    new_lat = output["last_clicked"]["lat"]
    new_lon = output["last_clicked"]["lng"]
    
    # Verifica se a coordenada mudou significativamente
    if abs(new_lat - st.session_state.lat) > 0.000001 or abs(new_lon - st.session_state.lon) > 0.000001:
        st.session_state.lat = new_lat
        st.session_state.lon = new_lon
        st.rerun()

# --- SEÇÃO DE APOIO E DOAÇÃO VIA PIX ---
# (Manter o restante do código igual a partir daqui...)
# --- SEÇÃO DE APOIO E DOAÇÃO VIA PIX ---
st.markdown("---")
st.markdown("### ☕ Apoie este Projeto")
st.markdown(
    "Este aplicativo é **100% gratuito** e desenvolvido para apoiar a meliponicultura, "
    "a pesquisa e o manejo consciente das nossas abelhas nativas. "
    "Se a ferramenta foi útil para você e quiser colaborar com a manutenção do projeto, "
    "qualquer contribuição via Pix é muito bem-vinda!"
)

st.markdown("**Dados para Doação via Pix:**")
st.write("👤 **Favorecido:** Paulo Eduardo Castelo Branco Geraldo")
st.write("🏦 **Banco:** Nubank")
st.markdown("🔑 **Chave Pix (Toque no campo abaixo para copiar):**")
st.code("02450e96-4a41-4b62-8275-0b741c23a42b", language="text")

st.success("💛 **Muito obrigado por apoiar a preservação das abelhas nativas e a meliponicultura!** 🐝")

import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from streamlit_geolocation import streamlit_geolocation

# Configuração da página do app
st.set_page_config(page_title="Raios de Forrageamento de Abelhas", layout="centered")

st.title("🌿 Rastreador de Forrageamento")
st.markdown("Descubra o raio de alcance das abelhas nativas a partir da sua localização.")

# Dicionário completo de espécies e raios em ordem alfabética
especies_abelhas = {
    "Apis mellifera (Abelha com ferrão / Europa/Africana)": 2500,
    "Boiassu (Melipona interrupta)": 1500,
    "Bugia (Melipona bicolor)": 1000,
    "Canudo (Scaptotrigona depilis)": 1500,
    "Cephalotrigona capitata (Mombucão)": 1000,
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

# Seção principal bem visível (Sem menu lateral escondido)
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

# Criando colunas para os botões de localização ficarem organizados no celular
col_gps, col_end = st.columns(1)

with col_gps:
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

# Ajuste fino opcional de coordenadas
with st.expander("⚙️ Ajustar coordenadas manualmente (Opcional)"):
    lat_inicial = st.number_input("Latitude", value=lat_padrao, format="%.6f")
    lon_inicial = st.number_input("Longitude", value=lon_padrao, format="%.6f")
else:
    lat_inicial, lon_inicial = lat_padrao, lon_padrao

# Inicializando estado da sessão
if 'lat' not in st.session_state:
    st.session_state.lat = lat_inicial
    st.session_state.lon = lon_inicial

# Atualiza se houver mudança relevante
if st.session_state.lat != lat_inicial or st.session_state.lon != lon_inicial:
    st.session_state.lat = lat_inicial
    st.session_state.lon = lon_inicial

st.markdown("---")
st.markdown("### 🗺️ Mapa de Forrageamento")
st.markdown("💡 *Toque no mapa para reposicionar o ninho se preferir.*")

# Criando o mapa base
m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=15, tiles="CartoDB positron")

# Adicionar camada de Satélite (Esri World Imagery)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Visão de Satélite',
    overlay=False,
    control=True
).add_to(m)

# Adicionando o círculo de forrageamento
folium.Circle(
    location=[st.session_state.lat, st.session_state.lon],
    radius=raio_metros,
    color='yellow',
    fill=True,
    fill_color='orange',
    fill_opacity=0.3,
    popup=f"{especie_escolhida} - Raio: {raio_metros}m"
).add_to(m)

# Marcador do Ninho
folium.Marker(
    location=[st.session_state.lat, st.session_state.lon],
    popup="Localização do Ninho",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# Exibir o mapa no Streamlit
output = st_folium(m, width=700, height=450, key="mapa_abelhas")

# Se o usuário clicar no mapa, atualizamos as coordenadas
if output and output.get("last_clicked"):
    clicked_lat = output["last_clicked"]["lat"]
    clicked_lon = output["last_clicked"]["lng"]
    if clicked_lat != st.session_state.lat or clicked_lon != st.session_state.lon:
        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lon
        st.rerun()

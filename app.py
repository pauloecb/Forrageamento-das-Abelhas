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

# Seção principal bem visível
st.subheader("1️⃣ Escolha a Espécie de Abelha")
especie_escolhida = st.selectbox(
    "Selecione na lista abaixo:", 
    sorted(list(especies_abelhas.keys())),
    label_visibility="collapsed"
)
raio_metros = especies_abelhas[especie_escolhida]

# Resumo e aviso colaborativo
st.info(f"🎯 Raio de alcance estimado para a **{especie_escolhida}**: **{raio_metros} metros**.")

st.markdown(
    """
    <div style="background-color: #f0f8ff; padding: 12px; border-radius: 5px; border-left: 5px solid #2196f3; margin-bottom: 20px;">
        🐝 <b>Não encontrou alguma abelha?</b><br>
        Envie um e-mail para <a href="mailto:paulo_eduardo_cb@hotmail.com">paulo_eduardo_cb@hotmail.com</a> 
        com o nome da abelha para que possamos adicionar.
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("---")
st.subheader("2️⃣ Localização do Ninho")

# Inicializa o session_state se não existir (Coordenadas padrão: Rio de Janeiro)
if 'lat' not in st.session_state:
    st.session_state.lat = -22.9068
if 'lon' not in st.session_state:
    st.session_state.lon = -43.1729
if 'last_gps_lat' not in st.session_state:
    st.session_state.last_gps_lat = None
if 'last_gps_lon' not in st.session_state:
    st.session_state.last_gps_lon = None

# Botão de GPS do dispositivo
st.markdown("**Opção A: Usar GPS do celular/computador**")
loc_gps = streamlit_geolocation()

if loc_gps and loc_gps.get('latitude') and loc_gps.get('longitude'):
    g_lat = loc_gps['latitude']
    g_lon = loc_gps['longitude']
    # Só atualiza se for um novo sinal de GPS real para evitar looping
    if g_lat != st.session_state.last_gps_lat or g_lon != st.session_state.last_gps_lon:
        st.session_state.last_gps_lat = g_lat
        st.session_state.last_gps_lon = g_lon
        st.session_state.lat = g_lat
        st.session_state.lon = g_lon
        st.success("📍 Localização obtida via GPS com sucesso!")

# Opção de busca por endereço
endereco_busca = st.text_input("🔍 **Opção B: Ou digite o endereço / cidade:**")

if endereco_busca:
    try:
        loc = geolocator.geocode(endereco_busca)
        if loc:
            st.session_state.lat = loc.latitude
            st.session_state.lon = loc.longitude
            st.success(f"Encontrado: {loc.address[:50]}...")
        else:
            st.error("Endereço não encontrado.")
    except Exception:
        st.error("Erro ao buscar endereço.")

# Inputs manuais atrelados diretamente ao session_state
lat_inicial = st.number_input("Latitude", value=float(st.session_state.lat), format="%.6f")
lon_inicial = st.number_input("Longitude", value=float(st.session_state.lon), format="%.6f")

# Se o usuário alterou manualmente nos números, atualiza o estado
if lat_inicial != st.session_state.lat or lon_inicial != st.session_state.lon:
    st.session_state.lat = lat_inicial
    st.session_state.lon = lon_inicial

st.markdown("---")
st.markdown("### 🗺️ Mapa de Forrageamento")
st.markdown("💡 *Toque no mapa para reposicionar o ninho.*")

# Definindo o centro atual do mapa
centro_mapa = [st.session_state.lat, st.session_state.lon]

# Criando o mapa base
m = folium.Map(location=centro_mapa, zoom_start=15, tiles="CartoDB positron")

# Adicionar camada de Satélite (Esri World Imagery)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Visão de Satélite',
    overlay=False,
    control=True
).add_to(m)

# Marcador do Ninho
folium.Marker(
    location=centro_mapa,
    popup="Localização do Ninho",
    icon=folium.Icon(color="green", icon="home", prefix="fa")
).add_to(m)

# Adicionando o círculo de forrageamento
folium.Circle(
    location=centro_mapa,
    radius=raio_metros,
    color='yellow',
    fill=True,
    fill_color='orange',
    fill_opacity=0.3,
    popup=f"{especie_escolhida} - Raio: {raio_metros}m"
).add_to(m)

# Exibir o mapa no Streamlit com chave única
output = st_folium(m, width=700, height=450, key="meu_mapa_abelhas")

# Se o usuário clicar no mapa, atualizamos as coordenadas no session_state e recarregamos imediatamente
if output and output.get("last_clicked"):
    clicked_lat = output["last_clicked"]["lat"]
    clicked_lon = output["last_clicked"]["lng"]
    if clicked_lat != st.session_state.lat or clicked_lon != st.session_state.lon:
        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lon
        st.rerun()

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

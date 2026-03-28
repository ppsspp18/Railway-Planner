import streamlit as st
import requests
from datetime import datetime

# ==========================================
# MAPPINGS
# ==========================================
STATION_MAP = {
    "New Delhi": "NDLS", "Kanpur Central": "CNB", "Lucknow NR": "LKO",
    "Varanasi Jn": "BSB", "Prayagraj Jn": "PRYJ", "Agra Cantt": "AGC",
    "Mathura Jn": "MTJ", "VGL Jhansi": "VGLJ", "Gwalior Jn": "GWL",
    "Bhopal Jn": "BPL", "Patna Jn": "PNBE", "Ayodhya Cantt": "AYC",
    "Gorakhpur Jn": "GKP", "Moradabad Jn": "MB", "Bareilly Jn": "BE"
}

CODE_TO_NAME = {code: f"{name} ({code})" for name, code in STATION_MAP.items()}
STATION_DISPLAY_LIST = list(CODE_TO_NAME.values())

TRAIN_MAP = {
    22436: "New Delhi - Varanasi Vande Bharat Express", 22435: "Varanasi - New Delhi Vande Bharat Express",
    12004: "New Delhi - Lucknow Swarna Shatabdi", 12003: "Lucknow - New Delhi Swarna Shatabdi",
    12310: "New Delhi - Patna Tejas Rajdhani", 12309: "Patna - New Delhi Tejas Rajdhani",
    12002: "New Delhi - Bhopal Shatabdi", 12001: "Bhopal - New Delhi Shatabdi",
    20172: "New Delhi - VGL Jhansi Vande Bharat", 20171: "VGL Jhansi - New Delhi Vande Bharat",
    22416: "New Delhi - Varanasi Mahamana Express", 22415: "Varanasi - New Delhi Mahamana Express",
    12418: "New Delhi - Prayagraj Prayagraj Express", 12417: "Prayagraj - New Delhi Prayagraj Express",
    12420: "New Delhi - Lucknow Gomti Express", 12419: "Lucknow - New Delhi Gomti Express",
    12226: "New Delhi - Ayodhya Kaifiyat Express", 12225: "Ayodhya - New Delhi Kaifiyat Express",
    12556: "New Delhi - Gorakhpur Gorakhdham Express", 12555: "Gorakhpur - New Delhi Gorakhdham Express",
    12566: "New Delhi - Bihar Sampark Kranti", 12565: "Bihar - New Delhi Sampark Kranti",
    14206: "New Delhi - Ayodhya Express", 14205: "Ayodhya - New Delhi Express",
    14208: "New Delhi - Bareilly Padmavat Express", 14207: "Bareilly - New Delhi Padmavat Express",
    14316: "New Delhi - Bareilly Intercity Express", 14315: "Bareilly - New Delhi Intercity Express",
    12230: "New Delhi - Lucknow Mail", 12229: "Lucknow - New Delhi Mail",
    12452: "New Delhi - Kanpur Shram Shakti Express", 12451: "Kanpur - New Delhi Shram Shakti Express",
    11109: "VGL Jhansi - Lucknow Intercity", 11110: "Lucknow - VGL Jhansi Intercity",
    14115: "Prayagraj - Mathura Express", 14116: "Mathura - Prayagraj Express",
    22454: "Meerut - Lucknow Rajya Rani Express", 22453: "Lucknow - Meerut Rajya Rani Express",
    13240: "Mathura - Patna Kota Express", 13239: "Patna - Mathura Kota Express",
    15003: "Kanpur - Gorakhpur Chauri Chaura Express", 15004: "Gorakhpur - Kanpur Chauri Chaura Express",
    15011: "Lucknow - Mathura Express", 15012: "Mathura - Lucknow Express",
    12280: "New Delhi - Gwalior Taj Express", 12279: "Gwalior - New Delhi Taj Express",
    12190: "Mathura - Bhopal Mahakoshal Express", 12189: "Bhopal - Mathura Mahakoshal Express",
    11058: "Mathura - VGL Jhansi Pathankot Express", 11057: "VGL Jhansi - Mathura Pathankot Express",
    12192: "New Delhi - Bhopal Shridham Express", 12191: "Bhopal - New Delhi Shridham Express",
    14212: "New Delhi - Agra Intercity", 14211: "Agra - New Delhi Intercity",
    15128: "Varanasi - Patna Kashi Vishwanath Express", 15127: "Patna - Varanasi Kashi Vishwanath Express",
    14224: "Varanasi - Ayodhya Budhpurnima Express", 14223: "Ayodhya - Varanasi Budhpurnima Express",
    15022: "Gorakhpur - Patna Maurya Express", 15021: "Patna - Gorakhpur Maurya Express",
    12530: "Lucknow - Patna Patliputra Express", 12529: "Patna - Lucknow Patliputra Express",
    14232: "Lucknow - Prayagraj Ganga Gomti Express", 14231: "Prayagraj - Lucknow Ganga Gomti Express",
    12034: "New Delhi - Kanpur Shatabdi", 12033: "Kanpur - New Delhi Shatabdi",
    12232: "Moradabad - Lucknow Superfast", 12231: "Lucknow - Moradabad Superfast",
    14308: "Bareilly - Prayagraj Express", 14307: "Prayagraj - Bareilly Express",
    14218: "Prayagraj - Varanasi Unchahar Express", 14217: "Varanasi - Prayagraj Unchahar Express",
    15104: "Gorakhpur - Varanasi Intercity", 15103: "Varanasi - Gorakhpur Intercity",
    15106: "Ayodhya - Gorakhpur Express", 15105: "Gorakhpur - Ayodhya Express",
    14260: "Lucknow - Varanasi Ekatmata Express", 14259: "Varanasi - Lucknow Ekatmata Express",
    12184: "Bhopal - Prayagraj Superfast", 12183: "Prayagraj - Bhopal Superfast",
    12294: "Prayagraj - Patna Duronto", 12293: "Patna - Prayagraj Duronto",
    12430: "New Delhi - Moradabad Garib Rath", 12429: "Moradabad - New Delhi Garib Rath",
    15044: "Lucknow - Gorakhpur Kathgodam Express", 15043: "Gorakhpur - Lucknow Kathgodam Express",
    14214: "Gwalior - Ayodhya Express", 14213: "Ayodhya - Gwalior Express",
    14112: "VGL Jhansi - Prayagraj Express", 14111: "Prayagraj - VGL Jhansi Express",
    12582: "New Delhi - Varanasi Shiv Ganga Express", 12581: "Varanasi - New Delhi Shiv Ganga Express",
    12596: "Gorakhpur - Ayodhya Humsafar", 12595: "Ayodhya - Gorakhpur Humsafar",
    11124: "Gwalior - Bareilly Express", 11123: "Bareilly - Gwalior Express",
    14322: "Bareilly - Varanasi Express", 14321: "Varanasi - Bareilly Express",
    14228: "Lucknow - Ayodhya Saryu Yamuna Express", 14227: "Ayodhya - Lucknow Saryu Yamuna Express"
}

def format_dt(dt_str):
    """Converts '2026-04-01 15:30' into '15:30, Apr 01'"""
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    return dt.strftime("%H:%M, %b %d")

# ==========================================
# UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="AI Routing", layout="centered")

st.title("🚂 Smart Routing")
st.markdown("Find the most reliable and fastest train routes with predictive waitlist analytics.")

# Selectboxes are searchable by default! Click and type "Kanpur"
col1, col2, col3 = st.columns(3)
with col1:
    src_display = st.selectbox("Source Station", STATION_DISPLAY_LIST, index=0)
with col2:
    dest_display = st.selectbox("Destination Station", STATION_DISPLAY_LIST, index=3)
with col3:
    date = st.date_input("Date of Journey", min_value=datetime(2026, 4, 1), max_value=datetime(2026, 4, 10))

if st.button("Search Best Routes", type="primary", use_container_width=True):
    if src_display == dest_display:
        st.error("Source and destination cannot be the same!")
    else:
        src_code = src_display.split("(")[-1].replace(")", "")
        dest_code = dest_display.split("(")[-1].replace(")", "")
        
        with st.spinner("Calculating optimal paths & probabilities..."):
            try:
                res = requests.get(f"http://127.0.0.1:8000/routes?src={src_code}&dest={dest_code}&date={date.strftime('%Y-%m-%d')}")
                data = res.json()
                
                if not data.get("routes"):
                    st.warning("No valid routes found (Direct or 1-Stop) matching constraints.")
                else:
                    for i, route in enumerate(data["routes"]):
                        hours = int(route['total_time_mins'] // 60)
                        mins = int(route['total_time_mins'] % 60)
                        prob_color = "green" if route['overall_prob'] > 80 else "orange" if route['overall_prob'] > 40 else "red"
                        
                        header_title = f"Option {i+1}: {route['type']} | {hours}h {mins}m | Probability: {route['overall_prob']}%"
                        
                        with st.expander(header_title, expanded=(i==0)):
                            st.markdown(f"**Overall Confirmation Confidence:** :{prob_color}[{route['overall_prob']}%]")
                            st.divider()
                            
                            legs = route['route_legs']
                            
                            # Render Train 1
                            t1 = legs[0]
                            st.markdown(f"🚆 **Train 1: {t1['train']} - {TRAIN_MAP.get(t1['train'], 'Express')}**")
                            st.write(f"**{CODE_TO_NAME[t1['src']]}** ({format_dt(t1['dep_dt'])}) ➔ **{CODE_TO_NAME[t1['dest']]}** ({format_dt(t1['arr_dt'])})")
                            st.write(f"Status: `{t1['status']}`")
                            
                            # Render Layover and Train 2 if it exists
                            if len(legs) > 1:
                                t2 = legs[1]
                                trans_hrs = int(route['transfer_mins'] // 60)
                                trans_mins = int(route['transfer_mins'] % 60)
                                
                                st.info(f"⏳ **Layover at {CODE_TO_NAME[t1['dest']]}: {trans_hrs}h {trans_mins}m**")
                                
                                st.markdown(f"🚆 **Train 2: {t2['train']} - {TRAIN_MAP.get(t2['train'], 'Express')}**")
                                st.write(f"**{CODE_TO_NAME[t2['src']]}** ({format_dt(t2['dep_dt'])}) ➔ **{CODE_TO_NAME[t2['dest']]}** ({format_dt(t2['arr_dt'])})")
                                st.write(f"Status: `{t2['status']}`")
            
            except Exception as e:
                st.error(f"Failed to connect to backend. Make sure the FastAPI server is running! Error: {e}")
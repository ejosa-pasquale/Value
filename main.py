import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="AI-Josa - Valutazione Rendimento", layout="wide", page_icon="📊")
st.title("📊 Valutazione Rendimento Punto di Ricarica")

# ---- CSS PERSONALIZZATO ----
st.markdown("""
<style>
    .metric-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 14px;
        color: #555;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .stProgress > div > div > div {
        background-color: #27ae60;
    }
    .stSlider > div > div > div {
        background-color: #3498db;
    }
    .stExpander > div {
        border: 1px solid #eee !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def calculate_charging_point_performance(params):
    potenza_totale_kw = (
        params['ac_22'] * 22 + params['dc_20'] * 20 + params['dc_30'] * 30 +
        params['dc_40'] * 40 + params['dc_60'] * 60 + params['dc_90'] * 90
    )
    
    energia_massima_giorno = potenza_totale_kw * params['ore_disponibili'] * (params['utilizzo_percentuale'] / 100)
    energia_richiesta_totale = params['num_auto_giorno'] * params['kwh_per_auto']
    energia_erogata_giorno = min(energia_massima_giorno, energia_richiesta_totale)
    energia_erogata_annuo = energia_erogata_giorno * params['giorni_attivi']
    
    auto_servite = int(energia_erogata_giorno // params['kwh_per_auto'])
    auto_non_servite = max(0, params['num_auto_giorno'] - auto_servite)
    guadagno_annuo = energia_erogata_annuo * params['prezzo_vendita']
    
    costo_colonnine = (
        params['ac_22'] * 1000 + params['dc_20'] * 8000 + params['dc_30'] * 12000 +
        params['dc_40'] * 15000 + params['dc_60'] * 18000 + params['dc_90'] * 25000
    )
    costo_installazione = potenza_totale_kw * 150
    costo_totale = costo_colonnine + costo_installazione
    ROI = guadagno_annuo / costo_totale if costo_totale > 0 else 0
    
    # Calcolo tasso di utilizzo effettivo
    tasso_utilizzo_effettivo = (energia_erogata_giorno / energia_massima_giorno) * 100 if energia_massima_giorno > 0 else 0
    
    return {
        'potenza_totale_kw': potenza_totale_kw,
        'energia_erogata_annuo': energia_erogata_annuo,
        'auto_servite': auto_servite,
        'auto_non_servite': auto_non_servite,
        'guadagno_annuo': guadagno_annuo,
        'costo_totale': costo_totale,
        'ROI': ROI,
        'entro_budget': costo_totale <= params['budget'],
        'tasso_utilizzo': tasso_utilizzo_effettivo
    }

# ---- INTERFACCIA ----
st.subheader("Parametri di Utilizzo")
    
with st.expander("Parametri base", expanded=True):
    num_auto_giorno = st.slider("Auto previste in ricarica al giorno", 1, 1000, 50, step=5)
    kwh_per_auto = st.slider("Energia media richiesta per auto (kWh)", 5, 100, 30, step=5)
    tempo_ricarica_media = st.slider("Tempo medio di ricarica per auto (ore)", 0.5, 12.0, 2.0, step=0.5)
    
with st.expander("Configurazione temporale", expanded=False):
    ore_disponibili = st.slider("Ore operative al giorno", 1, 24, 8, step=1)
    giorni_attivi = st.slider("Giorni operativi all'anno", 1, 365, 260, step=5)
    
with st.expander("Parametri economici", expanded=False):
    prezzo_vendita = st.slider("Prezzo di vendita energia (€/kWh)", 0.10, 1.00, 0.25, step=0.05)
    utilizzo_percentuale = st.slider("Probabilità di utilizzo dell'infrastruttura (%)", 10, 100, 85, step=5)
    budget = st.number_input("Investimento Iniziale (€)", 0, 500000, 20000, step=1000)
    
st.subheader("Configurazione Colonnine")
with st.expander("Seleziona tipologie di colonnine", expanded=True):
    ac_22 = st.slider("AC_22 (22 kW)", 0, 50, 2)
    dc_20 = st.slider("DC_20 (20 kW)", 0, 20, 0)
    dc_30 = st.slider("DC_30 (30 kW)", 0, 20, 0)
    dc_40 = st.slider("DC_40 (40 kW)", 0, 20, 0)
    dc_60 = st.slider("DC_60 (60 kW)", 0, 20, 0)
    dc_90 = st.slider("DC_90 (90 kW)", 0, 20, 0)
    
if st.button("📊 Calcola Rendimento Punto di Ricarica", type="primary"):
    params = {
        'num_auto_giorno': num_auto_giorno,
        'kwh_per_auto': kwh_per_auto,
        'tempo_ricarica_media': tempo_ricarica_media,
        'ore_disponibili': ore_disponibili,
        'giorni_attivi': giorni_attivi,
        'prezzo_vendita': prezzo_vendita,
        'utilizzo_percentuale': utilizzo_percentuale,
        'budget': budget,
        'ac_22': ac_22,
        'dc_20': dc_20,
        'dc_30': dc_30,
        'dc_40': dc_40,
        'dc_60': dc_60,
        'dc_90': dc_90
    }
    
    risultati = calculate_charging_point_performance(params)
    
    st.success("Analisi di rendimento completata!")
    st.divider()
    
    # Metriche principali
    col1, col2, col3 = st.columns(3)
    col1.metric("Potenza totale installata", f"{risultati['potenza_totale_kw']} kW")
    col2.metric("Energia erogata annuale", f"{risultati['energia_erogata_annuo']:,.0f} kWh")
    col3.metric("Auto servite giornaliere", f"{risultati['auto_servite']}/{num_auto_giorno}")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Ricavo annuo stimato", f"€{risultati['guadagno_annuo']:,.0f}")
    col5.metric("Costo totale impianto", f"€{risultati['costo_totale']:,.0f}", 
               "entro budget" if risultati['entro_budget'] else "sopra budget")
    col6.metric("Tasso di utilizzo effettivo", f"{risultati['tasso_utilizzo']:.1f}%")
    
    # ROI e Payback
    st.divider()
    st.subheader("Indicatori Economici")
    
    roi_col, payback_col, util_col = st.columns(3)
    roi_col.metric("ROI (Return on Investment)", f"{risultati['ROI']:.2f}")
    payback_col.metric("Periodo di Payback", f"{(1/risultati['ROI'] if risultati['ROI']>0 else 0):.1f} anni")
    util_col.metric("Efficienza Impianto", f"{risultati['tasso_utilizzo']:.1f}%")
    
    # Visualizzazione grafica
    with st.expander("Visualizzazione Dettagliata", expanded=True):
        fig_col1, fig_col2 = st.columns(2)
        
        with fig_col1:
            df_auto = pd.DataFrame({
                'Categoria': ['Auto servite', 'Auto non servite'],
                'Valore': [risultati['auto_servite'], risultati['auto_non_servite']]
            })
            fig = px.pie(df_auto, values='Valore', names='Categoria', 
                        title="Distribuzione Auto Servite/Non Servite")
            st.plotly_chart(fig, use_container_width=True)
        
        with fig_col2:
            months = range(1, 13)
            monthly_energy = [risultati['energia_erogata_annuo'] / 12 * (0.9 + 0.2 * (i % 12)/12) for i in months]
            df_monthly = pd.DataFrame({'Mese': months, 'Energia (kWh)': monthly_energy})
            fig = px.line(df_monthly, x='Mese', y='Energia (kWh)', title="Energia Erogata Mensile Stimata")
            st.plotly_chart(fig, use_container_width=True)
    
    # Consigli di ottimizzazione
    with st.expander("Raccomandazioni", expanded=True):
        if risultati['tasso_utilizzo'] > 90:
            st.warning("⚠️ L'infrastruttura è sovrautilizzata. Considera:")
            st.markdown("- Aggiungere più colonnine")
            st.markdown("- Aumentare la potenza installata")
            st.markdown("- Estendere le ore operative")
        
        elif risultati['tasso_utilizzo'] < 50:
            st.info("ℹ️ L'infrastruttura è sottoutilizzata. Potresti:")
            st.markdown("- Ridurre il numero di colonnine")
            st.markdown("- Cercare di attrarre più clienti")
            st.markdown("- Offrire tariffe promozionali")
        
        if not risultati['entro_budget']:
            st.error("❌ L'investimento supera il budget. Considera:")
            st.markdown("- Ridurre il numero di colonnine DC ad alta potenza")
            st.markdown("- Optare per più colonnine AC a minor costo")
            st.markdown("- Frazionare l'investimento in più fasi")
        
        if risultati['auto_non_servite'] > 0:
            st.warning(f"🔌 {risultati['auto_non_servite']} auto al giorno non possono essere servite. Soluzioni:")
            st.markdown("- Aumentare la potenza delle colonnine")
            st.markdown("- Ottimizzare i tempi di ricarica")
            st.markdown("- Implementare un sistema di prenotazione")

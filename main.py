# --- Inserimento veicoli singoli o per gruppi ---
def input_veicoli():
    modo = st.sidebar.radio("Modalità inserimento veicoli", ["Singolo", "Per Gruppi"])
    veicoli = []
    if modo == "Per Gruppi":
        gruppi = st.sidebar.number_input("Numero gruppi", 1, 10, 2)
        for i in range(gruppi):
            with st.expander(f"Gruppo {i+1}"):
                n = st.number_input("Numero veicoli", 1, 100, 3, key=f"n_{i}")
                km = st.number_input("Km giornalieri", 0.0, 500.0, 60.0, key=f"km_{i}")
                consumo = st.number_input("Consumo kWh/km", 0.1, 1.0, 0.18, 0.01, key=f"cons_{i}")
                sosta = st.number_input("Ore sosta", 0.0, 24.0, 8.0, 0.25, key=f"sosta_{i}")
                for j in range(n):
                    veicoli.append({
                        "nome": f"G{i+1}_Auto{j+1}",
                        "energia": km * consumo * MARGINE_SICUREZZA_TEMPO,
                        "sosta": sosta,
                        "km": km,
                        "consumo": consumo
                    })
    else:
        n = st.sidebar.number_input("Numero veicoli singoli", 1, 100, 3)
        for i in range(n):
            with st.expander(f"Veicolo {i+1}"):
                nome = st.text_input("Nome", f"Auto_{i+1}", key=f"nome_{i}")
                km = st.number_input("Km giornalieri", 0.0, 500.0, 60.0, key=f"km_s_{i}")
                consumo = st.number_input("Consumo kWh/km", 0.1, 1.0, 0.18, 0.01, key=f"cons_s_{i}")
                sosta = st.number_input("Ore sosta", 0.0, 24.0, 8.0, 0.25, key=f"sosta_s_{i}")
                veicoli.append({
                    "nome": nome,
                    "energia": km * consumo * MARGINE_SICUREZZA_TEMPO,
                    "sosta": sosta,
                    "km": km,
                    "consumo": consumo
                })
    return veicoli



def mostra(risultati, best, veicoli, budget, prezzo_benzina, consumo_l_100km, prezzo_privato, prezzo_pubblico):
    import pandas as pd
    import streamlit as st

    st.subheader("📊 Configurazioni testate")
    df = pd.DataFrame(risultati)
    colonne = [c for c in ['AC_22', 'DC_20', 'DC_30', 'DC_40', 'DC_60', 'DC_90'] if c in df.columns]
    altre_colonne = [c for c in df.columns if c not in colonne]
    df = df[colonne + altre_colonne]
    if "Copertura" in df.columns and "Entro Budget" in df.columns:
        cols = df.columns.tolist()
        cols.insert(cols.index("Copertura") + 1, cols.pop(cols.index("Entro Budget")))
        df = df[cols]
    st.dataframe(df.style.format("€{:,.0f}", subset=["Costo Colonnine", "Costo Installazione", "Totale"]))

    if best:
        st.subheader("✅ Configurazione ottimale")
        st.write(f"Totale: €{best['Totale']:,.0f} | Budget: €{budget:,.0f}")
        for c in best["colonnine"]:
            st.write(f"{c['tipo']} → {', '.join(c['veicoli'])} – Ore rimaste: {c['ore']:.2f}")

    st.subheader("📈 KPI")
    GIORNI_ANNUI = 260
    COSTO_INSTALLAZIONE_KW = 150

    km_annui = sum([v["km"] for v in veicoli]) * GIORNI_ANNUI
    energia_annua = sum([v["energia"] for v in veicoli]) * GIORNI_ANNUI
    costo_benzina = km_annui / 100 * consumo_l_100km * prezzo_benzina
    costo_privato = energia_annua * prezzo_privato
    costo_pubblico = energia_annua * prezzo_pubblico
    risparmio = costo_benzina - costo_privato
    differenza_pubblico = costo_pubblico - costo_privato
    guadagno_5a = differenza_pubblico * 5
    tempo_ore = sum([v["energia"] / 22 for v in veicoli]) * GIORNI_ANNUI
    roi = risparmio / (energia_annua * COSTO_INSTALLAZIONE_KW)

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Risparmio vs Benzina", f"€{risparmio:,.0f}")
    col2.metric("🔌 Risparmio vs Pubblico", f"€{differenza_pubblico:,.0f}")
    col3.metric("📈 ROI", f"{roi:.2f}")
    st.metric("📊 Guadagno 5 anni", f"€{guadagno_5a:,.0f}")
    st.metric("⏳ Tempo di ricarica (ore/anno)", f"{tempo_ore:.1f}")


import streamlit as st
import pandas as pd

GIORNI_ANNUI = 260
MARGINE_SICUREZZA_TEMPO = 1.2
UTILIZZO_MASSIMO_DC = 0.85
COSTO_INSTALLAZIONE_KW = 150

COLONNINE = {
    "AC_22": {"potenza": 22, "costo": 1500, "overhead": 0.25},
    "DC_30": {"potenza": 30, "costo": 9500, "overhead": 0.5},
    "DC_60": {"potenza": 60, "costo": 21000, "overhead": 0.5},
    "DC_90": {"potenza": 90, "costo": 26000, "overhead": 0.5}
}

def crea_colonnine(config, ore_turno):
    out = []
    for tipo, n in config.items():
        potenza = COLONNINE[tipo]["potenza"]
        overhead = COLONNINE[tipo]["overhead"]
        ore = ore_turno * (UTILIZZO_MASSIMO_DC if "DC" in tipo else 1)
        for _ in range(n):
            out.append({"tipo": tipo, "potenza": potenza, "overhead": overhead, "ore": ore, "veicoli": []})
    return out

def ottimizza(veicoli, budget, ore_turno):
    risultati = []
    migliore = None

    for ac in range(1, 6):
        for dc_tipo in ["DC_30", "DC_60", "DC_90"]:
            for n_dc in range(0, 4):
                config = {"AC_22": ac, dc_tipo: n_dc}
                colonnine = crea_colonnine(config, ore_turno)
                serviti = 0
                for v in veicoli:
                    for c in colonnine:
                        t = v["energia"] / c["potenza"] + c["overhead"]
                        if t <= v["sosta"] and t <= c["ore"]:
                            c["ore"] -= t
                            c["veicoli"].append(v["nome"])
                            serviti += 1
                            break
                costo_col = sum(COLONNINE[t]["costo"] * n for t, n in config.items())
                costo_inst = sum(COLONNINE[t]["potenza"] * n * COSTO_INSTALLAZIONE_KW for t, n in config.items())
                totale = costo_col + costo_inst
                risultati.append({
                    "AC_22": ac, dc_tipo: n_dc, "Serviti": serviti,
                    "Costo Colonnine": costo_col, "Installazione": costo_inst,
                    "Totale": totale, "Copertura": "✅" if serviti == len(veicoli) else "❌",
                    "Entro Budget": "✅" if totale <= budget else "❌"
                })
                if serviti == len(veicoli) and totale <= budget:
                    if migliore is None or totale < migliore[-1]:
                        migliore = (config, colonnine, costo_col, costo_inst, totale)

    return risultati, migliore


def modalita_comodita(veicoli, ore_turno):
    n_tot = len(veicoli)
    n_ac = int(n_tot * 0.7 + 0.999)
    veicoli_ac = veicoli[:n_ac]
    veicoli_restanti = veicoli[n_ac:]

    config = {"AC_22": n_ac}

    # Ora analizziamo chi tra i restanti ha bisogno di una DC
    dc_usata = None
    veicoli_dc = []

    for v in veicoli_restanti:
        tempo_ac = v["energia"] / COLONNINE["AC_22"]["potenza"] + COLONNINE["AC_22"]["overhead"]
        if tempo_ac > v["sosta"]:
            veicoli_dc.append(v)

    # Se almeno un veicolo richiede DC, scegliamo la più piccola sufficiente
    if veicoli_dc:
        for dc_tipo in ["DC_20", "DC_30", "DC_40", "DC_60", "DC_90"]:
            potenza = COLONNINE[dc_tipo]["potenza"]
            overhead = COLONNINE[dc_tipo]["overhead"]
            ore_massime = ore_turno * UTILIZZO_MASSIMO_DC
            totale_tempo = sum(v["energia"] / potenza + overhead for v in veicoli_dc)

            if totale_tempo <= ore_massime:
                config[dc_tipo] = 1
                dc_usata = dc_tipo
                break

    colonnine = crea_colonnine(config, ore_turno)
    copre, _ = assegna(veicoli, colonnine)
    c1 = sum(COLONNINE[t]["costo"] * n for t, n in config.items())
    c2 = sum(COLONNINE[t]["potenza"] * n * COSTO_INSTALLAZIONE_KW for t, n in config.items())
    totale = c1 + c2

    return {
        **config,
        "Totale Colonnine": sum(config.values()),
        "Copertura": "✅" if copre else "❌",
        "Costo Colonnine": c1,
        "Costo Installazione": c2,
        "Totale": totale,
        "Configurazione": colonnine
    }


    for dc_tipo in ["DC_30", "DC_60", "DC_90"]:
        potenza = COLONNINE[dc_tipo]["potenza"]
        overhead = COLONNINE[dc_tipo]["overhead"]
        ore_max = ore_turno * UTILIZZO_MASSIMO_DC
        servibili = all((v["energia"] / potenza + overhead <= v["sosta"] and v["energia"] / potenza + overhead <= ore_max) for v in veicoli_dc)
        if servibili:
            config[dc_tipo] = 1
            break

    colonnine = crea_colonnine(config, ore_turno)
    return config, colonnine, 0, 0, sum(COLONNINE[t]["costo"] * n + COLONNINE[t]["potenza"] * n * COSTO_INSTALLAZIONE_KW for t, n in config.items())

def main():
    st.set_page_config(page_title="AI-Josa", layout="wide")
    st.title("⚡ AI-Josa – Simulatore Infrastruttura EV")

    st.sidebar.selectbox("Modalità", ["Ottimizzazione", "Comodità", "Testa la tua infrastruttura", "Valuta il tuo investimento"])
    ore_turno = st.sidebar.number_input("🕒 Ore colonnina/giorno", 1, 24, 8)
    budget = st.sidebar.number_input("💶 Budget massimo (€)", 0, 200000, 20000, 1000)

    COSTO_BENZINA = st.sidebar.number_input("⛽ Costo Benzina (€/L)", 0.5, 3.0, 1.80, 0.01)
    CONSUMO_MEDIO_LITRI_100KM = st.sidebar.number_input("🚗 Consumo medio (L/100km)", 3.0, 20.0, 6.5, 0.1)
    COSTO_PUBBLICO = st.sidebar.number_input("🔌 Prezzo Pubblico (€/kWh)", 0.2, 2.0, 0.60, 0.01)
    COSTO_PRIVATO = st.sidebar.number_input("🏠 Prezzo Privato (€/kWh)", 0.1, 1.0, 0.25, 0.01)

    modo_input = st.radio("Metodo di inserimento veicoli", ["Singolo", "Per Gruppi"])
    veicoli = []
    if modo_input == "Singolo":
        n = st.number_input("Numero veicoli", 1, 100, 5)
        for i in range(n):
            with st.expander(f"Veicolo {i+1}"):
                nome = st.text_input("Nome", f"Auto_{i+1}", key=f"nome_{i}")
                km = st.number_input("Km giornalieri", 0.0, 500.0, 60.0, key=f"km_{i}")
                consumo = st.number_input("Consumo kWh/km", 0.1, 1.0, 0.18, 0.01, key=f"cons_{i}")
                sosta = st.number_input("Ore sosta", 0.0, 24.0, 8.0, 0.25, key=f"sosta_{i}")
                energia = km * consumo * MARGINE_SICUREZZA_TEMPO
                veicoli.append({"nome": nome, "km": km, "consumo": consumo, "sosta": sosta, "energia": energia})
    else:
        gruppi = st.number_input("Numero gruppi", 1, 10, 2)
        for i in range(gruppi):
            with st.expander(f"Gruppo {i+1}"):
                n = st.number_input("Numero veicoli", 1, 100, 5, key=f"g_n_{i}")
                km = st.number_input("Km giornalieri", 0.0, 500.0, 60.0, key=f"g_km_{i}")
                consumo = st.number_input("Consumo kWh/km", 0.1, 1.0, 0.18, 0.01, key=f"g_cons_{i}")
                sosta = st.number_input("Ore sosta", 0.0, 24.0, 8.0, 0.25, key=f"g_sosta_{i}")
                for j in range(n):
                    nome = f"G{i+1}_Auto{j+1}"
                    energia = km * consumo * MARGINE_SICUREZZA_TEMPO
                    veicoli.append({"nome": nome, "km": km, "consumo": consumo, "sosta": sosta, "energia": energia})
    if modalita in ["Ottimizzazione", "Comodità"] and st.button("🚀 Esegui Simulazione"):
        if modalita == "Ottimizzazione":
            risultati, migliore = ottimizza(veicoli, budget, ore_turno)
            st.subheader("📋 Tutte le combinazioni testate")
            st.dataframe(pd.DataFrame(risultati))
            if migliore:
                config, colonnine, costo_col, costo_inst, totale = migliore
        elif modalita == "Comodità":
            config, colonnine, costo_col, costo_inst, totale = modalita_comodita(veicoli, ore_turno)

        st.subheader("✅ Configurazione ottimale")
        st.write(f"Totale: €{totale:,.0f} | Budget: €{budget:,.0f}")
        for c in colonnine:
            st.write(f"{c['tipo']} → {', '.join(c['veicoli']) if c['veicoli'] else 'nessuna'} – Ore rimaste: {c['ore']:.2f}")

        km_annui = sum(v["km"] for v in veicoli) * GIORNI_ANNUI
        kwh_annui = sum(v["energia"] for v in veicoli) * GIORNI_ANNUI
        costo_benzina_km = COSTO_BENZINA * CONSUMO_MEDIO_LITRI_100KM / 100
        risparmio_benzina = (costo_benzina_km - COSTO_PRIVATO * 0.18) * km_annui
        risparmio_pubblica = (COSTO_PUBBLICO - COSTO_PRIVATO) * kwh_annui
        guadagno_5_anni = risparmio_benzina * 5
        roi = totale / risparmio_benzina if risparmio_benzina > 0 else 0

        st.subheader("📈 KPI Economici")
        st.metric("💰 Risparmio vs Benzina (€/anno)", f"{risparmio_benzina:,.0f}")
        st.metric("💡 Risparmio vs Ricarica Pubblica (€/anno)", f"{risparmio_pubblica:,.0f}")
        st.metric("📆 Guadagno su 5 Anni (€)", f"{guadagno_5_anni:,.0f}")
        st.metric("📉 ROI (anni)", f"{roi:.2f}")

    elif modalita == "Testa la tua infrastruttura":
        st.subheader("🔍 Testa la tua infrastruttura")
        ac = st.number_input("Numero AC_22", 0, 20, 2)
        dc30 = st.number_input("Numero DC_30", 0, 10, 0)
        dc60 = st.number_input("Numero DC_60", 0, 10, 0)
        dc90 = st.number_input("Numero DC_90", 0, 10, 0)

        if st.button("🔍 Analizza infrastruttura"):
            config = {"AC_22": ac, "DC_30": dc30, "DC_60": dc60, "DC_90": dc90}
            colonnine = crea_colonnine(config, ore_turno)
            energia_totale = sum(v["energia"] for v in veicoli)
            energia_erogata = 0.0
            auto_servite = 0

            for v in veicoli:
                for c in colonnine:
                    t = v["energia"] / c["potenza"] + c["overhead"]
                    if t <= v["sosta"] and t <= c["ore"]:
                        c["ore"] -= t
                        energia_erogata += v["energia"]
                        auto_servite += 1
                        break

            energia_esterna = energia_totale - energia_erogata

            st.subheader("📊 Risultati")
            st.metric("🚗 Veicoli serviti internamente", auto_servite)
            st.metric("🔋 Energia Interna (kWh/anno)", f"{energia_erogata * GIORNI_ANNUI:.1f}")
            st.metric("⚡ Energia Esterna Necessaria (kWh/anno)", f"{energia_esterna * GIORNI_ANNUI:.1f}")

    elif modalita == "Valuta il tuo investimento":

        st.header("💡 Valuta il tuo investimento")

        tipo_colonnina = st.selectbox("Seleziona la colonnina", list(COLONNINE.keys()))
        n_veicoli_giornalieri = st.number_input("Numero veicoli serviti al giorno", 1, 100, 5)
        percentuale_media_batteria = st.slider("Percentuale media ricarica", 10, 100, 60)
        taglia_media_batteria = st.number_input("Taglia media batteria (kWh)", 20, 150, 50)
        prezzo_vendita = st.number_input("Prezzo di vendita energia (€/kWh)", 0.10, 2.00, 0.50)

        energia_giorno = n_veicoli_giornalieri * (percentuale_media_batteria/100) * taglia_media_batteria
        energia_anno = energia_giorno * GIORNI_ANNUI
        ricavi_annui = energia_anno * prezzo_vendita

        costo_colonnina = COLONNINE[tipo_colonnina]["costo"]
        costo_installazione = COLONNINE[tipo_colonnina]["potenza"] * COSTO_INSTALLAZIONE_KW
        totale = costo_colonnina + costo_installazione

        st.metric("🔋 Energia venduta (kWh/anno)", f"{energia_anno:,.0f}")
        st.metric("💰 Ricavi potenziali annui", f"€{ricavi_annui:,.0f}")
        st.metric("💸 Costo totale (HW + installazione)", f"€{totale:,.0f}")


    if __name__ == "__main__":
    main()




def modalita_ottimizzazione(veicoli, budget, ore_turno):
    combinazioni_testate = []
    best_config = None

    for ac in range(0, 11):
        for dc_tipo in ["DC_20", "DC_30", "DC_40", "DC_60", "DC_90"]:
            for n_dc in range(0, 6):
                config = {"AC_22": ac, dc_tipo: n_dc}
                colonnine = crea_colonnine(config, ore_turno)
                copre, serviti = assegna(veicoli, colonnine)
                c1 = sum(COLONNINE[t]["costo"] * n for t, n in config.items())
                c2 = sum(COLONNINE[t]["potenza"] * n * COSTO_INSTALLAZIONE_KW for t, n in config.items())
                totale = c1 + c2
                combinazioni_testate.append({
                    **config,
                    "Totale Colonnine": ac + n_dc,
                    "Serviti": serviti,
                    "Copertura": "✅" if copre else "❌",
                    "Entro Budget": "✅" if totale <= budget else "❌",
                    "Costo Colonnine": c1,
                    "Costo Installazione": c2,
                    "Totale": totale
                })
                if copre and totale <= budget:
                    if best_config is None or totale < best_config["Totale"]:
                        best_config = {
                            "config": config,
                            "colonnine": colonnine,
                            "Costo Colonnine": c1,
                            "Costo Installazione": c2,
                            "Totale": totale
                        }

    return combinazioni_testate, best_config

def valuta_investimento():
    st.header("💡 Valuta il tuo investimento")
    tipo_colonnina = st.selectbox("Colonnina", list(COLONNINE.keys()))
    n_auto = st.number_input("Auto servite al giorno", 1, 100, 5)
    percentuale = st.slider("Percentuale media ricarica", 10, 100, 60)
    taglia = st.number_input("Taglia media batteria (kWh)", 20, 150, 50)
    prezzo = st.number_input("Prezzo di vendita energia (€/kWh)", 0.10, 2.00, 0.50)
    energia_annua = n_auto * (percentuale / 100) * taglia * GIORNI_ANNUI
    ricavi = energia_annua * prezzo
    costo_hw = COLONNINE[tipo_colonnina]["costo"]
    costo_inst = COLONNINE[tipo_colonnina]["potenza"] * COSTO_INSTALLAZIONE_KW
    totale = costo_hw + costo_inst
    st.metric("🔋 Energia venduta (kWh/anno)", f"{energia_annua:,.0f}")
    st.metric("💰 Ricavi annui", f"€{ricavi:,.0f}")
    st.metric("💸 Costo totale", f"€{totale:,.0f}")

def testa_infrastruttura(veicoli, config, ore_turno):
    colonnine = crea_colonnine(config, ore_turno)
    copre, serviti = assegna(veicoli, colonnine)
    energia_caricata = sum(v["energia"] * GIORNI_ANNUI for v in veicoli if v["nome"] in serviti)
    energia_totale = sum(v["energia"] * GIORNI_ANNUI for v in veicoli)
    energia_esterna = energia_totale - energia_caricata
    st.subheader("📊 Risultati simulazione")
    st.metric("Veicoli serviti", len(serviti))
    st.metric("Energia interna (kWh/anno)", f"{energia_caricata:,.0f}")
    st.metric("Energia esterna necessaria", f"{energia_esterna:,.0f}")

def mostra_kpi(veicoli):
    km = sum(v["km"] for v in veicoli) * GIORNI_ANNUI
    kwh = sum(v["energia"] for v in veicoli) * GIORNI_ANNUI
    cost_benzina = (km / 14) * 1.9
    cost_privato = kwh * 0.25
    cost_pubblico = kwh * 0.80
    risparmio = cost_benzina - cost_privato
    pubblico = cost_pubblico - cost_privato
    guadagno_5a = pubblico * 5
    tempo_ore = sum(v["energia"] / 22 for v in veicoli) * GIORNI_ANNUI
    roi = risparmio / (sum(v["energia"] for v in veicoli) * COSTO_INSTALLAZIONE_KW)
    st.subheader("📈 KPI")
    st.metric("💰 Risparmio vs Benzina", f"€{risparmio:,.0f}")
    st.metric("🔌 Risparmio vs Pubblico", f"€{pubblico:,.0f}")
    st.metric("📊 Guadagno 5 anni", f"€{guadagno_5a:,.0f}")
    st.metric("⏳ Tempo di ricarica (ore/anno)", f"{tempo_ore:.1f}")
    st.metric("📈 ROI", f"{roi:.2f}")

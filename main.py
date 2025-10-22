import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from math import ceil, floor
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Page configuration
st.set_page_config(page_title="AI-JoSa", layout="wide", page_icon="⚡")

# --- Custom Streamlit Theming ---
st.markdown("""
<style>
    .stApp {
        background-color: #E0F2F7; 
        color: #2E4053; 
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #A9D9D0; 
        border-radius: 5px 5px 0 0;
        margin-right: 2px;
        padding: 10px 15px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #6CBAB7; 
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1A5276; 
    }
    .stButton>button {
        background-color: #3498DB; 
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #2874A6;
    }
    .stMetric label {
        font-size: 1.1em;
        font-weight: bold;
        color: #1A5276;
    }
</style>
""", unsafe_allow_html=True)

# --- Language Selection and Translations ---
translations = {
    "it": {
        "app_title": "⚡ AI-JoSa ⚡",
        "tab1_title": "🔌 Ottimizzatore Colonnine ⚙️",
        "tab2_title": "📊 Testa Infrastruttura Esistente",
        "tab3_title": "📈 Valuta Rendimento (ROI)",
        "tab4_title": "💰 Stima Costo Wallbox Privata",
        "tab5_title": "🏗️ Stima Costo Colonnina Trifase", 
        
        # General & Tab 1 Keys 
        "optimizer_header": "🔌 Ottimizzatore Infrastruttura Colonnine",
        "optimizer_intro": "Trova la configurazione ottimale di colonnine per il tuo parco veicoli, rispettando budget e potenza massima.",
        "sidebar_config_params": "⚙️ Parametri Generali",
        "economic_tech_params": "Parametri Economici e Tecnici",
        "budget_available": "Budget disponibile (€)",
        "max_power_kw": "Potenza Massima Totale Impianto (kW)",
        "ac_turnover": "Turnazioni/Slot Giornalieri Colonnine AC", 
        "dc_turnover": "Turnazioni/Slot Giornalieri Colonnine DC",
        "charger_details_expander": "Dettagli Costo Caricatori",
        "unit_cost": "Costo Unitario (€)",
        "installation_cost": "Costo Installazione (€)",
        "energy_costs": "Costi Energetici",
        "private_charge_cost": "Costo kWh ricarica interna (€)",
        "public_charge_cost": "Costo kWh ricarica pubblica (€)",
        "vehicle_config": "🚗 Configurazione Veicoli",
        "num_vehicle_groups": "Numero gruppi veicoli",
        "group_header": "Gruppo Veicoli {i}",
        "group_quantity": "Quantità veicoli nel gruppo",
        "group_daily_km": "Km giornalieri (per veicolo)",
        "group_consumption": "Consumo (kWh/100km per veicolo)",
        "group_arrival_time": "Ora di Arrivo (h, 0-24)",
        "group_departure_time": "Ora di Partenza (h, 0-24)",
        "calculate_optimization": "🔍 Calcola Ottimizzazione Infrastruttura",
        "optimization_results": "📊 Risultati Ottimizzazione",
        "total_initial_cost": "Costo Totale Iniziale (CAPEX)",
        "internal_energy_charged": "Energia Caricata Internamente (kWh)", # Old label
        "estimated_annual_savings": "Risparmio Annuo Netto Stimato (€)", # Net vs Public EV Charge
        "combined_efficiency": "Copertura Ricarica (%)",
        "full_charge_success": "✅ Tutti i veicoli possono essere caricati completamente con questa configurazione.",
        "partial_charge_warning": "⚠️ **Attenzione:** Configurazione non ottimale.",
        "no_solution_found": "❌ Nessuna configurazione valida trovata.",
        "charging_plan_header": "Simulazione Piano di Ricarica (Gantt)",
        "vehicle_id_label": "Veicolo/Gruppo",
        "start_time_label": "Inizio",
        "end_time_label": "Fine",
        "charger_type_tooltip": "Caricatore Assegnato (ID)",
        "config_info_gantt": "Configurazione Caricatori", 
        "simulation_summary": "Riepilogo Simulazione",
        "charging_table_header": "Dettagli Ricariche Schedulate", 
        "cost_label": "Costo Iniziale (€)", 
        "efficiency_score_label": "Copertura Simulata (%)", 
        "charger_mix_chart": "Distribuzione Caricatori per Efficienza/Costo", 
        "cost_unit_label": "Costo Unità",
        "cost_install_label": "Costo Installazione",
        "cost_maintenance_label": "Costo Manutenzione Annuale",
        "power_label": "Potenza Totale Impianto (kW)",
        "final_config_header": "🎯 Configurazione Finale Raccomandata", 
        "total_vehicles_expected": "Veicoli totali attesi", 
        "vehicles_scheduled": "Veicoli Schedulati (Completati)", 
        
        # NUOVI KPI FINANZIARI
        "payback_period_label": "Payback Period (Anni)", 
        "annual_roi_label": "ROI Annuale Stimato (%)",
        "annual_maint_cost_label": "Costo Manutenzione Annuale (OPEX)",
        "energy_internal_charged_label": "Energia Caricata Internamente (kWh/Anno)", 
        "energy_external_needed_label": "Energia Esterna Necessaria", 
        "cost_external_annual_label": "Costo Ricarica Esterna Annuale (€)",
        "annual_savings_vs_fuel_label": "Risparmio Annuo vs. Benzina/Diesel (€)", 
        "fuel_equivalent_cost": "Costo kWh equivalente Benzina/Diesel (€)",

        # Tab 2 Keys
        "t2_header": "Testa la Tua Infrastruttura Esistente",
        "t2_intro": "Simula la performance di una configurazione fissa di caricatori con il tuo parco veicoli.",
        "t2_current_config": "Configurazione Caricatori Esistente",
        "t2_run_simulation": "▶️ Avvia Simulazione Schedulazione",
        "t2_results": "Risultati Simulazione",
        "t2_vehicles_served": "Veicoli Serviti (Completati)",
        "t2_energy_coverage": "Copertura Energetica Totale",
        "t2_time_needed": "Energia Totale Richiesta (kWh)",
        "t2_time_used": "Energia Totale Caricata (kWh)",
        "t2_config_details": "Inserisci il numero di unità per tipo di caricatore:",
        
        # Tab 3 Keys
        "t3_header": "Valuta Il Rendimento di un Punto di Ricarica Pubblico",
        "t3_intro": "Calcola il Ritorno sull'Investimento (ROI) e il Payback Period per un nuovo punto di ricarica pubblico.",
        "t3_charger_selection": "Seleziona Colonnina da Valutare",
        "t3_public_price": "Prezzo di vendita kWh al pubblico (€)",
        "t3_avg_utilization": "Utilizzo medio giornaliero (ore/giorno)",
        "t3_target_roi": "ROI annuale atteso (%)",
        "t3_calc_roi": "💰 Calcola Rendimento",
        "t3_roi_results": "Risultati Finanziari",
        "t3_roi_annual_revenue": "Ricavo Annuo Stimato",
        "t3_roi_annual_cost": "Costo Annuo Operativo (Manutenzione + Energia)",
        "t3_roi_net_profit": "Profitto Annuo Netto",
        "t3_payback": "Payback Period (Anni)",
        "t3_roi_perc": "ROI Annuale Raggiunto",
        "t3_cost_of_energy": "Costo kWh (Acquisto)",
        "t3_initial_investment": "Investimento Iniziale",
        
        # Tab 4 Keys
        "t4_header": "Stima Costo Wallbox Privata/Aziendale",
        "t4_intro": "Stima il costo totale di acquisto e installazione di una Wallbox a bassa potenza in base a un questionario tecnico.",
        "t4_power_select": "Potenza Wallbox",
        "t4_calc_cost": "✅ Stima Costo Totale",
        "t4_results": "Riepilogo Costi",
        "t4_wallbox_cost": "Costo Wallbox (Unità)",
        "t4_material_cost": "Costo Materiali (Quadro + Cavi)",
        "t4_labor_cost": "Costo Manodopera Stimato (Totale)",
        "t4_total_cost": "Costo Totale Stimato",
        "t4_installation_type": "Tipo di Installazione",
        "t4_new_installation": "Nuovo Impianto (necessari quadri/protezioni)",
        "t4_existing_predisp": "Predisposizione Esistente (cavo e protezioni già presenti)",
        "t4_distance": "Distanza dal quadro elettrico (metri)",
        "t4_cable_install_type": "Metodo di Installazione Cavi",
        "t4_on_wall": "Solo Canaline/Tubi a Parete/Soffitto",
        "t4_underground": "Richiesto Scavo e Posa a Terra",
        "t4_certification": "Include Dichiarazione di Conformità (DiCo)",
        "t4_condo_fire_cert": "Condominio con Certificato Prevenzione Incendi (Aggiungi 350€)",

        # Tab 5 Keys 
        "t5_header": "Stima Costo Impianto Colonnina (AC/DC) Trifase",
        "t5_intro": "Calcola il costo totale di acquisto e installazione di una colonnina ad alta potenza, includendo i costi di quadro elettrico e ingegneria.",
        "t5_config_select": "Seleziona Configurazione/Potenza",
        "t5_distance": "Distanza dal punto di connessione (metri)",
        "t5_material_cost": "Costo Materiali (Cavi, Protezioni) - Stimato",
        "t5_labor_cost": "Costo Manodopera Stimato (Ore/Multiplo)",
        "t5_panel_cost": "Costo Quadro Elettrico Principale",
        "t5_engineering_cost": "Costo Progettazione/Ingegneria",
        "t5_calc_cost": "✅ Stima Costo Totale",
        "t5_total_cost": "Costo Totale Stimato",
        "t5_wallbox_cost": "Costo Colonnina (Unità/e)",
        "t5_base_material_per_meter": "Costo Materiale Base per Metro (€)",
        "t5_material_multiplier": "Moltiplicatore Materiale (Fino 22kW/Unità)",
        "t5_labor_multiplier": "Moltiplicatore Complessità Manodopera (x Base Ore)",
        "t5_is_underground": "Posa a Terra (Scavo incluso)",
    }
}


def get_text(key):
    """Retrieves the text for the given key in Italian."""
    return translations.get("it", {}).get(key, f"Missing key: {key}")

# --- Parametri di Costo Standard per Calcoli Strutturati ---
def get_charger_costs(custom_costs=None):
    default_costs = {
        # Wallbox (Aggiunti per Tab 4)
        "WB_7_4": {"unit": 900, "install": 800, "power": 7.4, "maint_annual": 80},
        "WB_11": {"unit": 1200, "install": 1000, "power": 11, "maint_annual": 100},
        
        # Colonnine (Per Tab 1, 2, 3, 5)
        "AC_11": {"unit": 1800, "install": 1200, "power": 11, "maint_annual": 150},
        "AC_22": {"unit": 2500, "install": 1500, "power": 22, "maint_annual": 200},
        "DC_20": {"unit": 12000, "install": 2500, "power": 20, "maint_annual": 700}, 
        "DC_30": {"unit": 15000, "install": 3000, "power": 30, "maint_annual": 800},
        "DC_60": {"unit": 20000, "install": 5000, "power": 60, "maint_annual": 1000}, 
        "DC_90": {"unit": 25000, "install": 6000, "power": 90, "maint_annual": 1500}, 
        "DC_120": {"unit": 30000, "install": 7000, "power": 120, "maint_annual": 1800}, 
    }
    
    if custom_costs:
        for charger, costs in custom_costs.items():
            if charger in default_costs:
                default_costs[charger]['unit'] = costs.get('unit', default_costs[charger]['unit'])
                default_costs[charger]['install'] = costs.get('install', default_costs[charger]['install'])
                
    return default_costs

# --- Funzioni di utilità (non modificate) ---
def calculate_charger_costs(config, charger_costs_data):
    total_unit_cost = 0
    total_install_cost = 0
    total_maint_annual = 0
    total_power = 0
    
    for type, count in config.items():
        if count > 0 and type in charger_costs_data:
            costs = charger_costs_data[type]
            total_unit_cost += count * costs['unit']
            total_install_cost += count * costs['install']
            total_maint_annual += count * costs['maint_annual']
            total_power += count * costs['power']
            
    total_initial_cost = total_unit_cost + total_install_cost # CAPEX
    
    return {
        "total_initial_cost": total_initial_cost,
        "total_unit_cost": total_unit_cost,
        "total_install_cost": total_install_cost,
        "total_maint_annual": total_maint_annual,
        "total_power": total_power
    }

def get_color_for_vehicle(vehicle_id):
    """Associa un colore deterministico a un veicolo per il grafico Gantt."""
    hash_value = sum(ord(char) for char in vehicle_id)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    return colors[hash_value % len(colors)]

def get_effective_power(charger_type, nominal_power):
    """Restituisce la potenza effettiva di ricarica, considerando il limite del veicolo a 11kW per AC."""
    # Vincolo per riflettere il limite del caricatore di bordo AC a 11kW per la flotta
    if 'AC' in charger_type and nominal_power > 11:
        return 11 
    return nominal_power

def generate_vehicles_list(groups):
    """Genera la lista normalizzata dei veicoli dalla configurazione dei gruppi."""
    vehicles_to_charge = []
    
    for i, group in enumerate(groups):
        qty = group['quantity']
        daily_km = group['daily_km']
        consumption_kwh_per_km = group['consumption'] / 100
        energy_req_per_vehicle = daily_km * consumption_kwh_per_km
        arrival = group['arrival_time']
        departure = group['departure_time']

        # Normalizzazione: se partenza < arrivo, significa che la partenza è il giorno dopo
        departure_normalized = departure if departure > arrival else departure + 24
        
        for j in range(qty):
            vehicle_id = f"V{j+1}-G{i+1}" 
            vehicles_to_charge.append({
                'id': vehicle_id,
                'energy_needed': energy_req_per_vehicle,
                'arrival': arrival,
                'departure': departure_normalized,
                'group_id': f"G{i+1}",
                'charged_status': 0, 
                'color': get_color_for_vehicle(vehicle_id),
                'session': []
            })
            
    # Ordina per energia richiesta decrescente per dare priorità ai carichi maggiori
    vehicles_to_charge.sort(key=lambda x: x['energy_needed'], reverse=True) 
    return vehicles_to_charge

# --- FUNZIONE simulate_charging_plan ---
def simulate_charging_plan(config, groups, charger_costs_data, ac_slots, dc_slots):
    """
    Simulazione di scheduling con logica sequenziale per il veicolo: 
    un veicolo occupa un solo caricatore alla volta e non inizia una nuova sessione 
    fino a quando la precedente non è terminata (+ buffer).
    """
    
    # 1. Definizione Tipi Caricatore (Ordinati per potenza decrescente per priorità di schedulazione)
    charger_types = ["DC_120", "DC_90", "DC_60", "DC_30", "DC_20", "AC_22", "AC_11"] 
    charger_nominal_power = {t: charger_costs_data.get(t, {}).get('power', 0) for t in charger_types}
    vehicles_to_charge = generate_vehicles_list(groups)
    
    # 2. Preparazione Colonnine (Gestione Slot)
    charger_pool = []
    for t in charger_types:
        for i in range(config.get(t, 0)):
            # Per semplicità, usiamo solo il tempo di occupazione, ma teniamo i limiti di slot definiti
            slots = dc_slots if 'DC' in t else ac_slots
            charger_pool.append({
                'type': t, 
                'id': f"{t}-{i+1}", 
                'power': charger_nominal_power.get(t, 0),
                'total_slots': slots,
                'used_slots': 0,
                'schedule': [] # [(start, end), ...]
            })
            
    # 3. Simulazione di Scheduling
    charging_schedule = []
    BUFFER_TIME_H = 0.25 # 15 minuti di pausa tra una ricarica e l'altra
    
    # Initialize dynamic availability tracking for vehicles
    for vehicle in vehicles_to_charge:
        # available_from è l'orario in cui il veicolo finisce la ricarica precedente + buffer, o il suo arrivo
        vehicle['available_from'] = vehicle['arrival'] 

    # Loop a single vehicle until charged or departure
    for vehicle in vehicles_to_charge:
        remaining_energy = vehicle['energy_needed']
        
        # Inner loop per assegnare sessioni sequenziali fino a quando l'energia è soddisfatta o il tempo esaurito
        # La condizione vehicle['available_from'] < vehicle['departure'] garantisce che ci sia tempo per una potenziale sessione
        while remaining_energy > 0.01 and vehicle['available_from'] < vehicle['departure']:
            
            best_session_found = None
            best_session_charger = None
            
            # Trova la migliore *prossima* sessione per questo veicolo
            # Iteriamo sui caricatori ordinati per potenza decrescente (priorità per la ricarica più veloce)
            for charger in sorted(charger_pool, key=lambda c: charger_nominal_power.get(c['type'], 0), reverse=True): 
                
                # 1. Ora di fine dell'ultima ricarica schedulata su questo caricatore
                latest_end_time_on_charger = 0
                if charger['schedule']:
                    latest_end_time_on_charger = max(end for start, end in charger['schedule'])
                
                # 2. Ora di Inizio Potenziale (Max tra Veicolo Disponibile e Caricatore Disponibile + Buffer)
                potential_start_time = max(vehicle['available_from'], latest_end_time_on_charger + BUFFER_TIME_H)

                # 3. Tempo disponibile per questa sessione
                time_available = vehicle['departure'] - potential_start_time
                
                if time_available > 0.01: # Almeno 36 secondi
                    
                    # Potenza effettiva
                    charger_power_val = get_effective_power(charger['type'], charger['power'])
                    efficiency = 0.8 if 'DC' in charger['type'] else 0.9
                    
                    # Tempo ideale per caricare l'energia rimanente
                    ideal_charge_time_for_remaining = remaining_energy / (charger_power_val * efficiency + 0.001)
                    
                    time_this_session = min(ideal_charge_time_for_remaining, time_available)
                    end_time = potential_start_time + time_this_session
                    
                    # Ricalcola se il tempo eccede l'orario di partenza (anche se dovrebbe essere già gestito da time_available)
                    if end_time > vehicle['departure']:
                        time_this_session = vehicle['departure'] - potential_start_time
                        end_time = vehicle['departure']
                    
                    energy_charged_this_session = time_this_session * charger_power_val * efficiency
                    
                    if energy_charged_this_session > 0.01:
                        # Trovata la sessione più veloce. Scheduliamo e usciamo dal loop interno.
                        best_session_found = {
                            'start': potential_start_time,
                            'end': end_time,
                            'energy': energy_charged_this_session,
                            'time': time_this_session
                        }
                        best_session_charger = charger
                        break # Assegna la sessione e passa alla successiva potenziale per lo stesso veicolo
                        
            
            if best_session_found:
                # 1. Aggiorna Stato Caricatore
                best_session_charger['schedule'].append((best_session_found['start'], best_session_found['end']))
                best_session_charger['schedule'].sort(key=lambda x: x[0]) 
                best_session_charger['used_slots'] += 1
                
                # 2. Aggiorna Stato Veicolo
                remaining_energy -= best_session_found['energy']
                vehicle['charged_status'] += best_session_found['energy']
                # Il veicolo è disponibile solo dopo la fine della sessione + buffer
                vehicle['available_from'] = best_session_found['end'] + BUFFER_TIME_H 
                
                # 3. Registra Evento
                charging_schedule.append({
                    'Vehicle': vehicle['id'],
                    'Charger': best_session_charger['id'],
                    'Start': best_session_found['start'],
                    'End': best_session_found['end'],
                    'Type': best_session_charger['type'],
                    'Color': vehicle['color']
                })
                
                vehicle['session'].append({
                    'Charger': best_session_charger['id'],
                    'Start': best_session_found['start'],
                    'End': best_session_found['end'],
                    'Energy': best_session_found['energy']
                })

            else:
                # Nessun caricatore disponibile o tempo insufficiente
                break 

    # 4. Normalizzazione oraria per il grafico (shift al 24h)
    df_schedule = pd.DataFrame(charging_schedule)
    if not df_schedule.empty:
        df_schedule['Start_dt'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(df_schedule['Start'], unit='h')
        df_schedule['End_dt'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(df_schedule['End'], unit='h')
        
    return df_schedule, vehicles_to_charge 
# --- FINE FUNZIONE simulate_charging_plan ---


# --- FUNZIONE find_final_optimized_config ---
def find_final_optimized_config(all_configs, params):
    """
    Simula e seleziona la configurazione finale che massimizza i veicoli schedulati 
    e minimizza il costo tra quelle con la massima schedulazione.
    Aggiorna la lista 'all_configs' con i risultati di simulazione dettagliati.
    """
    
    groups = params['vehicle_groups']
    charger_costs_data = params['charger_costs']
    ac_slots = params['ac_slots']
    dc_slots = params['dc_slots']
    fuel_equivalent_cost = params['fuel_equivalent_cost']
    
    # Preparazione lista veicoli per calcolo richiesta totale (unica)
    all_vehicles = generate_vehicles_list(groups)
    total_vehicles_expected = sum(g['quantity'] for g in groups)
    total_daily_energy_req = sum(v['energy_needed'] for v in all_vehicles)
    
    best_final_results = None
    df_schedule_final = pd.DataFrame()
    vehicles_status_final = []
    
    max_scheduled_vehicles = -1
    min_cost_for_max_scheduled = float('inf')
    
    optimization_steps_log = ["Avvio simulazione dettagliata su configurazioni top (Massimo 50)..."]
    
    DAYS_PER_YEAR = 300 # Giorni operativi standard
    MAX_SIMULATIONS = 50 
    
    # Qui, all_configs è ancora ordinato per Efficienza Approssimata / Costo

    for i, config_result_approx in enumerate(all_configs[:MAX_SIMULATIONS]):
        
        current_config = config_result_approx['config']
        
        # Simula con la configurazione
        df_schedule_current, vehicles_status_current = simulate_charging_plan(
            current_config, groups, charger_costs_data, ac_slots, dc_slots
        )
        
        # Calcola i veicoli completamente caricati (>= 99% dell'energia richiesta)
        vehicles_scheduled_current = sum(1 for v in vehicles_status_current if v['charged_status'] >= v['energy_needed'] * 0.99)
        
        # -----------------------------------------------------------
        # CALCOLO KPI FINANZIERI DETTAGLIATI E RICHIESTI 
        # -----------------------------------------------------------
        final_cost_details = calculate_charger_costs(current_config, charger_costs_data)
        current_initial_cost = final_cost_details["total_initial_cost"]
        final_energy_charged = sum(v['charged_status'] for v in vehicles_status_current)
        
        
        # 1. Risparmio Annuo Lordo (vs. Public EV Charge)
        annual_savings_gross_ev = (final_energy_charged * DAYS_PER_YEAR * (params['public_cost'] - params['private_cost'])) 
        
        # 2. Risparmio Annuo Netto (vs. Public EV Charge - L'attuale 'estimated_annual_savings')
        annual_net_benefit = annual_savings_gross_ev - final_cost_details["total_maint_annual"] 
        
        # 3. Risparmio Annuo Netto vs. Benzina/Diesel 
        annual_savings_gross_fuel = (final_energy_charged * DAYS_PER_YEAR * (fuel_equivalent_cost - params['private_cost']))
        annual_savings_vs_fuel = annual_savings_gross_fuel - final_cost_details["total_maint_annual"]
        
        # 4. Energia Esterna e Costo
        daily_energy_deficit = max(0, total_daily_energy_req - final_energy_charged)
        energy_external_annual_kwh = daily_energy_deficit * DAYS_PER_YEAR
        cost_external_annual = energy_external_annual_kwh * params['public_cost']
        
        # 5. Payback Period e ROI Annuale
        if annual_net_benefit > 0:
            payback_period = current_initial_cost / annual_net_benefit
            annual_roi = (annual_net_benefit / current_initial_cost) * 100
        else:
            payback_period = float('inf') 
            annual_roi = 0.0
            
        energy_coverage_perc = (final_energy_charged / (total_daily_energy_req + 0.001)) * 100
        
        # Aggiorna la configurazione (che è una copia) con i risultati di schedulazione realistici e tutti i KPI
        config_result_approx['vehicles_scheduled'] = vehicles_scheduled_current
        config_result_approx['cost_initial'] = current_initial_cost
        config_result_approx['annual_net_savings'] = annual_net_benefit
        config_result_approx['total_maint_annual'] = final_cost_details["total_maint_annual"]
        config_result_approx['energy_external_kwh'] = energy_external_annual_kwh # Annual value
        config_result_approx['cost_external_annual'] = cost_external_annual
        config_result_approx['combined_efficiency'] = energy_coverage_perc # Efficienza SIMULATA
        config_result_approx['total_power'] = final_cost_details["total_power"]
        # -----------------------------------------------------------

        log_message = f"Configurazione {i+1} ({str({k: v for k, v in current_config.items() if v > 0})}): Schedulati {vehicles_scheduled_current} / {total_vehicles_expected}. Copertura {energy_coverage_perc:.1f}%. Costo: € {current_initial_cost:,.0f}."
        optimization_steps_log.append(log_message.replace(",", ".")) 
        
        
        # Logica di selezione: Massimizza Veicoli Schedulati (Primary), Minimizza Costo (Secondary)
        is_better = False
        
        if vehicles_scheduled_current > max_scheduled_vehicles:
            is_better = True
        elif vehicles_scheduled_current == max_scheduled_vehicles:
            if current_initial_cost < min_cost_for_max_scheduled:
                is_better = True

        if is_better:
            max_scheduled_vehicles = vehicles_scheduled_current
            min_cost_for_max_scheduled = current_initial_cost
            
            # Aggiornamento dei dati della migliore configurazione trovata finora
            best_final_results = {
                "config": current_config,
                "total_initial_cost": current_initial_cost,
                "total_power": final_cost_details["total_power"],
                "combined_efficiency": energy_coverage_perc,
                "vehicles_scheduled": vehicles_scheduled_current, 
                "total_vehicles_expected": total_vehicles_expected,
                "estimated_annual_savings": annual_net_benefit, # Net vs Public EV Charge
                "internal_energy_charged": final_energy_charged, # Daily value
                "total_energy_request": total_daily_energy_req,
                "is_full_charge": vehicles_scheduled_current == total_vehicles_expected,
                # AGGIUNTA DEI NUOVI KPI FINANZIAMI E ENERGETICI RICHIESTI
                "payback_period": payback_period, 
                "annual_roi": annual_roi,
                "total_maint_annual": final_cost_details["total_maint_annual"], 
                "energy_external_kwh": energy_external_annual_kwh, # Annual value
                "cost_external_annual": cost_external_annual,
                "annual_savings_vs_fuel": annual_savings_vs_fuel,
                **final_cost_details 
            }
            # Salvataggio anche dei dati di simulazione (Gantt, Status) della migliore configurazione
            df_schedule_final = df_schedule_current
            vehicles_status_final = vehicles_status_current # <-- CORREZIONE: Usare vehicles_status_current
            
        
        # Ottimizzazione del ciclo
        if max_scheduled_vehicles == total_vehicles_expected and config_result_approx['combined_efficiency'] < 70: 
             optimization_steps_log.append("Trovata soluzione al 100%. Le configurazioni rimanenti sono molto meno efficienti in stima. Termino l'analisi.")
             break
        
    
    optimization_steps_log.append(f"--- Risultato Finale ---")
    if best_final_results:
        optimization_steps_log.append(f"🎯 Configurazione Finale Selezionata: {str({k: v for k, v in best_final_results['config'].items() if v > 0})}. Schedulati: {max_scheduled_vehicles} / {total_vehicles_expected}. Costo Minimo per questa copertura: € {min_cost_for_max_scheduled:,.0f}.".replace(",", "."))
    
    # Ordina la lista completa dei risultati di schedulazione realistici per la visualizzazione delle alternative
    all_configs.sort(key=lambda x: (x.get('vehicles_scheduled', 0), -x.get('cost_initial', float('inf'))), reverse=True)
    
    return best_final_results, df_schedule_final, vehicles_status_final, optimization_steps_log, all_configs
# --- FINE FUNZIONE find_final_optimized_config ---


# --- Funzioni di Ottimizzazione/Calcolo (Tab 1) ---
def calculate_optimization_results(params):
    """
    Esegue il brute force con metriche approssimate (efficienza energetica).
    Ritorna la lista di tutte le configurazioni valide, ordinate per efficienza (max) e costo (min).
    """
    
    costs = params['charger_costs']
    budget = params['budget']
    max_power = params['max_power']
    groups = params['vehicle_groups']
    private_cost = params['private_cost']
    public_cost = params['public_cost']
    ac_slots = params['ac_slots']
    dc_slots = params['dc_slots']
    fuel_equivalent_cost = params['fuel_equivalent_cost']
    
    total_daily_energy_req = 0
    total_vehicles = 0
    for group in groups:
        qty = group['quantity']
        daily_km = group['daily_km']
        consumption_kwh_per_km = group['consumption'] / 100
        group_energy_req = qty * daily_km * consumption_kwh_per_km
        total_daily_energy_req += group_energy_req
        total_vehicles += qty
        
    # Limiti massimi per il brute force (ridotti per performance)
    max_units_per_type = min(15, ceil(total_vehicles * 0.5) + 3) if total_vehicles > 0 else 10 
    
    max_ac11 = min(max_units_per_type, ceil(budget / (costs.get("AC_11", {}).get("unit", float('inf')) + costs.get("AC_11", {}).get("install", float('inf')))))
    max_ac22 = min(max_units_per_type, ceil(budget / (costs.get("AC_22", {}).get("unit", float('inf')) + costs.get("AC_22", {}).get("install", float('inf')))))
    max_dc20 = min(max_units_per_type, ceil(budget / (costs.get("DC_20", {}).get("unit", float('inf')) + costs.get("DC_20", {}).get("install", float('inf'))))) 
    max_dc30 = min(max_units_per_type, ceil(budget / (costs.get("DC_30", {}).get("unit", float('inf')) + costs.get("DC_30", {}).get("install", float('inf')))))
    max_dc60 = min(max_units_per_type, ceil(budget / (costs.get("DC_60", {}).get("unit", float('inf')) + costs.get("DC_60", {}).get("install", float('inf')))))
    max_dc90 = min(max_units_per_type, ceil(budget / (costs.get("DC_90", {}).get("unit", float('inf')) + costs.get("DC_90", {}).get("install", float('inf'))))) 
    max_dc120 = min(max_units_per_type, ceil(budget / (costs.get("DC_120", {}).get("unit", float('inf')) + costs.get("DC_120", {}).get("install", float('inf'))))) 
    
    all_configs = []
    max_comb = 20000 
    comb_count = 0
    
    # Nested loops per la ricerca brute force (limitata per tempo di esecuzione)
    for n_ac11 in range(0, max_ac11 + 1):
        for n_ac22 in range(0, max_ac22 + 1):
            for n_dc20 in range(0, max_dc20 + 1):
                for n_dc30 in range(0, max_dc30 + 1):
                    for n_dc60 in range(0, max_dc60 + 1): 
                        for n_dc90 in range(0, max_dc90 + 1):
                            for n_dc120 in range(0, max_dc120 + 1):
                                
                                comb_count += 1
                                if comb_count > max_comb: break

                                config = {
                                    "AC_11": n_ac11, 
                                    "AC_22": n_ac22, 
                                    "DC_20": n_dc20, 
                                    "DC_30": n_dc30, 
                                    "DC_60": n_dc60, 
                                    "DC_90": n_dc90, 
                                    "DC_120": n_dc120
                                }
                                if sum(config.values()) == 0: continue
                                
                                cost_details = calculate_charger_costs(config, costs)
                                current_cost = cost_details["total_initial_cost"]
                                current_power = cost_details["total_power"]
                                total_maint_annual = cost_details["total_maint_annual"]
                                
                                if current_cost > budget: continue
                                if current_power > max_power: continue
                                
                                # Capacità stimata (approssimazione per l'ottimizzazione iniziale)
                                max_daily_energy_supply = 0
                                
                                # Calcoli per l'efficienza basati sulla potenza nominale e un tempo di ricarica tipico per slot
                                
                                # AC (Usa 11kW effettivi, assume 4h per slot)
                                max_daily_energy_supply += config["AC_11"] * ac_slots * (11 * 4 * 0.9) 
                                max_daily_energy_supply += config["AC_22"] * ac_slots * (11 * 4 * 0.9) 
                                
                                # DC
                                # Assumiamo ore di utilizzo per slot DC: 2.5h (20kW), 2h (30kW), 1.5h (60kW), 1h (90kW), 0.7h (120kW)
                                DC_HOURS = {"DC_20": 2.5, "DC_30": 2, "DC_60": 1.5, "DC_90": 1, "DC_120": 0.7}
                                for dc_type, hours in DC_HOURS.items():
                                    if config.get(dc_type, 0) > 0:
                                         max_daily_energy_supply += config[dc_type] * dc_slots * (costs.get(dc_type, {}).get("power", 0) * hours * 0.8)

                                internal_energy_charged = min(total_daily_energy_req, max_daily_energy_supply)
                                
                                DAYS_PER_YEAR = 300
                                # Netto vs Public EV Charge (per calcolo Payback/ROI)
                                annual_savings = (internal_energy_charged * DAYS_PER_YEAR * (public_cost - private_cost)) 
                                annual_net_benefit = annual_savings - total_maint_annual 
                                
                                # Netto vs Fuel Equivalent
                                annual_savings_vs_fuel = (internal_energy_charged * DAYS_PER_YEAR * (fuel_equivalent_cost - private_cost)) - total_maint_annual

                                energy_coverage_perc = (internal_energy_charged / (total_daily_energy_req + 0.001)) * 100
                                
                                config_result = {
                                    "config": config,
                                    "total_initial_cost": current_cost,
                                    "total_power": current_power,
                                    "internal_energy_charged": internal_energy_charged,
                                    "total_energy_request": total_daily_energy_req,
                                    "estimated_annual_savings": annual_net_benefit,
                                    "annual_savings_vs_fuel": annual_savings_vs_fuel,
                                    "combined_efficiency": energy_coverage_perc,
                                    "is_full_charge": internal_energy_charged >= total_daily_energy_req * 0.99,
                                    # Questi campi saranno sovrascritti dalla simulazione, ma li inseriamo per completezza
                                    "vehicles_scheduled": 0, 
                                    "energy_external_kwh": 0,
                                    **cost_details
                                }
                                all_configs.append(config_result)

                                if comb_count > max_comb: break
                            if comb_count > max_comb: break
                        if comb_count > max_comb: break
                    if comb_count > max_comb: break
                if comb_count > max_comb: break
            if comb_count > max_comb: break
        if comb_count > max_comb: break

    # Ordina: 1. Efficienza Approssimata (Decrescente), 2. Costo (Crescente)
    all_configs.sort(key=lambda x: (x['combined_efficiency'], -x['total_initial_cost']), reverse=True)
    return all_configs

def display_config_chart(config, title):
    """Genera un grafico a barre per visualizzare la configurazione delle colonnine."""
    # Prepara i dati per il grafico, filtrando le quantità pari a 0
    data = [{"Caricatore": k, "Quantità": v} for k, v in config.items() if v > 0]
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure()
        
    # Ordine personalizzato per coerenza grafica
    order = ["DC_120", "DC_90", "DC_60", "DC_30", "DC_20", "AC_22", "AC_11"]
    
    # Colori per AC (Verde) e DC (Blu)
    colors_map = { c: ('#3498DB' if 'DC' in c else '#2ECC71') for c in df['Caricatore'].unique() }

    fig = px.bar(df, x='Caricatore', y='Quantità', title=title, 
                 color='Caricatore', color_discrete_map=colors_map, 
                 text='Quantità')
                 
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': order}, 
                      yaxis_title="Numero di Unità", 
                      margin=dict(l=20, r=20, t=50, b=20),
                      showlegend=False)
    return fig

# --- Render Functions (Tab 1) ---
def render_tab1():
    st.header(get_text("optimizer_header"))
    st.markdown(get_text("optimizer_intro"))
    
    # --- Inizializzazione Session State per i Veicoli (CORREZIONE KeyError) ---
    default_groups = [
        {'quantity': 5, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8},
        {'quantity': 3, 'daily_km': 300, 'consumption': 20.0, 'arrival_time': 10, 'departure_time': 12}
    ]
    
    # Inizializza num_groups_tab1 e vehicle_groups_tab1 con i valori di default se non presenti
    st.session_state.setdefault('num_groups_tab1', 2)
    st.session_state.setdefault('vehicle_groups_tab1', default_groups)
    
    # Se il numero di gruppi o la lista è vuota, resetta al default (gestione di input manuali a 0)
    if st.session_state['num_groups_tab1'] == 0 or len(st.session_state['vehicle_groups_tab1']) == 0:
        st.session_state['num_groups_tab1'] = 2
        st.session_state['vehicle_groups_tab1'] = default_groups
        
    if 'optimization_results' not in st.session_state: st.session_state['optimization_results'] = None
    if 'optimization_alternatives' not in st.session_state: st.session_state['optimization_alternatives'] = []
    if 'df_schedule_final' not in st.session_state: st.session_state['df_schedule_final'] = pd.DataFrame()
    if 'vehicles_status_final' not in st.session_state: st.session_state['vehicles_status_final'] = []
    if 'optimization_log' not in st.session_state: st.session_state['optimization_log'] = []

    # --- Sidebar Inputs ---
    st.sidebar.header(get_text("sidebar_config_params"))
    
    all_charger_costs = get_charger_costs()
    default_ac11 = all_charger_costs["AC_11"]
    default_ac22 = all_charger_costs["AC_22"]
    default_dc20 = all_charger_costs["DC_20"]
    default_dc30 = all_charger_costs["DC_30"]
    default_dc60 = all_charger_costs["DC_60"]
    default_dc90 = all_charger_costs["DC_90"]
    default_dc120 = all_charger_costs["DC_120"]

    with st.sidebar.expander(get_text("economic_tech_params"), expanded=True):
        budget = st.number_input(get_text("budget_available"), min_value=1000, value=50000, step=1000, key="budget_tab1")
        max_power = st.number_input(get_text("max_power_kw"), min_value=10, value=150, step=5, key="max_power_tab1")
        
        col_t1, col_t2 = st.columns(2)
        # AC Turnover/Slots
        ac_slots_default = st.session_state.get('ac_turnover_tab1', 4)
        ac_slots = col_t1.number_input(get_text("ac_turnover"), min_value=1, value=ac_slots_default, step=1, key="ac_turnover_tab1", help="Numero di volte che la singola colonnina AC può ricaricare veicoli al giorno (Slot/Cicli)")
        
        # DC Turnover/Slots
        dc_slots_default = st.session_state.get('dc_turnover_tab1', 6)
        dc_slots = col_t2.number_input(get_text("dc_turnover"), min_value=1, value=dc_slots_default, step=1, key="dc_turnover_tab1", help="Numero di volte che la singola colonnina DC può ricaricare veicoli al giorno (Slot/Cicli)")

        with st.expander(get_text("charger_details_expander")):
            st.subheader("Colonnine AC")
            col_ac_11, col_ac_22 = st.columns(2)
            with col_ac_11:
                st.markdown("**AC 11 kW**")
                ac11_unit = st.number_input(get_text("unit_cost"), min_value=100, value=default_ac11["unit"], key="ac11_unit")
                ac11_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_ac11["install"], key="ac11_install")
            with col_ac_22:
                st.markdown("**AC 22 kW**")
                ac22_unit = st.number_input(get_text("unit_cost"), min_value=100, value=default_ac22["unit"], key="ac22_unit")
                ac22_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_ac22["install"], key="ac22_install")
                
            st.subheader("Colonnine DC")
            col_dc_20, col_dc_30, col_dc_60, col_dc_90, col_dc_120 = st.columns(5)
            with col_dc_20:
                st.markdown("**DC 20 kW**")
                dc20_unit = st.number_input(get_text("unit_cost"), min_value=1000, value=default_dc20["unit"], key="dc20_unit")
                dc20_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_dc20["install"], key="dc20_install")
            with col_dc_30:
                st.markdown("**DC 30 kW**")
                dc30_unit = st.number_input(get_text("unit_cost"), min_value=1000, value=default_dc30["unit"], key="dc30_unit")
                dc30_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_dc30["install"], key="dc30_install")
            with col_dc_60:
                st.markdown("**DC 60 kW**")
                dc60_unit = st.number_input(get_text("unit_cost"), min_value=1000, value=default_dc60["unit"], key="dc60_unit")
                dc60_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_dc60["install"], key="dc60_install")
            with col_dc_90:
                st.markdown("**DC 90 kW**")
                dc90_unit = st.number_input(get_text("unit_cost"), min_value=1000, value=default_dc90["unit"], key="dc90_unit")
                dc90_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_dc90["install"], key="dc90_install")
            with col_dc_120:
                st.markdown("**DC 120 kW**")
                dc120_unit = st.number_input(get_text("unit_cost"), min_value=1000, value=default_dc120["unit"], key="dc120_unit")
                dc120_install = st.number_input(get_text("installation_cost"), min_value=100, value=default_dc120["install"], key="dc120_install")
                
            
            st.subheader(get_text("energy_costs"))
            private_cost = st.number_input(get_text("private_charge_cost"), min_value=0.01, value=0.25, step=0.01, key="private_cost_tab1", help="Costo dell'energia elettrica aziendale/privata")
            public_cost = st.number_input(get_text("public_charge_cost"), min_value=0.1, value=0.60, step=0.01, key="public_cost_tab1", help="Costo stimato della ricarica pubblica (per calcolare il risparmio)")
            fuel_equivalent_cost = st.number_input(get_text("fuel_equivalent_cost"), min_value=0.1, value=1.00, step=0.01, key="fuel_equivalent_cost_tab1", help="Costo kWh equivalente a benzina/diesel (es. 1.8€/L / 5km/kWh = 0.36€/kWh)")


    # Raccogli i costi personalizzati
    custom_charger_costs = {
        "AC_11": {"unit": ac11_unit, "install": ac11_install, "power": default_ac11["power"], "maint_annual": default_ac11["maint_annual"]},
        "AC_22": {"unit": ac22_unit, "install": ac22_install, "power": default_ac22["power"], "maint_annual": default_ac22["maint_annual"]},
        "DC_20": {"unit": dc20_unit, "install": dc20_install, "power": default_dc20["power"], "maint_annual": default_dc20["maint_annual"]},
        "DC_30": {"unit": dc30_unit, "install": dc30_install, "power": default_dc30["power"], "maint_annual": default_dc30["maint_annual"]},
        "DC_60": {"unit": dc60_unit, "install": dc60_install, "power": default_dc60["power"], "maint_annual": default_dc60["maint_annual"]},
        "DC_90": {"unit": dc90_unit, "install": dc90_install, "power": default_dc90["power"], "maint_annual": default_dc90["maint_annual"]},
        "DC_120": {"unit": dc120_unit, "install": dc120_install, "power": default_dc120["power"], "maint_annual": default_dc120["maint_annual"]},
    }
    
    current_costs_data = get_charger_costs(custom_charger_costs)


    # --- Vehicle Groups Configuration ---
    st.subheader(get_text("vehicle_config"))
    
    # st.session_state['num_groups_tab1'] è garantito esistere qui
    num_groups = st.number_input(get_text("num_vehicle_groups"), min_value=1, value=st.session_state['num_groups_tab1'], step=1, key="num_groups_tab1")

    # Adatta la lista dei gruppi alla dimensione richiesta
    if len(st.session_state['vehicle_groups_tab1']) > num_groups:
        st.session_state['vehicle_groups_tab1'] = st.session_state['vehicle_groups_tab1'][:num_groups]
    while len(st.session_state['vehicle_groups_tab1']) < num_groups:
        st.session_state['vehicle_groups_tab1'].append({'quantity': 1, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8})
        
    vehicle_groups = st.session_state['vehicle_groups_tab1']
    
    for i in range(num_groups):
        with st.expander(get_text("group_header").format(i=i+1), expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Assicura che l'indice esista prima di accedere
            if i < len(vehicle_groups):
                group_data = vehicle_groups[i]
            else:
                # Caso di fallback (non dovrebbe accadere con la logica sopra)
                group_data = {'quantity': 1, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8}


            group_data['quantity'] = col1.number_input(get_text("group_quantity"), min_value=1, value=group_data['quantity'], step=1, key=f"qty_{i}")
            group_data['daily_km'] = col2.number_input(get_text("group_daily_km"), min_value=10, value=group_data['daily_km'], step=10, key=f"km_{i}")
            group_data['consumption'] = col3.number_input(get_text("group_consumption"), min_value=10.0, max_value=50.0, value=group_data['consumption'], step=0.1, key=f"cons_{i}")
            group_data['arrival_time'] = col4.slider(get_text("group_arrival_time"), min_value=0, max_value=23, value=group_data['arrival_time'], step=1, key=f"arr_{i}")
            group_data['departure_time'] = col5.slider(get_text("group_departure_time"), min_value=0, max_value=23, value=group_data['departure_time'], step=1, key=f"dep_{i}")
            
            # Aggiorna il gruppo nella lista principale
            vehicle_groups[i] = group_data


    # --- Calcolo e Logica ---
    if st.button(get_text("calculate_optimization"), key="calc_opt_btn"):
        
        # Validazione base
        if sum(g['quantity'] for g in vehicle_groups) == 0:
            st.error("Inserisci almeno un veicolo.")
            st.session_state['optimization_results'] = None
            return

        # Parametri completi
        params = {
            "budget": budget,
            "max_power": max_power,
            "private_cost": private_cost,
            "public_cost": public_cost,
            "ac_slots": ac_slots,
            "dc_slots": dc_slots,
            "charger_costs": current_costs_data,
            "vehicle_groups": vehicle_groups,
            "fuel_equivalent_cost": fuel_equivalent_cost
        }
        
        # 1. Brute force approssimato
        all_configs_approx = calculate_optimization_results(params)
        st.session_state['optimization_alternatives'] = all_configs_approx # Salva tutte le configurazioni

        if not all_configs_approx:
            st.error(get_text("no_solution_found"))
            st.session_state['optimization_results'] = None
        else:
            with st.spinner("Eseguo simulazione di scheduling dettagliata per l'ottimizzazione..."):
                # 2. Simulazione di scheduling e selezione finale
                # all_configs_updated è ora ordinata per Veicoli Schedulati / Costo (logica corretta)
                best_results, df_schedule, vehicles_status, log_steps, all_configs_updated = find_final_optimized_config(all_configs_approx, params)

            st.session_state['optimization_results'] = best_results
            st.session_state['df_schedule_final'] = df_schedule
            st.session_state['vehicles_status_final'] = vehicles_status
            st.session_state['optimization_alternatives'] = all_configs_updated # Aggiorna con i risultati di schedulazione realistici

            with st.expander("Log di Ottimizzazione", expanded=False):
                 st.code("\n".join(log_steps))


    # --- Visualizzazione Risultati ---
    if st.session_state['optimization_results']:
        results = st.session_state['optimization_results']
        df_schedule = st.session_state['df_schedule_final']
        vehicles_status = st.session_state['vehicles_status_final']
        
        st.divider()
        st.subheader(get_text("optimization_results"))
        
        
        # Sezione Configurazione Raccomandata
        st.markdown(f"### {get_text('final_config_header')}")
        final_config = {k: v for k, v in results['config'].items() if v > 0}
        st.code(str(final_config).replace("'", "").replace("{", "").replace("}", ""))
        
        col_kpi_1, col_kpi_2, col_kpi_3, col_kpi_4, col_kpi_5 = st.columns(5)
        
        # 1. Costo Iniziale
        col_kpi_1.metric(get_text("total_initial_cost"), f"€ {results['total_initial_cost']:,.0f}".replace(",", "."))
        
        # 2. Payback Period
        payback_display = f"{results['payback_period']:.1f} anni" if results['payback_period'] != float('inf') else "N/A"
        col_kpi_2.metric(get_text("payback_period_label"), payback_display)
        
        # 3. ROI Annuale
        col_kpi_3.metric(get_text("annual_roi_label"), f"{results['annual_roi']:.1f} %")
        
        # 4. Copertura / Schedulazione
        col_kpi_4.metric(get_text("combined_efficiency"), f"{results['combined_efficiency']:.1f} %")
        
        # 5. Potenza Impegnata
        col_kpi_5.metric(get_text("power_label"), f"{results['total_power']} kW")

        # Messaggio di stato
        if results['is_full_charge']:
            st.success(get_text("full_charge_success"))
        else:
            st.warning(get_text("partial_charge_warning") + 
                       f" Ricaricati completamente: **{results['vehicles_scheduled']} / {results['total_vehicles_expected']}** veicoli.")
        
        
        # Sezione Dettagli Finanziari ed Energetici
        st.markdown("#### Dettagli Finanziari ed Energetici (Annuali)")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        # Energia Caricata Internamente (kWh/Anno)
        annual_energy = results['internal_energy_charged'] * 300
        col_f1.metric(get_text("energy_internal_charged_label"), f"{annual_energy:,.0f} kWh".replace(",", "."))
        
        # Risparmio vs. Pubblico (Netto)
        col_f2.metric(get_text("estimated_annual_savings"), f"€ {results['annual_net_savings']:,.0f}".replace(",", "."), help="Risparmio Netto Annuo rispetto al costo della ricarica pubblica EV")
        
        # Risparmio vs. Carburante
        col_f3.metric(get_text("annual_savings_vs_fuel_label"), f"€ {results['annual_savings_vs_fuel']:,.0f}".replace(",", "."), help="Risparmio Netto Annuo rispetto al costo equivalente di Benzina/Diesel")

        # Costo Manutenzione
        col_f4.metric(get_text("annual_maint_cost_label"), f"€ {results['total_maint_annual']:,.0f}".replace(",", "."), help="Costo Annuo per manutenzione/software colonnine (OPEX)")

        # Energia e Costo Esterno
        if results['energy_external_kwh'] > 0:
            st.markdown(f"---")
            st.info(f"**{get_text('energy_external_needed_label')}**: {results['energy_external_kwh']:,.0f} kWh/Anno. "
                    f"**{get_text('cost_external_annual_label')}**: € {results['cost_external_annual']:,.0f}/Anno. "
                    "Questi veicoli dovranno ricaricare all'esterno o non copriranno i km giornalieri.".replace(",", "."))
        
        
        # Sezione Gantt e Dettagli
        st.markdown(f"#### {get_text('charging_plan_header')}")
        
        if not df_schedule.empty:
            
            # Formattazione per Plotly Gantt
            df_plot = df_schedule.copy()
            df_plot['Duration'] = df_plot['End_dt'] - df_plot['Start_dt']
            df_plot['Start_formatted'] = df_plot['End_dt'].dt.strftime('%H:%M')
            df_plot['End_formatted'] = df_plot['End_dt'].dt.strftime('%H:%M')
            
            # Ordina per Caricatore (per raggruppamento visivo)
            df_plot.sort_values(by='Charger', inplace=True)

            fig_gantt = px.timeline(df_plot, x_start="Start_dt", x_end="End_dt", y="Charger", 
                                    color="Vehicle", 
                                    text="Vehicle",
                                    hover_data={
                                        "Vehicle": True,
                                        "Start_formatted": True,
                                        "End_formatted": True,
                                        "Charger": True,
                                        "Type": False, # Non mostrare nel tooltip, è nel nome del caricatore
                                    },
                                    title=get_text("charging_plan_header"))

            fig_gantt.update_traces(textposition='outside')
            fig_gantt.update_yaxes(autorange="reversed") # Inverti l'ordine per avere il primo caricatore in alto
            fig_gantt.update_xaxes(title="Ora del Giorno (h)", tickformat="%H:%M",
                                   range=[df_plot['Start_dt'].min() - timedelta(minutes=15), df_plot['End_dt'].max() + timedelta(minutes=15)])
            fig_gantt.update_layout(height=400 + 40 * len(df_plot['Charger'].unique()),
                                    margin=dict(l=20, r=20, t=50, b=20),
                                    xaxis_tickangle=-45)
            
            st.plotly_chart(fig_gantt, use_container_width=True)

            
            # Tabella Dettagli Ricariche
            st.markdown(f"#### {get_text('charging_table_header')}")
            
            # Dettagli per il veicolo non schedulato/parziale
            vehicle_details = []
            for v in vehicles_status:
                energy_charged = v['charged_status']
                energy_needed = v['energy_needed']
                status = "✅ Completato" if energy_charged >= energy_needed * 0.99 else (f"⚠️ Parziale ({energy_charged / energy_needed * 100:.1f} %)" if energy_charged > 0 else "❌ Mancante")
                
                vehicle_details.append({
                    "Veicolo": v['id'],
                    "Gruppo": v['group_id'],
                    "Energia Richiesta (kWh)": f"{energy_needed:.1f}",
                    "Energia Caricata (kWh)": f"{energy_charged:.1f}",
                    "Status": status
                })
                
            df_vehicle_status = pd.DataFrame(vehicle_details)
            st.dataframe(df_vehicle_status, use_container_width=True, height=200)


        # Sezione Alternativa (AGGIORNATA PER INCLUDERE TUTTI I KPI SIMULATI)
        st.markdown("---")
        st.markdown("#### Alternativa: Configurazioni Ottimali Simulate")
        
        # Filtra solo le top N alternative (esclusa la prima, che è la 'migliore' già visualizzata)
        # La lista 'optimization_alternatives' è ora ordinata per Veicoli Schedulati / Costo
        top_alternatives = st.session_state['optimization_alternatives'][1:10] 
        
        if top_alternatives:
            
            alt_data = []
            for alt in top_alternatives:
                config_str = str({k: v for k, v in alt['config'].items() if v > 0}).replace("'", "").replace("{", "").replace("}", "")
                alt_data.append({
                    get_text("config_info_gantt"): config_str,
                    get_text("cost_label"): alt['total_initial_cost'], # Raw value for formatting
                    get_text("vehicles_scheduled"): f"{alt.get('vehicles_scheduled', 0)} / {results.get('total_vehicles_expected', '?')}", # Use results' total expected to be consistent
                    get_text("efficiency_score_label"): alt['combined_efficiency'], # Raw value
                    get_text("energy_external_needed_label"): alt.get('energy_external_kwh', 0), # Annual value
                })
            
            df_alt = pd.DataFrame(alt_data)
            
            # Formattazione per visualizzazione
            df_alt[get_text("cost_label")] = df_alt[get_text("cost_label")].apply(lambda x: f"€ {x:,.0f}".replace(",", "."))
            df_alt[get_text("efficiency_score_label")] = df_alt[get_text("efficiency_score_label")].apply(lambda x: f"{x:.1f} %")
            df_alt[get_text("energy_external_needed_label")] = df_alt[get_text("energy_external_needed_label")].apply(lambda x: f"{x:,.0f} kWh/Anno".replace(",", "."))

            df_alt.index = df_alt.index + 1
            df_alt.index.name = "Rank" 
            
            st.dataframe(df_alt, use_container_width=True)
        else:
            st.info("Nessuna altra configurazione valida trovata entro i limiti di ricerca.")
            

# --- Render Functions (Tab 2) ---
def render_tab2():
    st.header(get_text("t2_header"))
    st.markdown(get_text("t2_intro"))

    # Recupera i gruppi veicoli e i parametri tecnici dalla Tab 1
    # st.session_state['vehicle_groups_tab1'] è garantito esistere grazie all'inizializzazione in render_tab1 (o main logic)
    if 'vehicle_groups_tab1' not in st.session_state or sum(g['quantity'] for g in st.session_state['vehicle_groups_tab1']) == 0:
        st.warning("Configura i Gruppi Veicoli nella scheda 'Ottimizzatore Colonnine' (Tab 1) prima di procedere.")
        return
        
    # Costi
    all_charger_costs = get_charger_costs()
    ac_slots = st.session_state.get('ac_turnover_tab1', 4)
    dc_slots = st.session_state.get('dc_turnover_tab1', 6)
    
    # Gruppi
    vehicle_groups = st.session_state['vehicle_groups_tab1']
    total_vehicles = sum(g['quantity'] for g in vehicle_groups)
    all_vehicles = generate_vehicles_list(vehicle_groups)
    total_daily_energy_req = sum(v['energy_needed'] for v in all_vehicles)
    
    st.subheader(get_text("t2_current_config"))
    st.markdown(get_text("t2_config_details"))
    
    col_ac11, col_ac22, col_dc20, col_dc30, col_dc60, col_dc90, col_dc120 = st.columns(7)
    
    config = {
        "AC_11": col_ac11.number_input("AC 11 kW", min_value=0, value=1, step=1, key="t2_ac11_qty"),
        "AC_22": col_ac22.number_input("AC 22 kW", min_value=0, value=0, step=1, key="t2_ac22_qty"),
        "DC_20": col_dc20.number_input("DC 20 kW", min_value=0, value=0, step=1, key="t2_dc20_qty"),
        "DC_30": col_dc30.number_input("DC 30 kW", min_value=0, value=1, step=1, key="t2_dc30_qty"),
        "DC_60": col_dc60.number_input("DC 60 kW", min_value=0, value=0, step=1, key="t2_dc60_qty"),
        "DC_90": col_dc90.number_input("DC 90 kW", min_value=0, value=0, step=1, key="t2_dc90_qty"),
        "DC_120": col_dc120.number_input("DC 120 kW", min_value=0, value=0, step=1, key="t2_dc120_qty"),
    }
    
    # Rimuove le colonnine con 0 unità per la simulazione
    config_filtered = {k: v for k, v in config.items() if v > 0}
    
    if st.button(get_text("t2_run_simulation"), key="t2_run_btn"):
        if sum(config_filtered.values()) == 0:
            st.error("Inserisci almeno un caricatore per la simulazione.")
            st.session_state['t2_results'] = None
            return

        with st.spinner("Esecuzione simulazione di schedulazione..."):
            df_schedule, vehicles_status = simulate_charging_plan(
                config_filtered, vehicle_groups, all_charger_costs, ac_slots, dc_slots
            )
            
            # Calcoli KPI
            vehicles_scheduled = sum(1 for v in vehicles_status if v['charged_status'] >= v['energy_needed'] * 0.99)
            energy_charged = sum(v['charged_status'] for v in vehicles_status)
            energy_coverage = (energy_charged / (total_daily_energy_req + 0.001)) * 100
            
            st.session_state['t2_results'] = {
                "config": config_filtered,
                "df_schedule": df_schedule,
                "vehicles_status": vehicles_status,
                "vehicles_scheduled": vehicles_scheduled,
                "total_vehicles": total_vehicles,
                "energy_charged": energy_charged,
                "energy_coverage": energy_coverage,
                "total_daily_energy_req": total_daily_energy_req
            }

    # Visualizzazione Risultati
    if st.session_state.get('t2_results'):
        results = st.session_state['t2_results']
        
        st.divider()
        st.subheader(get_text("t2_results"))
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        col_m1.metric(get_text("t2_vehicles_served"), f"{results['vehicles_scheduled']} / {results['total_vehicles']}", 
                      delta_color="normal")
        col_m2.metric(get_text("t2_energy_coverage"), f"{results['energy_coverage']:.1f} %")
        col_m3.metric(get_text("t2_time_used"), f"{results['energy_charged']:.1f} kWh", 
                      help=f"{get_text('t2_time_needed')}: {results['total_daily_energy_req']:.1f} kWh")

        # Configurazione Utilizzata
        st.markdown(f"#### Configurazione Attuale Sottoposta al Test:")
        st.code(str({k: v for k, v in results['config'].items() if v > 0}).replace("'", "").replace("{", "").replace("}", ""))

        # Gantt Chart (riutilizzo codice Tab 1)
        df_schedule = results['df_schedule']
        if not df_schedule.empty:
            st.markdown(f"#### {get_text('charging_plan_header')} ")
            
            df_plot = df_schedule.copy()
            df_plot['Duration'] = df_plot['End_dt'] - df_plot['Start_dt']
            df_plot['Start_formatted'] = df_plot['Start_dt'].dt.strftime('%H:%M')
            df_plot['End_formatted'] = df_plot['End_dt'].dt.strftime('%H:%M')
            df_plot.sort_values(by='Charger', inplace=True)

            fig_gantt = px.timeline(df_plot, x_start="Start_dt", x_end="End_dt", y="Charger", 
                                    color="Vehicle", 
                                    text="Vehicle",
                                    hover_data={
                                        "Vehicle": True,
                                        "Start_formatted": True,
                                        "End_formatted": True,
                                        "Charger": True,
                                        "Type": False, 
                                    },
                                    title=get_text("charging_plan_header") + " (Test)")

            fig_gantt.update_traces(textposition='outside')
            fig_gantt.update_yaxes(autorange="reversed") 
            fig_gantt.update_xaxes(title="Ora del Giorno (h)", tickformat="%H:%M",
                                   range=[df_plot['Start_dt'].min() - timedelta(minutes=15), df_plot['End_dt'].max() + timedelta(minutes=15)])
            fig_gantt.update_layout(height=400 + 40 * len(df_plot['Charger'].unique()),
                                    margin=dict(l=20, r=20, t=50, b=20),
                                    xaxis_tickangle=-45)
            
            st.plotly_chart(fig_gantt, use_container_width=True)

# --- Render Functions (Tab 3) ---
def render_tab3():
    st.header(get_text("t3_header"))
    st.markdown(get_text("t3_intro"))
    
    all_charger_costs = get_charger_costs()
    charger_options = {
        "AC 22 kW": "AC_22",
        "DC 30 kW": "DC_30",
        "DC 60 kW": "DC_60",
        "DC 120 kW": "DC_120",
    }
    
    st.subheader(get_text("t3_charger_selection"))
    col_sel, col_cost = st.columns(2)
    
    selected_charger_name = col_sel.selectbox("Tipo di Colonnina", list(charger_options.keys()), key="t3_charger_select")
    selected_charger_key = charger_options[selected_charger_name]
    
    costs = all_charger_costs[selected_charger_key]
    
    # Parametri di input finanziari
    with col_cost:
        st.markdown("**Parametri Finanziari**")
        investment = st.number_input(get_text("t3_initial_investment"), min_value=1000, value=costs["unit"] + costs["install"], step=100, key="t3_investment", help="Costo totale di acquisto e installazione")
        cost_of_energy = st.number_input(get_text("t3_cost_of_energy"), min_value=0.01, value=0.18, step=0.01, key="t3_cost_of_energy")
        public_price = st.number_input(get_text("t3_public_price"), min_value=0.1, value=0.55, step=0.01, key="t3_public_price")
        avg_utilization = st.number_input(get_text("t3_avg_utilization"), min_value=0.5, max_value=24.0, value=4.0, step=0.5, key="t3_avg_utilization")
        target_roi = st.number_input(get_text("t3_target_roi"), min_value=0, max_value=100, value=15, step=1, key="t3_target_roi")
    
    
    if st.button(get_text("t3_calc_roi"), key="t3_calc_btn"):
        # Costanti
        DAYS_PER_YEAR = 365
        MAINT_ANNUAL = costs['maint_annual']
        POWER_KW = costs['power']
        
        # Calcoli
        # Energia erogata annua (assumendo efficienza 0.9 per AC, 0.8 per DC)
        efficiency = 0.8 if 'DC' in selected_charger_key else 0.9
        annual_energy_kwh = POWER_KW * avg_utilization * DAYS_PER_YEAR * efficiency
        
        # Ricavo
        annual_revenue = annual_energy_kwh * public_price
        
        # Costo Operativo
        annual_energy_cost = annual_energy_kwh * cost_of_energy
        annual_opex_cost = annual_energy_cost + MAINT_ANNUAL
        
        # Profitto
        annual_net_profit = annual_revenue - annual_opex_cost
        
        # Payback Period e ROI
        if annual_net_profit > 0:
            payback_period = investment / annual_net_profit
            annual_roi = (annual_net_profit / investment) * 100
        else:
            payback_period = float('inf')
            annual_roi = 0.0
            
        st.session_state['t3_roi_results'] = {
            "investment": investment,
            "annual_revenue": annual_revenue,
            "annual_opex_cost": annual_opex_cost,
            "annual_net_profit": annual_net_profit,
            "payback_period": payback_period,
            "annual_roi": annual_roi
        }
    
    
    # Visualizzazione Risultati
    if st.session_state.get('t3_roi_results'):
        results = st.session_state['t3_roi_results']
        
        st.divider()
        st.subheader(get_text("t3_roi_results"))
        
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        # 1. Investimento Iniziale
        col_m1.metric(get_text("t3_initial_investment"), f"€ {results['investment']:,.0f}".replace(",", "."))
        
        # 2. Ricavo Annuo
        col_m2.metric(get_text("t3_roi_annual_revenue"), f"€ {results['annual_revenue']:,.0f}".replace(",", "."))
        
        # 3. Costo Annuo Operativo (OPEX)
        col_m3.metric(get_text("t3_roi_annual_cost"), f"€ {results['annual_opex_cost']:,.0f}".replace(",", "."))
        
        # 4. Profitto Netto
        col_m4.metric(get_text("t3_roi_net_profit"), f"€ {results['annual_net_profit']:,.0f}".replace(",", "."), 
                      delta=f"{results['annual_net_profit']:,.0f}".replace(",", "."), 
                      delta_color="inverse" if results['annual_net_profit'] < 0 else "normal")
        
        # 5. ROI
        roi_delta = results['annual_roi'] - target_roi
        col_m5.metric(get_text("t3_roi_perc"), f"{results['annual_roi']:.1f} %", 
                      delta=f"{roi_delta:.1f} % vs target",
                      delta_color="normal" if roi_delta >= 0 else "inverse")
                      
        # Payback
        payback_display = f"{results['payback_period']:.1f} anni" if results['payback_period'] != float('inf') else "Non raggiunto"
        st.info(f"**{get_text('t3_payback')}**: {payback_display}")

# --- Render Functions (Tab 4) ---
def render_tab4():
    st.header(get_text("t4_header"))
    st.markdown(get_text("t4_intro"))

    all_charger_costs = get_charger_costs()
    wb_options = {
        "Wallbox 7.4 kW (Monofase)": "WB_7_4",
        "Wallbox 11 kW (Trifase)": "WB_11",
    }

    st.subheader("Configurazione e Dettagli Installazione")
    col_wb, col_inst = st.columns(2)
    
    with col_wb:
        selected_wb_name = st.selectbox(get_text("t4_power_select"), list(wb_options.keys()), key="t4_wb_select")
        selected_wb_key = wb_options[selected_wb_name]
        wb_costs = all_charger_costs[selected_wb_key]
        
        # Costo Wallbox (Unità) - personalizzabile
        wb_unit_cost = st.number_input(get_text("t4_wallbox_cost"), min_value=500, value=wb_costs["unit"], step=50, key="t4_wb_unit_cost")
    
    # Parametri tecnici di installazione
    with col_inst:
        installation_type = st.radio(get_text("t4_installation_type"), [get_text("t4_new_installation"), get_text("t4_existing_predisp")], key="t4_inst_type")
        distance_m = st.number_input(get_text("t4_distance"), min_value=1, max_value=100, value=15, step=1, key="t4_distance")
        cable_install_type = st.radio(get_text("t4_cable_install_type"), [get_text("t4_on_wall"), get_text("t4_underground")], key="t4_cable_inst")
        
        col_cert, col_fire = st.columns(2)
        include_cert = col_cert.checkbox(get_text("t4_certification"), value=True, key="t4_cert")
        condo_fire_cert = col_fire.checkbox(get_text("t4_condo_fire_cert"), value=False, key="t4_fire_cert")

    if st.button(get_text("t4_calc_cost"), key="t4_calc_btn"):
        
        # Parametri di base per la stima
        LABOR_BASE_HOUR = 40  # Costo orario manodopera
        LABOR_HOURS_WB = 8    # Ore base per installazione wallbox (cablaggio incluso)
        LABOR_HOURS_ADD_PER_METER = 0.1 # Ore aggiuntive per metro
        
        MATERIAL_COST_PER_METER = 20 # Costo cavo + canalina (stimato)
        if selected_wb_key == "WB_11": # Cavo trifase/sezione maggiore
            MATERIAL_COST_PER_METER = 30
        
        PANEL_COST = 300 # Costo medio quadro/protezioni
        FIRE_CERT_COST = 350
        
        # 1. Costo Wallbox (Unità)
        total_wb_cost = wb_unit_cost
        
        # 2. Costo Materiali (Cavi + Quadro)
        material_cost_cables = distance_m * MATERIAL_COST_PER_METER
        material_cost_panel = 0
        
        if installation_type == get_text("t4_new_installation"):
            material_cost_panel = PANEL_COST
            
        total_material_cost = material_cost_cables + material_cost_panel
        
        # Se c'è predisposizione, i costi sono ridotti
        if installation_type == get_text("t4_existing_predisp"):
            total_material_cost = 100 # Costo forfettario minimo per connettori/finali
            
        # 3. Costo Manodopera (Lavoro)
        labor_hours_total = LABOR_HOURS_WB + (distance_m * LABOR_HOURS_ADD_PER_METER)
        
        if cable_install_type == get_text("t4_underground"):
            # Aggiunge un moltiplicatore per lo scavo/posa a terra
            labor_hours_total *= 1.8 
        
        total_labor_cost = labor_hours_total * LABOR_BASE_HOUR
        
        # 4. Costi Aggiuntivi
        cert_cost = 150 if include_cert else 0 # Costo per DiCo
        fire_cost = FIRE_CERT_COST if condo_fire_cert else 0
        
        # 5. Costo Totale
        total_initial_cost = total_wb_cost + total_material_cost + total_labor_cost + cert_cost + fire_cost
        
        st.session_state['t4_results'] = {
            "wb_cost": total_wb_cost,
            "material_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "cert_cost": cert_cost + fire_cost,
            "total_cost": total_initial_cost
        }
    
    # Visualizzazione Risultati
    if st.session_state.get('t4_results'):
        results = st.session_state['t4_results']
        
        st.divider()
        st.subheader(get_text("t4_results"))
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        col_m1.metric(get_text("t4_wallbox_cost"), f"€ {results['wb_cost']:,.0f}".replace(",", "."))
        col_m2.metric(get_text("t4_material_cost"), f"€ {results['material_cost']:,.0f}".replace(",", "."))
        col_m3.metric(get_text("t4_labor_cost"), f"€ {results['labor_cost']:,.0f}".replace(",", "."))
        col_m4.metric("Costi Certificazioni/Extra", f"€ {results['cert_cost']:,.0f}".replace(",", "."))
        
        st.markdown(f"### {get_text('t4_total_cost')}: **€ {results['total_cost']:,.0f}**".replace(",", "."))

# --- Render Functions (Tab 5) ---
def render_tab5():
    st.header(get_text("t5_header"))
    st.markdown(get_text("t5_intro"))
    
    all_charger_costs = get_charger_costs()
    charger_options = {
        "AC 22 kW (1 unità)": "AC_22",
        "DC 30 kW (1 unità)": "DC_30",
        "DC 60 kW (1 unità)": "DC_60",
        "DC 120 kW (1 unità)": "DC_120",
    }
    
    st.subheader(get_text("t5_config_select"))
    col_sel, col_dist, col_labor = st.columns(3)
    
    selected_charger_name = col_sel.selectbox("Tipo di Colonnina", list(charger_options.keys()), key="t5_charger_select")
    selected_charger_key = charger_options[selected_charger_name]
    costs = all_charger_costs[selected_charger_key]
    
    # Parametri di input tecnici
    with col_dist:
        distance_m = st.number_input(get_text("t5_distance"), min_value=5, max_value=200, value=25, step=5, key="t5_distance_m")
        is_underground = st.checkbox(get_text("t5_is_underground"), value=False, key="t5_underground")

    with col_labor:
        material_multiplier = st.slider(get_text("t5_material_multiplier"), min_value=1.0, max_value=3.0, value=1.5, step=0.1, key="t5_mat_mult", help="Moltiplicatore sul costo base dei materiali (cavi e protezioni) per complessità/lunghezza")
        labor_multiplier = st.slider(get_text("t5_labor_multiplier"), min_value=1.0, max_value=3.0, value=1.5, step=0.1, key="t5_labor_mult", help="Moltiplicatore sulla manodopera base per complessità dell'installazione")
        

    # Costi Forfettari Personalizzabili
    st.subheader("Costi Forfettari e di Ingegneria (Stima)")
    col_cost_panel, col_cost_eng, col_cost_base_mat = st.columns(3)
    
    # Il costo della colonnina è personalizzabile dall'utente per la stima
    col_cost_panel.markdown(f"**{selected_charger_name}**")
    charger_unit_cost = col_cost_panel.number_input(get_text("t5_wallbox_cost"), min_value=costs["unit"] - 500, value=costs["unit"], step=100, key="t5_unit_cost")
    
    panel_cost = col_cost_eng.number_input(get_text("t5_panel_cost"), min_value=500, value=1500, step=100, key="t5_panel_cost", help="Costo del quadro elettrico principale/di sezionamento")
    engineering_cost = col_cost_eng.number_input(get_text("t5_engineering_cost"), min_value=0, value=2000, step=100, key="t5_engineering_cost", help="Costo per progettazione elettrica, pratiche autorizzative, ecc.")

    
    BASE_MATERIAL_PER_METER = 50 
    if costs['power'] >= 60:
         BASE_MATERIAL_PER_METER = 100
         
    material_base_per_meter = col_cost_base_mat.number_input(get_text("t5_base_material_per_meter"), min_value=20, value=BASE_MATERIAL_PER_METER, step=10, key="t5_mat_base_per_meter", help="Costo stimato per metro (cavi, guaine, tubo)")

    if st.button(get_text("t5_calc_cost"), key="t5_calc_btn"):
        
        # Parametri di base per la stima
        LABOR_BASE_HOURS = 24  # Ore base per installazione colonnina trifase/DC
        LABOR_BASE_RATE = 40  # Costo orario manodopera

        # 1. Costo Colonnina (Unità)
        total_charger_cost = charger_unit_cost
        
        # 2. Costo Materiali (Cavi + Protezioni + Lavori Edili)
        # Il costo del materiale è proporzionale alla distanza e alla potenza
        # Si aggiunge un costo forfettario per le protezioni locali (che è già incluso nell'installazione standard, qui lo si stima separatamente)
        material_cables_protections_cost = distance_m * material_base_per_meter * material_multiplier
        
        scavo_cost = 0
        if is_underground:
             # Costo scavo/ripristino per metro
             scavo_cost = distance_m * 40
            
        total_material_cost = material_cables_protections_cost + scavo_cost
        
        # 3. Costo Manodopera (Lavoro)
        # La manodopera è influenzata da distanza e complessità (multiplier)
        labor_hours_distance_component = (distance_m / 10) * 4 # 4 ore ogni 10 metri
        
        total_labor_hours = LABOR_BASE_HOURS + labor_hours_distance_component
        total_labor_cost = total_labor_hours * LABOR_BASE_RATE * labor_multiplier
        
        # 4. Costo Totale
        total_initial_cost = total_charger_cost + panel_cost + engineering_cost + total_material_cost + total_labor_cost
        
        st.session_state['t5_results'] = {
            "charger_cost": total_charger_cost,
            "panel_cost": panel_cost,
            "engineering_cost": engineering_cost,
            "material_cables_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "total_cost": total_initial_cost
        }
    
    # Visualizzazione Risultati
    if st.session_state.get('t5_results'):
        results = st.session_state['t5_results']
        
        st.divider()
        st.subheader(get_text("t5_total_cost"))
        
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        
        col_m1.metric(get_text("t5_wallbox_cost"), f"€ {results['charger_cost']:,.0f}".replace(",", "."))
        col_m2.metric(get_text("t5_material_cost"), f"€ {results['material_cables_cost']:,.0f}".replace(",", "."))
        col_m3.metric(get_text("t5_labor_cost"), f"€ {results['labor_cost']:,.0f}".replace(",", "."))
        col_m4.metric(get_text("t5_panel_cost"), f"€ {results['panel_cost']:,.0f}".replace(",", "."))
        col_m5.metric(get_text("t5_engineering_cost"), f"€ {results['engineering_cost']:,.0f}".replace(",", "."))
        
        st.markdown(f"### {get_text('t5_total_cost')}: **€ {results['total_cost']:,.0f}**".replace(",", "."))


# --- Main App Logic ---
# Inizializzazione per la CORREZIONE DEL KEYERROR e i default
if 'vehicle_groups_tab1' not in st.session_state: 
    st.session_state['vehicle_groups_tab1'] = [
        {'quantity': 5, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8},
        {'quantity': 3, 'daily_km': 300, 'consumption': 20.0, 'arrival_time': 10, 'departure_time': 12}
    ]
if 'num_groups_tab1' not in st.session_state: st.session_state['num_groups_tab1'] = 2

# Inizializzazione per i risultati (per evitare KeyErrors/TypeErrors)
if 'optimization_results' not in st.session_state: st.session_state['optimization_results'] = None
if 't2_results' not in st.session_state: st.session_state['t2_results'] = None
if 't3_roi_results' not in st.session_state: st.session_state['t3_roi_results'] = None
if 't4_results' not in st.session_state: st.session_state['t4_results'] = None
if 't5_results' not in st.session_state: st.session_state['t5_results'] = None 

# Inizializzazione per i parametri tecnici (usati in Tab 2 e Tab 1 sidebar)
if 'ac_turnover_tab1' not in st.session_state: st.session_state['ac_turnover_tab1'] = 4
if 'dc_turnover_tab1' not in st.session_state: st.session_state['dc_turnover_tab1'] = 6

st.title(get_text("app_title"))

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    get_text("tab1_title"), 
    get_text("tab2_title"), 
    get_text("tab3_title"), 
    get_text("tab4_title"), 
    get_text("tab5_title")
])

with tab1:
    render_tab1()
with tab2:
    render_tab2()
with tab3:
    render_tab3()
with tab4:
    render_tab4()
with tab5:
    render_tab5()

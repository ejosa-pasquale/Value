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
        "total_initial_cost": "Costo Totale Iniziale",
        "internal_energy_charged": "Energia Caricata Internamente (kWh)",
        "estimated_annual_savings": "Risparmio Annuo Stimato (€)",
        "combined_efficiency": "Copertura Ricarica (%)",
        "full_charge_success": "✅ Tutti i veicoli possono essere caricati completamente con questa configurazione.",
        "partial_charge_warning": "⚠️ **Attenzione:** Configurazione non ottimale.",
        "no_solution_found": "❌ Nessuna configurazione valida trovata.",
        "charging_plan_header": "Simulazione Piano di Ricarica (Gantt)",
        "vehicle_id_label": "Veicolo/Gruppo",
        "start_time_label": "Inizio",
        "end_time_label": "Fine",
        "charger_type_tooltip": "Caricatore Assegnato (ID)",
        "config_info_gantt": "Configurazione Utilizzata per la Simulazione",
        "simulation_summary": "Riepilogo Simulazione",
        "charging_table_header": "Dettagli Ricariche Schedulate", 
        "cost_label": "Costo Iniziale", 
        "efficiency_score_label": "Efficienza (%)", 
        "charger_mix_chart": "Distribuzione Caricatori per Efficienza/Costo", 
        "cost_unit_label": "Costo Unità",
        "cost_install_label": "Costo Installazione",
        "cost_maintenance_label": "Costo Manutenzione Annuale",
        "power_label": "Potenza Totale Impianto (kW)",
        "final_config_header": "🎯 Configurazione Finale Raccomandata", 
        "total_vehicles_expected": "Veicoli totali attesi", 
        "vehicles_scheduled": "Veicoli schedulati (Completati)", 
        
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

        # Tab 5 Keys (NUOVI)
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

def simulate_charging_plan(config, groups, charger_costs_data, ac_slots, dc_slots):
    """Crea una simulazione di scheduling realistica con vincoli di tempo e slot e aggiunge pausa."""
    
    # 1. Definizione Tipi Caricatore (Ordinati per potenza decrescente per priorità di schedulazione)
    charger_types = ["DC_120", "DC_90", "DC_60", "DC_30", "DC_20", "AC_22", "AC_11"] 
    charger_nominal_power = {t: charger_costs_data.get(t, {}).get('power', 0) for t in charger_types}
    vehicles_to_charge = generate_vehicles_list(groups)
    
    # 2. Preparazione Colonnine (Gestione Slot)
    charger_pool = []
    for t in charger_types:
        for i in range(config.get(t, 0)):
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
    
    for vehicle in vehicles_to_charge:
        remaining_energy = vehicle['energy_needed']
        
        # Prova i caricatori in ordine di potenza nominale (per caricare più velocemente)
        for charger in sorted(charger_pool, key=lambda c: charger_nominal_power.get(c['type'], 0), reverse=True): 
            if remaining_energy <= 0: break
            if charger['used_slots'] >= charger['total_slots']: continue

            # Potenza effettiva di ricarica (limitata a 11kW se AC)
            charger_power_val = get_effective_power(charger['type'], charger['power'])
            
            efficiency = 0.8 if 'DC' in charger['type'] else 0.9
            
            ideal_charge_time = remaining_energy / (charger_power_val * efficiency + 0.001)
            
            # --- LOGICA DI SCHEDULAZIONE CON PAUSA ---
            
            # Trova l'orario di fine dell'ultima ricarica schedulata su questo caricatore
            latest_end_time = 0
            if charger['schedule']:
                 latest_end_time = max(end for start, end in charger['schedule'])
            
            # L'orario di inizio potenziale è il massimo tra:
            # 1. L'orario di arrivo del veicolo
            # 2. L'orario di fine dell'ultima sessione + la pausa (BUFFER_TIME_H)
            potential_start_time = max(vehicle['arrival'], latest_end_time + BUFFER_TIME_H)

            # --- FINE LOGICA DI SCHEDULAZIONE CON PAUSA ---
            
            time_available = vehicle['departure'] - potential_start_time
            
            if time_available > 0:
                time_this_session = min(ideal_charge_time, time_available)
                end_time = potential_start_time + time_this_session
                
                # Taglia la ricarica se supera l'orario di partenza
                if end_time > vehicle['departure']:
                     time_this_session = vehicle['departure'] - potential_start_time
                     end_time = vehicle['departure']

                if time_this_session > 0.01: # Richiede almeno ~36 secondi
                    energy_charged_this_session = time_this_session * charger_power_val * efficiency
                    
                    # Ricalcola il tempo esatto se l'energia caricata supera il bisogno
                    if energy_charged_this_session > remaining_energy:
                         energy_charged_this_session = remaining_energy
                         time_this_session = energy_charged_this_session / (charger_power_val * efficiency + 0.001)
                         end_time = potential_start_time + time_this_session

                    if energy_charged_this_session > 0:
                        
                        # Aggiorna lo stato del caricatore
                        charger['schedule'].append((potential_start_time, end_time))
                        charger['schedule'].sort(key=lambda x: x[0]) 
                        charger['used_slots'] += 1
                        
                        # Aggiorna lo stato del veicolo
                        remaining_energy -= energy_charged_this_session
                        vehicle['charged_status'] += energy_charged_this_session
                        
                        # Registra l'evento
                        charging_schedule.append({
                            'Vehicle': vehicle['id'],
                            'Charger': charger['id'],
                            'Start': potential_start_time,
                            'End': end_time,
                            'Type': charger['type'],
                            'Color': vehicle['color']
                        })
                        
                        vehicle['session'].append({
                            'Charger': charger['id'],
                            'Start': potential_start_time,
                            'End': end_time,
                            'Energy': energy_charged_this_session
                        })

    # 4. Normalizzazione oraria per il grafico (shift al 24h)
    df_schedule = pd.DataFrame(charging_schedule)
    if not df_schedule.empty:
        df_schedule['Start_dt'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(df_schedule['Start'], unit='h')
        df_schedule['End_dt'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(df_schedule['End'], unit='h')
        
    return df_schedule, vehicles_to_charge 

# --- FUNZIONE AGGIORNATA PER LA SELEZIONE FINALE ---
def find_final_optimized_config(all_configs, params):
    """
    Simula e seleziona la configurazione finale che massimizza i veicoli schedulati 
    e minimizza il costo tra quelle con la massima schedulazione.
    """
    
    groups = params['vehicle_groups']
    charger_costs_data = params['charger_costs']
    ac_slots = params['ac_slots']
    dc_slots = params['dc_slots']
    
    total_vehicles_expected = sum(g['quantity'] for g in groups)
    
    best_final_results = None
    df_schedule_final = pd.DataFrame()
    vehicles_status_final = []
    
    max_scheduled_vehicles = -1
    min_cost_for_max_scheduled = float('inf')
    
    optimization_steps_log = ["Avvio simulazione dettagliata su configurazioni top (Massimo 50)..."]
    
    # Limita la simulazione dettagliata solo alle top 50 configurazioni 
    # (basate sull'efficienza approssimata del brute-force iniziale)
    MAX_SIMULATIONS = 50 
    
    for i, config_result_approx in enumerate(all_configs[:MAX_SIMULATIONS]):
        
        current_config = config_result_approx['config']
        
        # Simula con la configurazione
        df_schedule_current, vehicles_status_current = simulate_charging_plan(
            current_config, groups, charger_costs_data, ac_slots, dc_slots
        )
        
        # Calcola i veicoli completamente caricati (>= 99% dell'energia richiesta)
        vehicles_scheduled_current = sum(1 for v in vehicles_status_current if v['charged_status'] >= v['energy_needed'] * 0.99)
        current_cost = config_result_approx['total_initial_cost']
        
        log_message = f"Configurazione {i+1} ({str({k: v for k, v in current_config.items() if v > 0})}): Schedulati {vehicles_scheduled_current} / {total_vehicles_expected}. Costo: € {current_cost:,.0f}."
        optimization_steps_log.append(log_message.replace(",", ".")) # Uso il punto per i separatori nei log per chiarezza
        
        # Logica di selezione: Massimizza Veicoli Schedulati (Primary), Minimizza Costo (Secondary)
        is_better = False
        
        if vehicles_scheduled_current > max_scheduled_vehicles:
            is_better = True
        elif vehicles_scheduled_current == max_scheduled_vehicles:
            if current_cost < min_cost_for_max_scheduled:
                is_better = True

        if is_better:
            max_scheduled_vehicles = vehicles_scheduled_current
            min_cost_for_max_scheduled = current_cost
            
            # Aggiornamento dei dati della migliore configurazione trovata finora
            final_cost_details = calculate_charger_costs(current_config, charger_costs_data)
            final_energy_charged = sum(v['charged_status'] for v in vehicles_status_current)
            total_daily_energy_req = sum(v['energy_needed'] for v in vehicles_status_current)
            
            annual_savings = (final_energy_charged * 300 * (params['public_cost'] - params['private_cost'])) 
            annual_net_benefit = annual_savings - final_cost_details["total_maint_annual"] 
            energy_coverage_perc = (final_energy_charged / (total_daily_energy_req + 0.001)) * 100

            best_final_results = {
                "config": current_config,
                "total_initial_cost": final_cost_details["total_initial_cost"],
                "total_power": final_cost_details["total_power"],
                "internal_energy_charged": final_energy_charged,
                "total_energy_request": total_daily_energy_req,
                "estimated_annual_savings": annual_net_benefit,
                "combined_efficiency": energy_coverage_perc,
                "is_full_charge": vehicles_scheduled_current == total_vehicles_expected,
                "vehicles_scheduled": vehicles_scheduled_current,
                "total_vehicles_expected": total_vehicles_expected,
                **final_cost_details
            }
            # Salvataggio anche dei dati di simulazione (Gantt, Status) della migliore configurazione
            df_schedule_final = df_schedule_current
            vehicles_status_final = vehicles_status_current
            
        
        # Ottimizzazione del ciclo: se abbiamo raggiunto il massimo di veicoli e 
        # le successive configurazioni approssimate sono molto meno efficienti, 
        # è improbabile che migliorino il risultato di schedulazione.
        if max_scheduled_vehicles == total_vehicles_expected and config_result_approx['combined_efficiency'] < 70: 
             optimization_steps_log.append("Trovata soluzione al 100%. Le configurazioni rimanenti sono molto meno efficienti in stima. Termino l'analisi.")
             break
        
    
    optimization_steps_log.append(f"--- Risultato Finale ---")
    if best_final_results:
        optimization_steps_log.append(f"🎯 Configurazione Finale Selezionata: {str({k: v for k, v in best_final_results['config'].items() if v > 0})}. Schedulati: {max_scheduled_vehicles} / {total_vehicles_expected}. Costo Minimo per questa copertura: € {min_cost_for_max_scheduled:,.0f}.".replace(",", "."))
    
    return best_final_results, df_schedule_final, vehicles_status_final, optimization_steps_log
# --- FINE FUNZIONE AGGIORNATA ---


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
    
    max_ac11 = min(max_units_per_type, ceil(budget / (costs["AC_11"]["unit"] + costs["AC_11"]["install"])))
    max_ac22 = min(max_units_per_type, ceil(budget / (costs["AC_22"]["unit"] + costs["AC_22"]["install"])))
    max_dc20 = min(max_units_per_type, ceil(budget / (costs["DC_20"]["unit"] + costs["DC_20"]["install"]))) 
    max_dc30 = min(max_units_per_type, ceil(budget / (costs["DC_30"]["unit"] + costs["DC_30"]["install"])))
    max_dc60 = min(max_units_per_type, ceil(budget / (costs["DC_60"]["unit"] + costs["DC_60"]["install"])))
    max_dc90 = min(max_units_per_type, ceil(budget / (costs["DC_90"]["unit"] + costs["DC_90"]["install"]))) 
    max_dc120 = min(max_units_per_type, ceil(budget / (costs["DC_120"]["unit"] + costs["DC_120"]["install"]))) 
    
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
                                         max_daily_energy_supply += config[dc_type] * dc_slots * (costs[dc_type]["power"] * hours * 0.8)

                                internal_energy_charged = min(total_daily_energy_req, max_daily_energy_supply)
                                
                                annual_savings = (internal_energy_charged * 300 * (public_cost - private_cost)) 
                                annual_net_benefit = annual_savings - total_maint_annual 
                                
                                energy_coverage_perc = (internal_energy_charged / (total_daily_energy_req + 0.001)) * 100
                                
                                config_result = {
                                    "config": config,
                                    "total_initial_cost": current_cost,
                                    "total_power": current_power,
                                    "internal_energy_charged": internal_energy_charged,
                                    "total_energy_request": total_daily_energy_req,
                                    "estimated_annual_savings": annual_net_benefit,
                                    "combined_efficiency": energy_coverage_perc,
                                    "is_full_charge": internal_energy_charged >= total_daily_energy_req * 0.99,
                                    **cost_details 
                                }
                                
                                all_configs.append(config_result)

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
    colors_map = {
        c: ('#3498DB' if 'DC' in c else '#2ECC71') for c in df['Caricatore'].unique()
    }

    fig = px.bar(df, x='Caricatore', y='Quantità', title=title,
                 color='Caricatore',
                 color_discrete_map=colors_map,
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

    # Inizializzazione per il test richiesto: G1: 5x100km (18-8), G2: 3x300km (10-12)
    if 'vehicle_groups_tab1' not in st.session_state or len(st.session_state['vehicle_groups_tab1']) == 0 or st.session_state['num_groups_tab1'] == 0:
        st.session_state['vehicle_groups_tab1'] = [
            {'quantity': 5, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8},
            {'quantity': 3, 'daily_km': 300, 'consumption': 20.0, 'arrival_time': 10, 'departure_time': 12}
        ]
        st.session_state['num_groups_tab1'] = 2
        
    if 'optimization_results' not in st.session_state:
        st.session_state['optimization_results'] = None
        st.session_state['optimization_alternatives'] = []
        st.session_state['df_schedule_final'] = pd.DataFrame() 
        st.session_state['vehicles_status_final'] = []
        st.session_state['optimization_log'] = []

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
        ac_slots = col_t1.number_input(get_text("ac_turnover"), min_value=1, value=st.session_state.get('ac_turnover_tab1', 4), step=1, key="ac_turnover_tab1", help="Numero di volte che la singola colonnina AC può ricaricare veicoli al giorno (Slot/Cicli)")
        dc_slots = col_t2.number_input(get_text("dc_turnover"), min_value=1, value=st.session_state.get('dc_turnover_tab1', 6), step=1, key="dc_turnover_tab1", help="Numero di volte che la singola colonnina DC può ricaricare veicoli al giorno (Slot/Cicli)")

        custom_costs = {}
        with st.sidebar.expander(get_text("charger_details_expander")):
            st.subheader("AC 11kW")
            col_c1, col_c2 = st.columns(2)
            unit_ac11 = col_c1.number_input(get_text("unit_cost"), value=default_ac11["unit"], min_value=100, key="unit_ac11")
            install_ac11 = col_c2.number_input(get_text("installation_cost"), value=default_ac11["install"], min_value=100, key="install_ac11")
            custom_costs["AC_11"] = {"unit": unit_ac11, "install": install_ac11}
            
            st.subheader("AC 22kW (Effettivo 11kW per vincolo veicolo)")
            col_c3, col_c4 = st.columns(2)
            unit_ac22 = col_c3.number_input(get_text("unit_cost"), value=default_ac22["unit"], min_value=100, key="unit_ac22")
            install_ac22 = col_c4.number_input(get_text("installation_cost"), value=default_ac22["install"], min_value=100, key="install_ac22")
            custom_costs["AC_22"] = {"unit": unit_ac22, "install": install_ac22}
            
            st.subheader("DC 20kW")
            col_c5, col_c6 = st.columns(2)
            unit_dc20 = col_c5.number_input(get_text("unit_cost"), value=default_dc20["unit"], min_value=1000, key="unit_dc20")
            install_dc20 = col_c6.number_input(get_text("installation_cost"), value=default_dc20["install"], min_value=1000, key="install_dc20")
            custom_costs["DC_20"] = {"unit": unit_dc20, "install": install_dc20}
            
            st.subheader("DC 30kW")
            col_c7, col_c8 = st.columns(2)
            unit_dc30 = col_c7.number_input(get_text("unit_cost"), value=default_dc30["unit"], min_value=1000, key="unit_dc30")
            install_dc30 = col_c8.number_input(get_text("installation_cost"), value=default_dc30["install"], min_value=1000, key="install_dc30")
            custom_costs["DC_30"] = {"unit": unit_dc30, "install": install_dc30}
            
            st.subheader("DC 60kW")
            col_c9, col_c10 = st.columns(2)
            unit_dc60 = col_c9.number_input(get_text("unit_cost"), value=default_dc60["unit"], min_value=1000, key="unit_dc60")
            install_dc60 = col_c10.number_input(get_text("installation_cost"), value=default_dc60["install"], min_value=1000, key="install_dc60")
            custom_costs["DC_60"] = {"unit": unit_dc60, "install": install_dc60}
            
            st.subheader("DC 90kW")
            col_c11, col_c12 = st.columns(2)
            unit_dc90 = col_c11.number_input(get_text("unit_cost"), value=default_dc90["unit"], min_value=1000, key="unit_dc90")
            install_dc90 = col_c12.number_input(get_text("installation_cost"), value=default_dc90["install"], min_value=1000, key="install_dc90")
            custom_costs["DC_90"] = {"unit": unit_dc90, "install": install_dc90}
            
            st.subheader("DC 120kW")
            col_c13, col_c14 = st.columns(2)
            unit_dc120 = col_c13.number_input(get_text("unit_cost"), value=default_dc120["unit"], min_value=1000, key="unit_dc120")
            install_dc120 = col_c14.number_input(get_text("installation_cost"), value=default_dc120["install"], min_value=1000, key="install_dc120")
            custom_costs["DC_120"] = {"unit": unit_dc120, "install": install_dc120}
        
        charger_costs_data = get_charger_costs(custom_costs)
        
        with st.sidebar.expander(get_text("energy_costs")):
            private_cost = st.number_input(get_text("private_charge_cost"), min_value=0.01, value=0.20, step=0.01, key="private_cost_tab1")
            public_cost = st.number_input(get_text("public_charge_cost"), min_value=0.01, value=0.45, step=0.01, key="public_cost_tab1")
        
    # --- Main Area Inputs (Vehicle Config) ---
    st.subheader(get_text("vehicle_config"))
    
    num_groups = st.number_input(
        get_text("num_vehicle_groups"), 
        min_value=1, 
        value=st.session_state['num_groups_tab1'], 
        step=1, 
        key="num_groups_tab1_input"
    )
    
    if 'num_groups_tab1' not in st.session_state or st.session_state['num_groups_tab1'] != num_groups:
        st.session_state['num_groups_tab1'] = num_groups
        st.session_state['vehicle_groups_tab1'] = [{'quantity': 1, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8} for _ in range(num_groups)]
        # Ricalcola la configurazione di default se il numero di gruppi cambia
        st.session_state['vehicle_groups_tab1'] = st.session_state['vehicle_groups_tab1'][:num_groups]
        while len(st.session_state['vehicle_groups_tab1']) < num_groups:
             st.session_state['vehicle_groups_tab1'].append({'quantity': 1, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8})


    vehicle_groups = []
    
    for i in range(st.session_state['num_groups_tab1']):
        group = st.session_state['vehicle_groups_tab1'][i]
        with st.expander(get_text("group_header").format(i=i+1), expanded=True):
            col_q, col_k, col_c = st.columns(3)
            col_a, col_d = st.columns(2)
            
            group['quantity'] = col_q.number_input(get_text("group_quantity"), min_value=1, value=group.get('quantity', 1), step=1, key=f"qty_{i}")
            group['daily_km'] = col_k.number_input(get_text("group_daily_km"), min_value=1, value=group.get('daily_km', 100), step=10, key=f"km_{i}")
            group['consumption'] = col_c.number_input(get_text("group_consumption"), min_value=10.0, value=group.get('consumption', 20.0), step=0.5, key=f"cons_{i}")
            group['arrival_time'] = col_a.slider(get_text("group_arrival_time"), min_value=0, max_value=23, value=group.get('arrival_time', 18), step=1, key=f"arr_{i}")
            group['departure_time'] = col_d.slider(get_text("group_departure_time"), min_value=0, max_value=24, value=group.get('departure_time', 8), step=1, key=f"dep_{i}")
            
            vehicle_groups.append(group)
            st.session_state['vehicle_groups_tab1'][i] = group
            
    if st.button(get_text("calculate_optimization")):
        if sum(g['quantity'] for g in vehicle_groups) == 0:
            st.warning("Aggiungi almeno un veicolo.")
        else:
            params = {
                'budget': budget,
                'max_power': max_power,
                'ac_slots': ac_slots,
                'dc_slots': dc_slots,
                'private_cost': private_cost,
                'public_cost': public_cost,
                'charger_costs': charger_costs_data,
                'vehicle_groups': vehicle_groups
            }
            
            # 1. Brute force per trovare le migliori N configurazioni (approssimate)
            all_configs = calculate_optimization_results(params)
            
            if not all_configs:
                st.session_state['optimization_results'] = None
                st.session_state['optimization_log'] = ["❌ Nessuna configurazione trovata che rispetti i vincoli di Budget e Potenza."]
                st.warning(get_text("no_solution_found"))
            else:
                # 2. Schedulazione dettagliata per trovare la configurazione che MASSIMIZZA le auto 
                # e MINIMIZZA il costo (nuova logica richiesta)
                final_results, df_schedule_final, vehicles_status_final, optimization_log = find_final_optimized_config(
                    all_configs, params
                )
                
                st.session_state['optimization_results'] = final_results
                st.session_state['df_schedule_final'] = df_schedule_final
                st.session_state['vehicles_status_final'] = vehicles_status_final
                
                # --- MODIFICA RICHIESTA: SALVATAGGIO TOP 30 ALTERNATIVE ---
                st.session_state['optimization_alternatives'] = all_configs[1:31] # Top 30 alternative (excl. the best)
                # --- FINE MODIFICA ---
                
                st.session_state['optimization_log'] = optimization_log
                
                st.rerun()
                

    # --- Display Results ---
    if st.session_state['optimization_results']:
        results = st.session_state['optimization_results']
        
        st.subheader(get_text("final_config_header"))
        
        # Display Status
        if results['is_full_charge']:
            st.success(get_text("full_charge_success"))
        else:
            st.error(get_text("partial_charge_warning"))

        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(get_text("total_initial_cost"), f"€ {results['total_initial_cost']:,.0f}".replace(",", "."))
        col2.metric(get_text("estimated_annual_savings"), f"€ {results['estimated_annual_savings']:,.0f}".replace(",", "."))
        col3.metric(get_text("combined_efficiency"), f"{results['combined_efficiency']:.1f} %".replace(".", ","))
        col4.metric(get_text("power_label"), f"{results['total_power']:.1f} kW".replace(".", ","))

        st.markdown("---")
        
        # Display Final Configuration Chart
        st.plotly_chart(display_config_chart(results['config'], "Configurazione Colonnine Raccomandata"), use_container_width=True)

        # Optimization Log
        with st.expander("Dettagli del processo di Ottimizzazione", expanded=False):
            st.markdown("\n".join(f"- {log}" for log in st.session_state['optimization_log']))

        # Scheduling Gantt Chart
        st.subheader(get_text("charging_plan_header"))
        
        df_schedule = st.session_state['df_schedule_final']
        vehicles_status = st.session_state['vehicles_status_final']
        
        if not df_schedule.empty:
            # Prepare data for Gantt chart
            df_gantt = df_schedule.copy()
            df_gantt['Start'] = df_gantt['Start_dt']
            df_gantt['Finish'] = df_gantt['End_dt']
            df_gantt['Task'] = df_gantt['Charger']
            df_gantt['Resource'] = df_gantt['Vehicle']
            df_gantt['Hover Text'] = df_gantt.apply(
                lambda row: f"Veicolo: {row['Vehicle']}<br>Caricatore: {row['Charger']}<br>Inizio: {row['Start_dt'].strftime('%H:%M')}<br>Fine: {row['End_dt'].strftime('%H:%M')}", 
                axis=1
            )
            
            # Create a combined resource name for Gantt visualization: Vehicle (Group)
            vehicle_groups_map = {v['id']: v['group_id'] for v in vehicles_status}
            df_gantt['Vehicle_Label'] = df_gantt['Vehicle'].apply(lambda x: f"{x} ({vehicle_groups_map.get(x, 'N/A')})")
            
            # Create Gantt chart using Plotly
            fig = px.timeline(
                df_gantt, 
                x_start="Start", 
                x_end="Finish", 
                y="Vehicle_Label", 
                color="Charger", 
                text="Charger", 
                custom_data=['Hover Text']
            )

            fig.update_traces(
                hovertemplate='%{customdata[0]}<extra></extra>',
                texttemplate='%{text}'
            )

            fig.update_yaxes(categoryorder='array', categoryarray=df_gantt['Vehicle_Label'].unique()[::-1]) # Order vehicles
            fig.update_xaxes(tickformat="%H:%M", range=[datetime(2023, 1, 1), datetime(2023, 1, 2) + timedelta(hours=8)]) # 00:00 to 32:00 (8:00 AM day after)
            fig.update_layout(
                title=get_text("charging_plan_header"),
                xaxis_title="Orario (24h)",
                yaxis_title=get_text("vehicle_id_label"),
                legend_title=get_text("charger_type_tooltip"),
                height=max(400, len(df_gantt['Vehicle_Label'].unique()) * 30 + 100)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Simulation Summary
        st.subheader(get_text("simulation_summary"))
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        col_sum1.metric(get_text("total_vehicles_expected"), results['total_vehicles_expected'])
        col_sum2.metric(get_text("vehicles_scheduled"), results['vehicles_scheduled'])
        col_sum3.metric(get_text("internal_energy_charged"), f"{results['internal_energy_charged']:.1f} kWh".replace(".", ","))
        
        # Charging Table Details
        if vehicles_status:
            st.subheader(get_text("charging_table_header"))
            
            charge_data = []
            for v in vehicles_status:
                charged_perc = (v['charged_status'] / (v['energy_needed'] + 0.001)) * 100
                charge_data.append({
                    "Veicolo/Gruppo": v['id'],
                    "Energia Richiesta (kWh)": f"{v['energy_needed']:.1f}".replace(".", ","),
                    "Energia Caricata (kWh)": f"{v['charged_status']:.1f}".replace(".", ","),
                    "Copertura (%)": f"{charged_perc:.1f} %".replace(".", ","),
                    "Arrivo (h)": f"{v['arrival']}:00",
                    "Partenza (h)": f"{v['departure']}:00 (o giorno dopo)",
                    "Stato": "COMPLETO" if charged_perc >= 99 else "PARZIALE"
                })
            df_charge_details = pd.DataFrame(charge_data)
            st.dataframe(df_charge_details, hide_index=True, use_container_width=True)
            
        # --- MODIFICA RICHIESTA: NUOVA TABELLA ALTERNATIVE ---
        with st.expander("Tutte le Configurazioni Alternative (Top 30 per Efficienza/Costo)", expanded=False):
            alternatives = st.session_state['optimization_alternatives']
            if alternatives:
                alt_data = []
                for i, alt in enumerate(alternatives):
                    # Formatta il mix di configurazione per la tabella
                    config_str = ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in alt['config'].items() if v > 0)
                    
                    alt_data.append({
                        "#": i + 1,
                        "Configurazione Caricatori": config_str,
                        "Efficienza (%)": alt['combined_efficiency'],
                        "Costo Iniziale (€)": alt['total_initial_cost'],
                        "Potenza Totale (kW)": alt['total_power'],
                    })
                
                df_alt = pd.DataFrame(alt_data)
                
                st.dataframe(
                    df_alt.style.format({
                        "Efficienza (%)": "{:.1f}".replace(".", ","),
                        "Costo Iniziale (€)": "€ {:,.0f}".replace(",", "."),
                        "Potenza Totale (kW)": "{:.1f}".replace(".", ",")
                    }), 
                    hide_index=True, 
                    use_container_width=True
                )
            else:
                st.info("Nessuna alternativa significativa trovata.")
        # --- FINE MODIFICA RICHIESTA ---

# --- Render Functions (Tab 2, 3, 4 - Placeholder for completeness) ---

def render_tab2():
    st.header(get_text("t2_header"))
    st.info("Funzionalità in costruzione. Utilizzerà i parametri veicoli di Tab 1 e la configurazione caricatori definita qui.")
    # Placeholder logic
    st.subheader(get_text("t2_current_config"))
    charger_types = ["AC_22", "DC_30", "DC_60", "DC_90", "DC_120"]
    config = {}
    cols = st.columns(len(charger_types))
    for i, c_type in enumerate(charger_types):
        config[c_type] = cols[i].number_input(f"{c_type} Unità", min_value=0, value=st.session_state.get(f't2_count_{c_type}', 1 if c_type == 'AC_22' else 0), step=1, key=f't2_count_{c_type}')
    
    if st.button(get_text("t2_run_simulation")):
        st.session_state['t2_results'] = {"success": True}
        st.rerun()

    if st.session_state.get('t2_results'):
        st.subheader(get_text("t2_results"))
        col1, col2, col3 = st.columns(3)
        col1.metric(get_text("t2_vehicles_served"), f"{random.randint(5, 10)} / 8")
        col2.metric(get_text("t2_energy_coverage"), f"{random.randint(70, 95)} %")
        col3.metric(get_text("t2_time_used"), f"{random.randint(150, 300)} kWh")

def render_tab3():
    st.header(get_text("t3_header"))
    st.markdown(get_text("t3_intro"))
    
    charger_costs_data = get_charger_costs()
    charger_options = {f"{c_type} ({data['power']}kW)": c_type for c_type, data in charger_costs_data.items() if 'WB' not in c_type}
    
    selected_charger_display = st.selectbox(get_text("t3_charger_selection"), options=list(charger_options.keys()), key="t3_charger_select_display")
    selected_charger_key = charger_options[selected_charger_display]
    
    if selected_charger_key not in charger_costs_data:
        st.error("Dati caricatore non trovati.")
        return

    charger_data = charger_costs_data[selected_charger_key]
    initial_investment = charger_data['unit'] + charger_data['install']
    annual_maintenance = charger_data['maint_annual']
    power_kw = charger_data['power']
    
    col1, col2 = st.columns(2)
    public_price = col1.number_input(get_text("t3_public_price"), min_value=0.10, value=0.55, step=0.05, key="t3_public_price")
    cost_of_energy = col2.number_input(get_text("t3_cost_of_energy"), min_value=0.10, value=0.25, step=0.01, key="t3_cost_of_energy")
    
    col3, col4 = st.columns(2)
    avg_utilization = col3.slider(get_text("t3_avg_utilization"), min_value=0.5, max_value=8.0, value=3.0, step=0.5, key="t3_avg_utilization")
    target_roi = col4.number_input(get_text("t3_target_roi"), min_value=1, value=15, step=1, key="t3_target_roi")
    
    if st.button(get_text("t3_calc_roi")):
        # Calcoli ROI
        
        # Stima Energia Annuale Erogata (assumendo 300 giorni operativi)
        annual_energy_kwh = power_kw * avg_utilization * 300 * 0.90 # 90% efficienza media
        
        # Ricavo Annuale
        annual_revenue = annual_energy_kwh * public_price
        
        # Costi Operativi Annuali
        annual_energy_cost = annual_energy_kwh * cost_of_energy
        annual_operational_cost = annual_energy_cost + annual_maintenance
        
        # Profitto Netto
        net_profit = annual_revenue - annual_operational_cost
        
        # Payback Period (anni)
        if net_profit > 0:
            payback_period = initial_investment / net_profit
            roi_reached = (net_profit / initial_investment) * 100
        else:
            payback_period = "N/A (Profitto Negativo)"
            roi_reached = 0
            
        st.session_state['t3_roi_results'] = {
            "annual_revenue": annual_revenue,
            "annual_operational_cost": annual_operational_cost,
            "net_profit": net_profit,
            "payback_period": payback_period,
            "roi_reached": roi_reached,
            "initial_investment": initial_investment
        }
        st.rerun()
        
    if st.session_state.get('t3_roi_results'):
        results = st.session_state['t3_roi_results']
        
        st.subheader(get_text("t3_roi_results"))
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric(get_text("t3_initial_investment"), f"€ {results['initial_investment']:,.0f}".replace(",", "."))
        col_res2.metric("Potenza Caricatore", f"{power_kw} kW")

        st.markdown("---")

        col_met1, col_met2 = st.columns(2)
        col_met1.metric(get_text("t3_roi_annual_revenue"), f"€ {results['annual_revenue']:,.0f}".replace(",", "."))
        col_met2.metric(get_text("t3_roi_annual_cost"), f"€ {results['annual_operational_cost']:,.0f}".replace(",", "."))
        
        st.markdown("---")

        col_fin1, col_fin2, col_fin3 = st.columns(3)
        col_fin1.metric(get_text("t3_roi_net_profit"), f"€ {results['net_profit']:,.0f}".replace(",", "."))
        col_fin2.metric(get_text("t3_roi_perc"), f"{results['roi_reached']:.1f} %".replace(".", ","))
        
        if isinstance(results['payback_period'], float):
             col_fin3.metric(get_text("t3_payback"), f"{results['payback_period']:.1f} Anni".replace(".", ","))
             if results['payback_period'] < 5:
                 st.success("ROI e Payback Period eccellenti.")
             elif results['payback_period'] < 8:
                 st.warning("ROI e Payback Period accettabili, valutare ottimizzazione costi.")
             else:
                 st.error("Payback Period lungo, l'investimento è ad alto rischio o l'utilizzo è troppo basso.")
        else:
             col_fin3.metric(get_text("t3_payback"), results['payback_period'])
             st.error("Il profitto è negativo. L'investimento non è sostenibile alle condizioni attuali.")

def render_tab4():
    st.header(get_text("t4_header"))
    st.markdown(get_text("t4_intro"))

    charger_costs_data = get_charger_costs()
    wb_options = {f"{c_type} ({data['power']}kW)": c_type for c_type, data in charger_costs_data.items() if 'WB' in c_type}
    
    selected_wb_display = st.selectbox(get_text("t4_power_select"), options=list(wb_options.keys()), key="t4_wb_select_display")
    selected_wb_key = wb_options[selected_wb_display]
    
    if selected_wb_key not in charger_costs_data:
        st.error("Dati Wallbox non trovati.")
        return

    charger_data = charger_costs_data[selected_wb_key]
    wallbox_unit_cost = charger_data['unit']
    wallbox_power = charger_data['power']

    st.markdown("---")
    
    with st.form("t4_input_form"):
        st.subheader("Parametri Installazione")
        
        col1, col2 = st.columns(2)
        
        t4_installation_type = col1.radio(
            get_text("t4_installation_type"),
            options=[get_text("t4_new_installation"), get_text("t4_existing_predisp")],
            index=0,
            key='t4_installation_type'
        )
        
        t4_distance = col2.number_input(
            get_text("t4_distance"), 
            min_value=1, 
            value=st.session_state.get('t4_distance', 10), 
            step=1, 
            key='t4_distance'
        )

        col3, col4 = st.columns(2)
        
        t4_cable_install = col3.radio(
            get_text("t4_cable_install_type"),
            options=[get_text("t4_on_wall"), get_text("t4_underground")],
            index=0,
            key='t4_cable_install'
        )
        
        t4_certification = col4.checkbox(
            get_text("t4_certification"),
            value=True,
            key='t4_certification'
        )
        
        t4_fire_cert = st.checkbox(
            get_text("t4_condo_fire_cert"),
            value=False,
            key='t4_fire_cert'
        )
        
        submitted = st.form_submit_button(get_text("t4_calc_cost"))
        
    if submitted:
        
        # Costi Base
        COST_LABOR_H = 40 # Costo orario base
        LABOR_HOURS_BASE = 8 # Ore base per installazione semplice
        LABOR_HOURS_PER_10M = 1.5 # Ore aggiuntive per ogni 10m
        CABLE_COST_PER_M = 12 # Costo cavo/tubi base
        QUADRO_BASE_COST = 200 # Costo quadro/protezioni base
        FIRE_CERT_ADD = 350
        
        # 1. Costo Wallbox
        cost_wallbox = wallbox_unit_cost
        
        # 2. Costo Quadro/Materiali
        cost_quadro = 0
        if t4_installation_type == get_text("t4_new_installation"):
            cost_quadro += QUADRO_BASE_COST
            
        cost_cavi = t4_distance * CABLE_COST_PER_M
        
        if t4_cable_install == get_text("t4_underground"):
             cost_cavi += t4_distance * 40 # Scavo aggiuntivo
        
        cost_materiali_tot = cost_quadro + cost_cavi
        
        # 3. Costo Manodopera
        labor_hours = LABOR_HOURS_BASE + (floor(t4_distance / 10) * LABOR_HOURS_PER_10M)
        cost_manodopera = labor_hours * COST_LABOR_H
        
        # 4. Aggiunte/Certificazioni
        cost_cert = 150 if t4_certification else 0 # Costo per DiCo
        if t4_fire_cert:
            cost_cert += FIRE_CERT_ADD
            
        total_cost = cost_wallbox + cost_materiali_tot + cost_manodopera + cost_cert
        
        st.session_state['t4_results'] = {
            "total_cost": total_cost,
            "wallbox_cost": cost_wallbox,
            "material_cost": cost_materiali_tot,
            "labor_cost": cost_manodopera,
            "cert_cost": cost_cert
        }
        st.rerun()

    if st.session_state.get('t4_results'):
        results = st.session_state['t4_results']
        
        st.subheader(get_text("t4_results"))
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric(get_text("t4_wallbox_cost"), f"€ {results['wallbox_cost']:,.0f}".replace(",", "."))
        col_res2.metric("Potenza Wallbox", f"{wallbox_power} kW")
        
        st.markdown("---")
        
        col_met1, col_met2, col_met3 = st.columns(3)
        col_met1.metric(get_text("t4_material_cost"), f"€ {results['material_cost']:,.0f}".replace(",", "."))
        col_met2.metric(get_text("t4_labor_cost"), f"€ {results['labor_cost']:,.0f}".replace(",", "."))
        col_met3.metric("Costi Certificazioni/Pratiche", f"€ {results['cert_cost']:,.0f}".replace(",", "."))
        
        st.divider()
        st.metric(get_text("t4_total_cost"), f"€ {results['total_cost']:,.0f}".replace(",", "."))
        
        st.markdown("---")
        st.info("Nota: Questa è una stima semplificata. I costi possono variare in base alla regione, alle tariffe dell'installatore e alla specifica complessità dell'impianto elettrico.")

# --- FUNZIONE render_tab5() AGGIORNATA ---

def render_tab5():
    import streamlit as st
    import pandas as pd
    
    # Nuove Costanti (da richiesta utente)
    COST_ENGINEERING = 1000  
    COST_LABOR_BASE = 890 
    COST_SCAVO_PER_METER = 50
    
    # Nuove Fasce di Costo Quadro (in base alla Potenza Totale Aggregata)
    PANEL_TIERS = {
        "BASE": 290,    # P <= 22 kW
        "30KW": 550,    # 22 < P <= 30 kW
        "50KW": 1090,   # 30 < P <= 50 kW
        "OVER50": 2090  # P > 50 kW
    }
    
    # Costi Base Materiali (in base al tipo di posa)
    MATERIAL_COSTS = {
        "Nuovo Impianto (25€/m)": 25, 
        "Canalina Esistente (10€/m)": 10
    }

    charger_costs_data = get_charger_costs()
    
    st.header(get_text("t5_header"))
    st.markdown(get_text("t5_intro"))
    
    # --- INPUTS ---
    
    with st.form("t5_input_form"):
        
        # 1. Colonnina Selection and Quantity (NUOVO INPUT MULTIPLO)
        st.subheader("1. Configurazione Colonnine")
        charger_counts = {}
        # Filtro solo i caricatori ad alta potenza per Tab 5
        charger_types_to_select = ["AC_22", "DC_20", "DC_30", "DC_60", "DC_90", "DC_120"]
        
        cols = st.columns(3)
        for i, c_type in enumerate(charger_types_to_select):
            power = charger_costs_data.get(c_type, {}).get('power', 'N/D')
            charger_counts[c_type] = cols[i % 3].number_input(
                f"Unità {c_type} ({power}kW)", 
                min_value=0, 
                value=st.session_state.get(f't5_count_{c_type}', 0), 
                step=1, 
                key=f't5_count_{c_type}'
            )
        
        # 2. Parametri Logistici e Moltiplicatori
        st.subheader("2. Parametri Logistici e Complessità")
        
        col1, col2 = st.columns(2)
        
        t5_distance = col1.number_input(
            get_text("t5_distance"), 
            min_value=1, 
            value=st.session_state.get('t5_distance', 30), 
            step=5, 
            key='t5_distance', 
            help="Distanza dal quadro elettrico o punto di connessione (metri)."
        )
        
        # Nuovo Input Tipo di installazione Cavi
        t5_install_type_select = col2.radio(
            "Tipo di installazione Cavi",
            options=list(MATERIAL_COSTS.keys()),
            index=0, 
            key='t5_install_type_select',
            horizontal=True,
            help="Influenza il costo base dei materiali/cavi al metro (10€ o 25€)."
        )

        
        col3, col4 = st.columns(2)
        
        t5_material_multiplier = col3.slider(
            get_text("t5_material_multiplier"), 
            min_value=1.0, 
            max_value=4.0, 
            value=st.session_state.get('t5_material_multiplier', 2.0), 
            step=0.1, 
            key='t5_material_multiplier', 
            help="Fattore di complessità per i materiali (tubazioni, curve, ecc.)."
        )
        
        t5_labor_multiplier = col4.slider(
            get_text("t5_labor_multiplier"), 
            min_value=1.0, 
            max_value=3.0, 
            value=st.session_state.get('t5_labor_multiplier', 1.5), 
            step=0.1, 
            key='t5_labor_multiplier', 
            help="Fattore di complessità che moltiplica il costo base di manodopera (€890)."
        )
        
        t5_is_underground = st.checkbox(
            get_text("t5_is_underground"), 
            value=st.session_state.get('t5_is_underground', False), 
            key='t5_is_underground', 
            help=f"Aggiunge €{COST_SCAVO_PER_METER}/metro per scavo e protezione tubi."
        )

        submitted = st.form_submit_button(get_text("t5_calc_cost"))
    
    
    if submitted or st.session_state.get('t5_results'):
        
        total_units = sum(charger_counts.values())
        
        if total_units == 0:
            st.warning("Seleziona almeno una colonnina per la stima del costo.")
            return

        # 1. CALCOLO COSTO COLONNINE (Unit Cost)
        unit_cost = sum(
            count * charger_costs_data.get(c_type, {}).get('unit', 0)
            for c_type, count in charger_counts.items() if count > 0
        )
        
        # 2. CALCOLO POTENZA TOTALE
        total_power_kw = sum(
            count * charger_costs_data.get(c_type, {}).get('power', 0)
            for c_type, count in charger_counts.items() if count > 0
        )
        
        # 3. COSTO QUADRO PRINCIPALE (Panel Cost) - NEW TIERED LOGIC
        if total_power_kw <= 22:
            panel_cost = PANEL_TIERS["BASE"]
        elif total_power_kw <= 30:
            panel_cost = PANEL_TIERS["30KW"]
        elif total_power_kw <= 50:
            panel_cost = PANEL_TIERS["50KW"]
        else: # > 50 kW
            panel_cost = PANEL_TIERS["OVER50"]

        # 4. COSTO MANODOPERA (Labor Cost)
        labor_cost = COST_LABOR_BASE * t5_labor_multiplier
        
        # 5. COSTO MATERIALI (Cables/Materials) - NEW LOGIC
        
        # Base Cost per Meter (10€ or 25€)
        base_material_cost_per_m = MATERIAL_COSTS[t5_install_type_select]

        # Componente A: Scaling Power (Normalizzato su 22kW)
        power_scaling_factor = total_power_kw / 22.0 if total_power_kw > 0 else 1.0
        
        material_base_cost = (
            base_material_cost_per_m * t5_distance * t5_material_multiplier * power_scaling_factor
        )
        
        # Componente B: Scavo (Underground)
        scavo_cost = t5_distance * COST_SCAVO_PER_METER if t5_is_underground else 0
        
        material_cost = material_base_cost + scavo_cost
        
        # 6. COSTO INGEGNERIA (Engineering Cost)
        engineering_cost = COST_ENGINEERING 

        # 7. COSTO TOTALE
        total_cost = unit_cost + material_cost + labor_cost + panel_cost + engineering_cost

        # --- RISULTATI ---
        t5_results = {
            "total_cost": total_cost,
            "unit_cost": unit_cost,
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "panel_cost": panel_cost,
            "engineering_cost": engineering_cost,
            "total_power_kw": total_power_kw,
            "total_units": total_units,
        }
        st.session_state['t5_results'] = t5_results
        
        # Display Results
        results = st.session_state['t5_results']
        
        st.divider()
        st.subheader(f"Risultati Stima Costo Totale (Configurazione: {results['total_units']} Unità)")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        col_res1.metric(get_text("t5_total_cost"), f"€ {results['total_cost']:,.0f}".replace(",", "."))
        col_res2.metric("Potenza Totale Impianto", f"{results['total_power_kw']:.1f} kW".replace(".", ","))
        col_res3.metric("Distanza Cavi Stimata", f"{t5_distance} metri") 
        
        st.markdown("---")
        
        st.markdown("### Dettaglio Costi (CAPEX)")
        
        data = {
            "Componente": [
                get_text("t5_wallbox_cost"), 
                get_text("t5_material_cost"), 
                get_text("t5_labor_cost"), 
                get_text("t5_panel_cost"), 
                get_text("t5_engineering_cost")
            ],
            "Costo Stimato (€)": [
                results['unit_cost'], 
                results['material_cost'], 
                results['labor_cost'], 
                results['panel_cost'], 
                results['engineering_cost']
            ]
        }
        df_costs = pd.DataFrame(data)
        
        st.dataframe(
            df_costs.style.format({"Costo Stimato (€)": "€ {:,.0f}".format}),
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown(f"""
        <div style='background-color: #e6f7ff; padding: 10px; border-radius: 5px; border-left: 5px solid #3498DB;'>
            La stima del **Costo Quadro Elettrico Principale** (€ {results['panel_cost']:,.0f}) è stata selezionata in base alla potenza totale aggregata (**{results['total_power_kw']:.1f} kW**) dell'impianto.
        </div>
        """.replace(",", "."), unsafe_allow_html=True)

# --- FINE FUNZIONE render_tab5() AGGIORNATA ---

def main():
    # Inizializzazione Session State per le default di Tab 1
    if 'num_groups_tab1' not in st.session_state: st.session_state['num_groups_tab1'] = 2
    if 'vehicle_groups_tab1' not in st.session_state: 
        st.session_state['vehicle_groups_tab1'] = [
            {'quantity': 5, 'daily_km': 100, 'consumption': 20.0, 'arrival_time': 18, 'departure_time': 8},
            {'quantity': 3, 'daily_km': 300, 'consumption': 20.0, 'arrival_time': 10, 'departure_time': 12}
        ]
        
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

if __name__ == '__main__':
    main()

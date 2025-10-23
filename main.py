import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict
from datetime import datetime, timedelta

# ====================================================================
# VARIABILI E FUNZIONI DI CONFIGURAZIONE (ADATTALE ALLE TUE ESIGENZE)
# ====================================================================

# Funzione fittizia per la traduzione (da sostituire con la tua implementazione)
def get_text(key):
    # Mapping fittizio per le stringhe utilizzate nel codice
    translations = {
        "infrastructure_test_header": "Test di Infrastruttura di Ricarica",
        "infrastructure_test_intro": "Simula la necessità energetica della flotta e verifica la capacità dell'infrastruttura.",
        "test_params_vehicle_fleet": "Parametri della Flotta Veicoli",
        "num_ev_vehicles": "Numero di Veicoli Elettrici",
        "num_ev_vehicles_help": "Quanti veicoli EV simulare per la flotta.",
        "single_vehicle_test": "Veicolo {i}",
        "vehicle_name": "Nome Veicolo",
        "daily_km_test": "Km Giornalieri Richiesti",
        "daily_km_test_help": "Distanza media percorsa al giorno.",
        "avg_consumption_test": "Consumo (Wh/Km)",
        "avg_consumption_test_help": "Consumo medio del veicolo (es. 180 Wh/Km = 18 kWh/100km).",
        "orario_ingresso": "Orario di Ingresso (h)", 
        "orario_uscita": "Orario di Uscita (h)", 
        "existing_infra_config": "Configurazione Infrastruttura Esistente",
        "existing_infra_intro": "Definisci il numero di colonnine per tipo.",
        "ac_11_chargers": "Colonnine AC 11 kW", "ac_11_chargers_help": "Quantità di colonnine AC 11kW",
        "ac_22_chargers": "Colonnine AC 22 kW", "ac_22_chargers_help": "Quantità di colonnine AC 22kW",
        "dc_30_chargers": "Colonnine DC 30 kW", "dc_30_chargers_help": "Quantità di colonnine DC 30kW",
        "dc_60_chargers": "Colonnine DC 60 kW", "dc_60_chargers_help": "Quantità di colonnine DC 60kW",
        "dc_90_chargers": "Colonnine DC 90 kW", "dc_90_chargers_help": "Quantità di colonnine DC 90kW",
        "daily_charger_hours": "Ore di Disponibilità Giornaliera Colonnine", "daily_charger_hours_help": "Ore totali in cui le colonnine possono operare (es. 24h).",
        "economic_investment_params": "Parametri Economici e di Investimento",
        "economic_investment_intro": "Definisci i costi operativi e di acquisto.",
        "internal_energy_cost_test": "Costo Energia Interna (€/kWh)", "internal_energy_cost_test_help": "Costo dell'energia prelevata internamente (es. dal fotovoltaico o tariffa aziendale).",
        "external_energy_price_test": "Prezzo Energia Pubblica (€/kWh)", "external_energy_price_test_help": "Costo medio della ricarica esterna.",
        "charger_purchase_costs": "Costi di Acquisto Colonnine (per unità)",
        "investment_ac11": "Investimento AC 11kW (€)", "investment_ac11_help": "Costo di acquisto e installazione per AC 11kW.",
        "investment_ac22": "Investimento AC 22kW (€)", "investment_ac22_help": "Costo di acquisto e installazione per AC 22kW.",
        "investment_dc30": "Investimento DC 30kW (€)", "investment_dc30_help": "Costo di acquisto e installazione per DC 30kW.",
        "investment_dc60": "Investimento DC 60kW (€)", "investment_dc60_help": "Costo di acquisto e installazione per DC 60kW.",
        "investment_dc90": "Investimento DC 90kW (€)", "investment_dc90_help": "Costo di acquisto e installazione per DC 90kW.",
        "run_infra_analysis": "Esegui Analisi Infrastruttura",
        "add_vehicle_warning_analysis": "Devi aggiungere almeno un veicolo per eseguire l'analisi.",
        "analysis_execution": "Esecuzione simulazione...",
        "analysis_complete_success": "Analisi Completata!",
        "performance_summary": "Riepilogo delle Performance",
        "total_energy_requested": "Energia Totale Richiesta", "total_energy_requested_help": "Energia totale necessaria alla flotta per la giornata.",
        "internal_energy_charged_test": "Energia Caricata Internamente", "internal_energy_charged_test_help": "Energia erogata dalle colonnine interne.",
        "external_energy_to_charge": "Energia Esterna Residua", "external_energy_to_charge_help": "Energia che la flotta deve ricaricare all'esterno.",
        "estimated_time_lost": "Tempo Esterno Stimato", "estimated_time_lost_help": "Tempo stimato (in ore) speso per ricariche esterne non effettuate internamente.",
        "daily_external_charge_cost": "Costo Giornaliero Ricarica Esterna", "daily_external_charge_cost_help": "Costo della ricarica esterna residua.",
        "avg_charger_utilization_rate": "Tasso Medio Utilizzo Colonnine", "avg_charger_utilization_rate_help": "Percentuale di tempo in cui le colonnine sono state utilizzate rispetto al tempo disponibile.",
        "fully_charged_cars": "Auto Caricate Completamente", "fully_charged_cars_help": "Numero di veicoli che hanno raggiunto il 100% della richiesta energetica interna.",
        "internal_operating_cost": "Costo Operativo Interno", "internal_operating_cost_help": "Costo dell'energia utilizzata dalle colonnine interne.",
        "day_label": "giorno",
        "estimated_annual_savings_test": "Risparmio Annuo Stimato", "estimated_annual_savings_test_help": "Risparmio annuale generato dall'infrastruttura interna.",
        "roi_test": "ROI (Ritorno sull'Investimento)", "roi_test_help": "Tempo (in anni) necessario per ammortizzare l'investimento.",
        "charger_utilization_details": "Dettagli Utilizzo Colonnine",
        "vehicle_charge_status_test": "Stato di Ricarica Veicoli",
        "energy_req_vs_charged_test": "Energia Richiesta vs. Caricata",
        "operating_costs_analysis_test": "Analisi Costi Operativi",
        "hourly_utilization_details": "Ore di utilizzo aggregate per tipologia di colonnina.",
        "hourly_utilization_chart_title": "Ore di Utilizzo per Tipo Colonnina",
        "charger_type_label": "Tipo Colonnina",
        "hours_used_label": "Ore Utilizzate",
        "no_chargers_configured_analysis": "Nessuna colonnina configurata per l'analisi.",
        "gantt_planning_details": "Dettaglio Programmazione Ricariche (Gantt)",
        "gantt_planning_intro": "Visualizzazione temporale di tutte le ricariche assegnate.",
        "gantt_chart_title": "Pianificazione Ricarica (Timeline)",
        "charger": "Colonnina",
        "hour_of_day": "Ora del Giorno",
        "vehicle_label": "Veicolo",
        "start_time_label": "Inizio",
        "end_time_label": "Fine",
        "energy_kwh_label": "Energia (kWh)",
        "no_charges_recorded": "Nessuna ricarica assegnata nella simulazione.",
        "fully_charged": "Caricato Completamente",
        "partially_charged": "Caricato Parzialmente",
        "not_charged": "Non Caricato",
        "vehicle_charge_status_chart_title": "Distribuzione Stato di Ricarica Veicoli",
        "run_analysis_to_view_status": "Esegui l'analisi per visualizzare lo stato di ricarica.",
        "energy_comparison_chart_title": "Energia Richiesta vs. Caricata (Top 10)",
        "no_vehicle_data_for_chart": "Nessun dato veicolo disponibile per il grafico.",
        "run_analysis_to_view_comparison": "Esegui l'analisi per visualizzare il confronto energetico.",
        "operating_costs_distribution_chart_title": "Distribuzione Costi Operativi Giornalieri",
        "run_analysis_to_view_costs": "Esegui l'analisi per visualizzare i costi.",
        "optimization_suggestions": "Suggerimenti per l'Ottimizzazione",
        "improvement_opportunity": "Opportunità: {energy:.1f} kWh non sono stati ricaricati internamente. Considera l'aggiunta di colonnine o l'ottimizzazione degli orari.",
        "fleet_coverage": "Copertura Flotta: {charged}/{total} veicoli sono stati caricati completamente. Focalizzati sui veicoli con carenza energetica.",
        "high_utilization_warning": "Attenzione: L'utilizzo delle colonnine è alto ({utilization:.1f}%). Potrebbe esserci congestione. Considera l'ampliamento.",
        "low_utilization_info": "Informazione: L'utilizzo delle colonnine è basso ({utilization:.1f}%). L'infrastruttura è sovradimensionata rispetto alla richiesta attuale.",
        "well_balanced_utilization": "Utilizzo ben bilanciato. L'infrastruttura è ottimale per il carico attuale.",
        "good_roi_success": "Ottimo ROI: L'investimento ha un tasso di ritorno eccellente ({roi:.1f}%).",
        "positive_roi_info": "ROI Positivo: L'investimento è profittevole ({roi:.1f}%).",
        "negative_roi_error": "ROI Negativo: L'investimento non è profittevole ({roi:.1f}%). Rivedi i costi operativi e di investimento.",
        "roi_not_calculable": "ROI non calcolabile (Investimento iniziale pari a zero).",
        "configure_and_calculate": "Configura i parametri e premi 'Esegui Analisi Infrastruttura'."
    }
    return translations.get(key, key)

# Variabili di configurazione fittizie
COLONNINE_TAB1 = {'DC_20': {'potenza_effettiva': 20}, 'DC_40': {'potenza_effettiva': 40}}
MIN_DURATA_RICARICA = 0.5  # Durata minima di ricarica in ore (30 minuti)

# ====================================================================
# FUNZIONE DI SIMULAZIONE AGGIORNATA (FIX APPLICATO QUI)
# ====================================================================

def calculate_infrastructure_test(veicoli, colonnine_config, costo_energia_interna,
                                  prezzo_energia_pubblica, ore_disponibili, costi_investimento_colonnine):
    """
    Simula la ricarica per una data configurazione di infrastruttura e flotta veicoli.
    """
    MIN_INTERVALLO_RICARICA_SIM = 0.5 

    colonnine_instances = []
    power_map = {
        'ac_11': 11, 'ac_22': 22, 'dc_30': 30, 'dc_60': 60, 'dc_90': 90,
        'dc_20': COLONNINE_TAB1.get('DC_20', {}).get('potenza_effettiva', 20),
        'dc_40': COLONNINE_TAB1.get('DC_40', {}).get('potenza_effettiva', 40),
    }

    # 1. Creazione delle istanze delle colonnine
    for tipo, quantita in colonnine_config.items():
        potenza = power_map.get(tipo, 11)
        for i in range(quantita):
            colonnine_instances.append({
                'tipo': tipo,
                'nome': f"{tipo}_{i+1}",
                'potenza': potenza,
                # <<< FIX: Disponibilità colonnina fissata a 24h per lo scheduling >>>
                'available_slots': [(0.0, 24.0)], # Intervalli liberi (start, end)
                'bookings': [] 
            })

    risultati = {
        'energia_totale': 0, 'energia_caricata': 0, 'energia_esterna': 0,
        'tempo_esterno_stimato': 0, 'costo_ricariche_esterne': 0,
        'utilizzo_colonnine_ore': defaultdict(float), 'prenotazioni': [],
        'auto_caricate_completamente': 0, 'num_veicoli_totali': len(veicoli),
        'costo_operativo_interno': 0, 'investimento_totale_iniziale': 0,
        'risparmio_annuo_stimato': 0, 'ROI': 0
    }

    veicoli_for_sim = [v.copy() for v in veicoli]
    for v in veicoli_for_sim:
        v['energia_rimanente'] = v['energia_richiesta']
        v['caricata_completamente'] = False
        v['sosta_start'] = v.get('ingresso', 0.0)
        v['sosta_end'] = v.get('uscita', v.get('sosta', 0.0)) 
        v['colonnina_assegnata'] = None 

    veicoli_for_sim.sort(key=lambda x: x['sosta_end'])

    max_sim_iterations = len(veicoli_for_sim) * len(colonnine_instances) * 24

    for _ in range(max_sim_iterations):
        something_charged_in_this_iteration = False

        vehicles_needing_charge = sorted(
            [v for v in veicoli_for_sim if v['energia_rimanente'] > 0.01],
            key=lambda x: (x['sosta_end'], -x['energia_rimanente'])
        )

        if not vehicles_needing_charge:
            break

        for vehicle in vehicles_needing_charge:
            best_option = None

            for colonnina in colonnine_instances:
                for slot_idx, (slot_start, slot_end) in enumerate(colonnina['available_slots']):
                    
                    effective_charge_start = max(vehicle['sosta_start'], slot_start)
                    effective_charge_end = min(vehicle['sosta_end'], slot_end)

                    # Aggiusta per l'intervallo minimo
                    if colonnina['bookings']:
                        # Trova la fine dell'ultima ricarica completata prima di effective_charge_start
                        last_booking_end_list = [b['fine'] for b in colonnina['bookings'] if b['fine'] <= effective_charge_start]
                        last_booking_end = max(last_booking_end_list) if last_booking_end_list else effective_charge_start - 1
                        
                        effective_charge_start = max(effective_charge_start, last_booking_end + MIN_INTERVALLO_RICARICA_SIM)
                    
                    if effective_charge_end - effective_charge_start >= MIN_DURATA_RICARICA:
                        potential_duration = effective_charge_end - effective_charge_start
                        energy_possible_in_slot = colonnina['potenza'] * potential_duration
                        
                        energy_to_attempt = min(vehicle['energia_rimanente'], energy_possible_in_slot)

                        if energy_to_attempt > 0.01: # Check for meaningful energy
                            if not best_option or energy_to_attempt > best_option[3]:
                                best_option = (colonnina, effective_charge_start, effective_charge_end, energy_to_attempt)

            if best_option:
                colonnina_to_use, charge_start, charge_end, energy_to_charge = best_option
                
                actual_duration_needed = energy_to_charge / colonnina_to_use['potenza']
                final_charge_duration = actual_duration_needed # User all available time for the required energy

                # Ensure final charge duration does not exceed the available slot time
                final_charge_duration = min(final_charge_duration, charge_end - charge_start)

                # Ensure final charge duration respects minimum duration or is negligible if car is full
                if final_charge_duration < MIN_DURATA_RICARICA and vehicle['energia_rimanente'] > energy_to_charge * 1.01:
                    # If vehicle needs more energy, but the slot is too short, we skip this assignment for a small slot
                    continue
                
                if final_charge_duration > 0.01: 
                    actual_energy_charged = colonnina_to_use['potenza'] * final_charge_duration
                    vehicle['energia_rimanente'] -= actual_energy_charged
                    something_charged_in_this_iteration = True
                    
                    if not vehicle['colonnina_assegnata']:
                         vehicle['colonnina_assegnata'] = colonnina_to_use['nome']
                         
                    # Update the colonnina's available slots
                    charge_end_time = charge_start + final_charge_duration
                    release_time = charge_end_time + MIN_INTERVALLO_RICARICA_SIM
                    
                    new_slots_for_colonnina = []
                    
                    for s_start, s_end in colonnina_to_use['available_slots']:
                         if s_end <= charge_start or s_start >= release_time:
                            # Slot is completely before or after the booking + release time
                            new_slots_for_colonnina.append((s_start, s_end))
                         elif s_start < charge_start and s_end > release_time:
                            # Slot is split into two (before and after)
                            new_slots_for_colonnina.append((s_start, charge_start))
                            new_slots_for_colonnina.append((release_time, s_end))
                         elif s_start < charge_start and s_end <= release_time and s_end > charge_start:
                             # Slot is cut only at the end (before)
                             new_slots_for_colonnina.append((s_start, charge_start))
                         elif s_start >= charge_start and s_start < release_time and s_end > release_time:
                             # Slot is cut only at the start (after)
                             new_slots_for_colonnina.append((release_time, s_end))
                         # Otherwise, the slot is consumed/removed

                    colonnina_to_use['available_slots'] = sorted([slot for slot in new_slots_for_colonnina if slot[1] - slot[0] >= 0.01], key=lambda x: x[0])


                    # Record the booking
                    colonnina_to_use['bookings'].append({
                        'veicolo': vehicle['nome'],
                        'inizio': charge_start,
                        'fine': charge_end_time,
                        'energia': actual_energy_charged,
                        'tempo_ricarica': final_charge_duration
                    })
                    colonnina_to_use['bookings'].sort(key=lambda x: x['inizio'])

                    risultati['utilizzo_colonnine_ore'][f"{colonnina_to_use['potenza']} kW"] += final_charge_duration
                    risultati['prenotazioni'].append({
                        'veicolo': vehicle['nome'],
                        'colonnina': colonnina_to_use['nome'],
                        'inizio': charge_start,
                        'fine': charge_end_time,
                        'energia': actual_energy_charged,
                        'tipo_colonnina': colonnina_to_use['tipo']
                    })
                    
                    # Garantisce 1 ricarica per iterazione
                    break 

        if not something_charged_in_this_iteration:
            break 

    # Final aggregation for results
    risultati['energia_totale'] = sum(v['energia_richiesta'] for v in veicoli_for_sim)
    risultati['energia_caricata'] = sum(sum(b['energia'] for b in col['bookings']) for col in colonnine_instances)
    risultati['energia_esterna'] = risultati['energia_totale'] - risultati['energia_caricata']
    
    risultati['auto_caricate_completamente'] = sum(1 for v in veicoli_for_sim if v['energia_rimanente'] <= 0.01) 

    if risultati['energia_esterna'] > 0:
        risultati['tempo_esterno_stimato'] = (risultati['energia_esterna'] / 11) * 1.5 
        risultati['costo_ricariche_esterne'] = risultati['energia_esterna'] * prezzo_energia_pubblica

    total_colonnine_capacity_kwh = sum(col['potenza'] * ore_disponibili for col in colonnine_instances)
    risultati['tasso_utilizzo'] = (risultati['energia_caricata'] / total_colonnine_capacity_kwh) * 100 if total_colonnine_capacity_kwh > 0 else 0

    risultati['costo_operativo_interno'] = risultati['energia_caricata'] * costo_energia_interna
    
    costo_totale_esterno_se_nessuna_colonnina = risultati['energia_totale'] * prezzo_energia_pubblica
    risparmio_giornaliero = costo_totale_esterno_se_nessuna_colonnina - risultati['costo_ricariche_esterne'] - risultati['costo_operativo_interno']
    risultati['risparmio_annuo_stimato'] = risparmio_giornaliero * 365

    total_investment_tab2 = sum(quantita * costi_investimento_colonnine.get(tipo, 0) for tipo, quantita in colonnine_config.items())
    risultati['investimento_totale_iniziale'] = total_investment_tab2

    risultati['ROI'] = (risultati['risparmio_annuo_stimato'] / risultati['investimento_totale_iniziale']) * 100 if risultati['investimento_totale_iniziale'] > 0 else 0
    
    risultati['veicoli_simulati'] = veicoli_for_sim

    return risultati

# ====================================================================
# INTERFACCIA UTENTE (STREAMLIT) - NESSUNA MODIFICA NECESSARIA QUI
# ====================================================================

# Configurazione della pagina (opzionale)
st.set_page_config(layout="wide")

# Simula la struttura a tab
tab2 = st.container()

with tab2:
    st.header(get_text("infrastructure_test_header"))
    st.markdown(get_text("infrastructure_test_intro"))

    if 'risultati_tab2' not in st.session_state:
        st.session_state.risultati_tab2 = None

    with st.expander(get_text("test_params_vehicle_fleet"), expanded=True):
        n_auto_tab2 = st.slider(get_text("num_ev_vehicles"), 0, 100, 3, key="tab2_num_auto", help=get_text("num_ev_vehicles_help"))
        veicoli_tab2 = []

        cols_tab2_veicoli = st.columns(3)
        for i in range(n_auto_tab2):
            with cols_tab2_veicoli[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{get_text('single_vehicle_test').format(i=i+1)}**")
                    nome = st.text_input(get_text("vehicle_name").format(i=''), f"Auto_{i+1}", key=f"tab2_nome_{i}")
                    km = st.number_input(get_text("daily_km_test"), 0, 500, 100, step=10, key=f"tab2_km_{i}", help=get_text("daily_km_test_help"))
                    
                    consumo_wh_km = st.number_input(get_text("avg_consumption_test"), 100, 300, 180, step=10, key=f"tab2_cons_{i}", help=get_text("avg_consumption_test_help"))
                    
                    orario_ingresso = st.number_input(get_text("orario_ingresso"), 0.0, 24.0, 8.0, step=0.5, key=f"tab2_ingresso_{i}", help="Ora di arrivo del veicolo (es. 8.5 per 8:30)")
                    orario_uscita = st.number_input(get_text("orario_uscita"), 0.0, 24.0, 17.0, step=0.5, key=f"tab2_uscita_{i}", help="Ora di partenza del veicolo (es. 17.0 per 17:00)")

                    consumo_kwh_km = consumo_wh_km / 1000 
                    energia_richiesta = km * consumo_kwh_km
                    sosta_calcolata = max(0.0, orario_uscita - orario_ingresso) 

                    if orario_uscita <= orario_ingresso:
                        st.error("L'uscita deve essere successiva all'ingresso.")
                    
                    veicoli_tab2.append({
                        "nome": nome,
                        "km": km,
                        "consumo": consumo_kwh_km,
                        "sosta": sosta_calcolata,
                        "energia_richiesta": energia_richiesta,
                        "ingresso": orario_ingresso,
                        "uscita": orario_uscita
                    })

    with st.expander(get_text("existing_infra_config"), expanded=True):
        st.markdown(get_text("existing_infra_intro"))
        cols_infra = st.columns(3)
        with cols_infra[0]:
            ac_11_tab2 = st.number_input(get_text("ac_11_chargers"), 0, 20, 1, key="tab2_ac11", help=get_text("ac_11_chargers_help"))
            ac_22_tab2 = st.number_input(get_text("ac_22_chargers"), 0, 20, 0, key="tab2_ac22", help=get_text("ac_22_chargers_help"))
        with cols_infra[1]:
            dc_30_tab2 = st.number_input(get_text("dc_30_chargers"), 0, 10, 0, key="tab2_dc30", help=get_text("dc_30_chargers_help"))
            dc_60_tab2 = st.number_input(get_text("dc_60_chargers"), 0, 10, 0, key="tab2_dc60", help=get_text("dc_60_chargers_help"))
        with cols_infra[2]:
            dc_90_tab2 = st.number_input(get_text("dc_90_chargers"), 0, 10, 0, key="tab2_dc90", help=get_text("dc_90_chargers_help"))

    with st.expander(get_text("economic_investment_params"), expanded=False):
        st.markdown(get_text("economic_investment_intro"))

        costo_energia_interna_tab2 = st.slider(get_text("internal_energy_cost_test"), 0.10, 1.00, 0.25, step=0.05, key="tab2_costo_interno", help=get_text("internal_energy_cost_test_help"))
        prezzo_energia_pubblica_tab2 = st.slider(get_text("external_energy_price_test"), 0.10, 1.00, 0.80, step=0.05, key="tab2_prezzo_esterno", help=get_text("external_energy_price_test_help"))

        st.markdown("---")
        st.markdown(f"**{get_text('charger_purchase_costs')}**")
        col1_inv, col2_inv, col3_inv = st.columns(3)
        with col1_inv:
            inv_ac11 = st.number_input(get_text("investment_ac11"), 500, 5000, 1500, step=100, key="tab2_inv_ac11", help=get_text("investment_ac11_help"))
            inv_ac22 = st.number_input(get_text("investment_ac22"), 1000, 8000, 2500, step=100, key="tab2_inv_ac22", help=get_text("investment_ac22_help"))
        with col2_inv:
            inv_dc30 = st.number_input(get_text("investment_dc30"), 5000, 20000, 10000, step=500, key="tab2_inv_dc30", help=get_text("investment_dc30_help"))
            inv_dc60 = st.number_input(get_text("investment_dc60"), 10000, 40000, 20000, step=1000, key="tab2_inv_dc60", help=get_text("investment_dc60_help"))
        with col3_inv:
            inv_dc90 = st.number_input(get_text("investment_dc90"), 15000, 60000, 30000, step=1000, key="tab2_inv_dc90", help=get_text("investment_dc90_help"))

        costi_investimento_colonnine = {
            'ac_11': inv_ac11,
            'ac_22': inv_ac22,
            'dc_30': inv_dc30,
            'dc_60': inv_dc60,
            'dc_90': inv_dc90,
        }

    if st.button(get_text("run_infra_analysis"), key="tab2_analisi", type="primary"):
        if not veicoli_tab2:
            st.warning(get_text("add_vehicle_warning_analysis"))
        else:
            with st.spinner(get_text("analysis_execution")):
                risultati_tab2_temp = calculate_infrastructure_test(
                    veicoli_tab2,
                    {'ac_11': ac_11_tab2, 'ac_22': ac_22_tab2, 'dc_30': dc_30_tab2, 'dc_60': dc_60_tab2, 'dc_90': dc_90_tab2},
                    costo_energia_interna_tab2,
                    prezzo_energia_pubblica_tab2,
                    ore_disponibili_tab2,
                    costi_investimento_colonnine
                )
                st.session_state.risultati_tab2 = risultati_tab2_temp 

            st.success(get_text("analysis_complete_success"))
            st.divider()
            st.subheader(get_text("performance_summary"))

            risultati_tab2 = st.session_state.risultati_tab2

            col1_tab2, col2_tab2, col3_tab2 = st.columns(3)
            col1_tab2.metric(get_text("total_energy_requested"), f"{risultati_tab2['energia_totale']:.1f} kWh", help=get_text("total_energy_requested_help"))
            col2_tab2.metric(get_text("internal_energy_charged_test"), f"{risultati_tab2['energia_caricata']:.1f} kWh", f"{(risultati_tab2['energia_caricata']/risultati_tab2['energia_totale']*100 if risultati_tab2['energia_totale']>0 else 0):.1f}%", help=get_text("internal_energy_charged_test_help"))
            col3_tab2.metric(get_text("external_energy_to_charge"), f"{risultati_tab2['energia_esterna']:.1f} kWh", f"{(risultati_tab2['energia_esterna']/risultati_tab2['energia_totale']*100 if risultati_tab2['energia_totale']>0 else 0):.1f}%", help=get_text("external_energy_to_charge_help"))
            
            col4_tab2, col5_tab2, col6_tab2 = st.columns(3)
            col4_tab2.metric(get_text("estimated_time_lost"), f"{risultati_tab2['tempo_esterno_stimato']:.1f} h/{get_text('day_label')}", help=get_text("estimated_time_lost_help"))
            col5_tab2.metric(get_text("daily_external_charge_cost"), f"€{risultati_tab2['costo_ricariche_esterne']:.2f}", help=get_text("daily_external_charge_cost_help"))
            col6_tab2.metric(get_text("avg_charger_utilization_rate"), f"{risultati_tab2['tasso_utilizzo']:.1f}%", help=get_text("avg_charger_utilization_rate_help"))

            col7_tab2, col8_tab2, _ = st.columns(3)
            col7_tab2.metric(get_text("fully_charged_cars"), f"{risultati_tab2['auto_caricate_completamente']}/{risultati_tab2['num_veicoli_totali']}", help=get_text("fully_charged_cars_help"))
            col8_tab2.metric(get_text("internal_operating_cost"), f"€{risultati_tab2['costo_operativo_interno']:.2f}/{get_text('day_label')}", help=get_text("internal_operating_cost_help"))
            
            col_roi_1, col_roi_2 = st.columns(2)
            col_roi_1.metric(get_text("estimated_annual_savings_test"), f"€{risultati_tab2['risparmio_annuo_stimato']:.2f}", help=get_text("estimated_annual_savings_test_help"))
            col_roi_2.metric(get_text("roi_test"), f"{risultati_tab2['ROI']:.1f}%", help=get_text("roi_test_help"))

            tab2_1, tab2_2, tab2_3, tab2_4 = st.tabs([get_text("charger_utilization_details"), get_text("vehicle_charge_status_test"), get_text("energy_req_vs_charged_test"), get_text("operating_costs_analysis_test")])

            with tab2_1:
                st.markdown(get_text("hourly_utilization_details"))
                if risultati_tab2['utilizzo_colonnine_ore']:
                    df_utilizzo = pd.DataFrame({
                        "ChargerType": list(risultati_tab2['utilizzo_colonnine_ore'].keys()),
                        "HoursUsed": list(risultati_tab2['utilizzo_colonnine_ore'].values())
                    })
                    fig = px.bar(df_utilizzo, x="ChargerType", y="HoursUsed", title=get_text("hourly_utilization_chart_title"), color="ChargerType", color_discrete_sequence=px.colors.qualitative.Dark24, template="plotly_white")
                    fig.update_xaxes(title_text=get_text("charger_type_label"))
                    fig.update_yaxes(title_text=get_text("hours_used_label"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(get_text("no_chargers_configured_analysis"))
                
                st.markdown(f"##### {get_text('gantt_planning_details')}")
                st.markdown(get_text("gantt_planning_intro"))
                if risultati_tab2['prenotazioni']:
                    df_prenotazioni = pd.DataFrame(risultati_tab2['prenotazioni'])
                    
                    df_prenotazioni['StartTime'] = df_prenotazioni['inizio'].apply(lambda h: datetime(2023,1,1) + timedelta(hours=h))
                    df_prenotazioni['EndTime'] = df_prenotazioni['fine'].apply(lambda h: datetime(2023,1,1) + timedelta(hours=h))

                    tab2_color_map = {
                        'ac_11': '#808080', 'ac_22': '#666666',
                        'dc_30': '#0000FF', 'dc_60': '#FF4500', 'dc_90': '#FF0000',
                        'dc_20': '#00FF00', 'dc_40': '#FFA500' 
                    }
                    
                    fig = px.timeline(
                        df_prenotazioni,
                        x_start="StartTime",
                        x_end="EndTime",
                        y="colonnina",
                        color="tipo_colonnina",
                        title=get_text("gantt_chart_title"),
                        hover_name="veicolo",
                        hover_data={"StartTime": False, "EndTime": False, "tipo_colonnina": False, "colonnina": True, "veicolo": True, "energia": ':.1f kWh'},
                        color_discrete_map=tab2_color_map,
                        template="plotly_white"
                    )
                    fig.update_yaxes(title_text=get_text("charger"))
                    fig.update_xaxes(title_text=get_text("hour_of_day"), tickformat="%H:%M")
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        df_prenotazioni[["veicolo", "colonnina", 'inizio', 'fine', 'energia']],
                        column_config={
                            "veicolo": st.column_config.Column(get_text("vehicle_label")),
                            "colonnina": st.column_config.Column(get_text("charger")),
                            "inizio": st.column_config.NumberColumn(get_text("start_time_label"), format="%.1f h"),
                            "fine": st.column_config.NumberColumn(get_text("end_time_label"), format="%.1f h"),
                            "energia": st.column_config.NumberColumn(get_text("energy_kwh_label"), format="%.1f kWh")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info(get_text("no_charges_recorded"))

            with tab2_2:
                st.markdown(f"#### {get_text('vehicle_charge_status_test')}")
                if st.session_state.risultati_tab2 and 'veicoli_simulati' in st.session_state.risultati_tab2:
                    
                    charged_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] >= v['energia_richiesta'] * 0.99)
                    partial_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] > 0.01 and v['energia_richiesta'] - v['energia_rimanente'] < v['energia_richiesta'] * 0.99)
                    unassigned_count_tab2 = sum(1 for v in st.session_state.risultati_tab2['veicoli_simulati'] if v['energia_richiesta'] - v['energia_rimanente'] <= 0.01)

                    df_charge_status_tab2 = pd.DataFrame({
                        "ChargeStatus": [get_text("fully_charged"), get_text("partially_charged"), get_text("not_charged")],
                        "NumVehicles": [charged_count_tab2, partial_count_tab2, unassigned_count_tab2]
                    })
                    fig_charge_status_pie_tab2 = px.pie(df_charge_status_tab2, values="NumVehicles", names="ChargeStatus", title=get_text("vehicle_charge_status_chart_title"), color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white")
                    st.plotly_chart(fig_charge_status_pie_tab2, use_container_width=True)
                else:
                    st.info(get_text("run_analysis_to_view_status"))

            with tab2_3:
                st.markdown(f"#### {get_text('energy_req_vs_charged_test')}")
                if st.session_state.risultati_tab2 and 'veicoli_simulati' in st.session_state.risultati_tab2:
                    df_veicoli_charged_tab2 = pd.DataFrame([
                        {
                            "Vehicle": v["nome"],
                            "EnergyRequested": v["energia_richiesta"],
                            "InternalEnergy": v["energia_richiesta"] - v["energia_rimanente"]
                        } for v in st.session_state.risultati_tab2['veicoli_simulati']
                    ])
                    df_veicoli_charged_tab2 = df_veicoli_charged_tab2.sort_values(by="EnergyRequested", ascending=False).head(10)

                    if not df_veicoli_charged_tab2.empty:
                        fig_energy_comparison_tab2 = px.bar(df_veicoli_charged_tab2, x="Vehicle", y=["EnergyRequested", "InternalEnergy"], barmode='group', title=get_text("energy_comparison_chart_title"), template="plotly_white")
                        fig_energy_comparison_tab2.update_xaxes(title_text=get_text("vehicle_label"))
                        fig_energy_comparison_tab2.update_yaxes(title_text=get_text("energy_kwh_label"))
                        st.plotly_chart(fig_energy_comparison_tab2, use_container_width=True)
                    else:
                        st.info(get_text("no_vehicle_data_for_chart"))
                else:
                    st.info(get_text("run_analysis_to_view_comparison"))

            with tab2_4:
                st.markdown(f"#### {get_text('operating_costs_analysis_test')}")
                if st.session_state.risultati_tab2:
                    df_cost_breakdown_tab2 = pd.DataFrame({
                        "Type": [get_text("internal_operating_cost"), get_text("daily_external_charge_cost")],
                        "Cost": [st.session_state.risultati_tab2['costo_operativo_interno'], st.session_state.risultati_tab2['costo_ricariche_esterne']]
                    })
                    fig_cost_breakdown_tab2 = px.pie(df_cost_breakdown_tab2, values="Cost", names="Type", title=get_text("operating_costs_distribution_chart_title"), color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_white")
                    st.plotly_chart(fig_cost_breakdown_tab2, use_container_width=True)
                else:
                    st.info(get_text("run_analysis_to_view_costs"))

            with st.expander(get_text("optimization_suggestions"), expanded=True):
                if st.session_state.risultati_tab2:
                    risultati_tab2 = st.session_state.risultati_tab2

                    if risultati_tab2['energia_esterna'] > 0:
                        st.warning(get_text("improvement_opportunity").format(energy=risultati_tab2['energia_esterna']))

                    if risultati_tab2['auto_caricate_completamente'] < risultati_tab2['num_veicoli_totali']:
                        st.warning(get_text("fleet_coverage").format(charged=risultati_tab2['auto_caricate_completamente'], total=risultati_tab2['num_veicoli_totali']))

                    if risultati_tab2['tasso_utilizzo'] > 80:
                        st.warning(get_text("high_utilization_warning").format(utilization=risultati_tab2['tasso_utilizzo']))
                    elif risultati_tab2['tasso_utilizzo'] < 40:
                        st.info(get_text("low_utilization_info").format(utilization=risultati_tab2['tasso_utilizzo']))
                    else:
                        st.success(get_text("well_balanced_utilization"))

                    if risultati_tab2['investimento_totale_iniziale'] > 0:
                        if risultati_tab2['ROI'] > 15:
                            st.success(get_text("good_roi_success").format(roi=risultati_tab2['ROI']))
                        elif risultati_tab2['ROI'] > 0:
                            st.info(get_text("positive_roi_info").format(roi=risultati_tab2['ROI']))
                        else:
                            st.error(get_text("negative_roi_error").format(roi=risultati_tab2['ROI']))
                    else:
                        st.info(get_text("roi_not_calculable"))
                else:
                    st.info(get_text("run_analysis_to_view_suggestions"))
    else:
        st.info(get_text("configure_and_calculate"))

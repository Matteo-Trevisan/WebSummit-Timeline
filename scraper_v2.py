import requests
import json
import time

def fetch_events_for_date(date, base_url):
    """
    Esegue il fetching di tutti gli eventi per una data specifica, gestendo la paginazione.
    """
    params = {
        'slug': 'schedule',
        'typename': 'DefaultTemplate_Custompage_FlexibleContent_ScheduleList',
        'page': 1,
        'date': date
    }
    
    events_for_date = []
    total_pages = 1
    maximumPages = 1

    print(f"\n--- Inizio recupero eventi per la data: {date} ---")

    # 1. Prima richiesta per ottenere il numero di pagine per questa data
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        total_pages = data.get('data', {}).get('nbPages', 1)
        maximumPages = data.get('data', {}).get('maximumPages', 1)
        
        print(f"Trovate {total_pages} pagine per il {date}.")
        
        events_page_1 = data.get('data', {}).get('listItems', [])
        if events_page_1:
            events_for_date.extend(events_page_1)
            print(f"Recuperati {len(events_page_1)} eventi dalla pagina 1.")
        
    except requests.RequestException as e:
        print(f"Errore durante la richiesta della pagina 1 per la data {date}: {e}")
        return [] # Ritorna una lista vuota in caso di errore
    except json.JSONDecodeError:
        print(f"Errore nel decodificare il JSON dalla pagina 1 per la data {date}.")
        return []

    # 2. Ciclo per le pagine rimanenti per questa data
    limit = min(total_pages, maximumPages)
    if limit > 1:
        for page_num in range(2, limit + 1):
            print(f"Richiesta pagina {page_num} di {total_pages} per il {date}...")
            params['page'] = page_num
            
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                page_events = data.get('data', {}).get('listItems', [])
                if page_events:
                    events_for_date.extend(page_events)
                    print(f"Recuperati {len(page_events)} eventi.")
                else:
                    print(f"Nessun evento trovato sulla pagina {page_num}.")
                
                time.sleep(0.4)
                
            except requests.RequestException as e:
                print(f"Errore durante la richiesta della pagina {page_num} per il {date}: {e}. Pagina saltata.")
            except json.JSONDecodeError:
                print(f"Errore nel decodificare il JSON dalla pagina {page_num} per il {date}. Pagina saltata.")
    
    print(f"--- Fine recupero per la data: {date}. Totale eventi: {len(events_for_date)} ---")
    return events_for_date


def fetch_schedule():
    """
    Esegue il fetching dell'intera programmazione del Web Summit, prima ottenendo
    le date dell'evento e poi scaricando gli eventi per ogni singola data.
    Infine, salva tutti gli eventi in un unico file JSON.
    """
    base_url = "https://websummit.com/api/list/"
    all_events = []
    
    print("Avvio dello scraper...")

    # --- 1. Richiesta iniziale per ottenere le date della conferenza ---
    print("Recupero le date della conferenza...")
    initial_params = {
        'slug': 'schedule',
        'typename': 'DefaultTemplate_Custompage_FlexibleContent_ScheduleList',
        'page': 1
    }
    
    try:
        response = requests.get(base_url, params=initial_params)
        response.raise_for_status()
        data = response.json()
        
        conference_dates_data = data.get('data', {}).get('conferenceDates', [])
        if not conference_dates_data:
            print("Errore: Impossibile trovare le date della conferenza ('conferenceDates'). Interruzione.")
            return
            
        event_dates = [item['date'] for item in conference_dates_data]
        print(f"Date della conferenza trovate: {', '.join(event_dates)}")

    except requests.RequestException as e:
        print(f"Errore durante la richiesta iniziale per ottenere le date: {e}")
        return
    except json.JSONDecodeError:
        print("Errore nel decodificare il JSON dalla richiesta iniziale.")
        return

    # --- 2. Ciclo su ogni data per scaricare gli eventi ---
    for date in event_dates:
        daily_events = fetch_events_for_date(date, base_url)
        if daily_events:
            all_events.extend(daily_events)

    # --- 3. Salvataggio di tutti gli eventi in un file JSON ---
    if not all_events:
        print("\nNessun evento recuperato. Il file non verrà creato.")
        return

    output_filename = "websummit_schedule_completo_v5.json"
    print(f"\nDownload completato.")
    print(f"Eventi totali recuperati: {len(all_events)}")
    print(f"Salvataggio di tutti gli eventi in '{output_filename}'...")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_events, f, indent=2, ensure_ascii=False)
        
        print(f"Salvataggio completato con successo in '{output_filename}'.")
        
    except IOError as e:
        print(f"Errore durante il salvataggio del file: {e}")
    except Exception as e:
        print(f"Un errore inaspettato è occorso durante il salvataggio: {e}")

if __name__ == "__main__":
    fetch_schedule()
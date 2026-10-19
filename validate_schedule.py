import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime

REQUIRED_FIELDS = ['id', 'title', 'date', 'starts_at', 'ends_at', 'conferenceSlug']


def load_events(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"'{path}' non contiene una lista di eventi")
    return data


def parse_iso(value):
    """Ritorna un datetime se il valore è un timestamp ISO, altrimenti None (formato '5.00PM' delle vecchie edizioni)."""
    if not isinstance(value, str) or len(value) < 10 or value[4] != '-':
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def validate(new_events, current_events, year, min_events, min_ratio):
    """
    Controlla che il nuovo file sia sensato rispetto a quello pubblicato.
    Ritorna (errori, avvisi): con almeno un errore il file non va pubblicato.
    """
    errors = []
    warnings = []

    if len(new_events) < min_events:
        errors.append(f"Solo {len(new_events)} eventi scaricati (minimo richiesto: {min_events}).")

    if current_events and len(new_events) < len(current_events) * min_ratio:
        errors.append(
            f"Gli eventi sono scesi da {len(current_events)} a {len(new_events)} "
            f"(sotto il {min_ratio:.0%} di quelli attuali)."
        )

    # --- Campi obbligatori e coerenza dei singoli eventi ---
    expected_slug_suffix = str(year)[-2:]
    bad_events = 0
    wrong_edition = Counter()
    bad_times = 0
    for event in new_events:
        if not isinstance(event, dict) or any(not event.get(field) for field in REQUIRED_FIELDS):
            bad_events += 1
            continue

        slug = event['conferenceSlug']
        if not slug.endswith(expected_slug_suffix):
            wrong_edition[slug] += 1

        start, end = parse_iso(event['starts_at']), parse_iso(event['ends_at'])
        if start and end:
            if start.year != year:
                wrong_edition[f"anno {start.year}"] += 1
            if end < start:
                bad_times += 1

    if bad_events:
        errors.append(f"{bad_events} eventi senza uno dei campi obbligatori ({', '.join(REQUIRED_FIELDS)}).")
    if wrong_edition:
        found = ', '.join(f"{k} ({v})" for k, v in wrong_edition.most_common())
        errors.append(f"Eventi che non sembrano dell'edizione {year}: {found}. L'API sta forse servendo un'altra edizione?")
    if bad_times:
        errors.append(f"{bad_times} eventi finiscono prima di iniziare.")

    missing_location = sum(1 for e in new_events if isinstance(e, dict) and not (e.get('location') or {}).get('name'))
    if missing_location:
        warnings.append(f"{missing_location} eventi senza location (finiranno in 'Sede Sconosciuta').")

    ids = [e.get('id') for e in new_events if isinstance(e, dict)]
    duplicates = len(ids) - len(set(ids))
    if duplicates:
        errors.append(f"{duplicates} eventi duplicati (stesso id).")

    # --- Un giorno intero sparito di solito vuol dire che una richiesta è fallita ---
    new_per_day = Counter(e.get('date') for e in new_events if isinstance(e, dict))
    current_per_day = Counter(e.get('date') for e in current_events)
    for day, count in current_per_day.items():
        if count >= 20 and new_per_day.get(day, 0) < count * min_ratio:
            errors.append(f"Il giorno '{day}' è passato da {count} a {new_per_day.get(day, 0)} eventi.")

    return errors, warnings


def build_report(new_events, current_events, errors, warnings):
    new_per_day = Counter(e.get('date') for e in new_events if isinstance(e, dict))
    current_per_day = Counter(e.get('date') for e in current_events)
    new_ids = {e.get('id') for e in new_events if isinstance(e, dict)}
    current_ids = {e.get('id') for e in current_events}

    lines = [
        "## Validazione schedule",
        "",
        f"**{'❌ Non valido' if errors else '✅ Valido'}** — {len(new_events)} eventi "
        f"(prima: {len(current_events)}, nuovi: {len(new_ids - current_ids)}, rimossi: {len(current_ids - new_ids)})",
        "",
        "| Giorno | Prima | Ora |",
        "| ------ | ----- | --- |",
    ]
    for day in sorted(set(new_per_day) | set(current_per_day), key=str):
        lines.append(f"| {day} | {current_per_day.get(day, 0)} | {new_per_day.get(day, 0)} |")
    if errors:
        lines += ["", "### Errori", *[f"- {e}" for e in errors]]
    if warnings:
        lines += ["", "### Avvisi", *[f"- {w}" for w in warnings]]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description="Valida un file di schedule scaricato prima di pubblicarlo.")
    parser.add_argument('new_file', help="JSON appena scaricato dallo scraper")
    parser.add_argument('current_file', help="JSON attualmente pubblicato (può non esistere)")
    parser.add_argument('--year', type=int, required=True, help="Edizione attesa, es. 2026")
    parser.add_argument('--min-events', type=int, default=100, help="Numero minimo assoluto di eventi")
    parser.add_argument('--min-ratio', type=float, default=0.8,
                        help="Frazione minima di eventi rispetto al file attuale (0 per disattivare)")
    args = parser.parse_args()

    try:
        new_events = load_events(args.new_file)
    except (OSError, ValueError) as e:
        print(f"Errore: impossibile leggere il nuovo file: {e}")
        sys.exit(1)

    current_events = []
    if os.path.exists(args.current_file):
        try:
            current_events = load_events(args.current_file)
        except (OSError, ValueError) as e:
            print(f"Avviso: file attuale illeggibile, lo ignoro: {e}")

    errors, warnings = validate(new_events, current_events, args.year, args.min_events, args.min_ratio)
    report = build_report(new_events, current_events, errors, warnings)
    print(report)

    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a', encoding='utf-8') as f:
            f.write(report)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

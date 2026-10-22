"""Energy consumption and tariff calculator."""
import json
from datetime import datetime

METERS = {}
RATES = [3.5, 5.0, 7.5]
SPIKE_LIMIT = 500


def record_reading(meter_id, units, history=None):
    """Add units to a meter's total and log the reading. Returns the log."""
    if units < 0:
        raise ValueError("units cannot be negative")
    if history is None:
        history = []
    history.append((meter_id, units, str(datetime.now())))
    METERS[meter_id] = METERS.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    """Three-tier bill: first 100 units, next 200 units, then the rest."""
    units = METERS[meter_id]
    if units <= 100:
        return units * tier_rates[0]
    if units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]
    return 100 * tier_rates[0] + 200 * tier_rates[1] + (units - 300) * tier_rates[2]


def raise_rates(percent):
    """Increase every tier rate by the given percentage."""
    for i, rate in enumerate(RATES):
        RATES[i] = rate * (1 + percent / 100)


def flag_spikes():
    """Return meter ids whose usage exceeds SPIKE_LIMIT."""
    return [meter for meter, total in METERS.items() if total > SPIKE_LIMIT]


def load_meter_data(file="meters.json"):
    """Load meter totals from JSON; start empty if missing or corrupt."""
    try:
        with open(file, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        data = {}
    METERS.clear()
    METERS.update(data)


def save_meter_data(file="meters.json"):
    """Write meter totals to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(METERS, handle)


def main():
    """Run the demo."""
    history = []
    record_reading("M-01", 120, history)
    record_reading("M-02", 640, history)
    try:
        record_reading("M-03", -50, history)
    except ValueError as err:
        print("Rejected reading for M-03:", err)
    print("Readings stored so far:", len(history))

    raise_rates(10)
    print(f"Bill M-01: {compute_bill('M-01', RATES):.2f}")
    print("Spikes:", flag_spikes())

    adjustment = input("Extra units for M-01 (number, Enter for 0): ") or "0"
    try:
        record_reading("M-01", float(adjustment), history)
    except ValueError as err:
        print("Invalid input:", err)

    save_meter_data()
    load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill('M-01', RATES):.2f}")


if __name__ == "__main__":
    main()
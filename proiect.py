import random
import time
import os
import math
import heapq
import logging
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import tkinter as tk
from tkinter import ttk, messagebox

logging.basicConfig(
    filename="flight_system.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)

class FlightMonitoringSystem:
    def __init__(self, db_path: str = "flights.db"):
        self.flights_data: List[Dict[str, Any]] = []
        self.delay_history = defaultdict(list)
        self.company_stats = defaultdict(lambda: {'total': 0, 'delayed': 0})
        self.airlines = ['TAROM', 'Wizz Air', 'Lufthansa', 'Turkish Airlines', 'Air France']
        self.airports = ['OTP', 'CLJ', 'TSR', 'IST', 'MUC', 'CDG', 'VIE', 'FCO']
        self.db_path = db_path
        try:
            self.init_db()
        except Exception as e:
            logging.exception("DB init failed: %s", e)

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                id TEXT PRIMARY KEY,
                airline TEXT,
                origin TEXT,
                destination TEXT,
                scheduled_time TEXT,
                actual_delay INTEGER,
                weather_score REAL,
                traffic_score REAL,
                technical_score REAL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS airline_stats (
                airline TEXT PRIMARY KEY,
                total INTEGER,
                delayed INTEGER
            );
        """)
        conn.commit()
        conn.close()
        logging.info("Database initialized at %s", self.db_path)

    def save_flight_to_db(self, flight: Dict[str, Any]):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO flights (
                    id, airline, origin, destination, scheduled_time,
                    actual_delay, weather_score, traffic_score, technical_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight['id'],
                flight['airline'],
                flight['origin'],
                flight['destination'],
                flight['scheduled_time'].isoformat(),
                int(flight['actual_delay']),
                float(flight['weather_score']),
                float(flight['traffic_score']),
                float(flight['technical_score'])
            ))
            conn.commit()
            conn.close()
        except Exception:
            logging.exception("Failed to save flight %s to DB", flight.get('id'))

    def load_flights_from_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, airline, origin, destination, scheduled_time, actual_delay, weather_score, traffic_score, technical_score FROM flights")
            rows = cur.fetchall()
            conn.close()
            loaded = []
            for r in rows:
                flight = {
                    'id': r[0],
                    'airline': r[1],
                    'origin': r[2],
                    'destination': r[3],
                    'scheduled_time': datetime.fromisoformat(r[4]),
                    'actual_delay': int(r[5]),
                    'weather_score': float(r[6]),
                    'traffic_score': float(r[7]),
                    'technical_score': float(r[8])
                }
                loaded.append(flight)
            if loaded:
                self.flights_data = loaded
                self.company_stats = defaultdict(lambda: {'total': 0, 'delayed': 0})
                for f in self.flights_data:
                    a = f['airline']
                    self.company_stats[a]['total'] += 1
                    if f['actual_delay'] > 15:
                        self.company_stats[a]['delayed'] += 1
                logging.info("Loaded %d flights from DB", len(loaded))
        except Exception:
            logging.exception("Failed to load flights from DB")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def calculate_mean(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def generate_sample_data(self, num_flights: int = 50, persist: bool = True):
        print("\n Generare date de zbor...")
        logging.info("Generating %d sample flights", num_flights)
        for i in range(num_flights):
            origin = random.choice(self.airports)
            destination = random.choice([a for a in self.airports if a != origin])
            flight = {
                'id': f"FL{1000 + len(self.flights_data) + i}",
                'airline': random.choice(self.airlines),
                'origin': origin,
                'destination': destination,
                'scheduled_time': datetime.now() + timedelta(hours=random.randint(-2, 24)),
                'actual_delay': random.randint(-30, 180) if random.random() > 0.3 else 0,
                'weather_score': random.uniform(0, 10),
                'traffic_score': random.uniform(0, 10),
                'technical_score': random.uniform(0, 10)
            }
            self.flights_data.append(flight)
            airline = flight['airline']
            self.company_stats[airline]['total'] += 1
            if flight['actual_delay'] > 15:
                self.company_stats[airline]['delayed'] += 1
            if persist:
                self.save_flight_to_db(flight)
            logging.debug("Generated flight %s", flight['id'])
        print(f" Generat {num_flights} zboruri\n")
        time.sleep(0.5)

    # NOU: genereaza 1 zbor pentru GUI, fara sleep/print (ca sa nu inghete UI)
    def generate_one_flight(self, persist: bool = True) -> Dict[str, Any]:
        origin = random.choice(self.airports)
        destination = random.choice([a for a in self.airports if a != origin])

        new_flight = {
            'id': f"FL{2000 + len(self.flights_data)}",
            'airline': random.choice(self.airlines),
            'origin': origin,
            'destination': destination,
            'scheduled_time': datetime.now() + timedelta(hours=random.randint(1, 12)),
            'actual_delay': random.randint(0, 120) if random.random() > 0.4 else 0,
            'weather_score': random.uniform(0, 10),
            'traffic_score': random.uniform(0, 10),
            'technical_score': random.uniform(0, 10)
        }

        self.flights_data.append(new_flight)

        airline = new_flight['airline']
        self.company_stats[airline]['total'] += 1
        if new_flight['actual_delay'] > 15:
            self.company_stats[airline]['delayed'] += 1

        if persist:
            self.save_flight_to_db(new_flight)

        return new_flight

    def insertion_sort(self, arr, left, right, key):
        # DESC: mare -> mic
        for i in range(left + 1, right + 1):
            temp = arr[i]
            j = i - 1
            while j >= left and arr[j][key] < temp[key]:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = temp

    def merge(self, arr, l, m, r, key):
        # DESC: mare -> mic
        left = arr[l:m+1]
        right = arr[m+1:r+1]

        i = j = 0
        k = l

        while i < len(left) and j < len(right):
            # MODIFICAT: >= pentru DESC
            if left[i][key] >= right[j][key]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

    def timsort_delays(self, flights):
        n = len(flights)
        RUN = 32
        key = "actual_delay"

        for start in range(0, n, RUN):
            end = min(start + RUN - 1, n - 1)
            self.insertion_sort(flights, start, end, key)

        size = RUN
        while size < n:
            for left in range(0, n, 2 * size):
                mid = left + size - 1
                right = min((left + 2 * size - 1), n - 1)

                if mid < right:
                    self.merge(flights, left, mid, right, key)

            size *= 2

        return flights

    def quickselect_top_delays(self, flights: List[Dict[str, Any]], k: int = 10) -> List[Dict[str, Any]]:
        k = min(k, len(flights))
        if k == 0:
            return []
        return heapq.nlargest(k, flights, key=lambda f: f['actual_delay'])

    def misra_gries_frequent_delays(self, stream_data: List[Dict[str, Any]], k: int = 3) -> List[Tuple[str, int]]:
        counters: Dict[str, int] = {}
        for flight in stream_data:
            if flight['actual_delay'] > 30:
                airline = flight['airline']
                if airline in counters:
                    counters[airline] += 1
                elif len(counters) < max(1, k - 1):
                    counters[airline] = 1
                else:
                    counters = {a: c - 1 for a, c in counters.items()}
                    counters = {a: c for a, c in counters.items() if c > 0}
        if not counters:
            return []
        final_counts: Dict[str, int] = {}
        for flight in stream_data:
            if flight['actual_delay'] > 30 and flight['airline'] in counters:
                final_counts.setdefault(flight['airline'], 0)
                final_counts[flight['airline']] += 1
        return sorted(final_counts.items(), key=lambda x: x[1], reverse=True)

    def estimate_delay(self, flight: Dict[str, Any]) -> int:
        weighted = (
            flight['weather_score'] * 5.0 +
            flight['traffic_score'] * 3.0 +
            flight['technical_score'] * 4.0
        )
        base = weighted / 10.0
        airline_factor = self.company_stats.get(flight['airline'], {'total': 0, 'delayed': 0})
        if airline_factor['total'] > 0:
            delay_rate = airline_factor['delayed'] / airline_factor['total']
            base *= (1.0 + delay_rate * 0.5)

        estimated = int(max(0, min(base, 600)))
        return estimated

    def calculate_accuracy(self, actual: int, estimated: int) -> float:
        if actual == 0:
            return 100.0 if estimated == 0 else 0.0
        error = abs(actual - estimated) / max(actual, 1)
        return max(0.0, 100.0 * (1.0 - error))

    def calculate_error_metrics(self) -> Tuple[float, float]:
        errors: List[float] = []
        for flight in self.flights_data:
            predicted = self.estimate_delay(flight)
            errors.append(abs(predicted - flight['actual_delay']))
        if not errors:
            return 0.0, 0.0
        mae = sum(errors) / len(errors)
        rmse = math.sqrt(sum(e * e for e in errors) / len(errors))
        return mae, rmse

    # Restul functiilor CLI raman la fel (nu sunt folosite in GUI acum)
    def real_time_simulation(self, duration: int = 10):
        print("SIMULARE TIMP REAL")
        print("-" * 80)
        print("Monitorizare flux continuu de date...\n")
        for i in range(duration):
            origin = random.choice(self.airports)
            destination = random.choice([a for a in self.airports if a != origin])
            new_flight = {
                'id': f"FL{2000 + len(self.flights_data)}",
                'airline': random.choice(self.airlines),
                'origin': origin,
                'destination': destination,
                'scheduled_time': datetime.now() + timedelta(hours=random.randint(1, 12)),
                'actual_delay': random.randint(0, 120) if random.random() > 0.4 else 0,
                'weather_score': random.uniform(0, 10),
                'traffic_score': random.uniform(0, 10),
                'technical_score': random.uniform(0, 10)
            }
            self.flights_data.append(new_flight)
            airline = new_flight['airline']
            self.company_stats[airline]['total'] += 1
            if new_flight['actual_delay'] > 15:
                self.company_stats[airline]['delayed'] += 1
            self.save_flight_to_db(new_flight)
            estimated = self.estimate_delay(new_flight)
            print(
                f"Zbor nou: {new_flight['id']} | {new_flight['airline']} | "
                f"{new_flight['origin']}->{new_flight['destination']} | "
                f"Delay: {new_flight['actual_delay']} min | "
                f"Estimat: {estimated} min"
            )
            time.sleep(0.5)
        print("\nSimulare completa!\n")

class FlightUI:
    def __init__(self, root, system: FlightMonitoringSystem):
        self.root = root
        self.system = system

        root.title("✈ Flight Monitoring System — AirTech Dashboard")
        root.geometry("1250x720")
        root.configure(bg="#0f172a")

        navbar = tk.Frame(root, bg="#1e293b", height=60)
        navbar.pack(fill="x")

        title = tk.Label(
            navbar,
            text="✈  AirTech Flight Monitor",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(side="left", padx=20)

        sidebar = tk.Frame(root, bg="#1e293b", width=260)
        sidebar.pack(side="left", fill="y")

        def make_btn(text, command):
            btn = tk.Button(
                sidebar,
                text=text,
                font=("Segoe UI", 11),
                bg="#334155",
                fg="#e2e8f0",
                activebackground="#38bdf8",
                activeforeground="black",
                bd=0,
                height=2,
                relief="flat",
                command=command
            )
            btn.pack(fill="x", padx=18, pady=5)
            return btn

        buttons = [
            (" Generate 20 Flights", self.generate_flights),
            (" Real-Time Simulation", self.real_time_sim),
            (" Show Top Delays", self.show_top_delays),
            (" Sorted Delays (Timsort)", self.show_sorted),
            (" Frequent Companies (MG)", self.show_frequent),
            (" Database Info", self.show_db_info),
            (" Full Report", self.full_report),
            ("🔄 Reload Database", self.reload_db),
            ("📁 View Logs", self.open_log_viewer),
        ]
        for txt, cmd in buttons:
            make_btn(txt, cmd)

        main_area = tk.Frame(root, bg="#0f172a")
        main_area.pack(fill="both", expand=True, padx=20, pady=20)

        card = tk.Frame(main_area, bg="#1e293b", bd=0)
        card.pack(fill="both", expand=True)

        header = tk.Label(
            card,
            text="AirTech — Live Output",
            bg="#1e293b",
            fg="#38bdf8",
            font=("Segoe UI", 16, "bold")
        )
        header.pack(pady=10)

        self.output = tk.Text(
            card,
            font=("Consolas", 12),
            bg="#0f172a",
            fg="#cbd5e1",
            insertbackground="white",
            relief="flat",
            wrap="none"
        )
        self.output.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.output, command=self.output.yview)
        self.output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def print(self, text):
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def clear(self):
        self.output.delete("1.0", "end")

    def generate_flights(self):
        self.system.generate_sample_data(20, persist=True)
        self.print(">>> Generated 20 flights ✔")

    # MODIFICAT: real-time fara freeze (after)
    def real_time_sim(self):
        self.print(">>> Starting real-time simulation (10 flights)...")
        self._rt_remaining = 10

        def step():
            if self._rt_remaining <= 0:
                self.print(">>> Real-time simulation finished ✔")
                return

            new_flight = self.system.generate_one_flight(persist=True)
            self.print(f"[RT] {new_flight['id']} | {new_flight['airline']} | "
                       f"{new_flight['origin']}->{new_flight['destination']} | "
                       f"Delay: {new_flight['actual_delay']} min")

            self._rt_remaining -= 1
            self.root.after(500, step)

        step()

    def show_top_delays(self):
        self.clear()
        top = self.system.quickselect_top_delays(self.system.flights_data, 10)
        self.print("==== TOP 10 DELAYS (heapq.nlargest) ====\n")
        for f in top:
            self.print(f"{f['id']} | {f['airline']} | {f['actual_delay']} min")

    def show_sorted(self):
        self.clear()
        # IMPORTANT: timsort_delays sorteaza IN-PLACE; folosim copie ca sa nu stric ordinea originala
        data = self.system.timsort_delays(list(self.system.flights_data))
        self.print("==== SORTED DELAYS (Timsort DESC) ====\n")
        for f in data[:20]:
            self.print(f"{f['id']} | {f['airline']} | {f['actual_delay']} min")

    def show_frequent(self):
        self.clear()
        freq = self.system.misra_gries_frequent_delays(self.system.flights_data)
        self.print("==== FREQUENT AIRLINES (Misra-Gries) ====\n")
        for airline, count in freq:
            self.print(f"{airline} — {count} high delays")

    def show_db_info(self):
        self.clear()
        self.print("==== DATABASE INFO ====\n")
        self.print(f"Total flights: {len(self.system.flights_data)}")
        self.print(f"Airlines: {len(set(f['airline'] for f in self.system.flights_data))}")
        self.print(f"Origins: {len(set(f['origin'] for f in self.system.flights_data))}")
        self.print(f"Destinations: {len(set(f['destination'] for f in self.system.flights_data))}")

    def full_report(self):
        self.clear()
        self.print("==== FULL REPORT ====\n")
        mae, rmse = self.system.calculate_error_metrics()
        self.print(f"MAE: {mae:.2f}")
        self.print(f"RMSE: {rmse:.2f}")

    def reload_db(self):
        self.system.load_flights_from_db()
        self.print(">>> Database Reloaded ✔")

    def open_log_viewer(self):
        win = tk.Toplevel(self.root)
        win.title("Log Viewer — AirTech")
        win.geometry("850x600")
        win.configure(bg="#0f172a")

        text = tk.Text(
            win, font=("Consolas", 11), bg="#1e293b", fg="#cbd5e1",
            insertbackground="white", relief="flat"
        )
        text.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(text, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        try:
            with open("flight_system.log", "r") as file:
                text.insert("end", file.read())
        except:
            text.insert("end", "[ Log file not found ]")

        text.see("end")

if __name__ == "__main__":
    system = FlightMonitoringSystem()
    system.load_flights_from_db()

    root = tk.Tk()
    ui = FlightUI(root, system)
    root.mainloop()

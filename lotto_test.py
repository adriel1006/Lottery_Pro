import sys
import random
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QRadioButton, QCheckBox, QButtonGroup
)

# Define the filename where the past winning numbers will be stored
filename = "winning_numbers.json"

# Initialize past winning numbers with preloaded values
past_winning_numbers = [
    [3, 8, 10, 11, 12, 14, 15, 17, 19, 20, 24],
    [1, 2, 3, 7, 8, 10, 12, 16, 18, 20, 21],
    [1, 2, 3, 4, 14, 18, 19, 21, 22, 24, 25],
    [1, 2, 3, 7, 10, 12, 15, 18, 22, 24, 25],
    [1, 5, 6, 9, 13, 14, 16, 17, 18, 19, 24],
    [2, 5, 8, 9, 12, 13, 17, 20, 21, 22, 24],
    [1, 5, 8, 13, 14, 15, 17, 19, 20, 24, 25],
    [3, 4, 9, 10, 13, 15, 16, 18, 19, 20, 24],
    [4, 5, 7, 9, 10, 16, 17, 20, 21, 22, 24],
    [6, 8, 11, 14, 15, 16, 17, 18, 19, 23, 24],
    [1, 3, 5, 8, 10, 11, 13, 18, 19, 21, 22],
    [1, 2, 4, 8, 10, 11, 12, 13, 17, 20, 23],
    [3, 6, 8, 10, 11, 12, 14, 18, 20, 24, 25],
    [1, 4, 5, 6, 8, 9, 10, 11, 12, 14, 17],
    [1, 3, 4, 9, 11, 14, 15, 16, 17, 18, 19],
    [1, 4, 6, 7, 11, 13, 14, 16, 17, 19, 22],
    [1, 3, 4, 7, 8, 10, 12, 16, 21, 22, 23],
    [2, 5, 6, 7, 8, 10, 16, 17, 18, 22, 24],
    [4, 10, 14, 15, 16, 17, 19, 20, 22, 23, 24],
    [3, 6, 8, 9, 16, 20, 21, 22, 23, 24, 25],
    [3, 5, 6, 8, 10, 12, 14, 15, 18, 21, 23],
    [1, 2, 3, 8, 10, 12, 14, 15, 22, 23, 24],
    [3, 4, 5, 6, 11, 14, 16, 17, 18, 23, 24],
    [2, 7, 8, 11, 12, 15, 16, 18, 19, 24, 25],
    [2, 3, 4, 6, 9, 15, 17, 18, 20, 24, 25],
    [5, 6, 9, 10, 12, 13, 16, 19, 21, 22, 24],
    [1, 2, 4, 6, 8, 13, 18, 19, 20, 21, 24],
    [3, 4, 5, 6, 11, 12, 13, 17, 20, 21, 25],
    [3, 8, 9, 13, 14, 15, 19, 20, 21, 23, 25],
    [4, 7, 11, 14, 15, 16, 21, 22, 23, 24, 25],
    [4, 6, 7, 9, 11, 15, 16, 17, 20, 21, 24],
    [2, 3, 5, 6, 7, 9, 11, 13, 14, 20, 22],
    [2, 4, 5, 7, 8, 13, 18, 19, 20, 21, 22],
    [3, 4, 6, 9, 13, 15, 17, 18, 19, 21, 25],
    [2, 5, 6, 10, 13, 15, 17, 19, 21, 22, 25],
    [2, 4, 6, 7, 8, 9, 13, 16, 18, 21, 22]
    # Continue adding more sets as needed
]

# Load and save functions for JSON
def load_past_winning_numbers():
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_past_winning_numbers():
    with open(filename, 'w') as file:
        json.dump(past_winning_numbers, file)

# New strategies
def overdue_numbers_strategy(all_numbers, past_winning_numbers):
    last_drawn = {num: None for num in all_numbers}
    for draw_index, draw in enumerate(past_winning_numbers):
        for num in draw:
            last_drawn[num] = draw_index

    # Sort numbers by the draw index where they were last seen, prioritizing None (never seen)
    overdue_numbers = sorted(last_drawn, key=lambda x: last_drawn[x] if last_drawn[x] is not None else -1, reverse=True)

    return overdue_numbers[:15]  # Assuming you want the top 15 most overdue numbers
def adjacent_pairs_strategy(past_winning_numbers):
    pair_counts = defaultdict(int)
    for draw in past_winning_numbers:
        sorted_draw = sorted(draw)
        for i in range(len(sorted_draw) - 1):
            pair = (sorted_draw[i], sorted_draw[i + 1])
            pair_counts[pair] += 1
    sorted_pairs = sorted(pair_counts.items(), key=lambda item: item[1], reverse=True)
    selected_numbers = set()
    for pair, _ in sorted_pairs[:6]:
        selected_numbers.update(pair)
    return sorted(selected_numbers)

def cluster_analysis_strategy(past_winning_numbers):
    low_range = [num for num in range(1, 9)]
    mid_range = [num for num in range(9, 17)]
    high_range = [num for num in range(17, 26)]
    cluster_counts = {'low': 0, 'mid': 0, 'high': 0}
    
    for draw in past_winning_numbers:
        for num in draw:
            if num in low_range:
                cluster_counts['low'] += 1
            elif num in mid_range:
                cluster_counts['mid'] += 1
            elif num in high_range:
                cluster_counts['high'] += 1
    
    dominant_cluster = max(cluster_counts, key=cluster_counts.get)
    
    if dominant_cluster == 'low':
        return low_range
    elif dominant_cluster == 'mid':
        return mid_range
    else:
        return high_range

def pattern_repetition_strategy(past_winning_numbers):
    pattern_counts = defaultdict(int)
    for draw in past_winning_numbers:
        pattern = tuple(sorted(draw))
        pattern_counts[pattern] += 1
    most_common_pattern = max(pattern_counts, key=pattern_counts.get)
    return list(most_common_pattern)

# Combine selected strategies
def combine_strategies(selected_strategies, past_winning_numbers, preferred_even, preferred_odd):
    combined_numbers = set()
    all_numbers = list(range(1, 26))

    for strategy in selected_strategies:
        if strategy == 'overdue':
            combined_numbers.update(overdue_numbers_strategy(all_numbers, past_winning_numbers))
        elif strategy == 'adjacent':
            combined_numbers.update(adjacent_pairs_strategy(past_winning_numbers))
        elif strategy == 'cluster':
            combined_numbers.update(cluster_analysis_strategy(past_winning_numbers))
        elif strategy == 'pattern':
            combined_numbers.update(pattern_repetition_strategy(past_winning_numbers))

    # If less than 11 numbers, add random numbers to reach 11
    while len(combined_numbers) < 11:
        combined_numbers.add(random.choice(all_numbers))

    # If more than 11 numbers, randomly select 11 from the combined set
    combined_numbers = list(combined_numbers)  # Convert set to list
    if len(combined_numbers) > 11:
        combined_numbers = random.sample(combined_numbers, 11)
    
    # Adjust for even-odd preference
    evens = [num for num in combined_numbers if num % 2 == 0]
    odds = [num for num in combined_numbers if num % 2 != 0]
    
    selected_numbers = []
    selected_numbers += random.sample(evens, min(preferred_even, len(evens)))
    selected_numbers += random.sample(odds, min(preferred_odd, len(odds)))

    # If we don't have enough numbers, fill in the remaining slots
    remaining_numbers = list(set(all_numbers) - set(selected_numbers))
    while len(selected_numbers) < 11:
        selected_numbers.append(random.choice(remaining_numbers))
        remaining_numbers.remove(selected_numbers[-1])

    return sorted(selected_numbers)

# PyQt5 GUI implementation
class LottoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Pro")
        self.setGeometry(200, 200, 800, 600)

        # Define a larger font
        self.large_font = QFont('Arial', 16)  # Adjusted for better visibility

        # Main layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.generator_tab = QWidget()
        self.stats_tab = QWidget()
        self.add_numbers_tab = QWidget()

        self.tabs.addTab(self.generator_tab, "Generator")
        self.tabs.addTab(self.stats_tab, "Statistics")
        self.tabs.addTab(self.add_numbers_tab, "Winning Numbers")

        # Initialize the button group for even/odd selection
        self.even_odd_group = QButtonGroup()

        # Setup tabs
        self.setup_generator_tab()
        self.setup_stats_tab()
        self.setup_add_numbers_tab()
        self.init_timer()
    
    def fetch_latest_results(self):
        url = "https://lotteryguru.com/ecuador-lottery-results/ec-pozo/ec-pozo-results-history"
        response = requests.get(url)
        print("Status Code:", response.status_code)  # Check if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results_container = soup.find('div', {'id': 'results_container'})
            if results_container:
                results = results_container.text.strip()
                print("Results fetched:", results)  # Check what is being fetched
                return results
            else:
                print("Results container not found.")
                return "Results container not found."
        else:
            return "Failed to fetch results."

    def update_results_display(self):
        results = self.fetch_latest_results()
        if results:
            self.past_numbers_display.setText(results)
            print("Display updated.")  # Confirm the display updates
        else:
            self.past_numbers_display.setText("No results to display.")
            print("No results to display.")

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_results_display)
        self.timer.start(86400000)  # 86,400,000 milliseconds = 24 hours
        print("Timer started.")  # Confirm the timer starts

    def setup_generator_tab(self):
        layout = QVBoxLayout()
        self.generator_tab.setLayout(layout)
    # Strategy checkboxes
        self.overdue_checkbox = QCheckBox("Overdue Numbers Strategy")
        self.adjacent_checkbox = QCheckBox("Adjacent Pairs Strategy")
        self.cluster_checkbox = QCheckBox("Cluster Analysis Strategy")
        self.pattern_checkbox = QCheckBox("Pattern Repetition Strategy")

    # Apply large font to checkboxes
        for checkbox in [self.overdue_checkbox, self.adjacent_checkbox, self.cluster_checkbox, self.pattern_checkbox]:
            checkbox.setFont(self.large_font)

        layout.addWidget(self.overdue_checkbox)
        layout.addWidget(self.adjacent_checkbox)
        layout.addWidget(self.cluster_checkbox)
        layout.addWidget(self.pattern_checkbox)

    # Even/Odd selection label with large font
        even_odd_label = QLabel("Do you prefer more even or more odd numbers?")
        even_odd_label.setFont(self.large_font)  # Set the large font for the label
        layout.addWidget(even_odd_label)

        preferences = ["More Even (6 even, 5 odd)", "More Odd (5 even, 6 odd)"]
        for i, preference in enumerate(preferences):
            btn = QRadioButton(preference)
            btn.setFont(self.large_font)  # Apply large font
            self.even_odd_group.addButton(btn, i + 1)
            layout.addWidget(btn)
        self.even_odd_group.buttons()[0].setChecked(True)

    # Number of sets input
        self.num_sets_input = QLineEdit()
        self.num_sets_input.setPlaceholderText("Enter the number of sets to generate")
        self.num_sets_input.setFont(self.large_font)  # Apply large font
        layout.addWidget(self.num_sets_input)

    # Generate button
        self.generate_button = QPushButton("Generate")
        self.generate_button.setFont(self.large_font)  # Apply large font
        self.generate_button.clicked.connect(self.generate_numbers)
        layout.addWidget(self.generate_button)

    # Results display
        self.results_display = QTextEdit()
        self.results_display.setFont(self.large_font)  # Apply large font
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)

        self.generator_tab.setLayout(layout)
    
    def generate_numbers(self):
        self.results_display.clear()

        selected_strategies = []
        if self.overdue_checkbox.isChecked():
            selected_strategies.append('overdue')
        if self.adjacent_checkbox.isChecked():
            selected_strategies.append('adjacent')
        if self.cluster_checkbox.isChecked():
            selected_strategies.append('cluster')
        if self.pattern_checkbox.isChecked():
            selected_strategies.append('pattern')

        even_odd_preference = str(self.even_odd_group.checkedId())
        number_of_sets = int(self.num_sets_input.text())

        if even_odd_preference == '1':
            preferred_even = 6
            preferred_odd = 5
        else:
            preferred_even = 5
            preferred_odd = 6

        all_numbers = list(range(1, 26))  # Define all possible numbers

        for i in range(number_of_sets):
            generated_numbers = combine_strategies(selected_strategies, past_winning_numbers, preferred_even, preferred_odd)
            output = f"Set {i + 1}: {generated_numbers}\n"
            output += "Strategies used and their contributions:\n"
        
            if 'overdue' in selected_strategies:
                overdue_numbers = overdue_numbers_strategy(all_numbers, past_winning_numbers)  # Pass both required arguments
                output += f"  Overdue Numbers Strategy contributed: {list(set(overdue_numbers) & set(generated_numbers))}\n"
        
            if 'adjacent' in selected_strategies:
                adjacent_numbers = adjacent_pairs_strategy(past_winning_numbers)
                output += f"  Adjacent Pairs Strategy contributed: {list(set(adjacent_numbers) & set(generated_numbers))}\n"
        
            if 'cluster' in selected_strategies:
                cluster_numbers = cluster_analysis_strategy(past_winning_numbers)
                output += f"  Cluster Analysis Strategy contributed: {list(set(cluster_numbers) & set(generated_numbers))}\n"
        
            if 'pattern' in selected_strategies:
                pattern_numbers = pattern_repetition_strategy(past_winning_numbers)
                output += f"  Pattern Repetition Strategy contributed: {list(set(pattern_numbers) & set(generated_numbers))}\n"
        
            self.results_display.append(output)
    
    def setup_stats_tab(self):
        layout = QVBoxLayout()
        self.stats_tab.setLayout(layout)

        # Bar graph setup
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    # Buttons to switch graphs
        self.freq_button = QPushButton("Show Frequency Graph")
        self.freq_button.clicked.connect(self.plot_frequency)
        layout.addWidget(self.freq_button)

        self.even_odd_button = QPushButton("Show Even/Odd Distribution")
        self.even_odd_button.clicked.connect(self.plot_even_odd_distribution)
        layout.addWidget(self.even_odd_button)

    # Default plot
        self.plot_frequency()

    def plot_frequency(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        all_numbers = [num for draw in past_winning_numbers for num in draw]
        number_frequency = Counter(all_numbers)

        numbers = list(range(1, 26))
        frequencies = [number_frequency.get(num, 0) for num in numbers]

        bars = ax.bar(numbers, frequencies, color='skyblue', edgecolor='black')  # Added edge color for better separation

        ax.set_xlabel('Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Frequency of Lottery Numbers', fontsize=14, fontweight='bold')

        ax.set_xticks(numbers)
        ax.set_xticklabels(numbers, rotation=45)  # Rotate labels for better visibility

        # Highlight the most frequent numbers
        max_freq = max(frequencies)
        for bar, freq in zip(bars, frequencies):
            if freq == max_freq:
                bar.set_color('red')  # Highlight the most frequent bars
            ax.annotate(f'{freq}',  # Annotate the frequency on each bar
                        xy=(bar.get_x() + bar.get_width() / 2, freq),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

        ax.grid(True, linestyle='--', alpha=0.6)  # Make grid less prominent but still visible

        self.canvas.draw()

    def setup_add_numbers_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter 11 Winning Numbers (comma-separated):"))
        self.number_entry = QLineEdit()
        layout.addWidget(self.number_entry)

        self.add_button = QPushButton("Add Winning Numbers")
        self.add_button.clicked.connect(self.add_winning_numbers)
        layout.addWidget(self.add_button)

        self.past_numbers_display = QTextEdit()
        self.past_numbers_display.setReadOnly(True)
        layout.addWidget(self.past_numbers_display)

        self.add_numbers_tab.setLayout(layout)

        self.update_past_numbers_display()

    def add_winning_numbers(self):
        input_numbers = self.number_entry.text().strip()
        try:
            new_numbers = list(map(int, input_numbers.split(',')))
            if len(new_numbers) != 11:
                raise ValueError("Exactly 11 numbers must be entered.")
            past_winning_numbers.append(new_numbers)
            save_past_winning_numbers()
            self.number_entry.clear()
            self.update_past_numbers_display()
        except ValueError as e:
            self.results_display.append(f"Error: {e}")

    def update_past_numbers_display(self):
        self.past_numbers_display.clear()
        start_session = 1065
        for i, numbers in enumerate(past_winning_numbers):
            session_number = start_session + i
            self.past_numbers_display.append(f"Session {session_number}: {numbers}")
    
    def plot_even_odd_distribution(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        even_counts = []
        odd_counts = []
        sessions = []
    
        start_session = 1065  # Start session number
        for i, draw in enumerate(past_winning_numbers):
            even_count = sum(1 for num in draw if num % 2 == 0)
            odd_count = len(draw) - even_count
            even_counts.append(even_count)
            odd_counts.append(odd_count)
            sessions.append(start_session + i)  # Use start_session to label sessions

        ax.bar(sessions, even_counts, label='Even', color='blue')
        ax.bar(sessions, odd_counts, bottom=even_counts, label='Odd', color='green')

        ax.set_xlabel('Session', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title('Even and Odd Number Distribution per Session', fontsize=14, fontweight='bold')
    
        ax.set_xticks(sessions)  # Set x-ticks to session numbers
        ax.set_xticklabels([f"{s}" for s in sessions], rotation=45)  # Label x-ticks with session numbers
        ax.set_yticks(range(0, 12))  # Set y-ticks to cover counts from 0 to 11
        ax.set_ylim(0, 11)  # Set y-axis limits to ensure visibility of all counts
    
        ax.legend()

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LottoApp()
    window.show()
    sys.exit(app.exec_())

import tkinter as tk
from tkinter import ttk
import pandas as pd
import re

def parse_mac_to_int(mac):
    """Converts MAC address to an integer node number."""
    return int(mac.replace(':', ''), 16) -1

def parse_data():
    """Parses the manet file and returns a DataFrame based on specific conditions."""
    data_rows = []
    packet_number = 0
    source_node_number = None
    destination_node_number = None
    intermediate_nodes = []
    successful = False
    time_stamp = None
    total_sent = 0
    total_received = 0
    total_beacons = 0
    total_acknowledgements = 0
    total_informations = 0
    total_informations_lost = 0
    total_retry = 0

    with open('manet.tr', 'r') as file:
        lines = file.readlines()


    for line in lines:
        parts = line.split()
        if line.startswith('t'):
            total_sent += 1  # Increment total packets sent
            time_stamp = parts[1]  # Get time from the second string
            if packet_number > 0:
                data_rows.append([time_stamp, packet_number, source_node_number, destination_node_number, successful, intermediate_nodes.copy(), packet_type])
                intermediate_nodes = []
            packet_number += 1
            successful = False

            if "Retry=1" in line:
                total_retry += 1
                if total_retry == 1:
                    total_retry += 1

            if "DA=ff:ff:ff:ff:ff:ff" in line:
                packet_type = "Beacon"
                destination_node_number = -1
                total_beacons += 1

            elif "CTL_ACK" in line:
                packet_type = "Acknowledgement"
                node_match_ack = re.search(r'/NodeList/(\d+)/', line)
                if node_match_ack:
                    node_id = int(node_match_ack.group(1))
                    destination_node_number = source_node_number
                    source_node_number = node_id
                total_acknowledgements += 1

            else:
                packet_type = "Information"
            sa_match = re.search(r"SA=([\da-f:]+)", line)
            if sa_match:
                source_node_number = parse_mac_to_int(sa_match.group(1))
            da_match = re.search(r"DA=([\da-f:]+)", line)
            if da_match:
                destination_node_number = parse_mac_to_int(da_match.group(1))
        elif line.startswith('r'):
            total_received += 1  # Increment total packets received
            node_match = re.search(r'/NodeList/(\d+)/', line)
            if node_match:
                node_id = int(node_match.group(1))
                if node_id == destination_node_number:
                    successful = True
                else:
                    intermediate_nodes.append(node_id)

    if packet_number > 0:
        data_rows.append([time_stamp, packet_number, source_node_number, destination_node_number, successful, intermediate_nodes, packet_type])

    return pd.DataFrame(data_rows, columns=['Time', 'Packet Number', 'Source Node', 'Destination Node', 'Successful', 'Intermediate Nodes', 'Packet Type']), total_sent, total_received, total_beacons, total_acknowledgements, total_retry

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        style = ttk.Style(self)
        style.configure('TFrame', background='light green')
        self.title("MANET Packet Viewer")
        self.geometry("1200x600")
        self.df, self.total_sent, self.total_received, self.total_beacons, self.total_acknowledgements, self.total_retry = parse_data()
        self.total_information_packets = self.total_sent - (self.total_beacons + self.total_acknowledgements)
        # self.total_information_packets_lost = 7  # Set to 7 as per your requirement

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text='     Summary     ')
        self.setup_summary(self.summary_tab)

        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text='     Detailed Table      ')
        self.setup_widgets(self.main_tab)



    def setup_widgets(self, parent):
        self.tree = ttk.Treeview(parent, columns=[col for col in self.df.columns], show='headings')
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.populate_table()
        self.create_filters()

    def setup_summary(self, parent):
        # summary_frame = tk.Frame(parent)  # Create a Frame to hold the summary labels
        # summary_frame.pack(pady=20, expand=True)  # Center this frame vertically in the parent

        summary_frame = tk.Frame(parent, background='light green')  # Ensure the frame has a light green background
        summary_frame.pack(pady=20, expand=True)

        # Now place all labels within this frame, left-aligned
        tk.Label(summary_frame, text=f"Total Packets Sent: {self.total_sent}", anchor="w", background= 'light green', font=("Arial", 16)).pack(
            fill='x', padx=20, pady=5)
        tk.Label(summary_frame, text=f"Total Packets Received: {self.total_received}", background= 'light green', anchor="w",
                 font=("Arial", 16)).pack(fill='x', padx=20, pady=5)
        tk.Label(summary_frame, text=f"Total Beacons: {self.total_beacons}", anchor="w", background= 'light green', font=("Arial", 16)).pack(
            fill='x', padx=20, pady=5)
        tk.Label(summary_frame, text=f"Total Acknowledgements: {self.total_acknowledgements}", anchor="w", background= 'light green',
                 font=("Arial", 16)).pack(fill='x', padx=20, pady=5)
        tk.Label(summary_frame, text=f"Total Information Packets: {self.total_information_packets}", anchor="w", background= 'light green',
                 font=("Arial", 16)).pack(fill='x', padx=20, pady=5)
        tk.Label(summary_frame, text=f"Total Packets Lost: {self.total_retry}", anchor="w", background= 'light green', font=("Arial", 16)).pack(
            fill='x', padx=20, pady=5)
    def create_filters(self):

        filter_frame = ttk.Frame(self.main_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        # The rest of the filter setup code goes here, unchanged
        # Source Node Filter
        ttk.Label(filter_frame, text="Source Node:").pack(side=tk.LEFT)
        self.source_node_entry = ttk.Entry(filter_frame, width=10)
        self.source_node_entry.pack(side=tk.LEFT, padx=5)

        # Destination Node Filter
        ttk.Label(filter_frame, text="Destination Node:").pack(side=tk.LEFT)
        self.destination_node_entry = ttk.Entry(filter_frame, width=10)
        self.destination_node_entry.pack(side=tk.LEFT, padx=5)

        # Successful Filter
        ttk.Label(filter_frame, text="Successful:").pack(side=tk.LEFT)
        self.successful_var = tk.StringVar()
        successful_combo = ttk.Combobox(filter_frame, textvariable=self.successful_var, values=['True', 'False'])
        successful_combo.pack(side=tk.LEFT, padx=5)

        # Intermediate Nodes Filter
        ttk.Label(filter_frame, text="Intermediate Nodes (comma-separated):").pack(side=tk.LEFT)
        self.intermediate_nodes_entry = ttk.Entry(filter_frame, width=10)
        self.intermediate_nodes_entry.pack(side=tk.LEFT, padx=5)

        # Packet Type Filter
        ttk.Label(filter_frame, text="Packet Type:").pack(side=tk.LEFT)
        self.packet_type_var = tk.StringVar()
        packet_type_combo = ttk.Combobox(filter_frame, textvariable=self.packet_type_var,
                                         values=['Information', 'Beacon', 'Acknowledgement'])
        packet_type_combo.pack(side=tk.LEFT, padx=5)

        # Filter Button
        filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filters)
        filter_button.pack(side=tk.LEFT, padx=10)

        # Clear Filter Button
        clear_button = ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters)
        clear_button.pack(side=tk.LEFT, padx=10)



    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.df.itertuples(index=False):
            self.tree.insert('', 'end', values=row)

    def apply_filters(self):
        filtered_df = self.df
        if self.source_node_entry.get():
            filtered_df = filtered_df[filtered_df['Source Node'] == int(self.source_node_entry.get())]
        if self.destination_node_entry.get():
            filtered_df = filtered_df[filtered_df['Destination Node'] == int(self.destination_node_entry.get())]
        if self.successful_var.get():
            filtered_df = filtered_df[filtered_df['Successful'] == (self.successful_var.get() == 'True')]
        if self.intermediate_nodes_entry.get():
            nodes = list(map(int, self.intermediate_nodes_entry.get().split(',')))
            filtered_df = filtered_df[filtered_df['Intermediate Nodes'].apply(lambda x: any(item in nodes for item in x))]
        if self.packet_type_var.get():
            filtered_df = filtered_df[filtered_df['Packet Type'] == self.packet_type_var.get()]

        self.tree.delete(*self.tree.get_children())
        for row in filtered_df.itertuples(index=False):
            self.tree.insert('', 'end', values=row)

    def clear_filters(self):
        self.source_node_entry.delete(0, tk.END)
        self.destination_node_entry.delete(0, tk.END)
        self.successful_var.set('')
        self.intermediate_nodes_entry.delete(0, tk.END)
        self.packet_type_var.set('')
        self.populate_table()

if __name__ == "__main__":
    app = App()
    app.mainloop()

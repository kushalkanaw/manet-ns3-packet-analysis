# MANET Packet Analysis and Visualization using NS3

NS3-based MANET trace file analyzer with Python GUI for packet-level visualization and filtering.

## Overview
This project analyzes NS3 trace (.tr) files generated from MANET simulations and provides structured visualization of packet-level data using a Python-based GUI.

## Features
- Parses NS3 trace (.tr) files
- Displays packet-level details:
  - Time of transmission
  - Source and destination nodes
  - Packet type (Information, Beacon, Acknowledgment)
  - Delivery status
  - Intermediate nodes
- Provides filtering based on:
  - Source node
  - Destination node
  - Packet type
  - Delivery status
- GUI-based visualization for easier analysis

## Technologies Used
- Python (Tkinter)
- NS3 Network Simulator
- NetAnim
- FlowMonitor
- TraceMetrics

## How to Run
1. Place the `.tr` file in the project directory
2. Run the Python script (`trFileAnalyzer.py`) using a Python environment

## Purpose
This tool improves the analysis of NS3 trace data by providing a structured and interactive interface, reducing manual effort, and improving data interpretation.

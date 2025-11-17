"""
Advanced DC Motor Analysis Laboratory
Complete solution for Example 30.38 with comprehensive GUI and multi-physics simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import odeint, solve_ivp
import math
from datetime import datetime

class DCMotorLab:
    """Comprehensive DC Motor Analysis Laboratory"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced DC Motor Analysis Laboratory")
        self.root.geometry("1400x900")

        # Simulation state
        self.simulation_running = False
        self.simulation_time = 0
        self.simulation_data = {
            'time': [],
            'speed': [],
            'torque': [],
            'current': [],
            'voltage': [],
            'efficiency': [],
            'temperature': [],
            'power': []
        }

        # Motor parameters (Example 30.38)
        self.motor_params = {
            'poles': tk.IntVar(value=4),
            'voltage': tk.DoubleVar(value=250.0),
            'current': tk.DoubleVar(value=20.0),
            'speed': tk.DoubleVar(value=900.0),
            'ra': tk.DoubleVar(value=0.1),
            'rse_per_coil': tk.DoubleVar(value=0.025),
            'divertor_r': tk.DoubleVar(value=0.2),
            'inertia': tk.DoubleVar(value=0.5),
            'friction': tk.DoubleVar(value=0.01),
            'temp_ambient': tk.DoubleVar(value=25.0),
            'thermal_resistance': tk.DoubleVar(value=2.0),
            'thermal_capacitance': tk.DoubleVar(value=100.0)
        }

        # Control parameters
        self.control_params = {
            'control_mode': tk.StringVar(value='voltage'),
            'pid_kp': tk.DoubleVar(value=1.0),
            'pid_ki': tk.DoubleVar(value=0.1),
            'pid_kd': tk.DoubleVar(value=0.05),
            'speed_reference': tk.DoubleVar(value=900.0),
            'load_torque': tk.DoubleVar(value=0.0)
        }

        # Economic parameters
        self.economic_params = {
            'electricity_cost': tk.DoubleVar(value=0.12),
            'operating_hours': tk.DoubleVar(value=8760.0),
            'motor_cost': tk.DoubleVar(value=5000.0),
            'maintenance_cost': tk.DoubleVar(value=500.0),
            'lifetime_years': tk.DoubleVar(value=15.0)
        }

        # Solver settings
        self.solver_method = tk.StringVar(value='RK45')
        self.time_step = tk.DoubleVar(value=0.001)
        self.simulation_duration = tk.DoubleVar(value=5.0)

        # Results storage
        self.results_example_30_38 = {}

        # Setup UI
        self.setup_ui()

        # Solve Example 30.38 on startup
        self.solve_example_30_38()

    def setup_ui(self):
        """Setup the complete user interface"""

        # Main container with grid weight configuration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_main_tab()
        self.create_control_tab()
        self.create_multiphysics_tab()
        self.create_economic_tab()
        self.create_results_tab()

        # Control buttons at bottom
        self.create_control_buttons()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_main_tab(self):
        """Main tab with motor parameters and basic simulation"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text='Main Parameters')

        # Configure grid
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)

        # Left panel - Parameters
        left_panel = ttk.LabelFrame(main_frame, text='Motor Parameters (Example 30.38)')
        left_panel.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Motor parameters input
        params = [
            ('Number of Poles:', self.motor_params['poles'], 2, 10),
            ('Voltage (V):', self.motor_params['voltage'], 0, 500),
            ('Current (A):', self.motor_params['current'], 0, 100),
            ('Speed (RPM):', self.motor_params['speed'], 0, 3000),
            ('Armature Resistance Ra (Ω):', self.motor_params['ra'], 0, 10),
            ('Field Resistance per Coil (Ω):', self.motor_params['rse_per_coil'], 0, 1),
            ('Divertor Resistance (Ω):', self.motor_params['divertor_r'], 0, 10),
            ('Rotor Inertia (kg·m²):', self.motor_params['inertia'], 0.01, 10),
            ('Friction Coefficient:', self.motor_params['friction'], 0, 1),
            ('Ambient Temperature (°C):', self.motor_params['temp_ambient'], 0, 50),
            ('Thermal Resistance (°C/W):', self.motor_params['thermal_resistance'], 0.1, 10),
            ('Thermal Capacitance (J/°C):', self.motor_params['thermal_capacitance'], 10, 1000)
        ]

        for i, (label, var, min_val, max_val) in enumerate(params):
            ttk.Label(left_panel, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)

            entry = ttk.Entry(left_panel, textvariable=var, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)

            slider = ttk.Scale(left_panel, from_=min_val, to=max_val, variable=var,
                             orient='horizontal', length=200)
            slider.grid(row=i, column=2, padx=5, pady=2)

        # Right panel - Visualization
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure for main visualization
        self.main_fig = Figure(figsize=(8, 6), dpi=80)
        self.main_canvas = FigureCanvasTkAgg(self.main_fig, right_panel)
        self.main_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Create subplots
        self.main_axes = {
            'speed': self.main_fig.add_subplot(2, 2, 1),
            'current': self.main_fig.add_subplot(2, 2, 2),
            'torque': self.main_fig.add_subplot(2, 2, 3),
            'power': self.main_fig.add_subplot(2, 2, 4)
        }

        self.main_fig.tight_layout()

    def create_control_tab(self):
        """Control tab with advanced control features"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text='Advanced Control')

        control_frame.grid_rowconfigure(1, weight=1)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=2)

        # Left panel - Control parameters
        left_panel = ttk.LabelFrame(control_frame, text='Control Settings')
        left_panel.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        # Control mode selection
        ttk.Label(left_panel, text='Control Mode:').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        control_modes = ['voltage', 'current', 'speed', 'torque']
        mode_combo = ttk.Combobox(left_panel, textvariable=self.control_params['control_mode'],
                                  values=control_modes, state='readonly', width=15)
        mode_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        # PID parameters
        pid_params = [
            ('PID Kp (Proportional):', self.control_params['pid_kp'], 0, 10),
            ('PID Ki (Integral):', self.control_params['pid_ki'], 0, 5),
            ('PID Kd (Derivative):', self.control_params['pid_kd'], 0, 1),
            ('Speed Reference (RPM):', self.control_params['speed_reference'], 0, 3000),
            ('Load Torque (N·m):', self.control_params['load_torque'], 0, 100)
        ]

        for i, (label, var, min_val, max_val) in enumerate(pid_params, start=1):
            ttk.Label(left_panel, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            ttk.Entry(left_panel, textvariable=var, width=10).grid(row=i, column=1, padx=5, pady=2)
            ttk.Scale(left_panel, from_=min_val, to=max_val, variable=var,
                     orient='horizontal', length=200).grid(row=i, column=2, padx=5, pady=2)

        # Solver settings
        ttk.Label(left_panel, text='ODE Solver:').grid(row=10, column=0, sticky='w', padx=5, pady=5)
        solver_combo = ttk.Combobox(left_panel, textvariable=self.solver_method,
                                    values=['RK45', 'Euler', 'RK23', 'DOP853'],
                                    state='readonly', width=15)
        solver_combo.grid(row=10, column=1, columnspan=2, padx=5, pady=5)

        ttk.Label(left_panel, text='Time Step (s):').grid(row=11, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(left_panel, textvariable=self.time_step, width=10).grid(row=11, column=1, padx=5, pady=2)

        ttk.Label(left_panel, text='Duration (s):').grid(row=12, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(left_panel, textvariable=self.simulation_duration, width=10).grid(row=12, column=1, padx=5, pady=2)

        # Right panel - Control visualization
        right_panel = ttk.Frame(control_frame)
        right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self.control_fig = Figure(figsize=(8, 6), dpi=80)
        self.control_canvas = FigureCanvasTkAgg(self.control_fig, right_panel)
        self.control_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        self.control_axes = {
            'response': self.control_fig.add_subplot(2, 1, 1),
            'error': self.control_fig.add_subplot(2, 1, 2)
        }

        self.control_fig.tight_layout()

    def create_multiphysics_tab(self):
        """Multi-physics simulation tab"""
        mp_frame = ttk.Frame(self.notebook)
        self.notebook.add(mp_frame, text='Multi-Physics')

        mp_frame.grid_rowconfigure(0, weight=1)
        mp_frame.grid_columnconfigure(0, weight=1)

        # Create sub-notebook for different physics
        mp_notebook = ttk.Notebook(mp_frame)
        mp_notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Electromagnetic tab
        em_frame = ttk.Frame(mp_notebook)
        mp_notebook.add(em_frame, text='Electromagnetic')
        em_frame.grid_rowconfigure(0, weight=1)
        em_frame.grid_columnconfigure(0, weight=1)

        self.em_fig = Figure(figsize=(10, 6), dpi=80)
        em_canvas = FigureCanvasTkAgg(self.em_fig, em_frame)
        em_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        self.em_axes = {
            'flux': self.em_fig.add_subplot(2, 2, 1),
            'voltage': self.em_fig.add_subplot(2, 2, 2),
            'current': self.em_fig.add_subplot(2, 2, 3),
            'emf': self.em_fig.add_subplot(2, 2, 4)
        }
        self.em_fig.tight_layout()

        # Thermal tab
        thermal_frame = ttk.Frame(mp_notebook)
        mp_notebook.add(thermal_frame, text='Thermal')
        thermal_frame.grid_rowconfigure(0, weight=1)
        thermal_frame.grid_columnconfigure(0, weight=1)

        self.thermal_fig = Figure(figsize=(10, 6), dpi=80)
        thermal_canvas = FigureCanvasTkAgg(self.thermal_fig, thermal_frame)
        thermal_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        self.thermal_axes = {
            'temp': self.thermal_fig.add_subplot(2, 2, 1),
            'losses': self.thermal_fig.add_subplot(2, 2, 2),
            'derating': self.thermal_fig.add_subplot(2, 2, 3),
            'distribution': self.thermal_fig.add_subplot(2, 2, 4)
        }
        self.thermal_fig.tight_layout()

        # Mechanical tab
        mech_frame = ttk.Frame(mp_notebook)
        mp_notebook.add(mech_frame, text='Mechanical')
        mech_frame.grid_rowconfigure(0, weight=1)
        mech_frame.grid_columnconfigure(0, weight=1)

        self.mech_fig = Figure(figsize=(10, 6), dpi=80)
        mech_canvas = FigureCanvasTkAgg(self.mech_fig, mech_frame)
        mech_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        self.mech_axes = {
            'torque': self.mech_fig.add_subplot(2, 2, 1),
            'speed': self.mech_fig.add_subplot(2, 2, 2),
            'stress': self.mech_fig.add_subplot(2, 2, 3),
            'vibration': self.mech_fig.add_subplot(2, 2, 4)
        }
        self.mech_fig.tight_layout()

    def create_economic_tab(self):
        """Economic analysis tab"""
        econ_frame = ttk.Frame(self.notebook)
        self.notebook.add(econ_frame, text='Economic Analysis')

        econ_frame.grid_rowconfigure(1, weight=1)
        econ_frame.grid_columnconfigure(0, weight=1)
        econ_frame.grid_columnconfigure(1, weight=2)

        # Left panel - Economic parameters
        left_panel = ttk.LabelFrame(econ_frame, text='Economic Parameters')
        left_panel.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=5, pady=5)

        econ_params = [
            ('Electricity Cost ($/kWh):', self.economic_params['electricity_cost']),
            ('Operating Hours (h/year):', self.economic_params['operating_hours']),
            ('Motor Cost ($):', self.economic_params['motor_cost']),
            ('Maintenance Cost ($/year):', self.economic_params['maintenance_cost']),
            ('Lifetime (years):', self.economic_params['lifetime_years'])
        ]

        for i, (label, var) in enumerate(econ_params):
            ttk.Label(left_panel, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            ttk.Entry(left_panel, textvariable=var, width=15).grid(row=i, column=1, padx=5, pady=5)

        ttk.Button(left_panel, text='Calculate Economics',
                  command=self.calculate_economics).grid(row=len(econ_params), column=0,
                                                         columnspan=2, pady=10)

        # Results display
        self.econ_results = scrolledtext.ScrolledText(left_panel, width=40, height=15)
        self.econ_results.grid(row=len(econ_params)+1, column=0, columnspan=2, padx=5, pady=5)

        # Right panel - Economic visualization
        right_panel = ttk.Frame(econ_frame)
        right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=5, pady=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self.econ_fig = Figure(figsize=(8, 6), dpi=80)
        econ_canvas = FigureCanvasTkAgg(self.econ_fig, right_panel)
        econ_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        self.econ_axes = {
            'costs': self.econ_fig.add_subplot(2, 2, 1),
            'payback': self.econ_fig.add_subplot(2, 2, 2),
            'efficiency': self.econ_fig.add_subplot(2, 2, 3),
            'savings': self.econ_fig.add_subplot(2, 2, 4)
        }
        self.econ_fig.tight_layout()

    def create_results_tab(self):
        """Results and analysis tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text='Results & Analysis')

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # Create text widget for results
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                      font=('Courier', 10))
        self.results_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Add export button
        ttk.Button(results_frame, text='Export Results',
                  command=self.export_results).grid(row=1, column=0, pady=5)

    def create_control_buttons(self):
        """Create control buttons at bottom"""
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        ttk.Button(button_frame, text='Start Simulation',
                  command=self.start_simulation).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Stop Simulation',
                  command=self.stop_simulation).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Reset',
                  command=self.reset_simulation).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Solve Example 30.38',
                  command=self.solve_example_30_38).pack(side='left', padx=5)

        # Status label
        self.status_label = ttk.Label(button_frame, text='Ready', relief='sunken')
        self.status_label.pack(side='right', padx=5, fill='x', expand=True)

    def solve_example_30_38(self):
        """Solve Example 30.38 - DC Series Motor Speed Calculation"""
        try:
            # Get parameters
            V = self.motor_params['voltage'].get()
            Ia1 = self.motor_params['current'].get()
            N1 = self.motor_params['speed'].get()
            Ra = self.motor_params['ra'].get()
            Rse_per_coil = self.motor_params['rse_per_coil'].get()
            Rd = self.motor_params['divertor_r'].get()
            P = self.motor_params['poles'].get()

            # For 4-pole motor with series field, total field resistance
            # Assuming 4 coils in series (one per pole)
            Rse1 = 4 * Rse_per_coil  # Total series field resistance

            # Original condition
            E1 = V - Ia1 * (Ra + Rse1)

            # For series motor: E = k*phi*N and phi is proportional to Ia (unsaturated)
            # E = k1*Ia*N
            k1 = E1 / (Ia1 * N1)

            # Torque: T = k2*phi*Ia = k2*Ia^2 for series motor
            # T1 = k2 * Ia1^2

            results = f"""
{'='*80}
SOLUTION TO EXAMPLE 30.38 - DC SERIES MOTOR SPEED CALCULATION
{'='*80}

GIVEN DATA:
-----------
Motor Type: 4-pole DC Series Motor
Supply Voltage: {V} V
Armature Current: {Ia1} A
Speed: {N1} RPM
Armature Resistance (Ra): {Ra} Ω
Field Resistance per coil: {Rse_per_coil} Ω
Total Series Field Resistance (Rse): {Rse1} Ω
Divertor Resistance: {Rd} Ω

ORIGINAL CONDITION:
-------------------
Back EMF (E1) = V - Ia(Ra + Rse)
E1 = {V} - {Ia1} × ({Ra} + {Rse1})
E1 = {V} - {Ia1} × {Ra + Rse1}
E1 = {E1:.3f} V

Machine Constant (k): {k1:.6f}

Torque (T1) ∝ Φ × Ia ∝ Ia² (for series motor in unsaturated region)
T1 ∝ {Ia1}² = {Ia1**2:.2f}

{'='*80}
CASE (i): DIVERTOR OF {Rd} Ω IN PARALLEL WITH SERIES FIELD
{'='*80}
"""

            # Case (i): Divertor in parallel with series field
            # Equivalent resistance of parallel combination
            Rse_eq = (Rse1 * Rd) / (Rse1 + Rd)

            # For same torque: T2 = T1
            # Since T ∝ Φ × Ia and Φ ∝ If (field current)
            # With divertor: If2 = Ia2 × Rse_eq/(Rse_eq + Rd) = Ia2 × Rse1/(Rse1 + Rd)
            # Actually, with divertor in parallel, If2 = Ia2 × Rd/(Rse1 + Rd)

            # Field current with divertor
            # If = Ia × Rd/(Rse + Rd)

            # For same torque: Φ1 × Ia1 = Φ2 × Ia2
            # Φ1 = k × If1 = k × Ia1 (no divertor)
            # Φ2 = k × If2 = k × Ia2 × Rd/(Rse1 + Rd)

            # Therefore: Ia1² = Ia2 × (Ia2 × Rd/(Rse1 + Rd))
            # Ia1² = Ia2² × Rd/(Rse1 + Rd)
            # Ia2² = Ia1² × (Rse1 + Rd)/Rd
            # Ia2 = Ia1 × sqrt((Rse1 + Rd)/Rd)

            Ia2 = Ia1 * np.sqrt((Rse1 + Rd) / Rd)
            If2 = Ia2 * Rd / (Rse1 + Rd)

            E2 = V - Ia2 * (Ra + Rse_eq)

            # E1/N1 = k*Φ1 and E2/N2 = k*Φ2
            # E1/N1 = k*Ia1 and E2/N2 = k*If2
            # N2 = N1 × (E2/E1) × (Ia1/If2)

            N2 = N1 * (E2 / E1) * (Ia1 / If2)

            results += f"""
With Divertor in Parallel:
--------------------------
Equivalent Field Resistance: Rse_eq = (Rse × Rd)/(Rse + Rd)
Rse_eq = ({Rse1} × {Rd})/({Rse1} + {Rd}) = {Rse_eq:.4f} Ω

For same torque: Φ1 × Ia1 = Φ2 × Ia2
Since Φ ∝ If (field current):

Field current ratio with divertor: If2/Ia2 = Rd/(Rse + Rd) = {Rd/(Rse1 + Rd):.4f}

For same torque:
Ia1² = Ia2² × [Rd/(Rse + Rd)]
Ia2 = Ia1 × √[(Rse + Rd)/Rd]
Ia2 = {Ia1} × √[({Rse1} + {Rd})/{Rd}]
Ia2 = {Ia2:.3f} A

Field Current: If2 = {If2:.3f} A

Back EMF: E2 = V - Ia2(Ra + Rse_eq)
E2 = {V} - {Ia2:.3f} × ({Ra} + {Rse_eq:.4f})
E2 = {E2:.3f} V

Speed Calculation:
E1/N1 = k×Φ1 = k×Ia1
E2/N2 = k×Φ2 = k×If2

N2 = N1 × (E2/E1) × (Ia1/If2)
N2 = {N1} × ({E2:.3f}/{E1:.3f}) × ({Ia1}/{If2:.3f})
N2 = {N2:.2f} RPM

Speed Increase = {N2 - N1:.2f} RPM ({((N2-N1)/N1*100):.2f}%)

{'='*80}
CASE (ii): FIELD COILS IN TWO SERIES-PARALLEL GROUPS
{'='*80}
"""

            # Case (ii): Field coils rearranged in series-parallel
            # Original: 4 coils in series = 4 × Rse_per_coil
            # New: 2 groups of 2 coils in series, groups in parallel
            # Each group: 2 × Rse_per_coil
            # Parallel combination: (2×Rse_per_coil)/2 = Rse_per_coil

            Rse3 = Rse_per_coil  # Equivalent resistance in series-parallel

            # Each parallel branch carries Ia/2
            # Total MMF = 2 coils × (Ia/2) × 2 branches = 2 × Ia
            # Original MMF = 4 coils × Ia
            # MMF ratio = 2×Ia / (4×Ia) = 0.5

            # For same torque: Φ1 × Ia1 = Φ3 × Ia3
            # Φ ∝ MMF ∝ (number of series coils) × (current per branch)
            # Φ3/Φ1 = (2 × Ia3/2) / (4 × Ia1) × (Ia3/Ia1) = Ia3²/(2×Ia1²)

            # Actually, for series-parallel:
            # Φ3 ∝ turns × current per turn
            # With 2 coils in series per branch, 2 branches in parallel:
            # Φ3 ∝ 2 × (Ia3/2) = Ia3 (but only through 2 coils)
            # Original: Φ1 ∝ 4 × Ia1

            # More accurately:
            # Φ ∝ NI (ampere-turns)
            # Original: 4 coils × Ia1 = 4×Ia1 AT
            # Series-Parallel: 2 coils × Ia3 + 2 coils × Ia3 = 4×Ia3 AT
            # Wait, that's not right either.

            # Correct analysis:
            # Series-parallel: 2 parallel branches, each with 2 coils in series
            # Each branch carries Ia/2
            # Each coil in branch: Ia/2
            # Total AT = 4 coils × (Ia/2) = 2×Ia
            # Original AT = 4 coils × Ia = 4×Ia

            # So Φ3/Φ1 = 2×Ia3 / (4×Ia1) = Ia3/(2×Ia1)

            # For same torque: Φ1×Ia1 = Φ3×Ia3
            # (4×Ia1)×Ia1 = (2×Ia3)×Ia3
            # 4×Ia1² = 2×Ia3²
            # Ia3² = 2×Ia1²
            # Ia3 = Ia1×√2

            Ia3 = Ia1 * np.sqrt(2)
            If3_per_branch = Ia3 / 2  # Current per branch

            # Flux is proportional to AT per parallel path
            # Φ3 ∝ 2 × (Ia3/2) = Ia3
            # Φ1 ∝ Ia1
            # But there are 2 parallel paths vs 1 path

            # Actually for DC machine, flux depends on total MMF
            # With series-parallel, effective turns are halved
            # Φ3 = k × (4/2) × (Ia3/2) = k × Ia3
            # Φ1 = k × 4 × Ia1
            # So Φ3/Φ1 = Ia3/(4×Ia1)

            # For same torque:
            # T ∝ Φ × Ia
            # [k×4×Ia1] × Ia1 = [k×Ia3] × Ia3
            # 4×Ia1² = Ia3²
            # Ia3 = 2×Ia1

            Ia3 = 2 * Ia1

            E3 = V - Ia3 * (Ra + Rse3)

            # Effective flux for series-parallel
            # Φ3 ∝ Ia3 (but through half the coils in series)
            # Φ1 ∝ Ia1 (through all coils)
            # Actually Φ3/Φ1 = (Ia3/2)/Ia1 since effective turns halved

            # N3/N1 = (E3/E1) × (Φ1/Φ3)
            # With series-parallel: Φ ∝ (effective turns) × I = 2 × (Ia/2) = Ia
            # Original: Φ ∝ 4 × Ia
            # Φ3/Φ1 = Ia3/(4×Ia1) = (2×Ia1)/(4×Ia1) = 0.5

            phi_ratio = 0.5
            N3 = N1 * (E3 / E1) / phi_ratio

            results += f"""
Field Coils Rearrangement:
--------------------------
Original Configuration: 4 coils in series
New Configuration: 2 parallel groups, each with 2 coils in series

Each group resistance: 2 × {Rse_per_coil} = {2*Rse_per_coil} Ω
Equivalent resistance: Rse_eq = {2*Rse_per_coil}/2 = {Rse3} Ω

Current distribution: Each parallel branch carries Ia/2

Ampere-Turns Analysis:
Original: 4 coils × Ia1 = {4*Ia1:.2f} AT
Series-Parallel: 4 coils × (Ia3/2) = 2×Ia3 AT

For same torque: Φ1 × Ia1 = Φ3 × Ia3
Where Φ ∝ AT (ampere-turns)

(4×Ia1) × Ia1 = Ia3 × Ia3
4×Ia1² = Ia3²
Ia3 = 2×Ia1 = {Ia3:.3f} A

Current per branch: {Ia3/2:.3f} A

Back EMF: E3 = V - Ia3(Ra + Rse_eq)
E3 = {V} - {Ia3:.3f} × ({Ra} + {Rse3})
E3 = {E3:.3f} V

Flux ratio: Φ3/Φ1 = (2×Ia3)/(4×Ia1) = {phi_ratio:.3f}

Speed Calculation:
N3 = N1 × (E3/E1) × (Φ1/Φ3)
N3 = {N1} × ({E3:.3f}/{E1:.3f}) × (1/{phi_ratio})
N3 = {N3:.2f} RPM

Speed Increase = {N3 - N1:.2f} RPM ({((N3-N1)/N1*100):.2f}%)

{'='*80}
SUMMARY OF RESULTS
{'='*80}

Original Condition:
  Speed: {N1} RPM
  Current: {Ia1} A
  Back EMF: {E1:.3f} V

Case (i) - With {Rd} Ω Divertor:
  Speed: {N2:.2f} RPM (↑{((N2-N1)/N1*100):.2f}%)
  Current: {Ia2:.3f} A
  Back EMF: {E2:.3f} V

Case (ii) - Series-Parallel Field:
  Speed: {N3:.2f} RPM (↑{((N3-N1)/N1*100):.2f}%)
  Current: {Ia3:.3f} A
  Back EMF: {E3:.3f} V

{'='*80}
VERIFICATION AND INSIGHTS
{'='*80}

1. Power Balance:
   Original: P1 = {V*Ia1:.2f} W
   Case (i): P2 = {V*Ia2:.2f} W
   Case (ii): P3 = {V*Ia3:.2f} W

2. Efficiency Considerations:
   Higher speed with same torque indicates reduced flux, requiring higher current.
   This increases copper losses but maintains mechanical output.

3. Practical Applications:
   - Case (i): Divertor control is useful for speed control above base speed
   - Case (ii): Series-parallel provides different speed-torque characteristic

4. Assumptions:
   - Unsaturated magnetic circuit (Φ ∝ I)
   - Constant supply voltage
   - Neglecting armature reaction and voltage drops
   - Constant load torque

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
"""

            # Store results
            self.results_example_30_38 = {
                'original': {'speed': N1, 'current': Ia1, 'emf': E1},
                'case_i': {'speed': N2, 'current': Ia2, 'emf': E2},
                'case_ii': {'speed': N3, 'current': Ia3, 'emf': E3}
            }

            # Display results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results)

            self.status_label.config(text='Example 30.38 solved successfully!')

            # Update visualizations
            self.plot_example_results()

        except Exception as e:
            messagebox.showerror('Error', f'Error solving Example 30.38:\n{str(e)}')

    def plot_example_results(self):
        """Plot results from Example 30.38"""
        if not self.results_example_30_38:
            return

        # Clear previous plots
        for ax in self.main_axes.values():
            ax.clear()

        # Extract data
        cases = ['Original', 'Case (i)\nDivertor', 'Case (ii)\nSeries-Parallel']
        speeds = [
            self.results_example_30_38['original']['speed'],
            self.results_example_30_38['case_i']['speed'],
            self.results_example_30_38['case_ii']['speed']
        ]
        currents = [
            self.results_example_30_38['original']['current'],
            self.results_example_30_38['case_i']['current'],
            self.results_example_30_38['case_ii']['current']
        ]
        emfs = [
            self.results_example_30_38['original']['emf'],
            self.results_example_30_38['case_i']['emf'],
            self.results_example_30_38['case_ii']['emf']
        ]

        V = self.motor_params['voltage'].get()
        powers = [V * I for I in currents]

        # Speed comparison
        self.main_axes['speed'].bar(cases, speeds, color=['blue', 'green', 'orange'])
        self.main_axes['speed'].set_ylabel('Speed (RPM)')
        self.main_axes['speed'].set_title('Speed Comparison')
        self.main_axes['speed'].grid(True, alpha=0.3)

        # Current comparison
        self.main_axes['current'].bar(cases, currents, color=['blue', 'green', 'orange'])
        self.main_axes['current'].set_ylabel('Current (A)')
        self.main_axes['current'].set_title('Armature Current')
        self.main_axes['current'].grid(True, alpha=0.3)

        # EMF comparison
        self.main_axes['torque'].bar(cases, emfs, color=['blue', 'green', 'orange'])
        self.main_axes['torque'].set_ylabel('Back EMF (V)')
        self.main_axes['torque'].set_title('Back EMF Comparison')
        self.main_axes['torque'].grid(True, alpha=0.3)

        # Power comparison
        self.main_axes['power'].bar(cases, powers, color=['blue', 'green', 'orange'])
        self.main_axes['power'].set_ylabel('Power (W)')
        self.main_axes['power'].set_title('Input Power')
        self.main_axes['power'].grid(True, alpha=0.3)

        self.main_fig.tight_layout()
        self.main_canvas.draw()

    def dc_motor_ode_rk45(self, t, y):
        """ODE system for DC motor using RK45 method"""
        omega, theta, i_a, temp = y

        # Get parameters
        V = self.motor_params['voltage'].get()
        Ra = self.motor_params['ra'].get()
        Rse = 4 * self.motor_params['rse_per_coil'].get()
        J = self.motor_params['inertia'].get()
        B = self.motor_params['friction'].get()
        T_load = self.control_params['load_torque'].get()

        # Thermal parameters
        R_th = self.motor_params['thermal_resistance'].get()
        C_th = self.motor_params['thermal_capacitance'].get()
        T_amb = self.motor_params['temp_ambient'].get()

        # Motor constants
        k_e = 0.5  # Back EMF constant
        k_t = 0.5  # Torque constant

        # Voltage equation: V = E + Ia*(Ra + Rse)
        # E = k_e * omega
        E = k_e * omega

        # Current derivative
        L_a = 0.05  # Armature inductance (H)
        di_a_dt = (V - E - i_a * (Ra + Rse)) / L_a

        # Torque equation
        T_em = k_t * i_a  # Electromagnetic torque

        # Mechanical equation
        domega_dt = (T_em - B * omega - T_load) / J
        dtheta_dt = omega

        # Thermal equation
        P_loss = i_a**2 * (Ra + Rse)  # Copper losses
        dtemp_dt = (P_loss - (temp - T_amb) / R_th) / C_th

        return [domega_dt, dtheta_dt, di_a_dt, dtemp_dt]

    def dc_motor_ode_euler(self, y, t, dt):
        """ODE system for DC motor using Euler method"""
        dydt = self.dc_motor_ode_rk45(t, y)
        return [y[i] + dydt[i] * dt for i in range(len(y))]

    def start_simulation(self):
        """Start dynamic simulation"""
        try:
            self.simulation_running = True
            self.status_label.config(text='Simulation running...')

            # Initial conditions
            N0 = self.motor_params['speed'].get()
            omega0 = N0 * 2 * np.pi / 60  # Convert RPM to rad/s
            theta0 = 0
            i_a0 = self.motor_params['current'].get()
            temp0 = self.motor_params['temp_ambient'].get()

            y0 = [omega0, theta0, i_a0, temp0]

            # Time span
            duration = self.simulation_duration.get()
            dt = self.time_step.get()
            t_span = (0, duration)
            t_eval = np.arange(0, duration, dt)

            # Solve ODE
            method = self.solver_method.get()

            if method == 'Euler':
                # Euler method
                t = t_eval
                y = np.zeros((len(t), len(y0)))
                y[0] = y0

                for i in range(1, len(t)):
                    y[i] = self.dc_motor_ode_euler(y[i-1], t[i-1], dt)

                omega = y[:, 0]
                i_a = y[:, 2]
                temp = y[:, 3]
            else:
                # RK45 or other scipy methods
                sol = solve_ivp(self.dc_motor_ode_rk45, t_span, y0, method=method,
                              t_eval=t_eval, max_step=dt)
                t = sol.t
                omega = sol.y[0]
                i_a = sol.y[2]
                temp = sol.y[3]

            # Convert to engineering units
            speed = omega * 60 / (2 * np.pi)  # rad/s to RPM

            # Calculate other quantities
            V = self.motor_params['voltage'].get()
            Ra = self.motor_params['ra'].get()
            Rse = 4 * self.motor_params['rse_per_coil'].get()

            k_e = 0.5
            k_t = 0.5

            emf = k_e * omega
            torque = k_t * i_a
            voltage = V * np.ones_like(t)
            power_in = voltage * i_a
            power_out = torque * omega
            efficiency = np.where(power_in > 0, (power_out / power_in) * 100, 0)

            # Store simulation data
            self.simulation_data = {
                'time': t,
                'speed': speed,
                'torque': torque,
                'current': i_a,
                'voltage': voltage,
                'efficiency': efficiency,
                'temperature': temp,
                'power': power_in,
                'emf': emf,
                'power_out': power_out
            }

            # Update all visualizations
            self.update_all_plots()

            self.simulation_running = False
            self.status_label.config(text=f'Simulation completed using {method} method')

        except Exception as e:
            self.simulation_running = False
            self.status_label.config(text='Simulation failed')
            messagebox.showerror('Simulation Error', f'Error during simulation:\n{str(e)}')

    def stop_simulation(self):
        """Stop running simulation"""
        self.simulation_running = False
        self.status_label.config(text='Simulation stopped')

    def reset_simulation(self):
        """Reset simulation"""
        self.simulation_running = False
        self.simulation_time = 0
        self.simulation_data = {
            'time': [],
            'speed': [],
            'torque': [],
            'current': [],
            'voltage': [],
            'efficiency': [],
            'temperature': [],
            'power': []
        }

        # Clear all plots
        for axes_dict in [self.main_axes, self.control_axes, self.em_axes,
                         self.thermal_axes, self.mech_axes, self.econ_axes]:
            for ax in axes_dict.values():
                ax.clear()

        self.main_canvas.draw()
        self.control_canvas.draw()

        self.status_label.config(text='Simulation reset')

    def update_all_plots(self):
        """Update all visualization plots"""
        if not self.simulation_data['time']:
            return

        self.update_main_plots()
        self.update_control_plots()
        self.update_electromagnetic_plots()
        self.update_thermal_plots()
        self.update_mechanical_plots()

    def update_main_plots(self):
        """Update main tab plots"""
        t = self.simulation_data['time']

        # Speed plot
        self.main_axes['speed'].clear()
        self.main_axes['speed'].plot(t, self.simulation_data['speed'], 'b-', linewidth=2)
        self.main_axes['speed'].set_xlabel('Time (s)')
        self.main_axes['speed'].set_ylabel('Speed (RPM)')
        self.main_axes['speed'].set_title('Motor Speed')
        self.main_axes['speed'].grid(True, alpha=0.3)

        # Current plot
        self.main_axes['current'].clear()
        self.main_axes['current'].plot(t, self.simulation_data['current'], 'r-', linewidth=2)
        self.main_axes['current'].set_xlabel('Time (s)')
        self.main_axes['current'].set_ylabel('Current (A)')
        self.main_axes['current'].set_title('Armature Current')
        self.main_axes['current'].grid(True, alpha=0.3)

        # Torque plot
        self.main_axes['torque'].clear()
        self.main_axes['torque'].plot(t, self.simulation_data['torque'], 'g-', linewidth=2)
        self.main_axes['torque'].set_xlabel('Time (s)')
        self.main_axes['torque'].set_ylabel('Torque (N·m)')
        self.main_axes['torque'].set_title('Electromagnetic Torque')
        self.main_axes['torque'].grid(True, alpha=0.3)

        # Power plot
        self.main_axes['power'].clear()
        self.main_axes['power'].plot(t, self.simulation_data['power'], 'm-',
                                     linewidth=2, label='Input')
        if 'power_out' in self.simulation_data:
            self.main_axes['power'].plot(t, self.simulation_data['power_out'], 'c-',
                                        linewidth=2, label='Output')
        self.main_axes['power'].set_xlabel('Time (s)')
        self.main_axes['power'].set_ylabel('Power (W)')
        self.main_axes['power'].set_title('Power Flow')
        self.main_axes['power'].legend()
        self.main_axes['power'].grid(True, alpha=0.3)

        self.main_fig.tight_layout()
        self.main_canvas.draw()

    def update_control_plots(self):
        """Update control tab plots"""
        if not self.simulation_data['time']:
            return

        t = self.simulation_data['time']
        speed_ref = self.control_params['speed_reference'].get()

        # Response plot
        self.control_axes['response'].clear()
        self.control_axes['response'].plot(t, self.simulation_data['speed'], 'b-',
                                          linewidth=2, label='Actual')
        self.control_axes['response'].axhline(y=speed_ref, color='r', linestyle='--',
                                             linewidth=2, label='Reference')
        self.control_axes['response'].set_xlabel('Time (s)')
        self.control_axes['response'].set_ylabel('Speed (RPM)')
        self.control_axes['response'].set_title('Speed Response')
        self.control_axes['response'].legend()
        self.control_axes['response'].grid(True, alpha=0.3)

        # Error plot
        error = speed_ref - np.array(self.simulation_data['speed'])
        self.control_axes['error'].clear()
        self.control_axes['error'].plot(t, error, 'r-', linewidth=2)
        self.control_axes['error'].set_xlabel('Time (s)')
        self.control_axes['error'].set_ylabel('Error (RPM)')
        self.control_axes['error'].set_title('Tracking Error')
        self.control_axes['error'].grid(True, alpha=0.3)

        self.control_fig.tight_layout()
        self.control_canvas.draw()

    def update_electromagnetic_plots(self):
        """Update electromagnetic plots"""
        if not self.simulation_data['time']:
            return

        t = self.simulation_data['time']

        # Flux density (proportional to current in series motor)
        flux = np.array(self.simulation_data['current']) * 0.001  # Simplified
        self.em_axes['flux'].clear()
        self.em_axes['flux'].plot(t, flux, 'b-', linewidth=2)
        self.em_axes['flux'].set_xlabel('Time (s)')
        self.em_axes['flux'].set_ylabel('Flux (Wb)')
        self.em_axes['flux'].set_title('Magnetic Flux')
        self.em_axes['flux'].grid(True, alpha=0.3)

        # Voltage
        self.em_axes['voltage'].clear()
        self.em_axes['voltage'].plot(t, self.simulation_data['voltage'], 'r-',
                                     linewidth=2, label='Supply')
        if 'emf' in self.simulation_data:
            self.em_axes['voltage'].plot(t, self.simulation_data['emf'], 'g-',
                                        linewidth=2, label='Back EMF')
        self.em_axes['voltage'].set_xlabel('Time (s)')
        self.em_axes['voltage'].set_ylabel('Voltage (V)')
        self.em_axes['voltage'].set_title('Voltage Components')
        self.em_axes['voltage'].legend()
        self.em_axes['voltage'].grid(True, alpha=0.3)

        # Current
        self.em_axes['current'].clear()
        self.em_axes['current'].plot(t, self.simulation_data['current'], 'orange', linewidth=2)
        self.em_axes['current'].set_xlabel('Time (s)')
        self.em_axes['current'].set_ylabel('Current (A)')
        self.em_axes['current'].set_title('Armature Current (RMS)')
        self.em_axes['current'].grid(True, alpha=0.3)

        # EMF
        self.em_axes['emf'].clear()
        if 'emf' in self.simulation_data:
            self.em_axes['emf'].plot(t, self.simulation_data['emf'], 'm-', linewidth=2)
        self.em_axes['emf'].set_xlabel('Time (s)')
        self.em_axes['emf'].set_ylabel('EMF (V)')
        self.em_axes['emf'].set_title('Back EMF')
        self.em_axes['emf'].grid(True, alpha=0.3)

        self.em_fig.tight_layout()

    def update_thermal_plots(self):
        """Update thermal analysis plots"""
        if not self.simulation_data['time']:
            return

        t = self.simulation_data['time']
        temp = self.simulation_data['temperature']
        current = np.array(self.simulation_data['current'])

        Ra = self.motor_params['ra'].get()
        Rse = 4 * self.motor_params['rse_per_coil'].get()

        # Temperature plot
        self.thermal_axes['temp'].clear()
        self.thermal_axes['temp'].plot(t, temp, 'r-', linewidth=2, label='Winding')
        T_amb = self.motor_params['temp_ambient'].get()
        self.thermal_axes['temp'].axhline(y=T_amb, color='b', linestyle='--',
                                         linewidth=1, label='Ambient')
        self.thermal_axes['temp'].axhline(y=120, color='orange', linestyle='--',
                                         linewidth=1, label='Warning')
        self.thermal_axes['temp'].set_xlabel('Time (s)')
        self.thermal_axes['temp'].set_ylabel('Temperature (°C)')
        self.thermal_axes['temp'].set_title('Thermal Profile')
        self.thermal_axes['temp'].legend()
        self.thermal_axes['temp'].grid(True, alpha=0.3)

        # Losses breakdown
        copper_loss = current**2 * (Ra + Rse)
        iron_loss = 0.02 * np.array(self.simulation_data['speed'])**2 / 900**2 * 100  # Simplified
        friction_loss = 0.01 * np.array(self.simulation_data['speed']) / 900 * 50
        stray_loss = 0.01 * copper_loss

        self.thermal_axes['losses'].clear()
        self.thermal_axes['losses'].plot(t, copper_loss, label='Copper', linewidth=2)
        self.thermal_axes['losses'].plot(t, iron_loss, label='Iron', linewidth=2)
        self.thermal_axes['losses'].plot(t, friction_loss, label='Friction', linewidth=2)
        self.thermal_axes['losses'].plot(t, stray_loss, label='Stray', linewidth=2)
        self.thermal_axes['losses'].set_xlabel('Time (s)')
        self.thermal_axes['losses'].set_ylabel('Loss (W)')
        self.thermal_axes['losses'].set_title('Loss Breakdown')
        self.thermal_axes['losses'].legend()
        self.thermal_axes['losses'].grid(True, alpha=0.3)

        # Derating curve
        self.thermal_axes['derating'].clear()
        temp_range = np.linspace(T_amb, 150, 100)
        derating_factor = np.where(temp_range < 100, 1.0,
                                  np.maximum(0, 1.0 - (temp_range - 100) / 50))
        self.thermal_axes['derating'].plot(temp_range, derating_factor * 100, 'r-', linewidth=2)
        if len(temp) > 0:
            current_temp = temp[-1]
            current_derating = 100 if current_temp < 100 else max(0, (1.0 - (current_temp - 100) / 50) * 100)
            self.thermal_axes['derating'].plot(current_temp, current_derating, 'bo', markersize=10)
        self.thermal_axes['derating'].set_xlabel('Temperature (°C)')
        self.thermal_axes['derating'].set_ylabel('Derating Factor (%)')
        self.thermal_axes['derating'].set_title('Thermal Derating Curve')
        self.thermal_axes['derating'].grid(True, alpha=0.3)

        # Temperature distribution (simplified radial model)
        self.thermal_axes['distribution'].clear()
        if len(temp) > 0:
            r = np.linspace(0, 1, 50)  # Normalized radius
            T_core = temp[-1]
            T_surface = T_amb + (T_core - T_amb) * 0.5
            temp_profile = T_amb + (T_core - T_amb) * (1 - r**2)

            self.thermal_axes['distribution'].plot(r, temp_profile, 'r-', linewidth=2)
            self.thermal_axes['distribution'].set_xlabel('Normalized Radius')
            self.thermal_axes['distribution'].set_ylabel('Temperature (°C)')
            self.thermal_axes['distribution'].set_title('Radial Temperature Distribution')
            self.thermal_axes['distribution'].grid(True, alpha=0.3)

        self.thermal_fig.tight_layout()

    def update_mechanical_plots(self):
        """Update mechanical analysis plots"""
        if not self.simulation_data['time']:
            return

        t = self.simulation_data['time']
        torque = np.array(self.simulation_data['torque'])
        speed = np.array(self.simulation_data['speed'])

        # Torque vs time
        self.mech_axes['torque'].clear()
        self.mech_axes['torque'].plot(t, torque, 'g-', linewidth=2)
        T_load = self.control_params['load_torque'].get()
        self.mech_axes['torque'].axhline(y=T_load, color='r', linestyle='--',
                                        linewidth=2, label='Load')
        self.mech_axes['torque'].set_xlabel('Time (s)')
        self.mech_axes['torque'].set_ylabel('Torque (N·m)')
        self.mech_axes['torque'].set_title('Torque Transients')
        self.mech_axes['torque'].legend()
        self.mech_axes['torque'].grid(True, alpha=0.3)

        # Speed vs time
        self.mech_axes['speed'].clear()
        self.mech_axes['speed'].plot(t, speed, 'b-', linewidth=2)
        self.mech_axes['speed'].set_xlabel('Time (s)')
        self.mech_axes['speed'].set_ylabel('Speed (RPM)')
        self.mech_axes['speed'].set_title('Speed Profile')
        self.mech_axes['speed'].grid(True, alpha=0.3)

        # Shaft stress (simplified)
        shaft_diameter = 0.05  # m
        shaft_stress = torque * shaft_diameter / (2 * np.pi * (shaft_diameter/2)**3) / 1e6  # MPa

        self.mech_axes['stress'].clear()
        self.mech_axes['stress'].plot(t, shaft_stress, 'orange', linewidth=2)
        self.mech_axes['stress'].axhline(y=200, color='r', linestyle='--',
                                        linewidth=1, label='Yield Stress')
        self.mech_axes['stress'].set_xlabel('Time (s)')
        self.mech_axes['stress'].set_ylabel('Shear Stress (MPa)')
        self.mech_axes['stress'].set_title('Shaft Stress Analysis')
        self.mech_axes['stress'].legend()
        self.mech_axes['stress'].grid(True, alpha=0.3)

        # Vibration (simplified)
        if len(t) > 10:
            vibration = 0.1 * np.sin(2 * np.pi * speed / 60 * np.array(t)) + 0.02 * np.random.randn(len(t))
            self.mech_axes['vibration'].clear()
            self.mech_axes['vibration'].plot(t, vibration, 'm-', linewidth=1)
            self.mech_axes['vibration'].set_xlabel('Time (s)')
            self.mech_axes['vibration'].set_ylabel('Vibration (mm/s)')
            self.mech_axes['vibration'].set_title('Bearing Vibration')
            self.mech_axes['vibration'].grid(True, alpha=0.3)

        self.mech_fig.tight_layout()

    def calculate_economics(self):
        """Calculate economic analysis"""
        try:
            if not self.simulation_data['time']:
                messagebox.showwarning('Warning', 'Run simulation first!')
                return

            # Get parameters
            elec_cost = self.economic_params['electricity_cost'].get()
            op_hours = self.economic_params['operating_hours'].get()
            motor_cost = self.economic_params['motor_cost'].get()
            maint_cost = self.economic_params['maintenance_cost'].get()
            lifetime = self.economic_params['lifetime_years'].get()

            # Calculate average power
            avg_power = np.mean(self.simulation_data['power'])  # W
            avg_power_kw = avg_power / 1000

            # Calculate average efficiency
            avg_efficiency = np.mean(self.simulation_data['efficiency'])

            # Annual energy consumption
            annual_energy = avg_power_kw * op_hours  # kWh/year

            # Annual energy cost
            annual_energy_cost = annual_energy * elec_cost

            # Total annual cost
            annual_total_cost = annual_energy_cost + maint_cost

            # Lifetime costs
            lifetime_energy_cost = annual_energy_cost * lifetime
            lifetime_maint_cost = maint_cost * lifetime
            lifetime_total_cost = motor_cost + lifetime_energy_cost + lifetime_maint_cost

            # Cost per operating hour
            cost_per_hour = annual_total_cost / op_hours

            # CO2 emissions (assuming 0.5 kg CO2/kWh)
            annual_co2 = annual_energy * 0.5

            # Efficiency improvement potential
            ideal_efficiency = 95.0
            potential_savings = annual_energy * (1 - avg_efficiency/ideal_efficiency) * elec_cost

            # Display results
            results = f"""
{'='*60}
ECONOMIC ANALYSIS RESULTS
{'='*60}

OPERATING CONDITIONS:
--------------------
Average Power: {avg_power:.2f} W ({avg_power_kw:.3f} kW)
Average Efficiency: {avg_efficiency:.2f} %
Operating Hours: {op_hours:.0f} h/year
Electricity Cost: ${elec_cost:.3f}/kWh

ANNUAL COSTS:
-------------
Energy Consumption: {annual_energy:.2f} kWh/year
Energy Cost: ${annual_energy_cost:.2f}/year
Maintenance Cost: ${maint_cost:.2f}/year
Total Annual Cost: ${annual_total_cost:.2f}/year
Cost per Hour: ${cost_per_hour:.4f}/h

LIFETIME COSTS ({lifetime:.0f} years):
----------------------
Initial Investment: ${motor_cost:.2f}
Energy Cost: ${lifetime_energy_cost:.2f}
Maintenance Cost: ${lifetime_maint_cost:.2f}
Total Lifetime Cost: ${lifetime_total_cost:.2f}

ENVIRONMENTAL IMPACT:
--------------------
Annual CO2 Emissions: {annual_co2:.2f} kg/year
Lifetime CO2 Emissions: {annual_co2 * lifetime:.2f} kg

OPTIMIZATION POTENTIAL:
----------------------
Current Efficiency: {avg_efficiency:.2f}%
Target Efficiency: {ideal_efficiency:.2f}%
Potential Annual Savings: ${potential_savings:.2f}/year
Payback Period: {motor_cost / potential_savings if potential_savings > 0 else 0:.2f} years

{'='*60}
"""

            self.econ_results.delete(1.0, tk.END)
            self.econ_results.insert(1.0, results)

            # Update economic plots
            self.plot_economics(annual_energy_cost, maint_cost, avg_efficiency,
                              annual_co2, lifetime, potential_savings)

            self.status_label.config(text='Economic analysis completed')

        except Exception as e:
            messagebox.showerror('Error', f'Error in economic analysis:\n{str(e)}')

    def plot_economics(self, energy_cost, maint_cost, efficiency, co2, lifetime, savings):
        """Plot economic analysis results"""

        # Cost breakdown pie chart
        self.econ_axes['costs'].clear()
        costs = [energy_cost, maint_cost]
        labels = ['Energy', 'Maintenance']
        colors = ['#ff9999', '#66b3ff']
        self.econ_axes['costs'].pie(costs, labels=labels, colors=colors, autopct='%1.1f%%',
                                    startangle=90)
        self.econ_axes['costs'].set_title('Annual Cost Breakdown')

        # Cumulative cost over lifetime
        years = np.arange(0, lifetime + 1)
        motor_cost = self.economic_params['motor_cost'].get()
        cumulative_cost = motor_cost + (energy_cost + maint_cost) * years

        self.econ_axes['payback'].clear()
        self.econ_axes['payback'].plot(years, cumulative_cost, 'b-', linewidth=2)
        self.econ_axes['payback'].set_xlabel('Years')
        self.econ_axes['payback'].set_ylabel('Cumulative Cost ($)')
        self.econ_axes['payback'].set_title('Lifetime Cost Analysis')
        self.econ_axes['payback'].grid(True, alpha=0.3)

        # Efficiency comparison
        self.econ_axes['efficiency'].clear()
        categories = ['Current', 'Target']
        efficiencies = [efficiency, 95.0]
        colors = ['orange', 'green']
        self.econ_axes['efficiency'].bar(categories, efficiencies, color=colors)
        self.econ_axes['efficiency'].set_ylabel('Efficiency (%)')
        self.econ_axes['efficiency'].set_title('Efficiency Comparison')
        self.econ_axes['efficiency'].set_ylim([0, 100])
        self.econ_axes['efficiency'].grid(True, alpha=0.3, axis='y')

        # Savings potential
        self.econ_axes['savings'].clear()
        savings_years = savings * years
        self.econ_axes['savings'].plot(years, savings_years, 'g-', linewidth=2)
        self.econ_axes['savings'].set_xlabel('Years')
        self.econ_axes['savings'].set_ylabel('Cumulative Savings ($)')
        self.econ_axes['savings'].set_title('Potential Savings from Optimization')
        self.econ_axes['savings'].grid(True, alpha=0.3)

        self.econ_fig.tight_layout()

    def export_results(self):
        """Export results to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'dc_motor_results_{timestamp}.txt'

            with open(filename, 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))

            messagebox.showinfo('Success', f'Results exported to {filename}')
            self.status_label.config(text=f'Results exported to {filename}')

        except Exception as e:
            messagebox.showerror('Error', f'Error exporting results:\n{str(e)}')

    def on_window_resize(self, event):
        """Handle window resize events for auto-scaling"""
        # This is called automatically when window is resized
        # The grid weights handle the auto-scaling
        pass


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = DCMotorLab(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == '__main__':
    main()

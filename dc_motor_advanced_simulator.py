"""
Advanced DC Motor Simulator with Multi-Physics Analysis
Includes solutions to DC motor problems and comprehensive GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.integrate import solve_ivp
import threading
import time
from datetime import datetime

# ============================================================================
# DC MOTOR PROBLEM SOLUTIONS
# ============================================================================

class DCMotorProblems:
    """Solutions to the DC motor problems"""

    @staticmethod
    def problem_1():
        """
        Problem 1: 4-pole series-wound fan motor
        - Initial: 600 rpm, 250V, 20A, field coils in series
        - Find: Speed and current when coils reconnected in 2 parallel groups
        - Load torque ∝ speed²
        - Flux ∝ current
        """
        print("\n" + "="*70)
        print("PROBLEM 1: Series-Wound Fan Motor with Field Reconnection")
        print("="*70)

        # Initial conditions
        V = 250  # Voltage (V)
        N1 = 600  # Speed (rpm)
        I1 = 20  # Current (A)

        print(f"\nInitial Conditions (All coils in series):")
        print(f"  Voltage: {V} V")
        print(f"  Speed: {N1} rpm")
        print(f"  Current: {I1} A")

        # For series motor: E = V - I*Ra (ignoring losses, Ra ≈ 0)
        # E = k*φ*N, φ ∝ I for series motor
        # Therefore: E1 = k*φ1*N1 = k*I1*N1

        # When field coils reconnected: 2 parallel groups of 2 in series
        # Field MMF becomes half (since current path splits)
        # Flux φ2 = φ1/2 = I2/2 (if same current)
        # But current will change

        # Field resistance changes:
        # Original: 4 coils in series = 4Rf
        # New: 2 groups parallel, each with 2 coils = 2Rf || 2Rf = Rf
        # So new field resistance = Rf (vs 4Rf original)

        # Let's denote total resistance R1 = Ra + 4Rf (original)
        # New total resistance R2 = Ra + Rf
        # Assuming Ra is small: R2 ≈ R1/4

        # Voltage equation: V = E + I*R
        # Ignoring resistance drop: V ≈ E
        # E = k*φ*N, φ ∝ I (but with different field connection)

        # Original: φ1 ∝ I1 (all coils in series)
        # New: φ2 ∝ I2/2 (current splits in parallel groups)

        # At steady state:
        # E1 = k*I1*N1
        # E2 = k*(I2/2)*N2

        # Since V ≈ E (ignoring resistance):
        # V = k*I1*N1 = k*(I2/2)*N2
        # I1*N1 = (I2/2)*N2
        # N2 = 2*I1*N1/I2  ... (1)

        # Torque equation: T = k*φ*I
        # T1 = k*I1*I1 = k*I1²
        # T2 = k*(I2/2)*I2 = k*I2²/2

        # Load torque: T ∝ N²
        # T2/T1 = (N2/N1)²
        # (k*I2²/2)/(k*I1²) = (N2/N1)²
        # I2²/(2*I1²) = (N2/N1)²
        # I2/(√2*I1) = N2/N1
        # I2 = √2*I1*(N2/N1)  ... (2)

        # From (1): N2 = 2*I1*N1/I2
        # Substitute into (2): I2 = √2*I1*(2*I1*N1/I2)/N1
        # I2 = 2*√2*I1²/I2
        # I2² = 2*√2*I1²
        # I2 = I1*(2*√2)^0.5 = I1*1.682

        I2 = I1 * (2 * np.sqrt(2))**0.5
        N2 = 2 * I1 * N1 / I2

        print(f"\nField Reconnection (2 parallel groups of 2 in series):")
        print(f"  New Current: {I2:.2f} A")
        print(f"  New Speed: {N2:.2f} rpm")
        print(f"\nRatio Analysis:")
        print(f"  Current ratio (I2/I1): {I2/I1:.3f}")
        print(f"  Speed ratio (N2/N1): {N2/N1:.3f}")

        return {
            'V': V, 'N1': N1, 'I1': I1,
            'N2': N2, 'I2': I2
        }

    @staticmethod
    def problem_2():
        """
        Problem 2: 200V DC series motor with field shunt
        - Initial: 200V, 40A, 700 rpm
        - Field shunted by resistance equal to field resistance
        - Load torque increased by 50%
        - Ra = 0.15Ω, Rf = 0.1Ω
        - Find: New speed and current
        """
        print("\n" + "="*70)
        print("PROBLEM 2: DC Series Motor with Field Shunt")
        print("="*70)

        # Given data
        V = 200  # Voltage (V)
        I1 = 40  # Initial current (A)
        N1 = 700  # Initial speed (rpm)
        Ra = 0.15  # Armature resistance (Ω)
        Rf = 0.1  # Field resistance (Ω)

        print(f"\nGiven Parameters:")
        print(f"  Supply Voltage: {V} V")
        print(f"  Initial Current: {I1} A")
        print(f"  Initial Speed: {N1} rpm")
        print(f"  Armature Resistance: {Ra} Ω")
        print(f"  Field Resistance: {Rf} Ω")

        # Initial condition (no shunt)
        Rt1 = Ra + Rf  # Total resistance
        E1 = V - I1 * Rt1  # Back EMF
        If1 = I1  # Field current = armature current (series)

        print(f"\nInitial Conditions (No shunt):")
        print(f"  Total Resistance: {Rt1} Ω")
        print(f"  Back EMF: {E1:.2f} V")
        print(f"  Field Current: {If1} A")

        # With shunt resistance = Rf connected across field
        # Field and shunt in parallel
        # If2 = field current, Ish = shunt current, Ia2 = armature current
        # Ia2 = If2 + Ish
        # Voltage across field = If2 * Rf = Ish * Rf
        # Therefore: If2 = Ish, so Ia2 = 2*If2

        # Back EMF: E2 = V - Ia2*Ra - If2*Rf
        # E2 = V - 2*If2*Ra - If2*Rf = V - If2*(2*Ra + Rf)

        # EMF equation: E = k*φ*N, φ ∝ If
        # E1 = k*If1*N1
        # E2 = k*If2*N2

        # Torque equation: T = k*φ*Ia
        # T1 = k*If1*I1 = k*If1²  (since If1 = I1)
        # T2 = k*If2*Ia2 = k*If2*(2*If2) = 2*k*If2²

        # Load torque increases by 50%
        # T2 = 1.5*T1
        # 2*k*If2² = 1.5*k*If1²
        # If2² = 0.75*If1²
        # If2 = If1*√0.75 = If1*0.866

        If2 = If1 * np.sqrt(0.75)
        Ia2 = 2 * If2  # Armature current

        print(f"\nWith Field Shunt (Rsh = Rf = {Rf} Ω):")
        print(f"  Field Current: {If2:.2f} A")
        print(f"  Armature Current: {Ia2:.2f} A")
        print(f"  Shunt Current: {If2:.2f} A")

        # Calculate back EMFs
        E2 = V - Ia2*Ra - If2*Rf

        print(f"  Back EMF: {E2:.2f} V")

        # Calculate speed
        # E1/E2 = (If1*N1)/(If2*N2)
        # N2 = E2*If1*N1/(E1*If2)
        N2 = (E2 * If1 * N1) / (E1 * If2)

        print(f"  New Speed: {N2:.2f} rpm")

        # Supply current
        I2 = Ia2  # Current from supply

        print(f"  Supply Current: {I2:.2f} A")

        print(f"\nVerification:")
        T1 = If1 * I1
        T2 = If2 * Ia2
        print(f"  Torque ratio (T2/T1): {T2/T1:.3f} (should be ≈1.5)")
        print(f"  Speed ratio (N2/N1): {N2/N1:.3f}")
        print(f"  Current ratio (I2/I1): {I2/I1:.3f}")

        return {
            'V': V, 'N1': N1, 'I1': I1, 'Ra': Ra, 'Rf': Rf,
            'N2': N2, 'I2': I2, 'If2': If2, 'Ia2': Ia2,
            'E1': E1, 'E2': E2
        }

# ============================================================================
# ODE SOLVERS
# ============================================================================

class ODESolvers:
    """Numerical ODE solvers for dynamic simulation"""

    @staticmethod
    def euler(f, y0, t_span, dt):
        """
        Euler method for solving ODEs
        f: derivative function dy/dt = f(t, y)
        y0: initial conditions
        t_span: (t_start, t_end)
        dt: time step
        """
        t_start, t_end = t_span
        t = np.arange(t_start, t_end + dt, dt)
        y = np.zeros((len(t), len(y0)))
        y[0] = y0

        for i in range(len(t) - 1):
            y[i+1] = y[i] + dt * f(t[i], y[i])

        return t, y

    @staticmethod
    def rk45(f, y0, t_span, dt):
        """
        Runge-Kutta 4th/5th order (RK45) solver
        Uses scipy's solve_ivp with RK45 method
        """
        t_start, t_end = t_span
        t_eval = np.arange(t_start, t_end + dt, dt)

        sol = solve_ivp(f, t_span, y0, method='RK45',
                       t_eval=t_eval, rtol=1e-6, atol=1e-9)

        return sol.t, sol.y.T

# ============================================================================
# DC MOTOR DYNAMIC MODEL
# ============================================================================

class DCMotorModel:
    """
    Dynamic model of DC motor with multi-physics coupling
    """

    def __init__(self, params):
        # Electrical parameters
        self.V = params.get('voltage', 250)  # Supply voltage (V)
        self.Ra = params.get('Ra', 0.5)  # Armature resistance (Ω)
        self.La = params.get('La', 0.01)  # Armature inductance (H)
        self.Rf = params.get('Rf', 0.3)  # Field resistance (Ω)
        self.Lf = params.get('Lf', 0.05)  # Field inductance (H)

        # Mechanical parameters
        self.J = params.get('J', 0.02)  # Moment of inertia (kg·m²)
        self.B = params.get('B', 0.001)  # Viscous friction (N·m·s/rad)
        self.Kt = params.get('Kt', 1.5)  # Torque constant (N·m/A)
        self.Ke = params.get('Ke', 1.5)  # EMF constant (V·s/rad)

        # Thermal parameters
        self.R_th = params.get('R_th', 2.0)  # Thermal resistance (°C/W)
        self.C_th = params.get('C_th', 100)  # Thermal capacitance (J/°C)
        self.T_amb = params.get('T_amb', 25)  # Ambient temperature (°C)
        self.alpha = params.get('alpha', 0.004)  # Temperature coefficient (1/°C)

        # Motor type
        self.motor_type = params.get('motor_type', 'series')  # 'series', 'shunt', 'separately_excited'

        # Load parameters
        self.TL_const = params.get('TL_const', 0)  # Constant load torque
        self.TL_speed_coef = params.get('TL_speed_coef', 0.0001)  # Speed-dependent load

        # Loss parameters
        self.iron_loss_coef = params.get('iron_loss_coef', 0.01)  # Iron loss coefficient
        self.friction_coef = params.get('friction_coef', 0.001)  # Mechanical friction
        self.stray_loss_coef = params.get('stray_loss_coef', 0.005)  # Stray losses

    def motor_dynamics(self, t, state):
        """
        State-space model: [Ia, If, omega, theta, T_motor]
        Ia: Armature current (A)
        If: Field current (A)
        omega: Angular velocity (rad/s)
        theta: Angular position (rad)
        T_motor: Motor temperature (°C)
        """
        Ia, If, omega, theta, T_motor = state

        # Temperature-dependent resistance
        Ra_temp = self.Ra * (1 + self.alpha * (T_motor - self.T_amb))
        Rf_temp = self.Rf * (1 + self.alpha * (T_motor - self.T_amb))

        # Back EMF
        Eb = self.Ke * If * omega

        # Electrical equations
        if self.motor_type == 'series':
            # Series motor: same current through field and armature
            dIa_dt = (self.V - Eb - Ia * (Ra_temp + Rf_temp)) / (self.La + self.Lf)
            dIf_dt = dIa_dt
            If = Ia  # For series motor
        elif self.motor_type == 'shunt':
            # Shunt motor: separate field and armature circuits
            dIa_dt = (self.V - Eb - Ia * Ra_temp) / self.La
            dIf_dt = (self.V - If * Rf_temp) / self.Lf
        else:  # separately_excited
            dIa_dt = (self.V - Eb - Ia * Ra_temp) / self.La
            dIf_dt = 0  # Constant field current

        # Electromagnetic torque
        Te = self.Kt * If * Ia

        # Load torque (speed-dependent)
        TL = self.TL_const + self.TL_speed_coef * omega**2

        # Mechanical equation
        d_omega_dt = (Te - TL - self.B * omega) / self.J

        # Angular position
        d_theta_dt = omega

        # Losses
        copper_loss = Ia**2 * Ra_temp + If**2 * Rf_temp
        iron_loss = self.iron_loss_coef * omega**2
        mechanical_loss = self.friction_coef * omega**2
        stray_loss = self.stray_loss_coef * (Ia**2 + If**2)
        total_loss = copper_loss + iron_loss + mechanical_loss + stray_loss

        # Thermal equation
        dT_dt = (total_loss - (T_motor - self.T_amb) / self.R_th) / self.C_th

        return [dIa_dt, dIf_dt, d_omega_dt, d_theta_dt, dT_dt]

    def calculate_losses(self, Ia, If, omega, T_motor):
        """Calculate detailed losses"""
        Ra_temp = self.Ra * (1 + self.alpha * (T_motor - self.T_amb))
        Rf_temp = self.Rf * (1 + self.alpha * (T_motor - self.T_amb))

        copper_loss = Ia**2 * Ra_temp + If**2 * Rf_temp
        iron_loss = self.iron_loss_coef * omega**2
        mechanical_loss = self.friction_coef * omega**2
        stray_loss = self.stray_loss_coef * (Ia**2 + If**2)

        return {
            'copper': copper_loss,
            'iron': iron_loss,
            'mechanical': mechanical_loss,
            'stray': stray_loss,
            'total': copper_loss + iron_loss + mechanical_loss + stray_loss
        }

    def calculate_efficiency(self, Ia, If, omega, losses):
        """Calculate motor efficiency"""
        Te = self.Kt * If * Ia
        P_out = Te * omega
        P_in = self.V * Ia

        if P_in > 0:
            efficiency = (P_out / P_in) * 100
        else:
            efficiency = 0

        return efficiency, P_in, P_out

# ============================================================================
# ADVANCED DC MOTOR SIMULATOR GUI
# ============================================================================

class DCMotorSimulatorGUI:
    """
    Comprehensive GUI for DC motor simulation with multi-physics analysis
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced DC Motor Simulator - Multi-Physics Analysis")
        self.root.geometry("1400x900")

        # Simulation state
        self.is_running = False
        self.simulation_thread = None
        self.current_time = 0
        self.sim_data = {
            't': [], 'Ia': [], 'If': [], 'omega': [], 'N': [],
            'Te': [], 'TL': [], 'T_motor': [], 'efficiency': [],
            'P_in': [], 'P_out': [], 'losses': []
        }

        # Default parameters
        self.params = {
            'voltage': 250, 'Ra': 0.5, 'La': 0.01, 'Rf': 0.3, 'Lf': 0.05,
            'J': 0.02, 'B': 0.001, 'Kt': 1.5, 'Ke': 1.5,
            'R_th': 2.0, 'C_th': 100, 'T_amb': 25, 'alpha': 0.004,
            'motor_type': 'series', 'TL_const': 1.0, 'TL_speed_coef': 0.0001,
            'iron_loss_coef': 0.01, 'friction_coef': 0.001, 'stray_loss_coef': 0.005
        }

        # Create menu
        self.create_menu()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Create tabs
        self.create_main_tab()
        self.create_dynamics_tab()
        self.create_thermal_tab()
        self.create_losses_tab()
        self.create_economic_tab()
        self.create_problems_tab()

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

        self.update_status("DC Motor Simulator Ready")

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_command(label="Load Parameters", command=self.load_parameters)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self.start_simulation)
        sim_menu.add_command(label="Stop", command=self.stop_simulation)
        sim_menu.add_command(label="Reset", command=self.reset_simulation)

        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Solve Problem 1", command=self.solve_problem_1)
        analysis_menu.add_command(label="Solve Problem 2", command=self.solve_problem_2)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_tab(self):
        """Create main control tab"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Main Control")

        # Left panel - Parameters
        left_frame = ttk.LabelFrame(main_frame, text="Motor Parameters", padding=10)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Create parameter inputs with sliders
        self.param_vars = {}
        param_configs = [
            ('Voltage (V)', 'voltage', 50, 500, 250),
            ('Ra (Ω)', 'Ra', 0.1, 5, 0.5),
            ('La (H)', 'La', 0.001, 0.1, 0.01),
            ('Rf (Ω)', 'Rf', 0.1, 2, 0.3),
            ('Lf (H)', 'Lf', 0.01, 0.2, 0.05),
            ('J (kg·m²)', 'J', 0.001, 0.1, 0.02),
            ('B (N·m·s/rad)', 'B', 0.0001, 0.01, 0.001),
            ('Kt (N·m/A)', 'Kt', 0.5, 3, 1.5),
            ('Ke (V·s/rad)', 'Ke', 0.5, 3, 1.5),
        ]

        for i, (label, key, min_val, max_val, default) in enumerate(param_configs):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)

            var = tk.DoubleVar(value=default)
            self.param_vars[key] = var

            slider = ttk.Scale(left_frame, from_=min_val, to=max_val,
                             orient='horizontal', variable=var, length=200)
            slider.grid(row=i, column=1, padx=5, pady=2)

            entry = ttk.Entry(left_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=2)

        # Motor type selection
        ttk.Label(left_frame, text="Motor Type").grid(row=len(param_configs), column=0, sticky='w', pady=5)
        self.motor_type_var = tk.StringVar(value='series')
        motor_types = ttk.Combobox(left_frame, textvariable=self.motor_type_var,
                                   values=['series', 'shunt', 'separately_excited'],
                                   state='readonly', width=18)
        motor_types.grid(row=len(param_configs), column=1, columnspan=2, pady=5)

        # Right panel - Control
        right_frame = ttk.LabelFrame(main_frame, text="Simulation Control", padding=10)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Control buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_simulation, width=15)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_simulation,
                                   width=15, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_simulation, width=15)
        self.reset_btn.grid(row=1, column=0, padx=5, pady=5)

        # Solver selection
        ttk.Label(right_frame, text="ODE Solver:").pack(pady=5)
        self.solver_var = tk.StringVar(value='RK45')
        solver_frame = ttk.Frame(right_frame)
        solver_frame.pack()
        ttk.Radiobutton(solver_frame, text="RK45", variable=self.solver_var,
                       value='RK45').pack(side='left', padx=10)
        ttk.Radiobutton(solver_frame, text="Euler", variable=self.solver_var,
                       value='Euler').pack(side='left', padx=10)

        # Load controls
        load_frame = ttk.LabelFrame(right_frame, text="Load Configuration", padding=10)
        load_frame.pack(pady=10, fill='x')

        ttk.Label(load_frame, text="Constant Torque (N·m):").grid(row=0, column=0, sticky='w')
        self.tl_const_var = tk.DoubleVar(value=1.0)
        ttk.Scale(load_frame, from_=0, to=10, variable=self.tl_const_var,
                 orient='horizontal', length=150).grid(row=0, column=1)
        ttk.Entry(load_frame, textvariable=self.tl_const_var, width=10).grid(row=0, column=2)

        ttk.Label(load_frame, text="Speed Coef:").grid(row=1, column=0, sticky='w')
        self.tl_speed_var = tk.DoubleVar(value=0.0001)
        ttk.Scale(load_frame, from_=0, to=0.001, variable=self.tl_speed_var,
                 orient='horizontal', length=150).grid(row=1, column=1)
        ttk.Entry(load_frame, textvariable=self.tl_speed_var, width=10).grid(row=1, column=2)

        # Real-time display
        display_frame = ttk.LabelFrame(right_frame, text="Real-Time Display", padding=10)
        display_frame.pack(pady=10, fill='both', expand=True)

        self.display_labels = {}
        display_items = ['Time', 'Current', 'Speed', 'Torque', 'Temperature', 'Efficiency']
        for i, item in enumerate(display_items):
            ttk.Label(display_frame, text=f"{item}:").grid(row=i, column=0, sticky='w', pady=2)
            label = ttk.Label(display_frame, text="0.00", font=('Arial', 10, 'bold'))
            label.grid(row=i, column=1, sticky='w', pady=2, padx=10)
            self.display_labels[item] = label

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def create_dynamics_tab(self):
        """Create dynamics visualization tab"""
        dynamics_frame = ttk.Frame(self.notebook)
        self.notebook.add(dynamics_frame, text="Dynamics")

        # Create matplotlib figure
        self.dynamics_fig = Figure(figsize=(12, 8))
        self.dynamics_canvas = FigureCanvasTkAgg(self.dynamics_fig, dynamics_frame)
        self.dynamics_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Create subplots
        self.ax_speed = self.dynamics_fig.add_subplot(2, 2, 1)
        self.ax_current = self.dynamics_fig.add_subplot(2, 2, 2)
        self.ax_torque = self.dynamics_fig.add_subplot(2, 2, 3)
        self.ax_power = self.dynamics_fig.add_subplot(2, 2, 4)

        self.dynamics_fig.tight_layout(pad=3.0)

    def create_thermal_tab(self):
        """Create thermal analysis tab"""
        thermal_frame = ttk.Frame(self.notebook)
        self.notebook.add(thermal_frame, text="Thermal Analysis")

        # Thermal parameters
        param_frame = ttk.LabelFrame(thermal_frame, text="Thermal Parameters", padding=10)
        param_frame.pack(side='left', fill='y', padx=5, pady=5)

        thermal_params = [
            ('Thermal Resistance (°C/W)', 'R_th', 0.5, 10, 2.0),
            ('Thermal Capacitance (J/°C)', 'C_th', 10, 500, 100),
            ('Ambient Temp (°C)', 'T_amb', -20, 50, 25),
            ('Temp Coefficient (1/°C)', 'alpha', 0.001, 0.01, 0.004),
        ]

        for i, (label, key, min_val, max_val, default) in enumerate(thermal_params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)

            if key not in self.param_vars:
                var = tk.DoubleVar(value=default)
                self.param_vars[key] = var
            else:
                var = self.param_vars[key]

            slider = ttk.Scale(param_frame, from_=min_val, to=max_val,
                             orient='horizontal', variable=var, length=150)
            slider.grid(row=i, column=1, padx=5, pady=2)

            entry = ttk.Entry(param_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=2)

        # Thermal visualization
        viz_frame = ttk.Frame(thermal_frame)
        viz_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.thermal_fig = Figure(figsize=(10, 6))
        self.thermal_canvas = FigureCanvasTkAgg(self.thermal_fig, viz_frame)
        self.thermal_canvas.get_tk_widget().pack(fill='both', expand=True)

        self.ax_thermal = self.thermal_fig.add_subplot(2, 1, 1)
        self.ax_derating = self.thermal_fig.add_subplot(2, 1, 2)

        self.thermal_fig.tight_layout(pad=3.0)

    def create_losses_tab(self):
        """Create losses breakdown tab"""
        losses_frame = ttk.Frame(self.notebook)
        self.notebook.add(losses_frame, text="Losses & Efficiency")

        # Loss parameters
        param_frame = ttk.LabelFrame(losses_frame, text="Loss Coefficients", padding=10)
        param_frame.pack(side='left', fill='y', padx=5, pady=5)

        loss_params = [
            ('Iron Loss Coef', 'iron_loss_coef', 0, 0.1, 0.01),
            ('Friction Coef', 'friction_coef', 0, 0.01, 0.001),
            ('Stray Loss Coef', 'stray_loss_coef', 0, 0.05, 0.005),
        ]

        for i, (label, key, min_val, max_val, default) in enumerate(loss_params):
            ttk.Label(param_frame, text=label).grid(row=i, column=0, sticky='w', pady=2)

            if key not in self.param_vars:
                var = tk.DoubleVar(value=default)
                self.param_vars[key] = var
            else:
                var = self.param_vars[key]

            slider = ttk.Scale(param_frame, from_=min_val, to=max_val,
                             orient='horizontal', variable=var, length=150)
            slider.grid(row=i, column=1, padx=5, pady=2)

            entry = ttk.Entry(param_frame, textvariable=var, width=10)
            entry.grid(row=i, column=2, padx=5, pady=2)

        # Losses visualization
        viz_frame = ttk.Frame(losses_frame)
        viz_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.losses_fig = Figure(figsize=(10, 6))
        self.losses_canvas = FigureCanvasTkAgg(self.losses_fig, viz_frame)
        self.losses_canvas.get_tk_widget().pack(fill='both', expand=True)

        self.ax_losses_pie = self.losses_fig.add_subplot(1, 2, 1)
        self.ax_efficiency = self.losses_fig.add_subplot(1, 2, 2)

        self.losses_fig.tight_layout(pad=3.0)

    def create_economic_tab(self):
        """Create economic analysis tab"""
        economic_frame = ttk.Frame(self.notebook)
        self.notebook.add(economic_frame, text="Economic Analysis")

        # Economic parameters
        param_frame = ttk.LabelFrame(economic_frame, text="Economic Parameters", padding=10)
        param_frame.pack(side='top', fill='x', padx=5, pady=5)

        ttk.Label(param_frame, text="Electricity Cost ($/kWh):").grid(row=0, column=0, sticky='w', pady=2)
        self.elec_cost_var = tk.DoubleVar(value=0.12)
        ttk.Entry(param_frame, textvariable=self.elec_cost_var, width=15).grid(row=0, column=1, pady=2)

        ttk.Label(param_frame, text="Operating Hours/Day:").grid(row=1, column=0, sticky='w', pady=2)
        self.op_hours_var = tk.DoubleVar(value=8)
        ttk.Entry(param_frame, textvariable=self.op_hours_var, width=15).grid(row=1, column=1, pady=2)

        ttk.Label(param_frame, text="Operating Days/Year:").grid(row=2, column=0, sticky='w', pady=2)
        self.op_days_var = tk.DoubleVar(value=250)
        ttk.Entry(param_frame, textvariable=self.op_days_var, width=15).grid(row=2, column=1, pady=2)

        ttk.Button(param_frame, text="Calculate Economics",
                  command=self.calculate_economics).grid(row=3, column=0, columnspan=2, pady=10)

        # Results display
        results_frame = ttk.LabelFrame(economic_frame, text="Economic Analysis Results", padding=10)
        results_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        self.economic_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.economic_text.pack(fill='both', expand=True)

    def create_problems_tab(self):
        """Create DC motor problems tab"""
        problems_frame = ttk.Frame(self.notebook)
        self.notebook.add(problems_frame, text="DC Motor Problems")

        # Problem selection
        control_frame = ttk.Frame(problems_frame)
        control_frame.pack(side='top', fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="Solve Problem 1",
                  command=self.solve_problem_1).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Solve Problem 2",
                  command=self.solve_problem_2).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Clear Output",
                  command=self.clear_problems_output).pack(side='left', padx=5)

        # Output display
        output_frame = ttk.LabelFrame(problems_frame, text="Problem Solutions", padding=10)
        output_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)

        self.problems_text = scrolledtext.ScrolledText(output_frame, height=30, width=100,
                                                       font=('Courier', 10))
        self.problems_text.pack(fill='both', expand=True)

    def start_simulation(self):
        """Start the simulation"""
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        # Update parameters
        for key, var in self.param_vars.items():
            self.params[key] = var.get()

        self.params['motor_type'] = self.motor_type_var.get()
        self.params['TL_const'] = self.tl_const_var.get()
        self.params['TL_speed_coef'] = self.tl_speed_var.get()

        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

        self.update_status("Simulation running...")

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Simulation stopped")

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()
        self.current_time = 0
        self.sim_data = {
            't': [], 'Ia': [], 'If': [], 'omega': [], 'N': [],
            'Te': [], 'TL': [], 'T_motor': [], 'efficiency': [],
            'P_in': [], 'P_out': [], 'losses': []
        }

        # Clear plots
        for ax in [self.ax_speed, self.ax_current, self.ax_torque, self.ax_power,
                   self.ax_thermal, self.ax_derating, self.ax_losses_pie, self.ax_efficiency]:
            ax.clear()

        self.dynamics_canvas.draw()
        self.thermal_canvas.draw()
        self.losses_canvas.draw()

        self.update_status("Simulation reset")

    def run_simulation(self):
        """Run the simulation (in separate thread)"""
        # Create motor model
        motor = DCMotorModel(self.params)

        # Initial conditions: [Ia, If, omega, theta, T_motor]
        y0 = [0.0, 0.0, 0.0, 0.0, self.params['T_amb']]

        # Simulation parameters
        dt = 0.01  # Time step (s)
        t_max = 10.0  # Maximum simulation time (s)

        t = 0
        state = np.array(y0)

        while self.is_running and t < t_max:
            # Solve one time step
            if self.solver_var.get() == 'Euler':
                # Euler method
                derivatives = motor.motor_dynamics(t, state)
                state = state + dt * np.array(derivatives)
            else:
                # RK45 method (single step)
                sol = solve_ivp(motor.motor_dynamics, [t, t+dt], state,
                              method='RK45', dense_output=True)
                state = sol.y[:, -1]

            t += dt

            # Extract state
            Ia, If, omega, theta, T_motor = state
            N = omega * 30 / np.pi  # Convert to rpm

            # Calculate additional quantities
            Te = motor.Kt * If * Ia
            TL = motor.TL_const + motor.TL_speed_coef * omega**2
            losses = motor.calculate_losses(Ia, If, omega, T_motor)
            efficiency, P_in, P_out = motor.calculate_efficiency(Ia, If, omega, losses)

            # Store data
            self.sim_data['t'].append(t)
            self.sim_data['Ia'].append(Ia)
            self.sim_data['If'].append(If)
            self.sim_data['omega'].append(omega)
            self.sim_data['N'].append(N)
            self.sim_data['Te'].append(Te)
            self.sim_data['TL'].append(TL)
            self.sim_data['T_motor'].append(T_motor)
            self.sim_data['efficiency'].append(efficiency)
            self.sim_data['P_in'].append(P_in)
            self.sim_data['P_out'].append(P_out)
            self.sim_data['losses'].append(losses['total'])

            # Update display (every 10 steps)
            if len(self.sim_data['t']) % 10 == 0:
                self.root.after(0, self.update_display, t, Ia, N, Te, T_motor, efficiency)
                self.root.after(0, self.update_plots)

            time.sleep(0.01)  # Slow down for visualization

        self.is_running = False
        self.root.after(0, lambda: self.start_btn.config(state='normal'))
        self.root.after(0, lambda: self.stop_btn.config(state='disabled'))

    def update_display(self, t, Ia, N, Te, T_motor, efficiency):
        """Update real-time display"""
        self.display_labels['Time'].config(text=f"{t:.2f} s")
        self.display_labels['Current'].config(text=f"{Ia:.2f} A")
        self.display_labels['Speed'].config(text=f"{N:.1f} rpm")
        self.display_labels['Torque'].config(text=f"{Te:.2f} N·m")
        self.display_labels['Temperature'].config(text=f"{T_motor:.1f} °C")
        self.display_labels['Efficiency'].config(text=f"{efficiency:.1f} %")

    def update_plots(self):
        """Update all plots"""
        if len(self.sim_data['t']) < 2:
            return

        t = np.array(self.sim_data['t'])

        # Dynamics plots
        self.ax_speed.clear()
        self.ax_speed.plot(t, self.sim_data['N'], 'b-', linewidth=2)
        self.ax_speed.set_xlabel('Time (s)')
        self.ax_speed.set_ylabel('Speed (rpm)')
        self.ax_speed.set_title('Motor Speed')
        self.ax_speed.grid(True, alpha=0.3)

        self.ax_current.clear()
        self.ax_current.plot(t, self.sim_data['Ia'], 'r-', linewidth=2, label='Ia')
        self.ax_current.plot(t, self.sim_data['If'], 'g-', linewidth=2, label='If')
        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.set_title('Motor Currents')
        self.ax_current.legend()
        self.ax_current.grid(True, alpha=0.3)

        self.ax_torque.clear()
        self.ax_torque.plot(t, self.sim_data['Te'], 'b-', linewidth=2, label='Te')
        self.ax_torque.plot(t, self.sim_data['TL'], 'r--', linewidth=2, label='TL')
        self.ax_torque.set_xlabel('Time (s)')
        self.ax_torque.set_ylabel('Torque (N·m)')
        self.ax_torque.set_title('Torque')
        self.ax_torque.legend()
        self.ax_torque.grid(True, alpha=0.3)

        self.ax_power.clear()
        self.ax_power.plot(t, np.array(self.sim_data['P_in'])/1000, 'r-',
                          linewidth=2, label='P_in')
        self.ax_power.plot(t, np.array(self.sim_data['P_out'])/1000, 'b-',
                          linewidth=2, label='P_out')
        self.ax_power.plot(t, np.array(self.sim_data['losses'])/1000, 'g-',
                          linewidth=2, label='Losses')
        self.ax_power.set_xlabel('Time (s)')
        self.ax_power.set_ylabel('Power (kW)')
        self.ax_power.set_title('Power Flow')
        self.ax_power.legend()
        self.ax_power.grid(True, alpha=0.3)

        self.dynamics_fig.tight_layout(pad=3.0)
        self.dynamics_canvas.draw()

        # Thermal plots
        self.ax_thermal.clear()
        self.ax_thermal.plot(t, self.sim_data['T_motor'], 'r-', linewidth=2)
        self.ax_thermal.axhline(y=self.params['T_amb'], color='b', linestyle='--',
                               label=f"Ambient ({self.params['T_amb']}°C)")
        self.ax_thermal.set_xlabel('Time (s)')
        self.ax_thermal.set_ylabel('Temperature (°C)')
        self.ax_thermal.set_title('Motor Temperature')
        self.ax_thermal.legend()
        self.ax_thermal.grid(True, alpha=0.3)

        self.ax_derating.clear()
        # Derating curve (typical motor can operate at 100% up to 40°C, then derate)
        T_rated = 40
        T_max = 120
        derating = np.clip(100 * (1 - (np.array(self.sim_data['T_motor']) - T_rated) / (T_max - T_rated)), 0, 100)
        self.ax_derating.plot(t, derating, 'orange', linewidth=2)
        self.ax_derating.set_xlabel('Time (s)')
        self.ax_derating.set_ylabel('Capacity (%)')
        self.ax_derating.set_title('Thermal Derating')
        self.ax_derating.grid(True, alpha=0.3)
        self.ax_derating.set_ylim([0, 105])

        self.thermal_fig.tight_layout(pad=3.0)
        self.thermal_canvas.draw()

        # Losses plots
        if len(self.sim_data['t']) > 10:
            # Get latest losses breakdown
            motor = DCMotorModel(self.params)
            Ia = self.sim_data['Ia'][-1]
            If = self.sim_data['If'][-1]
            omega = self.sim_data['omega'][-1]
            T_motor = self.sim_data['T_motor'][-1]
            losses = motor.calculate_losses(Ia, If, omega, T_motor)

            self.ax_losses_pie.clear()
            loss_labels = ['Copper', 'Iron', 'Mechanical', 'Stray']
            loss_values = [losses['copper'], losses['iron'],
                          losses['mechanical'], losses['stray']]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

            if sum(loss_values) > 0:
                self.ax_losses_pie.pie(loss_values, labels=loss_labels, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
                self.ax_losses_pie.set_title('Loss Distribution')

            self.ax_efficiency.clear()
            self.ax_efficiency.plot(t, self.sim_data['efficiency'], 'g-', linewidth=2)
            self.ax_efficiency.set_xlabel('Time (s)')
            self.ax_efficiency.set_ylabel('Efficiency (%)')
            self.ax_efficiency.set_title('Motor Efficiency')
            self.ax_efficiency.grid(True, alpha=0.3)
            self.ax_efficiency.set_ylim([0, 105])

            self.losses_fig.tight_layout(pad=3.0)
            self.losses_canvas.draw()

    def calculate_economics(self):
        """Calculate economic analysis"""
        if len(self.sim_data['P_in']) == 0:
            messagebox.showwarning("Warning", "Please run simulation first!")
            return

        # Average power consumption
        P_avg = np.mean(self.sim_data['P_in']) / 1000  # kW

        # Economic parameters
        elec_cost = self.elec_cost_var.get()
        op_hours = self.op_hours_var.get()
        op_days = self.op_days_var.get()

        # Calculations
        energy_per_day = P_avg * op_hours  # kWh/day
        energy_per_year = energy_per_day * op_days  # kWh/year

        cost_per_day = energy_per_day * elec_cost
        cost_per_month = cost_per_day * 30
        cost_per_year = energy_per_year * elec_cost

        # Efficiency impact
        avg_efficiency = np.mean(self.sim_data['efficiency'])
        ideal_energy = energy_per_year / (avg_efficiency / 100)
        energy_loss_per_year = ideal_energy - energy_per_year
        cost_loss_per_year = energy_loss_per_year * elec_cost

        # Display results
        results = f"""
{'='*70}
ECONOMIC ANALYSIS REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OPERATING PARAMETERS:
  Electricity Cost:        ${elec_cost:.3f} / kWh
  Operating Hours/Day:     {op_hours:.1f} hours
  Operating Days/Year:     {op_days:.0f} days

POWER CONSUMPTION:
  Average Power:           {P_avg:.2f} kW
  Energy per Day:          {energy_per_day:.2f} kWh
  Energy per Year:         {energy_per_year:.2f} kWh

OPERATING COSTS:
  Cost per Day:            ${cost_per_day:.2f}
  Cost per Month:          ${cost_per_month:.2f}
  Cost per Year:           ${cost_per_year:.2f}

EFFICIENCY ANALYSIS:
  Average Efficiency:      {avg_efficiency:.1f} %
  Energy Loss/Year:        {energy_loss_per_year:.2f} kWh
  Cost of Losses/Year:     ${cost_loss_per_year:.2f}

POTENTIAL SAVINGS (with 95% efficiency):
  Improved Energy/Year:    {energy_per_year * 0.95 / (avg_efficiency/100):.2f} kWh
  Annual Savings:          ${cost_per_year - (energy_per_year * 0.95 / (avg_efficiency/100) * elec_cost):.2f}

CARBON FOOTPRINT (assuming 0.5 kg CO2/kWh):
  CO2 Emissions/Year:      {energy_per_year * 0.5:.2f} kg
  Equivalent Trees:        {energy_per_year * 0.5 / 20:.1f} trees needed to offset

{'='*70}
"""

        self.economic_text.delete(1.0, tk.END)
        self.economic_text.insert(1.0, results)

    def solve_problem_1(self):
        """Solve DC motor problem 1"""
        self.problems_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.problems_text.insert(tk.END, "SOLVING PROBLEM 1...\n")
        self.problems_text.insert(tk.END, "="*70 + "\n")

        result = DCMotorProblems.problem_1()

        # Redirect print output
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        DCMotorProblems.problem_1()
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        self.problems_text.insert(tk.END, output)
        self.problems_text.see(tk.END)

    def solve_problem_2(self):
        """Solve DC motor problem 2"""
        self.problems_text.insert(tk.END, "\n" + "="*70 + "\n")
        self.problems_text.insert(tk.END, "SOLVING PROBLEM 2...\n")
        self.problems_text.insert(tk.END, "="*70 + "\n")

        # Redirect print output
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        DCMotorProblems.problem_2()
        output = sys.stdout.getvalue()

        sys.stdout = old_stdout

        self.problems_text.insert(tk.END, output)
        self.problems_text.see(tk.END)

    def clear_problems_output(self):
        """Clear problems output"""
        self.problems_text.delete(1.0, tk.END)

    def save_results(self):
        """Save simulation results"""
        if len(self.sim_data['t']) == 0:
            messagebox.showwarning("Warning", "No simulation data to save!")
            return

        filename = f"motor_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, 'w') as f:
            f.write("DC Motor Simulation Results\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("Parameters:\n")
            for key, value in self.params.items():
                f.write(f"  {key}: {value}\n")

            f.write("\n" + "="*70 + "\n")
            f.write("Time Series Data:\n")
            f.write("="*70 + "\n")
            f.write("Time(s), Ia(A), If(A), Speed(rpm), Torque(Nm), Temp(C), Eff(%)\n")

            for i in range(len(self.sim_data['t'])):
                f.write(f"{self.sim_data['t'][i]:.3f}, ")
                f.write(f"{self.sim_data['Ia'][i]:.3f}, ")
                f.write(f"{self.sim_data['If'][i]:.3f}, ")
                f.write(f"{self.sim_data['N'][i]:.2f}, ")
                f.write(f"{self.sim_data['Te'][i]:.3f}, ")
                f.write(f"{self.sim_data['T_motor'][i]:.2f}, ")
                f.write(f"{self.sim_data['efficiency'][i]:.2f}\n")

        messagebox.showinfo("Success", f"Results saved to {filename}")
        self.update_status(f"Results saved to {filename}")

    def load_parameters(self):
        """Load parameters"""
        messagebox.showinfo("Info", "Load parameters feature - to be implemented")

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced DC Motor Simulator
Version 1.0

Multi-Physics Analysis Tool for DC Motors

Features:
• Dynamic simulation with RK45/Euler solvers
• Electromagnetic-thermal-mechanical coupling
• Real-time visualization
• Economic analysis
• Loss breakdown and efficiency analysis
• DC motor problem solver

Developed for Advanced Electrical Engineering Applications
        """
        messagebox.showinfo("About", about_text)

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)

    def on_window_resize(self, event):
        """Handle window resize"""
        # Auto-scale plots when window is resized
        if hasattr(self, 'dynamics_canvas'):
            self.dynamics_canvas.draw()
        if hasattr(self, 'thermal_canvas'):
            self.thermal_canvas.draw()
        if hasattr(self, 'losses_canvas'):
            self.losses_canvas.draw()

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main function"""
    # Print problem solutions to console
    print("\n" + "="*70)
    print("DC MOTOR ADVANCED SIMULATOR")
    print("="*70)
    print("\nSolving DC Motor Problems...")

    # Solve problems
    DCMotorProblems.problem_1()
    DCMotorProblems.problem_2()

    print("\n" + "="*70)
    print("Launching GUI Application...")
    print("="*70 + "\n")

    # Create GUI
    root = tk.Tk()
    app = DCMotorSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

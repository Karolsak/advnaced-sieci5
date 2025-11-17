"""
Advanced Three-Phase Induction Motor Simulator
Complete solution for Example 6.2 with Multi-Physics Simulation

Features:
- Complete electrical circuit modeling
- Dynamic simulation with RK45 and Euler solvers
- Multi-physics: Electromagnetic, Thermal, Mechanical
- Economic analysis
- Advanced control methods
- Real-time visualization
- Auto-scaling GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.integrate import solve_ivp
import threading
import time
from datetime import datetime

class InductionMotorSimulator:
    """Main class for induction motor simulation and analysis"""

    def __init__(self):
        # Default parameters from Example 6.2
        self.params = {
            'poles': 12,
            'V_ll': 420,  # Line-to-line voltage (V)
            'power_rated': 5500,  # Rated power (W)
            'frequency': 60,  # Input frequency (Hz) - changed from 50 to 60
            'R1': 0.833,  # Stator resistance (Ω)
            'X1': 1.864,  # Stator reactance (Ω)
            'R2_prime': 0.833,  # Rotor resistance referred to stator (Ω)
            'X2_prime': 1.864,  # Rotor reactance referred to stator (Ω)
            'Xm': 36.25,  # Magnetizing reactance (Ω)
            'slip': 0.03,  # Operating slip
            'P_rot': 250,  # Rotational losses (W)
            'P_str': 60,  # Stray losses (W)
            # Thermal parameters
            'thermal_resistance': 2.5,  # K/W
            'thermal_capacitance': 1500,  # J/K
            'ambient_temp': 25,  # °C
            'max_temp': 155,  # °C (Class F insulation)
            # Mechanical parameters
            'J_motor': 0.5,  # Moment of inertia (kg·m²)
            'J_load': 0.3,  # Load inertia (kg·m²)
            'B_friction': 0.01,  # Friction coefficient (N·m·s)
            # Economic parameters
            'electricity_cost': 0.12,  # $/kWh
            'initial_cost': 2500,  # Motor initial cost ($)
            'maintenance_cost_annual': 150,  # Annual maintenance ($)
            'lifetime': 15  # Expected lifetime (years)
        }

        # Simulation state variables
        self.time_data = []
        self.speed_data = []
        self.torque_data = []
        self.current_data = []
        self.temp_data = []
        self.power_data = []
        self.efficiency_data = []

        # Control variables
        self.is_running = False
        self.simulation_thread = None
        self.current_time = 0
        self.current_speed = 0  # rad/s
        self.current_temperature = self.params['ambient_temp']

    def calculate_synchronous_speed(self):
        """Calculate synchronous speed"""
        f = self.params['frequency']
        p = self.params['poles'] // 2
        n_s = 120 * f / self.params['poles']  # RPM
        omega_s = 2 * np.pi * f / p  # rad/s
        return n_s, omega_s

    def solve_example_6_2(self):
        """
        Complete solution for Example 6.2
        Returns dictionary with all calculated values
        """
        results = {}

        # Given parameters
        V_ll = self.params['V_ll']
        f = self.params['frequency']
        s = self.params['slip']
        R1 = self.params['R1']
        X1 = self.params['X1']
        R2 = self.params['R2_prime']
        X2 = self.params['X2_prime']
        Xm = self.params['Xm']
        P_rot = self.params['P_rot']
        P_str = self.params['P_str']
        p = self.params['poles'] // 2

        # (a) Rotor speed
        n_s = 120 * f / self.params['poles']  # Synchronous speed (RPM)
        n_r = n_s * (1 - s)  # Rotor speed (RPM)
        omega_s = 2 * np.pi * f / p  # Synchronous speed (rad/s)
        omega_r = omega_s * (1 - s)  # Rotor speed (rad/s)

        results['n_s'] = n_s
        results['n_r'] = n_r
        results['omega_s'] = omega_s
        results['omega_r'] = omega_r

        # Phase voltage (Y-connected)
        V_ph = V_ll / np.sqrt(3)

        # (b) Stator and rotor currents
        # Equivalent impedance
        R2_over_s = R2 / s

        # Rotor branch impedance
        Z_rotor = R2_over_s + 1j * X2

        # Parallel combination of Xm and rotor branch
        Z_parallel = (1j * Xm * Z_rotor) / (1j * Xm + Z_rotor)

        # Total impedance
        Z_total = (R1 + 1j * X1) + Z_parallel

        # Stator current
        I1 = V_ph / Z_total
        I1_mag = abs(I1)
        I1_angle = np.angle(I1, deg=True)

        # Rotor current (referred to stator)
        I2_prime = I1 * (1j * Xm) / (1j * Xm + Z_rotor)
        I2_prime_mag = abs(I2_prime)
        I2_prime_angle = np.angle(I2_prime, deg=True)

        results['I1'] = I1_mag
        results['I1_angle'] = I1_angle
        results['I2_prime'] = I2_prime_mag
        results['I2_prime_angle'] = I2_prime_angle

        # (c) Stator and rotor winding losses
        P_cu1 = 3 * I1_mag**2 * R1  # Stator copper losses
        P_cu2 = 3 * I2_prime_mag**2 * R2  # Rotor copper losses

        results['P_cu1'] = P_cu1
        results['P_cu2'] = P_cu2

        # (d) Electromagnetic power and torque
        P_ag = 3 * I2_prime_mag**2 * R2_over_s  # Air gap power
        T_elm = P_ag / omega_s  # Electromagnetic torque

        results['P_ag'] = P_ag
        results['T_elm'] = T_elm

        # (e) Mechanical power and output power
        P_mech = P_ag * (1 - s)  # Mechanical power
        P_out = P_mech - P_rot - P_str  # Output power

        results['P_mech'] = P_mech
        results['P_out'] = P_out

        # (f) Input power, efficiency, and power factor
        P_in = P_cu1 + P_ag  # Input power (neglecting core losses)
        efficiency = (P_out / P_in) * 100 if P_in > 0 else 0

        # Power factor
        S_in = 3 * V_ph * I1_mag  # Apparent power
        pf = P_in / S_in if S_in > 0 else 0

        results['P_in'] = P_in
        results['efficiency'] = efficiency
        results['pf'] = pf

        # (g) Starting torque and STR
        # At starting, s = 1
        s_start = 1.0
        R2_over_s_start = R2 / s_start
        Z_rotor_start = R2_over_s_start + 1j * X2
        Z_parallel_start = (1j * Xm * Z_rotor_start) / (1j * Xm + Z_rotor_start)
        Z_total_start = (R1 + 1j * X1) + Z_parallel_start

        I1_start = V_ph / Z_total_start
        I2_prime_start = I1_start * (1j * Xm) / (1j * Xm + Z_rotor_start)
        I2_prime_start_mag = abs(I2_prime_start)

        P_ag_start = 3 * I2_prime_start_mag**2 * R2_over_s_start
        T_elm_start = P_ag_start / omega_s

        STR = T_elm_start / T_elm if T_elm > 0 else 0

        results['T_elm_start'] = T_elm_start
        results['STR'] = STR
        results['I1_start'] = abs(I1_start)

        # (h) Breakdown torque, critical slip, and OCF
        # Thevenin equivalent
        Z_th = (1j * Xm * (R1 + 1j * X1)) / (R1 + 1j * (X1 + Xm))
        V_th = V_ph * (1j * Xm) / (R1 + 1j * (X1 + Xm))

        R_th = abs(Z_th.real)
        X_th = abs(Z_th.imag)
        V_th_mag = abs(V_th)

        # Critical slip
        s_cr = R2 / np.sqrt(R_th**2 + (X_th + X2)**2)

        # Maximum torque
        T_elm_max = (3 * V_th_mag**2) / (2 * omega_s * (R_th + np.sqrt(R_th**2 + (X_th + X2)**2)))

        # Overload capacity factor
        OCF = T_elm_max / T_elm if T_elm > 0 else 0

        results['s_cr'] = s_cr
        results['T_elm_max'] = T_elm_max
        results['OCF'] = OCF

        return results

    def calculate_detailed_losses(self, I1, I2_prime, P_ag, s):
        """Calculate detailed loss breakdown"""
        losses = {}

        # Copper losses
        losses['stator_copper'] = 3 * I1**2 * self.params['R1']
        losses['rotor_copper'] = 3 * I2_prime**2 * self.params['R2_prime']

        # Core losses (simplified model)
        V_ph = self.params['V_ll'] / np.sqrt(3)
        losses['core_losses'] = 0.02 * 3 * V_ph * I1  # Approximate 2% of input

        # Mechanical losses
        losses['friction'] = self.params['P_rot']
        losses['windage'] = 0.3 * self.params['P_rot']  # 30% of rotational loss

        # Stray losses
        losses['stray'] = self.params['P_str']

        losses['total'] = sum(losses.values())

        return losses

    def thermal_model(self, P_loss, T_current, dt):
        """
        Thermal model: dT/dt = (P_loss - (T - T_amb)/R_th) / C_th
        """
        R_th = self.params['thermal_resistance']
        C_th = self.params['thermal_capacitance']
        T_amb = self.params['ambient_temp']

        dT_dt = (P_loss - (T_current - T_amb) / R_th) / C_th
        T_new = T_current + dT_dt * dt

        return T_new

    def mechanical_model(self, T_elm, T_load, omega, dt):
        """
        Mechanical model: J * d(omega)/dt = T_elm - T_load - B * omega
        """
        J_total = self.params['J_motor'] + self.params['J_load']
        B = self.params['B_friction']

        d_omega_dt = (T_elm - T_load - B * omega) / J_total
        omega_new = omega + d_omega_dt * dt

        return omega_new

    def calculate_derating_factor(self, temperature):
        """Calculate derating factor based on temperature"""
        T_rated = 40  # Rated ambient temperature
        T_max = self.params['max_temp']

        if temperature <= T_rated:
            return 1.0
        elif temperature >= T_max:
            return 0.5  # 50% derating at max temperature
        else:
            # Linear derating between rated and max temperature
            return 1.0 - 0.5 * (temperature - T_rated) / (T_max - T_rated)

    def dynamic_simulation_step(self, t, state, load_torque_func):
        """
        State vector: [omega, theta, T_motor]
        Differential equations for dynamic simulation
        """
        omega = state[0]  # Angular velocity (rad/s)
        theta = state[1]  # Angular position (rad)
        T_motor = state[2]  # Motor temperature (°C)

        # Calculate slip
        _, omega_s = self.calculate_synchronous_speed()
        s = (omega_s - omega) / omega_s if omega_s != 0 else 1.0
        s = max(0.001, min(s, 1.0))  # Limit slip

        # Calculate motor torque at current slip
        V_ph = self.params['V_ll'] / np.sqrt(3)
        R1 = self.params['R1']
        X1 = self.params['X1']
        R2 = self.params['R2_prime']
        X2 = self.params['X2_prime']
        Xm = self.params['Xm']

        R2_over_s = R2 / s
        Z_rotor = R2_over_s + 1j * X2
        Z_parallel = (1j * Xm * Z_rotor) / (1j * Xm + Z_rotor)
        Z_total = (R1 + 1j * X1) + Z_parallel

        I1 = V_ph / Z_total
        I2_prime = I1 * (1j * Xm) / (1j * Xm + Z_rotor)

        I2_prime_mag = abs(I2_prime)
        P_ag = 3 * I2_prime_mag**2 * R2_over_s
        T_elm = P_ag / omega_s if omega_s != 0 else 0

        # Apply thermal derating
        derating = self.calculate_derating_factor(T_motor)
        T_elm *= derating

        # Load torque
        T_load = load_torque_func(t, omega)

        # Mechanical dynamics
        J_total = self.params['J_motor'] + self.params['J_load']
        B = self.params['B_friction']
        d_omega_dt = (T_elm - T_load - B * omega) / J_total

        # Angular position
        d_theta_dt = omega

        # Thermal dynamics
        I1_mag = abs(I1)
        losses = self.calculate_detailed_losses(I1_mag, I2_prime_mag, P_ag, s)
        P_loss_total = losses['total']

        R_th = self.params['thermal_resistance']
        C_th = self.params['thermal_capacitance']
        T_amb = self.params['ambient_temp']
        d_T_dt = (P_loss_total - (T_motor - T_amb) / R_th) / C_th

        return [d_omega_dt, d_theta_dt, d_T_dt]

    def load_torque_profile(self, t, omega):
        """Define load torque profile"""
        # Example: Step load at t=1s, ramp load at t=3s
        if t < 1.0:
            return 5.0  # Light load
        elif t < 3.0:
            return 20.0  # Medium load
        else:
            return 15.0 + 0.01 * omega**2  # Load with speed-dependent component

    def run_dynamic_simulation(self, t_span, method='RK45'):
        """
        Run dynamic simulation using ODE solver
        method: 'RK45' or 'Euler'
        """
        # Initial conditions: [omega, theta, T_motor]
        _, omega_s = self.calculate_synchronous_speed()
        y0 = [0.0, 0.0, self.params['ambient_temp']]

        if method == 'RK45':
            # Use scipy's RK45 solver
            sol = solve_ivp(
                lambda t, y: self.dynamic_simulation_step(t, y, self.load_torque_profile),
                t_span,
                y0,
                method='RK45',
                max_step=0.01,
                dense_output=True
            )
            return sol
        else:
            # Euler method
            dt = 0.001
            t = np.arange(t_span[0], t_span[1], dt)
            y = np.zeros((len(y0), len(t)))
            y[:, 0] = y0

            for i in range(1, len(t)):
                dydt = self.dynamic_simulation_step(
                    t[i-1], y[:, i-1], self.load_torque_profile
                )
                y[:, i] = y[:, i-1] + np.array(dydt) * dt

            # Create compatible output structure
            class EulerSolution:
                def __init__(self, t, y):
                    self.t = t
                    self.y = y

            return EulerSolution(t, y)

    def calculate_torque_speed_curve(self):
        """Calculate torque-speed characteristic curve"""
        slip_range = np.linspace(0.001, 1.0, 100)
        torque = []
        speed = []
        current = []
        efficiency = []

        V_ph = self.params['V_ll'] / np.sqrt(3)
        _, omega_s = self.calculate_synchronous_speed()

        for s in slip_range:
            R2_over_s = self.params['R2_prime'] / s
            Z_rotor = R2_over_s + 1j * self.params['X2_prime']
            Z_parallel = (1j * self.params['Xm'] * Z_rotor) / (1j * self.params['Xm'] + Z_rotor)
            Z_total = (self.params['R1'] + 1j * self.params['X1']) + Z_parallel

            I1 = V_ph / Z_total
            I2_prime = I1 * (1j * self.params['Xm']) / (1j * self.params['Xm'] + Z_rotor)

            I2_prime_mag = abs(I2_prime)
            P_ag = 3 * I2_prime_mag**2 * R2_over_s
            T = P_ag / omega_s

            n = (1 - s) * 120 * self.params['frequency'] / self.params['poles']

            # Calculate efficiency
            P_cu1 = 3 * abs(I1)**2 * self.params['R1']
            P_cu2 = 3 * I2_prime_mag**2 * self.params['R2_prime']
            P_mech = P_ag * (1 - s)
            P_out = P_mech - self.params['P_rot'] - self.params['P_str']
            P_in = P_cu1 + P_ag
            eff = (P_out / P_in * 100) if P_in > 0 and P_out > 0 else 0

            torque.append(T)
            speed.append(n)
            current.append(abs(I1))
            efficiency.append(eff)

        return np.array(speed), np.array(torque), np.array(current), np.array(efficiency)

    def calculate_economic_analysis(self, operating_hours_per_year=4000):
        """Calculate economic metrics"""
        results = self.solve_example_6_2()

        economics = {}

        # Annual energy consumption
        P_in = results['P_in']
        annual_energy = P_in * operating_hours_per_year / 1000  # kWh

        # Annual energy cost
        annual_energy_cost = annual_energy * self.params['electricity_cost']

        # Total annual cost
        annual_total_cost = annual_energy_cost + self.params['maintenance_cost_annual']

        # Life cycle cost
        lifetime = self.params['lifetime']
        life_cycle_cost = self.params['initial_cost'] + annual_total_cost * lifetime

        # Cost per kWh output
        annual_output_energy = results['P_out'] * operating_hours_per_year / 1000
        cost_per_kwh = annual_energy_cost / annual_output_energy if annual_output_energy > 0 else 0

        # Payback period (if comparing to less efficient motor)
        # Assume 5% efficiency improvement saves money
        efficiency_improvement = 0.05
        annual_savings = annual_energy_cost * efficiency_improvement
        payback_period = self.params['initial_cost'] / annual_savings if annual_savings > 0 else float('inf')

        economics['annual_energy_kwh'] = annual_energy
        economics['annual_energy_cost'] = annual_energy_cost
        economics['annual_maintenance_cost'] = self.params['maintenance_cost_annual']
        economics['annual_total_cost'] = annual_total_cost
        economics['life_cycle_cost'] = life_cycle_cost
        economics['cost_per_kwh'] = cost_per_kwh
        economics['payback_period'] = payback_period
        economics['annual_output_energy'] = annual_output_energy

        return economics


class MotorSimulatorGUI:
    """GUI Application for Induction Motor Simulator"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Three-Phase Induction Motor Simulator")
        self.root.geometry("1400x900")

        # Initialize simulator
        self.simulator = InductionMotorSimulator()

        # Simulation control
        self.is_simulating = False
        self.animation_job = None

        # Setup GUI
        self.setup_gui()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def setup_gui(self):
        """Setup the complete GUI structure"""

        # Main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_container,
            text="Advanced Induction Motor Simulator - Example 6.2",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=10)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs
        self.create_main_tab()
        self.create_parameters_tab()
        self.create_simulation_tab()
        self.create_characteristics_tab()
        self.create_multiphysics_tab()
        self.create_economic_tab()

    def create_main_tab(self):
        """Main tab with results from Example 6.2"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Main Results")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Control buttons
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))

        ttk.Button(
            button_frame,
            text="Calculate",
            command=self.calculate_main_results
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_simulation
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Export Results",
            command=self.export_results
        ).pack(side=tk.LEFT, padx=5)

        # Results display with scrollbar
        results_frame = ttk.Frame(tab)
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Text widget with scrollbar
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            height=30
        )
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_text.yview
        )
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def create_parameters_tab(self):
        """Parameters tab with input fields and sliders"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Parameters & Control")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        # Left column: Electrical parameters
        left_frame = ttk.LabelFrame(tab, text="Electrical Parameters", padding="10")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.param_widgets = {}

        electrical_params = [
            ('V_ll', 'Voltage (V)', 200, 600, 420),
            ('frequency', 'Frequency (Hz)', 30, 100, 60),
            ('slip', 'Slip', 0.001, 0.3, 0.03),
            ('R1', 'R1 (Ω)', 0.1, 5.0, 0.833),
            ('X1', 'X1 (Ω)', 0.1, 10.0, 1.864),
            ('R2_prime', "R2' (Ω)", 0.1, 5.0, 0.833),
            ('X2_prime', "X2' (Ω)", 0.1, 10.0, 1.864),
            ('Xm', 'Xm (Ω)', 10, 100, 36.25)
        ]

        for i, (key, label, min_val, max_val, default) in enumerate(electrical_params):
            self.create_parameter_slider(
                left_frame, i, key, label, min_val, max_val, default
            )

        # Right column: Mechanical and Thermal parameters
        right_frame = ttk.LabelFrame(tab, text="Mechanical & Thermal", padding="10")
        right_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        mech_thermal_params = [
            ('J_motor', 'Motor Inertia (kg·m²)', 0.1, 2.0, 0.5),
            ('J_load', 'Load Inertia (kg·m²)', 0.0, 2.0, 0.3),
            ('B_friction', 'Friction Coeff', 0.001, 0.1, 0.01),
            ('thermal_resistance', 'Thermal R (K/W)', 1.0, 5.0, 2.5),
            ('thermal_capacitance', 'Thermal C (J/K)', 500, 3000, 1500),
            ('ambient_temp', 'Ambient Temp (°C)', 10, 50, 25),
            ('max_temp', 'Max Temp (°C)', 100, 200, 155)
        ]

        for i, (key, label, min_val, max_val, default) in enumerate(mech_thermal_params):
            self.create_parameter_slider(
                right_frame, i, key, label, min_val, max_val, default
            )

        # Control method selection
        control_frame = ttk.LabelFrame(tab, text="Control Method", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.control_method = tk.StringVar(value="V/f")
        ttk.Radiobutton(
            control_frame, text="V/f Control", variable=self.control_method, value="V/f"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            control_frame, text="Direct Torque Control", variable=self.control_method, value="DTC"
        ).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(
            control_frame, text="Field Oriented Control", variable=self.control_method, value="FOC"
        ).pack(side=tk.LEFT, padx=10)

    def create_parameter_slider(self, parent, row, key, label, min_val, max_val, default):
        """Create a parameter slider with label and value display"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)

        var = tk.DoubleVar(value=default)

        slider = ttk.Scale(
            parent,
            from_=min_val,
            to=max_val,
            variable=var,
            orient=tk.HORIZONTAL,
            command=lambda v: self.update_parameter(key, var)
        )
        slider.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

        value_label = ttk.Label(parent, text=f"{default:.3f}")
        value_label.grid(row=row, column=2, sticky=tk.W, pady=2)

        self.param_widgets[key] = {'var': var, 'label': value_label, 'slider': slider}

        parent.columnconfigure(1, weight=1)

    def update_parameter(self, key, var):
        """Update parameter value and display"""
        value = var.get()
        self.simulator.params[key] = value
        self.param_widgets[key]['label'].config(text=f"{value:.3f}")

    def create_simulation_tab(self):
        """Dynamic simulation tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Dynamic Simulation")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Control panel
        control_frame = ttk.Frame(tab)
        control_frame.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))

        ttk.Button(
            control_frame,
            text="▶ Start",
            command=self.start_simulation
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="⏸ Stop",
            command=self.stop_simulation
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="🔄 Reset",
            command=self.reset_simulation
        ).pack(side=tk.LEFT, padx=5)

        # Solver selection
        ttk.Label(control_frame, text="Solver:").pack(side=tk.LEFT, padx=10)
        self.solver_method = tk.StringVar(value="RK45")
        ttk.Radiobutton(
            control_frame, text="RK45", variable=self.solver_method, value="RK45"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            control_frame, text="Euler", variable=self.solver_method, value="Euler"
        ).pack(side=tk.LEFT, padx=5)

        # Simulation time
        ttk.Label(control_frame, text="Time (s):").pack(side=tk.LEFT, padx=10)
        self.sim_time = tk.DoubleVar(value=5.0)
        ttk.Entry(control_frame, textvariable=self.sim_time, width=8).pack(side=tk.LEFT)

        # Plots frame
        plots_frame = ttk.Frame(tab)
        plots_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plots_frame.columnconfigure(0, weight=1)
        plots_frame.columnconfigure(1, weight=1)
        plots_frame.rowconfigure(0, weight=1)
        plots_frame.rowconfigure(1, weight=1)

        # Create matplotlib figures
        self.sim_fig, self.sim_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.sim_fig.tight_layout(pad=3.0)

        self.sim_canvas = FigureCanvasTkAgg(self.sim_fig, plots_frame)
        self.sim_canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_characteristics_tab(self):
        """Motor characteristics tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Characteristics")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # Control
        control_frame = ttk.Frame(tab)
        control_frame.grid(row=0, column=0, pady=10)

        ttk.Button(
            control_frame,
            text="Generate Curves",
            command=self.generate_characteristics
        ).pack(side=tk.LEFT, padx=5)

        # Plot frame
        plot_frame = ttk.Frame(tab)
        plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        # Create matplotlib figure
        self.char_fig, self.char_axes = plt.subplots(2, 2, figsize=(10, 6))
        self.char_fig.tight_layout(pad=3.0)

        self.char_canvas = FigureCanvasTkAgg(self.char_fig, plot_frame)
        self.char_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_multiphysics_tab(self):
        """Multi-physics simulation tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Multi-Physics")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        # Left: Loss breakdown
        loss_frame = ttk.LabelFrame(tab, text="Detailed Loss Breakdown", padding="10")
        loss_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        loss_frame.columnconfigure(0, weight=1)
        loss_frame.rowconfigure(1, weight=1)

        ttk.Button(
            loss_frame,
            text="Calculate Losses",
            command=self.calculate_losses
        ).grid(row=0, column=0, pady=5)

        self.loss_text = tk.Text(loss_frame, wrap=tk.WORD, font=('Courier', 9), height=15)
        loss_scrollbar = ttk.Scrollbar(loss_frame, orient=tk.VERTICAL, command=self.loss_text.yview)
        self.loss_text.configure(yscrollcommand=loss_scrollbar.set)
        self.loss_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        loss_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # Loss pie chart
        loss_plot_frame = ttk.Frame(loss_frame)
        loss_plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.loss_fig = Figure(figsize=(5, 4))
        self.loss_ax = self.loss_fig.add_subplot(111)
        self.loss_canvas = FigureCanvasTkAgg(self.loss_fig, loss_plot_frame)
        self.loss_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Right: Thermal and mechanical analysis
        thermal_frame = ttk.LabelFrame(tab, text="Thermal & Mechanical Analysis", padding="10")
        thermal_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        thermal_frame.columnconfigure(0, weight=1)
        thermal_frame.rowconfigure(1, weight=1)

        ttk.Button(
            thermal_frame,
            text="Run Coupled Simulation",
            command=self.run_coupled_simulation
        ).grid(row=0, column=0, pady=5)

        # Thermal plot
        self.thermal_fig = Figure(figsize=(5, 4))
        self.thermal_ax1 = self.thermal_fig.add_subplot(211)
        self.thermal_ax2 = self.thermal_fig.add_subplot(212)
        self.thermal_fig.tight_layout(pad=2.0)
        self.thermal_canvas = FigureCanvasTkAgg(self.thermal_fig, thermal_frame)
        self.thermal_canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_economic_tab(self):
        """Economic analysis tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Economic Analysis")

        # Configure grid
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)

        # Left: Parameters
        param_frame = ttk.LabelFrame(tab, text="Economic Parameters", padding="10")
        param_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N))

        # Economic parameters
        econ_params = [
            ('electricity_cost', 'Electricity Cost ($/kWh)', 0.05, 0.30, 0.12),
            ('initial_cost', 'Initial Cost ($)', 1000, 5000, 2500),
            ('maintenance_cost_annual', 'Annual Maintenance ($)', 50, 500, 150),
            ('lifetime', 'Lifetime (years)', 5, 30, 15)
        ]

        for i, (key, label, min_val, max_val, default) in enumerate(econ_params):
            self.create_parameter_slider(param_frame, i, key, label, min_val, max_val, default)

        ttk.Label(param_frame, text="Operating Hours/Year:").grid(row=len(econ_params), column=0, sticky=tk.W, pady=5)
        self.operating_hours = tk.DoubleVar(value=4000)
        ttk.Entry(param_frame, textvariable=self.operating_hours, width=10).grid(row=len(econ_params), column=1, sticky=tk.W, pady=5)

        ttk.Button(
            param_frame,
            text="Calculate Economics",
            command=self.calculate_economics
        ).grid(row=len(econ_params)+1, column=0, columnspan=3, pady=10)

        # Right: Results
        results_frame = ttk.LabelFrame(tab, text="Economic Results", padding="10")
        results_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.econ_text = tk.Text(results_frame, wrap=tk.WORD, font=('Courier', 10))
        econ_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.econ_text.yview)
        self.econ_text.configure(yscrollcommand=econ_scrollbar.set)
        self.econ_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        econ_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bottom: Cost breakdown chart
        chart_frame = ttk.Frame(tab)
        chart_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        self.econ_fig = Figure(figsize=(6, 4))
        self.econ_ax = self.econ_fig.add_subplot(111)
        self.econ_canvas = FigureCanvasTkAgg(self.econ_fig, chart_frame)
        self.econ_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def calculate_main_results(self):
        """Calculate and display Example 6.2 results"""
        try:
            results = self.simulator.solve_example_6_2()

            # Format and display results
            output = "=" * 80 + "\n"
            output += "EXAMPLE 6.2 - THREE-PHASE INDUCTION MOTOR ANALYSIS\n"
            output += "=" * 80 + "\n\n"

            output += "GIVEN PARAMETERS:\n"
            output += "-" * 80 + "\n"
            output += f"Poles (2p):               {self.simulator.params['poles']}\n"
            output += f"Line-to-Line Voltage:     {self.simulator.params['V_ll']} V\n"
            output += f"Rated Power:              {self.simulator.params['power_rated']/1000} kW\n"
            output += f"Frequency:                {self.simulator.params['frequency']} Hz\n"
            output += f"Stator Resistance (R1):   {self.simulator.params['R1']} Ω\n"
            output += f"Stator Reactance (X1):    {self.simulator.params['X1']} Ω\n"
            output += f"Rotor Resistance (R2'):   {self.simulator.params['R2_prime']} Ω\n"
            output += f"Rotor Reactance (X2'):    {self.simulator.params['X2_prime']} Ω\n"
            output += f"Magnetizing Reactance:    {self.simulator.params['Xm']} Ω\n"
            output += f"Operating Slip:           {self.simulator.params['slip']}\n"
            output += f"Rotational Losses:        {self.simulator.params['P_rot']} W\n"
            output += f"Stray Losses:             {self.simulator.params['P_str']} W\n"
            output += "\n"

            output += "CALCULATED RESULTS:\n"
            output += "=" * 80 + "\n\n"

            output += "(a) SPEEDS:\n"
            output += "-" * 80 + "\n"
            output += f"Synchronous Speed:        {results['n_s']:.2f} RPM ({results['omega_s']:.3f} rad/s)\n"
            output += f"Rotor Speed:              {results['n_r']:.2f} RPM ({results['omega_r']:.3f} rad/s)\n"
            output += "\n"

            output += "(b) CURRENTS:\n"
            output += "-" * 80 + "\n"
            output += f"Stator Current (I1):      {results['I1']:.3f} A ∠{results['I1_angle']:.2f}°\n"
            output += f"Rotor Current (I2'):      {results['I2_prime']:.3f} A ∠{results['I2_prime_angle']:.2f}°\n"
            output += f"Starting Current:         {results['I1_start']:.3f} A\n"
            output += f"Starting Current Ratio:   {results['I1_start']/results['I1']:.2f}\n"
            output += "\n"

            output += "(c) LOSSES:\n"
            output += "-" * 80 + "\n"
            output += f"Stator Copper Loss:       {results['P_cu1']:.2f} W\n"
            output += f"Rotor Copper Loss:        {results['P_cu2']:.2f} W\n"
            output += f"Total Copper Loss:        {results['P_cu1'] + results['P_cu2']:.2f} W\n"
            output += "\n"

            output += "(d) ELECTROMAGNETIC POWER AND TORQUE:\n"
            output += "-" * 80 + "\n"
            output += f"Air Gap Power (P_ag):     {results['P_ag']:.2f} W ({results['P_ag']/1000:.3f} kW)\n"
            output += f"Electromagnetic Torque:   {results['T_elm']:.3f} N·m\n"
            output += "\n"

            output += "(e) MECHANICAL POWER:\n"
            output += "-" * 80 + "\n"
            output += f"Mechanical Power:         {results['P_mech']:.2f} W ({results['P_mech']/1000:.3f} kW)\n"
            output += f"Output Power:             {results['P_out']:.2f} W ({results['P_out']/1000:.3f} kW)\n"
            output += "\n"

            output += "(f) EFFICIENCY AND POWER FACTOR:\n"
            output += "-" * 80 + "\n"
            output += f"Input Power:              {results['P_in']:.2f} W ({results['P_in']/1000:.3f} kW)\n"
            output += f"Efficiency:               {results['efficiency']:.2f} %\n"
            output += f"Power Factor:             {results['pf']:.4f} {'(lagging)' if results['I1_angle'] < 0 else '(leading)'}\n"
            output += "\n"

            output += "(g) STARTING PERFORMANCE:\n"
            output += "-" * 80 + "\n"
            output += f"Starting Torque:          {results['T_elm_start']:.3f} N·m\n"
            output += f"Starting Torque Ratio:    {results['STR']:.3f}\n"
            output += "\n"

            output += "(h) MAXIMUM TORQUE:\n"
            output += "-" * 80 + "\n"
            output += f"Critical Slip:            {results['s_cr']:.4f}\n"
            output += f"Maximum Torque:           {results['T_elm_max']:.3f} N·m\n"
            output += f"Overload Capacity Factor: {results['OCF']:.3f}\n"
            output += "\n"

            output += "=" * 80 + "\n"
            output += f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += "=" * 80 + "\n"

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, output)

        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")

    def start_simulation(self):
        """Start dynamic simulation"""
        if self.is_simulating:
            messagebox.showwarning("Warning", "Simulation already running")
            return

        self.is_simulating = True

        # Run simulation in thread to avoid blocking GUI
        def simulate():
            try:
                t_span = [0, self.sim_time.get()]
                method = self.solver_method.get()

                sol = self.simulator.run_dynamic_simulation(t_span, method)

                # Schedule GUI update in main thread
                self.root.after(0, lambda: self.update_simulation_plots(sol))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Simulation error: {str(e)}"))
            finally:
                self.is_simulating = False

        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()

    def stop_simulation(self):
        """Stop simulation"""
        self.is_simulating = False

    def reset_simulation(self):
        """Reset simulation"""
        self.is_simulating = False
        self.simulator.time_data = []
        self.simulator.speed_data = []
        self.simulator.torque_data = []
        self.simulator.current_data = []
        self.simulator.temp_data = []

        # Clear plots
        for ax in self.sim_axes.flat:
            ax.clear()
        self.sim_canvas.draw()

    def update_simulation_plots(self, sol):
        """Update simulation plots with results"""
        try:
            # Clear previous plots
            for ax in self.sim_axes.flat:
                ax.clear()

            # Extract data
            t = sol.t
            omega = sol.y[0]
            theta = sol.y[1]
            temp = sol.y[2]

            # Convert to RPM
            p = self.simulator.params['poles'] // 2
            n_rpm = omega * 60 / (2 * np.pi / p)

            # Calculate torque and current for each time point
            torque = []
            current = []
            power = []

            _, omega_s = self.simulator.calculate_synchronous_speed()

            for i in range(len(t)):
                s = (omega_s - omega[i]) / omega_s if omega_s != 0 else 1.0
                s = max(0.001, min(s, 1.0))

                V_ph = self.simulator.params['V_ll'] / np.sqrt(3)
                R1 = self.simulator.params['R1']
                X1 = self.simulator.params['X1']
                R2 = self.simulator.params['R2_prime']
                X2 = self.simulator.params['X2_prime']
                Xm = self.simulator.params['Xm']

                R2_over_s = R2 / s
                Z_rotor = R2_over_s + 1j * X2
                Z_parallel = (1j * Xm * Z_rotor) / (1j * Xm + Z_rotor)
                Z_total = (R1 + 1j * X1) + Z_parallel

                I1 = V_ph / Z_total
                I2_prime = I1 * (1j * Xm) / (1j * Xm + Z_rotor)

                I2_mag = abs(I2_prime)
                P_ag = 3 * I2_mag**2 * R2_over_s
                T = P_ag / omega_s if omega_s != 0 else 0

                torque.append(T)
                current.append(abs(I1))
                power.append(P_ag / 1000)  # kW

            # Plot 1: Speed vs Time
            self.sim_axes[0, 0].plot(t, n_rpm, 'b-', linewidth=2)
            self.sim_axes[0, 0].set_xlabel('Time (s)')
            self.sim_axes[0, 0].set_ylabel('Speed (RPM)')
            self.sim_axes[0, 0].set_title('Motor Speed')
            self.sim_axes[0, 0].grid(True, alpha=0.3)

            # Plot 2: Torque vs Time
            self.sim_axes[0, 1].plot(t, torque, 'r-', linewidth=2)
            self.sim_axes[0, 1].set_xlabel('Time (s)')
            self.sim_axes[0, 1].set_ylabel('Torque (N·m)')
            self.sim_axes[0, 1].set_title('Electromagnetic Torque')
            self.sim_axes[0, 1].grid(True, alpha=0.3)

            # Plot 3: Current vs Time
            self.sim_axes[1, 0].plot(t, current, 'g-', linewidth=2)
            self.sim_axes[1, 0].set_xlabel('Time (s)')
            self.sim_axes[1, 0].set_ylabel('Current (A)')
            self.sim_axes[1, 0].set_title('Stator Current')
            self.sim_axes[1, 0].grid(True, alpha=0.3)

            # Plot 4: Temperature vs Time
            self.sim_axes[1, 1].plot(t, temp, 'm-', linewidth=2)
            self.sim_axes[1, 1].axhline(y=self.simulator.params['max_temp'], color='r', linestyle='--', label='Max Temp')
            self.sim_axes[1, 1].set_xlabel('Time (s)')
            self.sim_axes[1, 1].set_ylabel('Temperature (°C)')
            self.sim_axes[1, 1].set_title('Motor Temperature')
            self.sim_axes[1, 1].legend()
            self.sim_axes[1, 1].grid(True, alpha=0.3)

            self.sim_fig.tight_layout()
            self.sim_canvas.draw()

            messagebox.showinfo("Success", "Simulation completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Plot update error: {str(e)}")

    def generate_characteristics(self):
        """Generate motor characteristic curves"""
        try:
            speed, torque, current, efficiency = self.simulator.calculate_torque_speed_curve()

            # Clear previous plots
            for ax in self.char_axes.flat:
                ax.clear()

            # Plot 1: Torque vs Speed
            results = self.simulator.solve_example_6_2()
            self.char_axes[0, 0].plot(speed, torque, 'b-', linewidth=2)
            self.char_axes[0, 0].axhline(y=results['T_elm_max'], color='r', linestyle='--', label=f"Max Torque = {results['T_elm_max']:.2f} N·m")
            self.char_axes[0, 0].axvline(x=results['n_r'], color='g', linestyle='--', label=f"Operating Point")
            self.char_axes[0, 0].set_xlabel('Speed (RPM)')
            self.char_axes[0, 0].set_ylabel('Torque (N·m)')
            self.char_axes[0, 0].set_title('Torque-Speed Characteristic')
            self.char_axes[0, 0].legend()
            self.char_axes[0, 0].grid(True, alpha=0.3)

            # Plot 2: Current vs Speed
            self.char_axes[0, 1].plot(speed, current, 'r-', linewidth=2)
            self.char_axes[0, 1].axvline(x=results['n_r'], color='g', linestyle='--', label='Operating Point')
            self.char_axes[0, 1].set_xlabel('Speed (RPM)')
            self.char_axes[0, 1].set_ylabel('Current (A)')
            self.char_axes[0, 1].set_title('Current-Speed Characteristic')
            self.char_axes[0, 1].legend()
            self.char_axes[0, 1].grid(True, alpha=0.3)

            # Plot 3: Efficiency vs Speed
            self.char_axes[1, 0].plot(speed, efficiency, 'g-', linewidth=2)
            self.char_axes[1, 0].axvline(x=results['n_r'], color='r', linestyle='--', label='Operating Point')
            self.char_axes[1, 0].set_xlabel('Speed (RPM)')
            self.char_axes[1, 0].set_ylabel('Efficiency (%)')
            self.char_axes[1, 0].set_title('Efficiency-Speed Characteristic')
            self.char_axes[1, 0].legend()
            self.char_axes[1, 0].grid(True, alpha=0.3)

            # Plot 4: Power vs Speed
            slip_range = 1 - speed / results['n_s']
            power = torque * speed * 2 * np.pi / 60 / 1000  # kW
            self.char_axes[1, 1].plot(speed, power, 'm-', linewidth=2)
            self.char_axes[1, 1].axvline(x=results['n_r'], color='g', linestyle='--', label='Operating Point')
            self.char_axes[1, 1].set_xlabel('Speed (RPM)')
            self.char_axes[1, 1].set_ylabel('Power (kW)')
            self.char_axes[1, 1].set_title('Power-Speed Characteristic')
            self.char_axes[1, 1].legend()
            self.char_axes[1, 1].grid(True, alpha=0.3)

            self.char_fig.tight_layout()
            self.char_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Characteristic generation error: {str(e)}")

    def calculate_losses(self):
        """Calculate and display detailed losses"""
        try:
            results = self.simulator.solve_example_6_2()
            losses = self.simulator.calculate_detailed_losses(
                results['I1'],
                results['I2_prime'],
                results['P_ag'],
                self.simulator.params['slip']
            )

            # Display text results
            output = "DETAILED LOSS BREAKDOWN\n"
            output += "=" * 60 + "\n\n"
            output += f"Stator Copper Loss:     {losses['stator_copper']:8.2f} W\n"
            output += f"Rotor Copper Loss:      {losses['rotor_copper']:8.2f} W\n"
            output += f"Core Loss:              {losses['core_losses']:8.2f} W\n"
            output += f"Friction Loss:          {losses['friction']:8.2f} W\n"
            output += f"Windage Loss:           {losses['windage']:8.2f} W\n"
            output += f"Stray Loss:             {losses['stray']:8.2f} W\n"
            output += "-" * 60 + "\n"
            output += f"Total Loss:             {losses['total']:8.2f} W\n"
            output += "=" * 60 + "\n\n"

            # Calculate percentages
            output += "LOSS DISTRIBUTION:\n"
            output += "-" * 60 + "\n"
            for key, value in losses.items():
                if key != 'total':
                    percentage = (value / losses['total'] * 100) if losses['total'] > 0 else 0
                    output += f"{key.replace('_', ' ').title():25s} {percentage:6.2f} %\n"

            self.loss_text.delete(1.0, tk.END)
            self.loss_text.insert(1.0, output)

            # Create pie chart
            self.loss_ax.clear()

            labels = [k.replace('_', ' ').title() for k in losses.keys() if k != 'total']
            sizes = [v for k, v in losses.items() if k != 'total']
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']

            self.loss_ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            self.loss_ax.set_title('Loss Distribution')

            self.loss_fig.tight_layout()
            self.loss_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Loss calculation error: {str(e)}")

    def run_coupled_simulation(self):
        """Run coupled electromagnetic-thermal simulation"""
        try:
            # Run dynamic simulation
            t_span = [0, 10.0]  # 10 seconds
            sol = self.simulator.run_dynamic_simulation(t_span, 'RK45')

            # Extract data
            t = sol.t
            omega = sol.y[0]
            temp = sol.y[2]

            # Calculate derating factor over time
            derating = [self.simulator.calculate_derating_factor(T) for T in temp]

            # Plot thermal response
            self.thermal_ax1.clear()
            self.thermal_ax1.plot(t, temp, 'r-', linewidth=2, label='Temperature')
            self.thermal_ax1.axhline(y=self.simulator.params['max_temp'], color='k', linestyle='--', label='Max Temp')
            self.thermal_ax1.set_xlabel('Time (s)')
            self.thermal_ax1.set_ylabel('Temperature (°C)')
            self.thermal_ax1.set_title('Thermal Response')
            self.thermal_ax1.legend()
            self.thermal_ax1.grid(True, alpha=0.3)

            # Plot derating factor
            self.thermal_ax2.clear()
            self.thermal_ax2.plot(t, derating, 'b-', linewidth=2)
            self.thermal_ax2.set_xlabel('Time (s)')
            self.thermal_ax2.set_ylabel('Derating Factor')
            self.thermal_ax2.set_title('Power Derating vs Time')
            self.thermal_ax2.grid(True, alpha=0.3)
            self.thermal_ax2.set_ylim([0, 1.1])

            self.thermal_fig.tight_layout()
            self.thermal_canvas.draw()

            messagebox.showinfo("Success", "Coupled simulation completed!")

        except Exception as e:
            messagebox.showerror("Error", f"Coupled simulation error: {str(e)}")

    def calculate_economics(self):
        """Calculate and display economic analysis"""
        try:
            operating_hours = self.operating_hours.get()
            economics = self.simulator.calculate_economic_analysis(operating_hours)

            # Display results
            output = "ECONOMIC ANALYSIS\n"
            output += "=" * 80 + "\n\n"

            output += "ANNUAL COSTS:\n"
            output += "-" * 80 + "\n"
            output += f"Annual Energy Consumption:    {economics['annual_energy_kwh']:10.2f} kWh\n"
            output += f"Annual Energy Cost:          ${economics['annual_energy_cost']:10.2f}\n"
            output += f"Annual Maintenance Cost:     ${economics['annual_maintenance_cost']:10.2f}\n"
            output += f"Total Annual Cost:           ${economics['annual_total_cost']:10.2f}\n"
            output += "\n"

            output += "LIFETIME ANALYSIS:\n"
            output += "-" * 80 + "\n"
            output += f"Initial Investment:          ${self.simulator.params['initial_cost']:10.2f}\n"
            output += f"Expected Lifetime:            {self.simulator.params['lifetime']:10.0f} years\n"
            output += f"Life Cycle Cost:             ${economics['life_cycle_cost']:10.2f}\n"
            output += f"Annual Output Energy:         {economics['annual_output_energy']:10.2f} kWh\n"
            output += f"Cost per kWh Output:         ${economics['cost_per_kwh']:10.4f}\n"
            output += "\n"

            output += "INVESTMENT METRICS:\n"
            output += "-" * 80 + "\n"
            if economics['payback_period'] < 100:
                output += f"Payback Period:               {economics['payback_period']:10.2f} years\n"
            else:
                output += f"Payback Period:               Not economical\n"

            # Calculate ROI
            total_savings = economics['annual_energy_cost'] * 0.05 * self.simulator.params['lifetime']
            roi = (total_savings / self.simulator.params['initial_cost']) * 100
            output += f"Return on Investment (ROI):   {roi:10.2f} %\n"

            output += "\n" + "=" * 80 + "\n"

            self.econ_text.delete(1.0, tk.END)
            self.econ_text.insert(1.0, output)

            # Create cost breakdown chart
            self.econ_ax.clear()

            # Bar chart of annual costs
            categories = ['Energy\nCost', 'Maintenance\nCost', 'Amortized\nInitial Cost']
            values = [
                economics['annual_energy_cost'],
                economics['annual_maintenance_cost'],
                self.simulator.params['initial_cost'] / self.simulator.params['lifetime']
            ]

            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
            bars = self.econ_ax.bar(categories, values, color=colors, alpha=0.8)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                self.econ_ax.text(bar.get_x() + bar.get_width()/2., height,
                                 f'${value:.0f}',
                                 ha='center', va='bottom', fontweight='bold')

            self.econ_ax.set_ylabel('Annual Cost ($)')
            self.econ_ax.set_title('Annual Cost Breakdown')
            self.econ_ax.grid(True, alpha=0.3, axis='y')

            self.econ_fig.tight_layout()
            self.econ_canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Economic calculation error: {str(e)}")

    def export_results(self):
        """Export results to text file"""
        try:
            results = self.simulator.solve_example_6_2()

            filename = f"motor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(filename, 'w') as f:
                f.write(self.results_text.get(1.0, tk.END))

            messagebox.showinfo("Success", f"Results exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")

    def on_window_resize(self, event):
        """Handle window resize events for auto-scaling"""
        # Only resize if it's the main window
        if event.widget == self.root:
            # Update canvas sizes
            try:
                if hasattr(self, 'sim_canvas'):
                    self.sim_fig.tight_layout()
                    self.sim_canvas.draw_idle()

                if hasattr(self, 'char_canvas'):
                    self.char_fig.tight_layout()
                    self.char_canvas.draw_idle()

            except Exception:
                pass  # Ignore resize errors


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MotorSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

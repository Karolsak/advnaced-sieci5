#!/usr/bin/env python3
"""
Advanced Alternator EMF Analysis Laboratory
Comprehensive multi-physics simulation with GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.integrate import odeint, solve_ivp
import math
from dataclasses import dataclass
from typing import Tuple, List, Dict
import time

# ==================== Data Classes ====================

@dataclass
class AlternatorParameters:
    """Core alternator parameters"""
    poles: int = 10
    frequency: float = 50.0  # Hz
    speed: float = 600.0  # r.p.m.
    slots: int = 180
    layers: int = 2
    turns_per_coil: int = 3
    coil_span_slots: int = 15
    group_angle: float = 60.0  # degrees
    diameter: float = 1.2  # meters
    core_length: float = 0.4  # meters

    # Flux density harmonics (B = B1*sin(θ) + B3*sin(3θ) + B5*sin(5θ))
    B1: float = 1.0
    B3: float = 0.4
    B5: float = 0.2

    # Additional electrical parameters
    resistance_per_phase: float = 0.5  # Ohms
    inductance_per_phase: float = 0.01  # H
    load_resistance: float = 10.0  # Ohms
    load_inductance: float = 0.02  # H

    # Thermal parameters
    ambient_temp: float = 25.0  # °C
    thermal_resistance: float = 2.0  # °C/W
    thermal_capacitance: float = 500.0  # J/°C
    max_temp: float = 155.0  # °C (Class F insulation)

    # Mechanical parameters
    moment_of_inertia: float = 5.0  # kg·m²
    friction_coefficient: float = 0.01  # N·m·s/rad
    shaft_stiffness: float = 1e6  # N·m/rad

    # Cost parameters
    energy_cost: float = 0.15  # $/kWh
    maintenance_cost_per_hour: float = 5.0  # $/hr

@dataclass
class SimulationState:
    """Current simulation state"""
    time: float = 0.0
    current_phase_a: float = 0.0
    current_phase_b: float = 0.0
    current_phase_c: float = 0.0
    voltage_phase_a: float = 0.0
    voltage_phase_b: float = 0.0
    voltage_phase_c: float = 0.0
    temperature: float = 25.0
    angular_velocity: float = 0.0
    shaft_angle: float = 0.0
    torque: float = 0.0
    power_output: float = 0.0
    efficiency: float = 0.0
    copper_losses: float = 0.0
    iron_losses: float = 0.0
    mechanical_losses: float = 0.0
    stray_losses: float = 0.0

# ==================== Mathematical Models ====================

class AlternatorMathModel:
    """Mathematical model for alternator calculations"""

    def __init__(self, params: AlternatorParameters):
        self.params = params
        self._precompute_constants()

    def _precompute_constants(self):
        """Precompute frequently used constants"""
        p = self.params

        # Angular frequency
        self.omega = 2 * np.pi * p.frequency  # rad/s
        self.omega_mech = 2 * np.pi * p.speed / 60  # mechanical rad/s

        # Pole pitch
        self.pole_pitch = np.pi * p.diameter / p.poles  # meters

        # Slot pitch
        self.slot_pitch = (np.pi * p.diameter) / p.slots  # meters
        self.slot_angle = 2 * np.pi / p.slots  # radians

        # Coil span angle
        self.coil_span_angle = p.coil_span_slots * self.slot_angle

        # Distribution factor
        self.slots_per_pole_per_phase = p.slots / (p.poles * 3)
        beta = p.group_angle * np.pi / 180  # group angle in radians

        # Pitch factor for each harmonic
        self.kp1 = np.sin(self.coil_span_angle / 2)
        self.kp3 = np.sin(3 * self.coil_span_angle / 2)
        self.kp5 = np.sin(5 * self.coil_span_angle / 2)

        # Distribution factor for each harmonic
        self.kd1 = self._distribution_factor(1, beta)
        self.kd3 = self._distribution_factor(3, beta)
        self.kd5 = self._distribution_factor(5, beta)

        # Area per pole
        self.area_per_pole = self.pole_pitch * p.core_length

        # Number of coils per phase
        self.coils_per_phase = p.slots / (3 * p.layers)

        # Total conductors per phase
        self.conductors_per_phase = self.coils_per_phase * p.turns_per_coil * 2

    def _distribution_factor(self, n: int, beta: float) -> float:
        """Calculate distribution factor for nth harmonic"""
        p = self.params
        q = self.slots_per_pole_per_phase
        n_beta = n * beta

        if abs(np.sin(q * n_beta / 2)) < 1e-10:
            return 1.0

        return np.sin(q * n_beta / 2) / (q * np.sin(n_beta / 2))

    def instantaneous_emf_per_conductor(self, t: float, theta: float) -> float:
        """
        Calculate instantaneous EMF per conductor
        e = Blv where v is the peripheral velocity
        """
        p = self.params

        # Peripheral velocity
        v = self.omega_mech * p.diameter / 2  # m/s

        # Flux density at angle theta
        B = (p.B1 * np.sin(theta) +
             p.B3 * np.sin(3 * theta) +
             p.B5 * np.sin(5 * theta))

        # EMF per conductor
        emf = B * p.core_length * v

        return emf

    def instantaneous_emf_per_coil(self, t: float, theta: float) -> float:
        """
        Calculate instantaneous EMF per coil (considering pitch and distribution)
        """
        p = self.params

        # EMF for fundamental and harmonics
        emf1 = self._emf_harmonic(1, theta) * self.kp1 * self.kd1
        emf3 = self._emf_harmonic(3, theta) * self.kp3 * self.kd3
        emf5 = self._emf_harmonic(5, theta) * self.kp5 * self.kd5

        # Total EMF per coil (considering turns)
        total_emf = (emf1 + emf3 + emf5) * p.turns_per_coil

        return total_emf

    def _emf_harmonic(self, n: int, theta: float) -> float:
        """Calculate EMF contribution from nth harmonic"""
        p = self.params

        # Get flux density coefficient for this harmonic
        if n == 1:
            Bn = p.B1
        elif n == 3:
            Bn = p.B3
        elif n == 5:
            Bn = p.B5
        else:
            Bn = 0.0

        # Angular velocity for this harmonic
        omega_n = n * self.omega

        # Peripheral velocity
        v = self.omega_mech * p.diameter / 2

        # EMF for this harmonic
        emf = Bn * p.core_length * v * np.sin(n * theta)

        return emf

    def rms_phase_voltage(self) -> Tuple[float, float, float]:
        """
        Calculate RMS phase voltage for each harmonic component
        Returns: (V1_rms, V3_rms, V5_rms)
        """
        p = self.params

        # Maximum flux per pole for each harmonic
        phi1_max = p.B1 * self.area_per_pole
        phi3_max = p.B3 * self.area_per_pole
        phi5_max = p.B5 * self.area_per_pole

        # RMS voltage per phase for each harmonic
        # V = 4.44 * f * N * phi * kp * kd / sqrt(2)
        V1_rms = 4.44 * p.frequency * self.conductors_per_phase * phi1_max * self.kp1 * self.kd1
        V3_rms = 4.44 * (3 * p.frequency) * self.conductors_per_phase * phi3_max * self.kp3 * self.kd3
        V5_rms = 4.44 * (5 * p.frequency) * self.conductors_per_phase * phi5_max * self.kp5 * self.kd5

        return V1_rms, V3_rms, V5_rms

    def total_rms_phase_voltage(self) -> float:
        """Calculate total RMS phase voltage"""
        V1, V3, V5 = self.rms_phase_voltage()
        # RMS of sum = sqrt(V1^2 + V3^2 + V5^2)
        return np.sqrt(V1**2 + V3**2 + V5**2)

    def line_voltage(self) -> float:
        """Calculate line voltage for star connection"""
        Vph = self.total_rms_phase_voltage()
        return np.sqrt(3) * Vph

# ==================== Multi-Physics Simulation ====================

class MultiPhysicsSimulator:
    """Combined electromagnetic-thermal-mechanical simulation"""

    def __init__(self, params: AlternatorParameters, math_model: AlternatorMathModel):
        self.params = params
        self.math_model = math_model
        self.state = SimulationState()
        self.state.angular_velocity = math_model.omega_mech
        self.state.temperature = params.ambient_temp

        # History for plotting
        self.time_history = []
        self.voltage_history = []
        self.current_history = []
        self.temp_history = []
        self.power_history = []
        self.torque_history = []
        self.efficiency_history = []
        self.losses_history = []

    def reset(self):
        """Reset simulation state"""
        self.state = SimulationState()
        self.state.angular_velocity = self.math_model.omega_mech
        self.state.temperature = self.params.ambient_temp

        self.time_history.clear()
        self.voltage_history.clear()
        self.current_history.clear()
        self.temp_history.clear()
        self.power_history.clear()
        self.torque_history.clear()
        self.efficiency_history.clear()
        self.losses_history.clear()

    def electrical_ode(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Electrical circuit ODE: di/dt for three-phase system
        y = [i_a, i_b, i_c]
        """
        i_a, i_b, i_c = y

        # Calculate phase voltages (EMF)
        theta = self.math_model.omega * t
        V_a = self.math_model.total_rms_phase_voltage() * np.sqrt(2) * np.sin(theta)
        V_b = self.math_model.total_rms_phase_voltage() * np.sqrt(2) * np.sin(theta - 2*np.pi/3)
        V_c = self.math_model.total_rms_phase_voltage() * np.sqrt(2) * np.sin(theta + 2*np.pi/3)

        # Total resistance and inductance
        R_total = self.params.resistance_per_phase + self.params.load_resistance
        L_total = self.params.inductance_per_phase + self.params.load_inductance

        # Apply voltage equation: V = Ri + L(di/dt)
        # di/dt = (V - Ri) / L
        di_a_dt = (V_a - R_total * i_a) / L_total
        di_b_dt = (V_b - R_total * i_b) / L_total
        di_c_dt = (V_c - R_total * i_c) / L_total

        return np.array([di_a_dt, di_b_dt, di_c_dt])

    def thermal_ode(self, t: float, temp: float, power_loss: float) -> float:
        """
        Thermal ODE: dT/dt
        C * dT/dt = P_loss - (T - T_amb) / R_th
        """
        p = self.params
        dT_dt = (power_loss - (temp - p.ambient_temp) / p.thermal_resistance) / p.thermal_capacitance
        return dT_dt

    def mechanical_ode(self, t: float, y: np.ndarray, torque_load: float) -> np.ndarray:
        """
        Mechanical ODE: shaft dynamics
        y = [theta, omega]
        """
        theta, omega = y

        # Calculate electromagnetic torque (simplified)
        torque_em = self.state.power_output / (omega + 1e-6)

        # Friction torque
        torque_friction = self.params.friction_coefficient * omega

        # Net torque
        torque_net = torque_em - torque_friction - torque_load

        # Angular acceleration: J * d_omega/dt = T_net
        d_omega_dt = torque_net / self.params.moment_of_inertia
        d_theta_dt = omega

        return np.array([d_theta_dt, d_omega_dt])

    def calculate_losses(self, i_rms: float) -> Dict[str, float]:
        """Calculate detailed loss breakdown"""
        p = self.params

        # Copper losses (I²R losses)
        copper_loss = 3 * i_rms**2 * p.resistance_per_phase

        # Iron losses (hysteresis + eddy current)
        # Simplified: P_iron = k_h * f * B_max^2 + k_e * f^2 * B_max^2
        B_max = p.B1  # Approximate with fundamental
        k_h = 50.0  # Hysteresis coefficient (W)
        k_e = 2.0   # Eddy current coefficient (W)
        iron_loss = k_h * p.frequency * B_max**2 + k_e * p.frequency**2 * B_max**2

        # Mechanical losses (friction and windage)
        omega = self.state.angular_velocity
        mechanical_loss = self.params.friction_coefficient * omega**2

        # Stray load losses (approximately 1% of output power)
        stray_loss = 0.01 * abs(self.state.power_output)

        return {
            'copper': copper_loss,
            'iron': iron_loss,
            'mechanical': mechanical_loss,
            'stray': stray_loss,
            'total': copper_loss + iron_loss + mechanical_loss + stray_loss
        }

    def step_euler(self, dt: float):
        """Single step using Euler method"""
        t = self.state.time

        # Electrical state update
        y_elec = np.array([
            self.state.current_phase_a,
            self.state.current_phase_b,
            self.state.current_phase_c
        ])

        dy_elec = self.electrical_ode(t, y_elec)
        y_elec_new = y_elec + dy_elec * dt

        self.state.current_phase_a = y_elec_new[0]
        self.state.current_phase_b = y_elec_new[1]
        self.state.current_phase_c = y_elec_new[2]

        # Calculate voltages
        theta = self.math_model.omega * t
        Vph_rms = self.math_model.total_rms_phase_voltage()
        self.state.voltage_phase_a = Vph_rms * np.sqrt(2) * np.sin(theta)
        self.state.voltage_phase_b = Vph_rms * np.sqrt(2) * np.sin(theta - 2*np.pi/3)
        self.state.voltage_phase_c = Vph_rms * np.sqrt(2) * np.sin(theta + 2*np.pi/3)

        # Calculate power
        P_a = self.state.voltage_phase_a * self.state.current_phase_a
        P_b = self.state.voltage_phase_b * self.state.current_phase_b
        P_c = self.state.voltage_phase_c * self.state.current_phase_c
        self.state.power_output = P_a + P_b + P_c

        # Calculate losses
        i_rms = np.sqrt((self.state.current_phase_a**2 +
                        self.state.current_phase_b**2 +
                        self.state.current_phase_c**2) / 3)
        losses = self.calculate_losses(i_rms)

        self.state.copper_losses = losses['copper']
        self.state.iron_losses = losses['iron']
        self.state.mechanical_losses = losses['mechanical']
        self.state.stray_losses = losses['stray']

        # Thermal state update
        total_loss = losses['total']
        dT_dt = self.thermal_ode(t, self.state.temperature, total_loss)
        self.state.temperature += dT_dt * dt

        # Mechanical state update (simplified - constant speed assumption)
        self.state.angular_velocity = self.math_model.omega_mech
        self.state.shaft_angle += self.state.angular_velocity * dt

        # Calculate torque
        if abs(self.state.angular_velocity) > 1e-6:
            self.state.torque = self.state.power_output / self.state.angular_velocity

        # Calculate efficiency
        P_input = abs(self.state.power_output) + total_loss
        if P_input > 1e-6:
            self.state.efficiency = abs(self.state.power_output) / P_input * 100
        else:
            self.state.efficiency = 0.0

        # Update time
        self.state.time += dt

        # Store history
        self.time_history.append(self.state.time)
        self.voltage_history.append([
            self.state.voltage_phase_a,
            self.state.voltage_phase_b,
            self.state.voltage_phase_c
        ])
        self.current_history.append([
            self.state.current_phase_a,
            self.state.current_phase_b,
            self.state.current_phase_c
        ])
        self.temp_history.append(self.state.temperature)
        self.power_history.append(self.state.power_output)
        self.torque_history.append(self.state.torque)
        self.efficiency_history.append(self.state.efficiency)
        self.losses_history.append([
            self.state.copper_losses,
            self.state.iron_losses,
            self.state.mechanical_losses,
            self.state.stray_losses
        ])

    def step_rk45(self, dt: float):
        """Single step using RK45 method"""
        t = self.state.time
        t_span = (t, t + dt)

        # Electrical state update using RK45
        y0_elec = np.array([
            self.state.current_phase_a,
            self.state.current_phase_b,
            self.state.current_phase_c
        ])

        sol_elec = solve_ivp(
            self.electrical_ode,
            t_span,
            y0_elec,
            method='RK45',
            dense_output=True
        )

        if sol_elec.success:
            y_elec_new = sol_elec.y[:, -1]
            self.state.current_phase_a = y_elec_new[0]
            self.state.current_phase_b = y_elec_new[1]
            self.state.current_phase_c = y_elec_new[2]

        # Calculate voltages
        theta = self.math_model.omega * (t + dt)
        Vph_rms = self.math_model.total_rms_phase_voltage()
        self.state.voltage_phase_a = Vph_rms * np.sqrt(2) * np.sin(theta)
        self.state.voltage_phase_b = Vph_rms * np.sqrt(2) * np.sin(theta - 2*np.pi/3)
        self.state.voltage_phase_c = Vph_rms * np.sqrt(2) * np.sin(theta + 2*np.pi/3)

        # Calculate power
        P_a = self.state.voltage_phase_a * self.state.current_phase_a
        P_b = self.state.voltage_phase_b * self.state.current_phase_b
        P_c = self.state.voltage_phase_c * self.state.current_phase_c
        self.state.power_output = P_a + P_b + P_c

        # Calculate losses
        i_rms = np.sqrt((self.state.current_phase_a**2 +
                        self.state.current_phase_b**2 +
                        self.state.current_phase_c**2) / 3)
        losses = self.calculate_losses(i_rms)

        self.state.copper_losses = losses['copper']
        self.state.iron_losses = losses['iron']
        self.state.mechanical_losses = losses['mechanical']
        self.state.stray_losses = losses['stray']

        # Thermal state update using RK45
        total_loss = losses['total']

        def thermal_ode_wrapper(t, y):
            return [self.thermal_ode(t, y[0], total_loss)]

        sol_thermal = solve_ivp(
            thermal_ode_wrapper,
            t_span,
            [self.state.temperature],
            method='RK45'
        )

        if sol_thermal.success:
            self.state.temperature = sol_thermal.y[0, -1]

        # Mechanical state (simplified)
        self.state.angular_velocity = self.math_model.omega_mech
        self.state.shaft_angle += self.state.angular_velocity * dt

        # Calculate torque
        if abs(self.state.angular_velocity) > 1e-6:
            self.state.torque = self.state.power_output / self.state.angular_velocity

        # Calculate efficiency
        P_input = abs(self.state.power_output) + total_loss
        if P_input > 1e-6:
            self.state.efficiency = abs(self.state.power_output) / P_input * 100
        else:
            self.state.efficiency = 0.0

        # Update time
        self.state.time += dt

        # Store history
        self.time_history.append(self.state.time)
        self.voltage_history.append([
            self.state.voltage_phase_a,
            self.state.voltage_phase_b,
            self.state.voltage_phase_c
        ])
        self.current_history.append([
            self.state.current_phase_a,
            self.state.current_phase_b,
            self.state.current_phase_c
        ])
        self.temp_history.append(self.state.temperature)
        self.power_history.append(self.state.power_output)
        self.torque_history.append(self.state.torque)
        self.efficiency_history.append(self.state.efficiency)
        self.losses_history.append([
            self.state.copper_losses,
            self.state.iron_losses,
            self.state.mechanical_losses,
            self.state.stray_losses
        ])

# ==================== Control Systems ====================

class AlternatorController:
    """Advanced control system for alternator"""

    def __init__(self, params: AlternatorParameters):
        self.params = params
        self.control_mode = "Manual"  # Manual, PID, Adaptive
        self.setpoint_voltage = 400.0  # V
        self.setpoint_frequency = 50.0  # Hz

        # PID parameters
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.05
        self.integral_error = 0.0
        self.previous_error = 0.0

    def pid_control(self, measured_value: float, setpoint: float, dt: float) -> float:
        """PID controller"""
        error = setpoint - measured_value

        # Proportional term
        P = self.kp * error

        # Integral term
        self.integral_error += error * dt
        I = self.ki * self.integral_error

        # Derivative term
        D = self.kd * (error - self.previous_error) / (dt + 1e-10)

        # Update previous error
        self.previous_error = error

        # Control output
        output = P + I + D

        return output

    def thermal_derating(self, temperature: float) -> float:
        """Calculate derating factor based on temperature"""
        if temperature < 100:
            return 1.0
        elif temperature < self.params.max_temp:
            # Linear derating between 100°C and max temp
            return 1.0 - 0.5 * (temperature - 100) / (self.params.max_temp - 100)
        else:
            return 0.5  # 50% derating at max temperature

# ==================== GUI Application ====================

class AlternatorLabGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Alternator EMF Analysis Laboratory")
        self.root.geometry("1400x900")

        # Initialize parameters and models
        self.params = AlternatorParameters()
        self.math_model = AlternatorMathModel(self.params)
        self.simulator = MultiPhysicsSimulator(self.params, self.math_model)
        self.controller = AlternatorController(self.params)

        # Simulation control
        self.is_running = False
        self.sim_dt = 0.001  # 1ms time step
        self.sim_speed = 1.0
        self.solver_method = "RK45"  # RK45 or Euler
        self.update_interval = 50  # ms

        # Setup GUI
        self.setup_menu()
        self.setup_main_layout()
        self.setup_tabs()

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

        # Update display
        self.update_display()

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset Simulation", command=self.reset_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Solver menu
        solver_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Solver", menu=solver_menu)
        solver_menu.add_command(label="Use RK45", command=lambda: self.set_solver("RK45"))
        solver_menu.add_command(label="Use Euler", command=lambda: self.set_solver("Euler"))

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_main_layout(self):
        """Setup main layout with control panel and tabs"""
        # Control panel frame (left side)
        self.control_frame = ttk.Frame(self.root, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        self.control_frame.pack_propagate(False)

        # Tabs frame (right side)
        self.tabs_frame = ttk.Frame(self.root)
        self.tabs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.setup_control_panel()

    def setup_control_panel(self):
        """Setup control panel with parameters and buttons"""
        # Title
        title_label = ttk.Label(self.control_frame, text="Control Panel",
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Simulation control buttons
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Start",
                                       command=self.start_simulation, width=10)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop",
                                      command=self.stop_simulation, width=10,
                                      state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.reset_button = ttk.Button(button_frame, text="Reset",
                                       command=self.reset_simulation, width=10)
        self.reset_button.grid(row=1, column=0, columnspan=2, pady=5)

        # Solver selection
        solver_frame = ttk.LabelFrame(self.control_frame, text="Solver Method", padding=10)
        solver_frame.pack(fill=tk.X, pady=10, padx=10)

        self.solver_var = tk.StringVar(value="RK45")
        ttk.Radiobutton(solver_frame, text="RK45 (Accurate)",
                       variable=self.solver_var, value="RK45",
                       command=self.on_solver_change).pack(anchor=tk.W)
        ttk.Radiobutton(solver_frame, text="Euler (Fast)",
                       variable=self.solver_var, value="Euler",
                       command=self.on_solver_change).pack(anchor=tk.W)

        # Parameters frame with scrollbar
        params_canvas = tk.Canvas(self.control_frame, highlightthickness=0)
        params_scrollbar = ttk.Scrollbar(self.control_frame, orient="vertical",
                                        command=params_canvas.yview)
        self.params_frame = ttk.Frame(params_canvas)

        self.params_frame.bind(
            "<Configure>",
            lambda e: params_canvas.configure(scrollregion=params_canvas.bbox("all"))
        )

        params_canvas.create_window((0, 0), window=self.params_frame, anchor="nw")
        params_canvas.configure(yscrollcommand=params_scrollbar.set)

        params_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        params_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add parameter controls
        self.setup_parameter_controls()

    def setup_parameter_controls(self):
        """Setup parameter sliders and inputs"""
        self.param_widgets = {}

        # Define parameters with ranges
        param_config = [
            ("Frequency (Hz)", "frequency", 10, 100, self.params.frequency),
            ("Speed (RPM)", "speed", 100, 1500, self.params.speed),
            ("Load R (Ω)", "load_resistance", 1, 50, self.params.load_resistance),
            ("Load L (H)", "load_inductance", 0.001, 0.1, self.params.load_inductance),
            ("B1 Coeff", "B1", 0.1, 2.0, self.params.B1),
            ("B3 Coeff", "B3", 0.0, 1.0, self.params.B3),
            ("B5 Coeff", "B5", 0.0, 1.0, self.params.B5),
            ("Ambient T (°C)", "ambient_temp", 0, 50, self.params.ambient_temp),
            ("Sim Speed", "sim_speed", 0.1, 5.0, 1.0),
        ]

        for label, param_name, min_val, max_val, default in param_config:
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill=tk.X, pady=5, padx=5)

            label_widget = ttk.Label(frame, text=label, width=15)
            label_widget.pack(side=tk.LEFT)

            value_var = tk.DoubleVar(value=default)
            value_label = ttk.Label(frame, text=f"{default:.3f}", width=8)
            value_label.pack(side=tk.RIGHT)

            slider = ttk.Scale(frame, from_=min_val, to=max_val,
                              variable=value_var, orient=tk.HORIZONTAL,
                              command=lambda v, p=param_name, l=value_label, var=value_var:
                                     self.on_param_change(p, float(v), l, var))
            slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

            self.param_widgets[param_name] = {
                'var': value_var,
                'label': value_label,
                'slider': slider
            }

    def setup_tabs(self):
        """Setup notebook tabs for different views"""
        self.notebook = ttk.Notebook(self.tabs_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_main_display_tab()
        self.create_waveforms_tab()
        self.create_thermal_tab()
        self.create_losses_tab()
        self.create_economic_tab()
        self.create_multi_physics_tab()

    def create_main_display_tab(self):
        """Main display with key metrics"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Main Display")

        # Create text display
        self.main_text = tk.Text(tab, wrap=tk.WORD, font=('Courier', 10))
        self.main_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure tags for formatting
        self.main_text.tag_configure("header", font=('Courier', 12, 'bold'))
        self.main_text.tag_configure("subheader", font=('Courier', 10, 'bold'))
        self.main_text.tag_configure("warning", foreground="red")
        self.main_text.tag_configure("good", foreground="green")

    def create_waveforms_tab(self):
        """Voltage and current waveforms"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Waveforms")

        self.fig_waveforms = Figure(figsize=(8, 6), dpi=100)

        self.ax_voltage = self.fig_waveforms.add_subplot(211)
        self.ax_voltage.set_title("Phase Voltages")
        self.ax_voltage.set_xlabel("Time (s)")
        self.ax_voltage.set_ylabel("Voltage (V)")
        self.ax_voltage.grid(True, alpha=0.3)

        self.ax_current = self.fig_waveforms.add_subplot(212)
        self.ax_current.set_title("Phase Currents")
        self.ax_current.set_xlabel("Time (s)")
        self.ax_current.set_ylabel("Current (A)")
        self.ax_current.grid(True, alpha=0.3)

        self.fig_waveforms.tight_layout()

        self.canvas_waveforms = FigureCanvasTkAgg(self.fig_waveforms, tab)
        self.canvas_waveforms.draw()
        self.canvas_waveforms.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas_waveforms, tab)
        toolbar.update()

    def create_thermal_tab(self):
        """Thermal analysis"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Thermal Analysis")

        self.fig_thermal = Figure(figsize=(8, 6), dpi=100)

        self.ax_temp = self.fig_thermal.add_subplot(211)
        self.ax_temp.set_title("Temperature vs Time")
        self.ax_temp.set_xlabel("Time (s)")
        self.ax_temp.set_ylabel("Temperature (°C)")
        self.ax_temp.grid(True, alpha=0.3)

        self.ax_power = self.fig_thermal.add_subplot(212)
        self.ax_power.set_title("Power Output vs Time")
        self.ax_power.set_xlabel("Time (s)")
        self.ax_power.set_ylabel("Power (W)")
        self.ax_power.grid(True, alpha=0.3)

        self.fig_thermal.tight_layout()

        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, tab)
        self.canvas_thermal.draw()
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas_thermal, tab)
        toolbar.update()

    def create_losses_tab(self):
        """Losses breakdown"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Losses Analysis")

        self.fig_losses = Figure(figsize=(8, 6), dpi=100)

        self.ax_losses_time = self.fig_losses.add_subplot(211)
        self.ax_losses_time.set_title("Losses vs Time")
        self.ax_losses_time.set_xlabel("Time (s)")
        self.ax_losses_time.set_ylabel("Power Loss (W)")
        self.ax_losses_time.grid(True, alpha=0.3)

        self.ax_losses_pie = self.fig_losses.add_subplot(212)
        self.ax_losses_pie.set_title("Loss Distribution")

        self.fig_losses.tight_layout()

        self.canvas_losses = FigureCanvasTkAgg(self.fig_losses, tab)
        self.canvas_losses.draw()
        self.canvas_losses.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas_losses, tab)
        toolbar.update()

    def create_economic_tab(self):
        """Economic analysis"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Economic Analysis")

        # Create frame for economic metrics
        metrics_frame = ttk.LabelFrame(tab, text="Operating Costs", padding=20)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.economic_text = tk.Text(metrics_frame, wrap=tk.WORD, font=('Courier', 10))
        self.economic_text.pack(fill=tk.BOTH, expand=True)

        self.economic_text.tag_configure("header", font=('Courier', 12, 'bold'))
        self.economic_text.tag_configure("value", font=('Courier', 10, 'bold'), foreground="blue")

    def create_multi_physics_tab(self):
        """Multi-physics coupled simulation results"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Multi-Physics")

        self.fig_multiphysics = Figure(figsize=(8, 8), dpi=100)

        self.ax_efficiency = self.fig_multiphysics.add_subplot(221)
        self.ax_efficiency.set_title("Efficiency")
        self.ax_efficiency.set_xlabel("Time (s)")
        self.ax_efficiency.set_ylabel("Efficiency (%)")
        self.ax_efficiency.grid(True, alpha=0.3)

        self.ax_torque = self.fig_multiphysics.add_subplot(222)
        self.ax_torque.set_title("Electromagnetic Torque")
        self.ax_torque.set_xlabel("Time (s)")
        self.ax_torque.set_ylabel("Torque (N·m)")
        self.ax_torque.grid(True, alpha=0.3)

        self.ax_temp_power = self.fig_multiphysics.add_subplot(223)
        self.ax_temp_power.set_title("Temperature-Power Coupling")
        self.ax_temp_power.set_xlabel("Power Output (W)")
        self.ax_temp_power.set_ylabel("Temperature (°C)")
        self.ax_temp_power.grid(True, alpha=0.3)

        self.ax_stress = self.fig_multiphysics.add_subplot(224)
        self.ax_stress.set_title("Shaft Stress Analysis")
        self.ax_stress.set_xlabel("Time (s)")
        self.ax_stress.set_ylabel("Stress (MPa)")
        self.ax_stress.grid(True, alpha=0.3)

        self.fig_multiphysics.tight_layout()

        self.canvas_multiphysics = FigureCanvasTkAgg(self.fig_multiphysics, tab)
        self.canvas_multiphysics.draw()
        self.canvas_multiphysics.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas_multiphysics, tab)
        toolbar.update()

    def on_param_change(self, param_name, value, label, var):
        """Handle parameter change"""
        # Update label
        label.config(text=f"{value:.3f}")

        # Update parameter
        if param_name == "sim_speed":
            self.sim_speed = value
        else:
            setattr(self.params, param_name, value)
            # Recreate models with new parameters
            self.math_model = AlternatorMathModel(self.params)
            self.simulator = MultiPhysicsSimulator(self.params, self.math_model)
            self.controller = AlternatorController(self.params)

    def on_solver_change(self):
        """Handle solver method change"""
        self.solver_method = self.solver_var.get()

    def set_solver(self, method):
        """Set solver method from menu"""
        self.solver_var.set(method)
        self.solver_method = method

    def start_simulation(self):
        """Start the simulation"""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.run_simulation()

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()
        self.simulator.reset()
        self.update_display()
        self.update_plots()

    def run_simulation(self):
        """Run simulation loop"""
        if not self.is_running:
            return

        # Perform multiple steps per update for smoother simulation
        steps_per_update = int(self.sim_speed * 10)

        for _ in range(steps_per_update):
            if self.solver_method == "RK45":
                self.simulator.step_rk45(self.sim_dt)
            else:
                self.simulator.step_euler(self.sim_dt)

        # Update display
        self.update_display()
        self.update_plots()

        # Check thermal limits
        if self.simulator.state.temperature > self.params.max_temp:
            messagebox.showwarning("Temperature Warning",
                                  f"Temperature exceeds limit: {self.simulator.state.temperature:.1f}°C")
            self.stop_simulation()
            return

        # Schedule next update
        self.root.after(self.update_interval, self.run_simulation)

    def update_display(self):
        """Update main display with current values"""
        self.main_text.delete(1.0, tk.END)

        # Header
        self.main_text.insert(tk.END, "ALTERNATOR EMF ANALYSIS\n", "header")
        self.main_text.insert(tk.END, "=" * 60 + "\n\n")

        # Machine parameters
        self.main_text.insert(tk.END, "MACHINE PARAMETERS\n", "subheader")
        self.main_text.insert(tk.END, f"Poles:            {self.params.poles}\n")
        self.main_text.insert(tk.END, f"Frequency:        {self.params.frequency:.2f} Hz\n")
        self.main_text.insert(tk.END, f"Speed:            {self.params.speed:.2f} RPM\n")
        self.main_text.insert(tk.END, f"Slots:            {self.params.slots}\n")
        self.main_text.insert(tk.END, f"Coil Span:        {self.params.coil_span_slots} slots\n")
        self.main_text.insert(tk.END, f"Diameter:         {self.params.diameter:.3f} m\n")
        self.main_text.insert(tk.END, f"Core Length:      {self.params.core_length:.3f} m\n\n")

        # Flux density expression
        self.main_text.insert(tk.END, "FLUX DENSITY DISTRIBUTION\n", "subheader")
        self.main_text.insert(tk.END, f"B = {self.params.B1:.2f}·sin(θ) + ")
        self.main_text.insert(tk.END, f"{self.params.B3:.2f}·sin(3θ) + ")
        self.main_text.insert(tk.END, f"{self.params.B5:.2f}·sin(5θ)\n\n")

        # Calculated EMF values
        self.main_text.insert(tk.END, "EMF CALCULATIONS\n", "subheader")
        V1, V3, V5 = self.math_model.rms_phase_voltage()
        Vph = self.math_model.total_rms_phase_voltage()
        Vline = self.math_model.line_voltage()

        self.main_text.insert(tk.END, f"RMS Phase Voltage Components:\n")
        self.main_text.insert(tk.END, f"  Fundamental (V1):  {V1:.2f} V\n")
        self.main_text.insert(tk.END, f"  3rd Harmonic (V3): {V3:.2f} V\n")
        self.main_text.insert(tk.END, f"  5th Harmonic (V5): {V5:.2f} V\n")
        self.main_text.insert(tk.END, f"Total RMS Phase Voltage: {Vph:.2f} V\n")
        self.main_text.insert(tk.END, f"Line Voltage (Star):     {Vline:.2f} V\n\n")

        # Current state
        self.main_text.insert(tk.END, "CURRENT STATE\n", "subheader")
        self.main_text.insert(tk.END, f"Simulation Time:  {self.simulator.state.time:.3f} s\n")
        self.main_text.insert(tk.END, f"Temperature:      {self.simulator.state.temperature:.2f} °C")

        if self.simulator.state.temperature > self.params.max_temp * 0.9:
            self.main_text.insert(tk.END, " [WARNING]", "warning")
        elif self.simulator.state.temperature < self.params.max_temp * 0.7:
            self.main_text.insert(tk.END, " [OK]", "good")

        self.main_text.insert(tk.END, f"\nPower Output:     {self.simulator.state.power_output:.2f} W\n")
        self.main_text.insert(tk.END, f"Efficiency:       {self.simulator.state.efficiency:.2f} %\n")
        self.main_text.insert(tk.END, f"Torque:           {self.simulator.state.torque:.2f} N·m\n\n")

        # Losses breakdown
        self.main_text.insert(tk.END, "LOSSES BREAKDOWN\n", "subheader")
        self.main_text.insert(tk.END, f"Copper Losses:    {self.simulator.state.copper_losses:.2f} W\n")
        self.main_text.insert(tk.END, f"Iron Losses:      {self.simulator.state.iron_losses:.2f} W\n")
        self.main_text.insert(tk.END, f"Mechanical Loss:  {self.simulator.state.mechanical_losses:.2f} W\n")
        self.main_text.insert(tk.END, f"Stray Losses:     {self.simulator.state.stray_losses:.2f} W\n")
        total_losses = (self.simulator.state.copper_losses +
                       self.simulator.state.iron_losses +
                       self.simulator.state.mechanical_losses +
                       self.simulator.state.stray_losses)
        self.main_text.insert(tk.END, f"Total Losses:     {total_losses:.2f} W\n\n")

        # Thermal derating
        derating = self.controller.thermal_derating(self.simulator.state.temperature)
        self.main_text.insert(tk.END, "THERMAL DERATING\n", "subheader")
        self.main_text.insert(tk.END, f"Derating Factor:  {derating:.2%}\n")
        self.main_text.insert(tk.END, f"Max Safe Power:   {derating * abs(self.simulator.state.power_output):.2f} W\n\n")

        # Update economic display
        self.update_economic_display()

    def update_economic_display(self):
        """Update economic analysis display"""
        self.economic_text.delete(1.0, tk.END)

        self.economic_text.insert(tk.END, "ECONOMIC ANALYSIS\n", "header")
        self.economic_text.insert(tk.END, "=" * 60 + "\n\n")

        # Calculate costs
        runtime_hours = self.simulator.state.time / 3600

        # Energy consumption
        total_losses = (self.simulator.state.copper_losses +
                       self.simulator.state.iron_losses +
                       self.simulator.state.mechanical_losses +
                       self.simulator.state.stray_losses)
        energy_consumed_kwh = (abs(self.simulator.state.power_output) + total_losses) * runtime_hours / 1000
        energy_cost = energy_consumed_kwh * self.params.energy_cost

        # Maintenance cost
        maintenance_cost = runtime_hours * self.params.maintenance_cost_per_hour

        # Total cost
        total_cost = energy_cost + maintenance_cost

        # Output energy
        energy_output_kwh = abs(self.simulator.state.power_output) * runtime_hours / 1000

        # Cost per kWh
        if energy_output_kwh > 1e-6:
            cost_per_kwh = total_cost / energy_output_kwh
        else:
            cost_per_kwh = 0.0

        self.economic_text.insert(tk.END, f"Runtime:              {runtime_hours:.4f} hours\n\n")

        self.economic_text.insert(tk.END, "Energy Consumption:\n")
        self.economic_text.insert(tk.END, f"  Total Consumed:     {energy_consumed_kwh:.4f} kWh\n")
        self.economic_text.insert(tk.END, f"  Energy Cost Rate:   ${self.params.energy_cost:.3f}/kWh\n")
        self.economic_text.insert(tk.END, f"  Energy Cost:        ", "value")
        self.economic_text.insert(tk.END, f"${energy_cost:.4f}\n\n")

        self.economic_text.insert(tk.END, "Maintenance:\n")
        self.economic_text.insert(tk.END, f"  Rate:               ${self.params.maintenance_cost_per_hour:.2f}/hour\n")
        self.economic_text.insert(tk.END, f"  Maintenance Cost:   ", "value")
        self.economic_text.insert(tk.END, f"${maintenance_cost:.4f}\n\n")

        self.economic_text.insert(tk.END, "Total Operating Cost:   ", "header")
        self.economic_text.insert(tk.END, f"${total_cost:.4f}\n\n", "value")

        self.economic_text.insert(tk.END, f"Energy Output:          {energy_output_kwh:.4f} kWh\n")
        self.economic_text.insert(tk.END, f"Cost per kWh Output:    ${cost_per_kwh:.4f}/kWh\n")
        self.economic_text.insert(tk.END, f"Overall Efficiency:     {self.simulator.state.efficiency:.2f}%\n")

    def update_plots(self):
        """Update all plots"""
        if len(self.simulator.time_history) < 2:
            return

        # Limit history length for performance
        max_points = 5000
        if len(self.simulator.time_history) > max_points:
            self.simulator.time_history = self.simulator.time_history[-max_points:]
            self.simulator.voltage_history = self.simulator.voltage_history[-max_points:]
            self.simulator.current_history = self.simulator.current_history[-max_points:]
            self.simulator.temp_history = self.simulator.temp_history[-max_points:]
            self.simulator.power_history = self.simulator.power_history[-max_points:]
            self.simulator.torque_history = self.simulator.torque_history[-max_points:]
            self.simulator.efficiency_history = self.simulator.efficiency_history[-max_points:]
            self.simulator.losses_history = self.simulator.losses_history[-max_points:]

        time_array = np.array(self.simulator.time_history)

        # Update waveforms
        self.update_waveforms_plot(time_array)

        # Update thermal plots
        self.update_thermal_plot(time_array)

        # Update losses plots
        self.update_losses_plot(time_array)

        # Update multi-physics plots
        self.update_multiphysics_plot(time_array)

    def update_waveforms_plot(self, time_array):
        """Update voltage and current waveforms"""
        self.ax_voltage.clear()
        self.ax_current.clear()

        voltage_array = np.array(self.simulator.voltage_history)
        current_array = np.array(self.simulator.current_history)

        # Plot voltages
        self.ax_voltage.plot(time_array, voltage_array[:, 0], 'r-', label='Phase A', linewidth=1.5)
        self.ax_voltage.plot(time_array, voltage_array[:, 1], 'g-', label='Phase B', linewidth=1.5)
        self.ax_voltage.plot(time_array, voltage_array[:, 2], 'b-', label='Phase C', linewidth=1.5)
        self.ax_voltage.set_title("Phase Voltages")
        self.ax_voltage.set_xlabel("Time (s)")
        self.ax_voltage.set_ylabel("Voltage (V)")
        self.ax_voltage.legend(loc='upper right')
        self.ax_voltage.grid(True, alpha=0.3)

        # Plot currents
        self.ax_current.plot(time_array, current_array[:, 0], 'r-', label='Phase A', linewidth=1.5)
        self.ax_current.plot(time_array, current_array[:, 1], 'g-', label='Phase B', linewidth=1.5)
        self.ax_current.plot(time_array, current_array[:, 2], 'b-', label='Phase C', linewidth=1.5)
        self.ax_current.set_title("Phase Currents")
        self.ax_current.set_xlabel("Time (s)")
        self.ax_current.set_ylabel("Current (A)")
        self.ax_current.legend(loc='upper right')
        self.ax_current.grid(True, alpha=0.3)

        self.fig_waveforms.tight_layout()
        self.canvas_waveforms.draw()

    def update_thermal_plot(self, time_array):
        """Update thermal analysis plots"""
        self.ax_temp.clear()
        self.ax_power.clear()

        temp_array = np.array(self.simulator.temp_history)
        power_array = np.array(self.simulator.power_history)

        # Plot temperature
        self.ax_temp.plot(time_array, temp_array, 'r-', linewidth=2, label='Temperature')
        self.ax_temp.axhline(y=self.params.max_temp, color='orange', linestyle='--',
                            label='Max Temp', linewidth=1.5)
        self.ax_temp.axhline(y=self.params.ambient_temp, color='blue', linestyle='--',
                            label='Ambient', linewidth=1.5)
        self.ax_temp.set_title("Temperature vs Time")
        self.ax_temp.set_xlabel("Time (s)")
        self.ax_temp.set_ylabel("Temperature (°C)")
        self.ax_temp.legend(loc='upper right')
        self.ax_temp.grid(True, alpha=0.3)

        # Plot power
        self.ax_power.plot(time_array, power_array, 'b-', linewidth=2)
        self.ax_power.set_title("Power Output vs Time")
        self.ax_power.set_xlabel("Time (s)")
        self.ax_power.set_ylabel("Power (W)")
        self.ax_power.grid(True, alpha=0.3)

        self.fig_thermal.tight_layout()
        self.canvas_thermal.draw()

    def update_losses_plot(self, time_array):
        """Update losses analysis plots"""
        self.ax_losses_time.clear()
        self.ax_losses_pie.clear()

        losses_array = np.array(self.simulator.losses_history)

        # Plot losses over time
        self.ax_losses_time.plot(time_array, losses_array[:, 0], 'r-',
                                label='Copper', linewidth=1.5)
        self.ax_losses_time.plot(time_array, losses_array[:, 1], 'g-',
                                label='Iron', linewidth=1.5)
        self.ax_losses_time.plot(time_array, losses_array[:, 2], 'b-',
                                label='Mechanical', linewidth=1.5)
        self.ax_losses_time.plot(time_array, losses_array[:, 3], 'm-',
                                label='Stray', linewidth=1.5)
        self.ax_losses_time.set_title("Losses vs Time")
        self.ax_losses_time.set_xlabel("Time (s)")
        self.ax_losses_time.set_ylabel("Power Loss (W)")
        self.ax_losses_time.legend(loc='upper right')
        self.ax_losses_time.grid(True, alpha=0.3)

        # Pie chart of current losses
        if len(losses_array) > 0:
            current_losses = losses_array[-1]
            labels = ['Copper', 'Iron', 'Mechanical', 'Stray']
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24']

            # Filter out zero or very small values
            nonzero_mask = current_losses > 0.01
            if np.any(nonzero_mask):
                self.ax_losses_pie.pie(current_losses[nonzero_mask],
                                       labels=[l for l, m in zip(labels, nonzero_mask) if m],
                                       autopct='%1.1f%%',
                                       colors=[c for c, m in zip(colors, nonzero_mask) if m],
                                       startangle=90)
                self.ax_losses_pie.set_title("Current Loss Distribution")

        self.fig_losses.tight_layout()
        self.canvas_losses.draw()

    def update_multiphysics_plot(self, time_array):
        """Update multi-physics plots"""
        self.ax_efficiency.clear()
        self.ax_torque.clear()
        self.ax_temp_power.clear()
        self.ax_stress.clear()

        efficiency_array = np.array(self.simulator.efficiency_history)
        torque_array = np.array(self.simulator.torque_history)
        temp_array = np.array(self.simulator.temp_history)
        power_array = np.array(self.simulator.power_history)

        # Efficiency plot
        self.ax_efficiency.plot(time_array, efficiency_array, 'g-', linewidth=2)
        self.ax_efficiency.set_title("Efficiency")
        self.ax_efficiency.set_xlabel("Time (s)")
        self.ax_efficiency.set_ylabel("Efficiency (%)")
        self.ax_efficiency.grid(True, alpha=0.3)

        # Torque plot
        self.ax_torque.plot(time_array, torque_array, 'b-', linewidth=2)
        self.ax_torque.set_title("Electromagnetic Torque")
        self.ax_torque.set_xlabel("Time (s)")
        self.ax_torque.set_ylabel("Torque (N·m)")
        self.ax_torque.grid(True, alpha=0.3)

        # Temperature-Power coupling
        if len(temp_array) > 1 and len(power_array) > 1:
            self.ax_temp_power.scatter(power_array, temp_array, c=time_array,
                                      cmap='viridis', s=10, alpha=0.6)
            self.ax_temp_power.set_title("Temperature-Power Coupling")
            self.ax_temp_power.set_xlabel("Power Output (W)")
            self.ax_temp_power.set_ylabel("Temperature (°C)")
            self.ax_temp_power.grid(True, alpha=0.3)

        # Shaft stress (simplified calculation)
        shaft_diameter = 0.05  # 50mm diameter
        shaft_area = np.pi * (shaft_diameter/2)**2
        stress_array = np.abs(torque_array) / (shaft_area * shaft_diameter/2) / 1e6  # MPa

        self.ax_stress.plot(time_array, stress_array, 'r-', linewidth=2)
        self.ax_stress.set_title("Shaft Stress Analysis")
        self.ax_stress.set_xlabel("Time (s)")
        self.ax_stress.set_ylabel("Stress (MPa)")
        self.ax_stress.grid(True, alpha=0.3)

        self.fig_multiphysics.tight_layout()
        self.canvas_multiphysics.draw()

    def on_window_resize(self, event):
        """Handle window resize for auto-scaling"""
        # This is called on every resize event
        # The matplotlib figures automatically handle rescaling
        pass

    def show_about(self):
        """Show about dialog"""
        about_text = """
Advanced Alternator EMF Analysis Laboratory
Version 1.0

Features:
- Multi-physics simulation (electromagnetic, thermal, mechanical)
- Real-time ODE solvers (RK45, Euler)
- Comprehensive loss analysis
- Economic analysis
- Advanced control systems
- Thermal derating
- Auto-scaling visualizations

Developed for electrical engineering education and research.
        """
        messagebox.showinfo("About", about_text)

# ==================== Main Entry Point ====================

def main():
    """Main entry point"""
    root = tk.Tk()
    app = AlternatorLabGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

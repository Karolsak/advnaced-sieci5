# Advanced Three-Phase Induction Motor Simulator

## Overview
A comprehensive Python application for analyzing and simulating three-phase induction motors with complete solution for Example 6.2.

## Features

### 1. **Complete Electrical Circuit Modeling**
- Accurate equivalent circuit representation
- RMS voltage and current calculations
- Complex impedance analysis
- Power flow calculations

### 2. **Dynamic Simulation**
- Real-time ODE solvers (RK45 and Euler methods)
- Transient response analysis
- Speed and torque dynamics
- Load variation simulation

### 3. **Multi-Physics Simulation**
- **Electromagnetic Model**: Air gap power, electromagnetic torque
- **Thermal Model**: Temperature rise, thermal time constants
- **Mechanical Model**: Shaft dynamics, inertia, friction
- Coupled simulations with thermal derating

### 4. **Advanced Visualization**
- Real-time dynamic plots
- Torque-speed characteristics
- Current-speed curves
- Efficiency curves
- Temperature profiles
- Loss distribution pie charts

### 5. **Economic Analysis**
- Annual energy consumption and cost
- Life cycle cost analysis
- Payback period calculation
- ROI (Return on Investment)
- Cost breakdown visualization

### 6. **Control Methods**
- V/f (Voltage/Frequency) Control
- Direct Torque Control (DTC)
- Field Oriented Control (FOC)

### 7. **User Interface**
- Intuitive Tkinter GUI with tabs
- Interactive parameter sliders
- Real-time parameter adjustment
- Auto-scaling window layout
- Start/Stop/Reset controls

## Example 6.2 Solution

### Given Parameters:
- **Poles**: 12 (2p = 12)
- **Voltage**: 420 V (line-to-line), Y-connected
- **Power**: 5.5 kW rated
- **Frequency**: 60 Hz
- **R₁**: 0.833 Ω (Stator resistance)
- **X₁**: 1.864 Ω (Stator reactance)
- **R₂'**: 0.833 Ω (Rotor resistance)
- **X₂'**: 1.864 Ω (Rotor reactance)
- **Xₘ**: 36.25 Ω (Magnetizing reactance)
- **Slip**: 0.03
- **Rotational Loss**: 250 W
- **Stray Loss**: 60 W

### Calculated Results:
The application calculates:
- **(a)** Rotor speed (RPM and rad/s)
- **(b)** Stator and rotor currents with angles
- **(c)** Stator and rotor winding losses
- **(d)** Electromagnetic (air gap) power and developed torque
- **(e)** Mechanical power and output power
- **(f)** Input power, efficiency, and power factor
- **(g)** Starting torque and starting torque ratio (STR)
- **(h)** Breakdown torque, critical slip, and overload capacity factor (OCF)

## Installation

### Requirements:
```bash
pip install numpy scipy matplotlib tkinter
```

Note: `tkinter` typically comes pre-installed with Python.

### Running the Application:
```bash
python3 induction_motor_simulator.py
```

## Usage Guide

### Tab 1: Main Results
- Click "Calculate" to solve Example 6.2
- View comprehensive analysis results
- Export results to text file

### Tab 2: Parameters & Control
- Adjust electrical parameters with sliders
- Modify mechanical and thermal parameters
- Select control method (V/f, DTC, FOC)
- Real-time parameter updates

### Tab 3: Dynamic Simulation
- Select solver method (RK45 or Euler)
- Set simulation time
- Click "Start" to run simulation
- View real-time plots:
  - Motor speed vs time
  - Torque vs time
  - Current vs time
  - Temperature vs time

### Tab 4: Characteristics
- Generate torque-speed curves
- View current-speed characteristics
- Analyze efficiency curves
- Identify operating points

### Tab 5: Multi-Physics
- Calculate detailed loss breakdown
- View loss distribution pie chart
- Run coupled electromagnetic-thermal simulation
- Analyze thermal derating effects

### Tab 6: Economic Analysis
- Set electricity cost and operating hours
- Calculate annual energy consumption
- View life cycle costs
- Analyze payback period and ROI

## Technical Details

### Loss Calculations
The simulator calculates:
- **Copper Losses**: I²R losses in stator and rotor
- **Core Losses**: Hysteresis and eddy current losses
- **Mechanical Losses**: Friction and windage
- **Stray Losses**: Additional losses from harmonics

### Thermal Model
First-order thermal model:
```
dT/dt = (P_loss - (T - T_amb)/R_th) / C_th
```
Where:
- `P_loss`: Total power losses
- `T`: Motor temperature
- `T_amb`: Ambient temperature
- `R_th`: Thermal resistance
- `C_th`: Thermal capacitance

### Mechanical Model
Rotational dynamics:
```
J * dω/dt = T_elm - T_load - B * ω
```
Where:
- `J`: Total moment of inertia
- `ω`: Angular velocity
- `T_elm`: Electromagnetic torque
- `T_load`: Load torque
- `B`: Friction coefficient

### Derating Factor
Temperature-based power derating:
- No derating below 40°C
- Linear derating between 40°C and max temperature
- 50% capacity at maximum temperature (155°C for Class F)

## Advanced Features

### 1. Real-Time Simulation
- Uses scipy's `solve_ivp` with RK45 method
- Alternative Euler method for comparison
- Adaptive time stepping
- Handles stiff equations

### 2. Auto-Scaling GUI
- Responsive layout with grid weights
- Automatic canvas resizing
- Maintains aspect ratios
- Optimized for different screen sizes

### 3. Thread-Safe Operations
- Background simulation threads
- Non-blocking GUI updates
- Safe state management

### 4. Comprehensive Error Handling
- Input validation
- Numerical stability checks
- User-friendly error messages

## Practical Applications

### 1. Motor Selection
- Compare different motor designs
- Evaluate performance at various operating points
- Assess thermal limits

### 2. Drive System Design
- Size power electronics
- Select appropriate control method
- Calculate cooling requirements

### 3. Energy Efficiency Analysis
- Identify optimal operating conditions
- Calculate energy savings
- Justify efficiency upgrades

### 4. Educational Tool
- Visualize motor behavior
- Understand electromagnetic principles
- Learn control strategies

## Limitations and Assumptions

1. Core losses are simplified (2% approximation)
2. Skin effect in rotor bars is neglected
3. Magnetic saturation is not modeled
4. Constant rotor resistance (no temperature dependence in basic model)
5. Ideal voltage source assumed

## Future Enhancements

Potential improvements:
- Vector control implementation
- Magnetic saturation modeling
- Advanced thermal networks
- Bearing life calculation
- Vibration analysis
- Database integration for motor catalog

## References

Based on electrical machines theory and induction motor analysis from standard electrical engineering textbooks.

## License

Educational and research use.

## Author

Created for advanced electrical engineering education and practical motor analysis.

---

**Note**: This simulator is designed for educational purposes and provides accurate results for standard induction motor analysis. For critical industrial applications, additional validation and detailed modeling may be required.

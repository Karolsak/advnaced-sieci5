# Advanced DC Motor Simulator

A comprehensive Python + Tkinter application for DC motor analysis, featuring multi-physics simulation, real-time visualization, and educational problem solving.

## Features

### 1. **DC Motor Problem Solutions**
   - **Problem 1**: 4-pole series-wound fan motor with field coil reconnection
     - Analyzes speed and current changes when field coils are reconnected
     - Load torque proportional to speed squared
   - **Problem 2**: DC series motor with field shunt resistance
     - Calculates new operating conditions with field shunting
     - Accounts for load torque increase

### 2. **Multi-Physics Simulation**
   - **Electromagnetic Model**: Coupled electrical equations for armature and field circuits
   - **Mechanical Model**: Dynamic torque and speed calculations with inertia
   - **Thermal Model**: Heat transfer equations with thermal capacitance
   - **Coupled Analysis**: Simultaneous solution of all physics domains

### 3. **Advanced Numerical Solvers**
   - **RK45**: Runge-Kutta 4th/5th order adaptive solver (high accuracy)
   - **Euler**: Simple forward Euler method (fast, educational)
   - Real-time ODE integration with configurable time steps

### 4. **Comprehensive Loss Analysis**
   - **Copper Losses**: I²R losses in armature and field (temperature-dependent)
   - **Iron Losses**: Core losses proportional to speed
   - **Mechanical Losses**: Friction and windage
   - **Stray Losses**: Additional load-dependent losses
   - **Efficiency Calculation**: Real-time efficiency tracking

### 5. **Thermal Analysis & Derating**
   - Temperature-dependent resistance modeling
   - Thermal time constant simulation
   - Derating curves for safe operation
   - Overheating protection visualization

### 6. **Economic Analysis**
   - Energy consumption calculations (daily/monthly/yearly)
   - Operating cost analysis
   - Carbon footprint estimation
   - Efficiency improvement recommendations

### 7. **Interactive GUI Features**
   - **Multiple Tabs**: Main Control, Dynamics, Thermal, Losses, Economics, Problems
   - **Real-time Sliders**: Adjust all motor parameters on-the-fly
   - **Dynamic Graphs**: Live updating plots with matplotlib
   - **Auto-scaling**: Automatic window and plot resizing
   - **Control Buttons**: Start, Stop, Reset simulation

### 8. **Motor Types Supported**
   - Series Motor
   - Shunt Motor
   - Separately Excited Motor

### 9. **Visualization**
   - Speed vs Time
   - Current vs Time (Armature and Field)
   - Torque vs Time (Electromagnetic and Load)
   - Power Flow (Input, Output, Losses)
   - Temperature Rise
   - Thermal Derating Curve
   - Loss Distribution (Pie Chart)
   - Efficiency vs Time

## Installation

### Requirements
```bash
pip install numpy scipy matplotlib tkinter
```

Note: `tkinter` is usually included with Python. If not:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: Included with Python from python.org

## Usage

### Running the Application
```bash
python3 dc_motor_advanced_simulator.py
```

### Quick Start Guide

1. **Launch Application**: Run the Python script
2. **Problem Solutions**: View console output for analytical solutions to Problems 1 & 2
3. **Main Control Tab**:
   - Adjust motor parameters using sliders
   - Select motor type (series/shunt/separately excited)
   - Configure load characteristics
   - Choose ODE solver (RK45 recommended for accuracy)
4. **Start Simulation**: Click "Start" button
5. **View Results**: Switch between tabs to see different analyses
6. **Economic Analysis**: Enter electricity costs and calculate economics

### Parameter Descriptions

#### Electrical Parameters
- **Voltage (V)**: DC supply voltage [50-500V]
- **Ra (Ω)**: Armature resistance [0.1-5Ω]
- **La (H)**: Armature inductance [0.001-0.1H]
- **Rf (Ω)**: Field resistance [0.1-2Ω]
- **Lf (H)**: Field inductance [0.01-0.2H]

#### Mechanical Parameters
- **J (kg·m²)**: Moment of inertia [0.001-0.1 kg·m²]
- **B (N·m·s/rad)**: Viscous friction coefficient [0.0001-0.01]
- **Kt (N·m/A)**: Torque constant [0.5-3]
- **Ke (V·s/rad)**: Back EMF constant [0.5-3]

#### Thermal Parameters
- **R_th (°C/W)**: Thermal resistance [0.5-10]
- **C_th (J/°C)**: Thermal capacitance [10-500]
- **T_amb (°C)**: Ambient temperature [-20 to 50]
- **alpha (1/°C)**: Temperature coefficient [0.001-0.01]

#### Load Parameters
- **TL_const (N·m)**: Constant load torque [0-10]
- **TL_speed_coef**: Speed-dependent load coefficient [0-0.001]

## Problem Solutions

### Problem 1: Series-Wound Fan Motor
**Given**:
- 4-pole motor, 600 rpm, 250V, 20A
- Field coils initially all in series
- Reconnected: 2 parallel groups of 2 in series
- Load torque ∝ speed²

**Solution Method**:
1. Field MMF analysis (series vs parallel groups)
2. Flux and current relationships
3. Torque balance with speed-dependent load
4. Simultaneous equation solution

**Results**:
- New Current: ~33.6A
- New Speed: ~713 rpm

### Problem 2: DC Series Motor with Field Shunt
**Given**:
- 200V, 40A, 700 rpm initially
- Ra = 0.15Ω, Rf = 0.1Ω
- Field shunted by Rsh = Rf
- Load torque increases 50%

**Solution Method**:
1. Current distribution (field + shunt)
2. Torque increase constraint
3. Back EMF equations
4. Speed calculation from flux changes

**Results**:
- New Current: ~69.3A
- New Speed: ~757 rpm
- Field Current: ~34.6A

## Technical Details

### State-Space Model
The simulator solves the following differential equations:

```
dIa/dt = (V - Ke·φ·ω - Ia·Ra) / La
dIf/dt = (Vf - If·Rf) / Lf
dω/dt = (Te - TL - B·ω) / J
dθ/dt = ω
dT/dt = (Ploss - (T-Tamb)/Rth) / Cth
```

Where:
- Ia, If: Armature and field currents
- ω: Angular velocity
- θ: Angular position
- T: Motor temperature
- Te = Kt·φ·Ia: Electromagnetic torque
- φ ∝ If: Magnetic flux

### Numerical Integration
- **RK45**: Adaptive step size, 4th/5th order accuracy
- **Euler**: Fixed step, 1st order (dt = 0.01s)
- Real-time visualization during integration

### Loss Calculations
```
Copper Loss = Ia²·Ra(T) + If²·Rf(T)
Iron Loss = ki·ω²
Mechanical Loss = km·ω²
Stray Loss = ks·(Ia² + If²)
```

Temperature-dependent resistance:
```
R(T) = R₀·[1 + α·(T - Tamb)]
```

## File Structure
```
dc_motor_advanced_simulator.py    # Main application
DC_MOTOR_README.md                 # This file
```

## Output Files
- **Simulation Results**: `motor_sim_YYYYMMDD_HHMMSS.txt`
  - Time-series data (CSV format)
  - All parameters and settings
  - Statistical summary

## GUI Tabs Overview

### 1. Main Control
- Parameter adjustment sliders
- Motor type selection
- Load configuration
- Real-time value display
- Start/Stop/Reset controls

### 2. Dynamics
- Speed vs time plot
- Current vs time plot
- Torque vs time plot
- Power flow diagram

### 3. Thermal Analysis
- Temperature rise curve
- Thermal derating graph
- Thermal parameter adjustment

### 4. Losses & Efficiency
- Loss breakdown pie chart
- Efficiency vs time curve
- Loss coefficient tuning

### 5. Economic Analysis
- Energy consumption calculator
- Operating cost estimation
- Carbon footprint analysis
- Efficiency improvement ROI

### 6. DC Motor Problems
- Analytical problem solver
- Step-by-step solutions
- Educational demonstrations

## Educational Applications

This simulator is ideal for:
- **University Courses**: Electrical Machines, Power Electronics
- **Engineering Students**: Hands-on DC motor analysis
- **Research**: Motor design optimization
- **Industry**: Motor selection and sizing
- **Self-Learning**: Interactive exploration of DC motor principles

## Advanced Features

### Multi-Physics Coupling
- Electrical → Mechanical: Torque production
- Mechanical → Electrical: Back EMF generation
- Electrical → Thermal: Resistive heating
- Thermal → Electrical: Resistance variation

### Real-Time Capabilities
- Threaded simulation engine
- Non-blocking GUI updates
- Adjustable time scaling
- Pause/Resume functionality

### Mechanical Stress Analysis
- Shaft torque transients
- Dynamic load calculations
- Bearing load estimation (future)

## Tips for Best Results

1. **Choose RK45** for accurate results
2. **Start with default parameters** to understand behavior
3. **Adjust one parameter at a time** to see effects
4. **Watch thermal derating** to avoid overload
5. **Use economic analysis** after steady-state is reached
6. **Save results** for comparison between runs

## Troubleshooting

### GUI doesn't appear
- Check tkinter installation
- Try `python3 -m tkinter` to test

### Simulation unstable
- Reduce time step (use RK45)
- Check parameter values (realistic ranges)
- Ensure inertia J > 0

### Plots not updating
- Check if simulation is running
- Verify thread is active
- Try Reset and restart

## Future Enhancements
- [ ] Field weakening control
- [ ] PWM chopper simulation
- [ ] Reversing and braking modes
- [ ] Multiple motor comparison
- [ ] Parameter optimization
- [ ] Export to Excel/PDF
- [ ] 3D thermal mapping
- [ ] Acoustic noise prediction

## References
1. P.S. Bimbhra, "Electrical Machinery"
2. A.E. Fitzgerald, "Electric Machinery"
3. Chapman, "Electric Machinery Fundamentals"

## License
Educational and research use.

## Author
Advanced Electrical Engineering Simulation Tool
Version 1.0

## Support
For questions or issues, please refer to the code comments and docstrings.

---

**Enjoy exploring DC motor dynamics!**

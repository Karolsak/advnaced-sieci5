# Advanced DC Motor Analysis Laboratory

## Overview
A comprehensive Python application for DC motor analysis with multi-physics simulation, advanced controls, and economic analysis.

## Features

### 1. Example 30.38 Solution
Automatically solves the classic DC series motor problem:
- **Given**: 4-pole, 250V DC series motor, 20A, 900 RPM
- **Case (i)**: Speed calculation with 0.2Ω divertor in parallel with field
- **Case (ii)**: Speed calculation with field coils in series-parallel arrangement
- Complete mathematical analysis with step-by-step solution

### 2. Multi-Tab Interface

#### Main Parameters Tab
- Adjustable motor parameters with sliders
- Real-time visualization of:
  - Speed (RPM)
  - Current (A)
  - Torque (N·m)
  - Power (W)

#### Advanced Control Tab
- Control modes: Voltage, Current, Speed, Torque
- PID controller with adjustable parameters (Kp, Ki, Kd)
- ODE solver selection: RK45, Euler, RK23, DOP853
- Speed response and error tracking

#### Multi-Physics Tab
- **Electromagnetic Analysis**:
  - Magnetic flux dynamics
  - Voltage components (supply and back EMF)
  - Current (RMS values)

- **Thermal Analysis**:
  - Temperature profile over time
  - Detailed loss breakdown:
    - Copper losses
    - Iron losses
    - Friction losses
    - Stray load losses
  - Thermal derating curve
  - Radial temperature distribution

- **Mechanical Analysis**:
  - Torque transients
  - Speed profile
  - Shaft stress analysis
  - Bearing vibration monitoring

#### Economic Analysis Tab
- Operating cost calculations
- Lifetime cost analysis
- Efficiency comparisons
- CO2 emissions tracking
- Optimization potential and payback period
- Visual breakdowns:
  - Cost distribution pie chart
  - Cumulative cost over lifetime
  - Efficiency comparison
  - Savings potential

#### Results & Analysis Tab
- Comprehensive results display
- Export functionality

### 3. Dynamic Simulation Features
- Real-time ODE solvers (RK45, Euler, RK23, DOP853)
- Coupled electromagnetic-thermal-mechanical models
- Heat transfer equations solved simultaneously
- Mechanical stress analysis
- Detailed loss calculations

### 4. Controls
- **Start**: Begin dynamic simulation
- **Stop**: Pause simulation
- **Reset**: Clear all data and restart
- **Solve Example 30.38**: Calculate the classic problem solution

## Installation

### Requirements
```bash
pip install numpy scipy matplotlib tkinter
```

### Running the Application
```bash
python3 dc_motor_advanced_lab.py
```

## Usage Guide

### Quick Start
1. Launch the application
2. The solution to Example 30.38 is automatically calculated on startup
3. View results in the "Results & Analysis" tab
4. Adjust parameters using sliders in the "Main Parameters" tab
5. Click "Start Simulation" to run dynamic analysis

### Parameter Adjustment
All motor parameters can be adjusted via:
- Direct entry in text fields
- Sliders for visual adjustment
- Changes update in real-time

### Running Simulations
1. Set desired parameters
2. Choose ODE solver method (RK45 recommended for accuracy)
3. Set time step and duration
4. Click "Start Simulation"
5. View results across all tabs

### Economic Analysis
1. Run a simulation first
2. Navigate to "Economic Analysis" tab
3. Adjust economic parameters (electricity cost, operating hours, etc.)
4. Click "Calculate Economics"
5. View cost breakdowns and savings potential

### Exporting Results
1. Navigate to "Results & Analysis" tab
2. Click "Export Results"
3. Results saved to timestamped text file

## Technical Details

### Mathematical Models

#### DC Series Motor Equations
- Voltage: `V = E + Ia(Ra + Rse)`
- Back EMF: `E = ke × ω`
- Torque: `T = kt × Ia`
- For series motor: `Φ ∝ Ia` (unsaturated)

#### Dynamic Equations (ODE System)
```
dω/dt = (T_em - B×ω - T_load) / J
di_a/dt = (V - E - i_a×(Ra + Rse)) / L_a
dT/dt = (P_loss - (T - T_amb)/R_th) / C_th
```

Where:
- ω: Angular velocity
- i_a: Armature current
- T: Temperature
- J: Moment of inertia
- B: Friction coefficient
- L_a: Armature inductance
- R_th: Thermal resistance
- C_th: Thermal capacitance

#### Loss Calculations
- **Copper losses**: `P_cu = I²(Ra + Rse)`
- **Iron losses**: Core losses (simplified model)
- **Friction losses**: Mechanical friction
- **Stray losses**: Additional load losses

### Solution to Example 30.38

#### Original Condition
- Back EMF: E1 = 250 - 20×(0.1 + 0.1) = 246 V
- Speed: 900 RPM

#### Case (i) - With Divertor
- Divertor reduces field current
- Higher armature current needed for same torque
- Speed increases due to reduced flux
- Typical result: ~1200-1400 RPM

#### Case (ii) - Series-Parallel
- Field resistance reduced by 50%
- Flux reduced for same current
- Speed increases significantly
- Typical result: ~1800 RPM

## Features Highlights

### Auto-Scaling
- Responsive design with automatic width/height adjustment
- Grid-based layout adapts to window size
- Matplotlib figures resize automatically

### Real-Time Visualization
- Dynamic plots update during simulation
- Multiple synchronized views
- Color-coded data series

### Advanced Analysis
- Multi-physics coupling
- Thermal derating based on temperature
- Mechanical stress calculations
- Economic optimization

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Display Issues**: Update matplotlib backend if needed
3. **Slow Performance**: Reduce simulation duration or increase time step

### Performance Tips
- Use Euler method for faster (less accurate) results
- Use RK45 for accurate results
- Adjust time step based on system dynamics
- Typical time step: 0.001s for smooth results

## Educational Value

This laboratory tool is designed for:
- Electrical engineering students
- Motor control engineers
- Energy efficiency analysts
- Research and development

### Learning Outcomes
- Understanding DC motor dynamics
- Control system design
- Thermal management
- Economic optimization
- Multi-physics analysis

## Author
Created for Advanced Electrical Networks Course
Example 30.38 Implementation with Complete Laboratory Suite

## Version
1.0.0 - Full featured release with all advanced capabilities

## License
Educational use

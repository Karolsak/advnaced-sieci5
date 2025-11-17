# Quick Start Guide
## Advanced Three-Phase Induction Motor Simulator

### Installation

1. **Install Python Dependencies**
   ```bash
   pip install numpy scipy matplotlib
   ```

2. **Verify Installation**
   ```bash
   python3 -c "import numpy, scipy, matplotlib, tkinter; print('All dependencies OK!')"
   ```

### Running the Simulator

```bash
python3 induction_motor_simulator.py
```

### Quick Tutorial

#### 1. Calculate Example 6.2 (5 seconds)
1. Launch the application
2. Go to **"Main Results"** tab (default)
3. Click **"Calculate"** button
4. View complete analysis results

#### 2. Run Dynamic Simulation (1 minute)
1. Go to **"Dynamic Simulation"** tab
2. Select solver: **RK45** (recommended) or **Euler**
3. Set simulation time: **5.0** seconds (default)
4. Click **"▶ Start"** button
5. Watch real-time plots:
   - Speed ramp-up
   - Torque transients
   - Current variations
   - Temperature rise

#### 3. View Motor Characteristics (30 seconds)
1. Go to **"Characteristics"** tab
2. Click **"Generate Curves"** button
3. Analyze:
   - Torque-speed curve (with max torque point)
   - Current-speed curve (starting current)
   - Efficiency curve (optimal operating point)
   - Power-speed curve

#### 4. Analyze Losses (1 minute)
1. Go to **"Multi-Physics"** tab
2. Left panel: Click **"Calculate Losses"**
3. View detailed loss breakdown:
   - Stator copper loss
   - Rotor copper loss
   - Core loss
   - Friction and windage
   - Stray losses
4. See loss distribution pie chart

#### 5. Run Coupled Simulation (2 minutes)
1. Stay in **"Multi-Physics"** tab
2. Right panel: Click **"Run Coupled Simulation"**
3. View electromagnetic-thermal interaction:
   - Temperature rise over 10 seconds
   - Power derating factor
   - Thermal time constant

#### 6. Economic Analysis (1 minute)
1. Go to **"Economic Analysis"** tab
2. Adjust parameters (optional):
   - Electricity cost ($/kWh)
   - Operating hours per year
   - Initial cost
   - Maintenance cost
3. Click **"Calculate Economics"**
4. Review:
   - Annual energy cost
   - Life cycle cost
   - Payback period
   - ROI

### Experiment with Parameters

#### Modify Voltage (See Effect on Torque)
1. Go to **"Parameters & Control"** tab
2. Adjust **"Voltage (V)"** slider: 300V → 420V → 500V
3. Return to **"Main Results"** tab
4. Click **"Calculate"**
5. Observe torque changes (proportional to V²)

#### Change Frequency (V/f Control)
1. Adjust **"Frequency (Hz)"** slider: 30Hz → 60Hz → 90Hz
2. Click **"Calculate"**
3. Note synchronous speed changes

#### Vary Slip (Load Condition)
1. Adjust **"Slip"** slider: 0.01 → 0.03 → 0.10
2. Click **"Calculate"**
3. See efficiency and current variations

#### Thermal Analysis
1. Increase **"Ambient Temp (°C)"**: 25°C → 40°C
2. Run **"Coupled Simulation"**
3. Observe faster temperature rise and increased derating

### Key Features to Explore

#### Control Methods
- **V/f Control**: Constant V/f ratio, simple implementation
- **DTC**: Fast torque response, no encoder needed
- **FOC**: Excellent dynamic performance, requires position sensor

#### Solver Comparison
- **RK45**: Adaptive, accurate, slower
- **Euler**: Fixed step, faster, less accurate

Run same simulation with both methods and compare!

#### Operating Points
The simulator marks operating points on characteristic curves:
- **Green dashed line**: Current operating speed
- **Red dashed line**: Maximum torque point
- **Critical slip**: Point of maximum torque

### Common Results (Example 6.2)

Expected values at 60 Hz, 420V, slip=0.03:
- **Synchronous Speed**: 600 RPM
- **Rotor Speed**: ~582 RPM
- **Efficiency**: ~85-90%
- **Power Factor**: ~0.75-0.85 lagging
- **Starting Torque Ratio**: ~1.5-2.0
- **Overload Capacity**: ~2.0-2.5

### Troubleshooting

#### GUI doesn't open
- Check tkinter installation: `python3 -m tkinter`
- Install system package: `sudo apt-get install python3-tk` (Linux)

#### Simulation runs slowly
- Reduce simulation time
- Try Euler method instead of RK45
- Close other resource-intensive applications

#### Plots don't update
- Click "Reset" and try again
- Check console for error messages
- Ensure parameters are in valid ranges

#### Unrealistic results
- Verify input parameters
- Check slip is between 0.001 and 0.3
- Ensure voltage and frequency are reasonable

### Tips for Best Experience

1. **Start Simple**: Run default Example 6.2 first
2. **Change One Parameter**: Vary one parameter at a time to see effects
3. **Save Results**: Use "Export Results" to save calculations
4. **Compare Methods**: Run simulations with different solvers
5. **Thermal Limits**: Watch temperature approach max (155°C)
6. **Economic Sense**: Calculate ROI for motor upgrades

### Advanced Usage

#### Custom Load Profile
Edit `load_torque_profile()` method in code:
```python
def load_torque_profile(self, t, omega):
    if t < 1.0:
        return 5.0  # Light load
    elif t < 3.0:
        return 20.0  # Step load
    else:
        return 15.0 + 0.01 * omega**2  # Quadratic load
```

#### Batch Analysis
Run simulations for multiple parameter sets programmatically.

#### Export Data
Modify `export_results()` to save to CSV for further analysis.

### Learning Path

1. **Day 1**: Understand basic calculations (Main Results tab)
2. **Day 2**: Explore characteristics (Torque-speed curves)
3. **Day 3**: Dynamic behavior (Transient simulations)
4. **Day 4**: Multi-physics (Thermal analysis)
5. **Day 5**: Economic analysis (Cost optimization)

### Next Steps

After mastering the basics:
1. Study different control methods
2. Analyze energy efficiency
3. Optimize motor selection
4. Design drive systems
5. Contribute enhancements

### Getting Help

- Read comprehensive `README_motor_simulator.md`
- Check code comments for implementation details
- Review electrical machines textbooks for theory

---

**Happy Simulating!** 🔧⚡🎯

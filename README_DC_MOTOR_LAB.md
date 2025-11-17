# Advanced DC Motor Analysis Laboratory

## Comprehensive Multi-Physics Simulation Tool

### Problem Statement

This laboratory solves the following DC motor problem:

**A 440-V shunt motor takes an armature current of 50 A and has a flux/pole of 50 mWb. If the flux is suddenly decreased to 45 mWb, calculate:**

- **(a)** Instantaneous increase in armature current
- **(b)** Percentage increase in the motor torque due to increase in current
- **(c)** Value of steady current which motor will take eventually
- **(d)** The final percentage increase in motor speed

### Solution Summary

When flux drops from 50 mWb to 45 mWb:
- **Current instantly increases by 68.33 A** (from 50 A to 118.33 A)
- **Torque temporarily increases by 113.0%**
- **Final steady-state current: 55.56 A**
- **Final speed increases by 10.21%**

---

## Features

- Complete theoretical solution with verification
- Multi-physics simulation (electromagnetic-thermal-mechanical coupling)
- Real-time ODE solvers (RK45, Euler, BDF, LSODA)
- Comprehensive GUI with multiple analysis tabs
- Detailed loss breakdown
- Economic analysis
- Auto-scaling responsive interface

---

## Usage

### Run Full GUI Application:
```bash
python3 dc_motor_advanced_lab_comprehensive.py
```

### Run CLI Test:
```bash
python3 test_solver_only.py
```

---

## Test Results

```
(a) Instantaneous current increase:  68.33 A
(b) Torque increase percentage:      113.00%
(c) Steady state current:            55.56 A
(d) Speed increase percentage:       10.21%
```

✓ All calculations verified!

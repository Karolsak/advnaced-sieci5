"""
Induction Motor Calculator (No GUI Version)
Standalone script for Example 6.2 calculations without tkinter dependency
"""

import numpy as np
from scipy.integrate import solve_ivp


class InductionMotorCalculator:
    """Calculator for induction motor analysis without GUI dependencies"""

    def __init__(self):
        # Default parameters from Example 6.2
        self.params = {
            'poles': 12,
            'V_ll': 420,  # Line-to-line voltage (V)
            'power_rated': 5500,  # Rated power (W)
            'frequency': 60,  # Input frequency (Hz)
            'R1': 0.833,  # Stator resistance (Ω)
            'X1': 1.864,  # Stator reactance (Ω)
            'R2_prime': 0.833,  # Rotor resistance referred to stator (Ω)
            'X2_prime': 1.864,  # Rotor reactance referred to stator (Ω)
            'Xm': 36.25,  # Magnetizing reactance (Ω)
            'slip': 0.03,  # Operating slip
            'P_rot': 250,  # Rotational losses (W)
            'P_str': 60,  # Stray losses (W)
        }

    def solve_example_6_2(self):
        """Complete solution for Example 6.2"""
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
        R2_over_s = R2 / s
        Z_rotor = R2_over_s + 1j * X2
        Z_parallel = (1j * Xm * Z_rotor) / (1j * Xm + Z_rotor)
        Z_total = (R1 + 1j * X1) + Z_parallel

        I1 = V_ph / Z_total
        I1_mag = abs(I1)
        I1_angle = np.angle(I1, deg=True)

        I2_prime = I1 * (1j * Xm) / (1j * Xm + Z_rotor)
        I2_prime_mag = abs(I2_prime)
        I2_prime_angle = np.angle(I2_prime, deg=True)

        results['I1'] = I1_mag
        results['I1_angle'] = I1_angle
        results['I2_prime'] = I2_prime_mag
        results['I2_prime_angle'] = I2_prime_angle

        # (c) Stator and rotor winding losses
        P_cu1 = 3 * I1_mag**2 * R1
        P_cu2 = 3 * I2_prime_mag**2 * R2

        results['P_cu1'] = P_cu1
        results['P_cu2'] = P_cu2

        # (d) Electromagnetic power and torque
        P_ag = 3 * I2_prime_mag**2 * R2_over_s
        T_elm = P_ag / omega_s

        results['P_ag'] = P_ag
        results['T_elm'] = T_elm

        # (e) Mechanical power and output power
        P_mech = P_ag * (1 - s)
        P_out = P_mech - P_rot - P_str

        results['P_mech'] = P_mech
        results['P_out'] = P_out

        # (f) Input power, efficiency, and power factor
        P_in = P_cu1 + P_ag
        efficiency = (P_out / P_in) * 100 if P_in > 0 else 0

        S_in = 3 * V_ph * I1_mag
        pf = P_in / S_in if S_in > 0 else 0

        results['P_in'] = P_in
        results['efficiency'] = efficiency
        results['pf'] = pf

        # (g) Starting torque and STR
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
        Z_th = (1j * Xm * (R1 + 1j * X1)) / (R1 + 1j * (X1 + Xm))
        V_th = V_ph * (1j * Xm) / (R1 + 1j * (X1 + Xm))

        R_th = abs(Z_th.real)
        X_th = abs(Z_th.imag)
        V_th_mag = abs(V_th)

        s_cr = R2 / np.sqrt(R_th**2 + (X_th + X2)**2)

        T_elm_max = (3 * V_th_mag**2) / (2 * omega_s * (R_th + np.sqrt(R_th**2 + (X_th + X2)**2)))

        OCF = T_elm_max / T_elm if T_elm > 0 else 0

        results['s_cr'] = s_cr
        results['T_elm_max'] = T_elm_max
        results['OCF'] = OCF

        return results

    def print_results(self, results):
        """Print formatted results"""
        print("=" * 80)
        print("EXAMPLE 6.2 - THREE-PHASE INDUCTION MOTOR ANALYSIS")
        print("=" * 80)
        print()
        print("GIVEN PARAMETERS:")
        print("-" * 80)
        print(f"Poles (2p):               {self.params['poles']}")
        print(f"Line-to-Line Voltage:     {self.params['V_ll']} V")
        print(f"Rated Power:              {self.params['power_rated']/1000} kW")
        print(f"Frequency:                {self.params['frequency']} Hz")
        print(f"Stator Resistance (R1):   {self.params['R1']} Ω")
        print(f"Stator Reactance (X1):    {self.params['X1']} Ω")
        print(f"Rotor Resistance (R2'):   {self.params['R2_prime']} Ω")
        print(f"Rotor Reactance (X2'):    {self.params['X2_prime']} Ω")
        print(f"Magnetizing Reactance:    {self.params['Xm']} Ω")
        print(f"Operating Slip:           {self.params['slip']}")
        print(f"Rotational Losses:        {self.params['P_rot']} W")
        print(f"Stray Losses:             {self.params['P_str']} W")
        print()
        print("CALCULATED RESULTS:")
        print("=" * 80)
        print()
        print("(a) SPEEDS:")
        print("-" * 80)
        print(f"Synchronous Speed:        {results['n_s']:.2f} RPM ({results['omega_s']:.3f} rad/s)")
        print(f"Rotor Speed:              {results['n_r']:.2f} RPM ({results['omega_r']:.3f} rad/s)")
        print()
        print("(b) CURRENTS:")
        print("-" * 80)
        print(f"Stator Current (I1):      {results['I1']:.3f} A ∠{results['I1_angle']:.2f}°")
        print(f"Rotor Current (I2'):      {results['I2_prime']:.3f} A ∠{results['I2_prime_angle']:.2f}°")
        print(f"Starting Current:         {results['I1_start']:.3f} A")
        print(f"Starting Current Ratio:   {results['I1_start']/results['I1']:.2f}")
        print()
        print("(c) LOSSES:")
        print("-" * 80)
        print(f"Stator Copper Loss:       {results['P_cu1']:.2f} W")
        print(f"Rotor Copper Loss:        {results['P_cu2']:.2f} W")
        print(f"Total Copper Loss:        {results['P_cu1'] + results['P_cu2']:.2f} W")
        print()
        print("(d) ELECTROMAGNETIC POWER AND TORQUE:")
        print("-" * 80)
        print(f"Air Gap Power (P_ag):     {results['P_ag']:.2f} W ({results['P_ag']/1000:.3f} kW)")
        print(f"Electromagnetic Torque:   {results['T_elm']:.3f} N·m")
        print()
        print("(e) MECHANICAL POWER:")
        print("-" * 80)
        print(f"Mechanical Power:         {results['P_mech']:.2f} W ({results['P_mech']/1000:.3f} kW)")
        print(f"Output Power:             {results['P_out']:.2f} W ({results['P_out']/1000:.3f} kW)")
        print()
        print("(f) EFFICIENCY AND POWER FACTOR:")
        print("-" * 80)
        print(f"Input Power:              {results['P_in']:.2f} W ({results['P_in']/1000:.3f} kW)")
        print(f"Efficiency:               {results['efficiency']:.2f} %")
        print(f"Power Factor:             {results['pf']:.4f} {'(lagging)' if results['I1_angle'] < 0 else '(leading)'}")
        print()
        print("(g) STARTING PERFORMANCE:")
        print("-" * 80)
        print(f"Starting Torque:          {results['T_elm_start']:.3f} N·m")
        print(f"Starting Torque Ratio:    {results['STR']:.3f}")
        print()
        print("(h) MAXIMUM TORQUE:")
        print("-" * 80)
        print(f"Critical Slip:            {results['s_cr']:.4f}")
        print(f"Maximum Torque:           {results['T_elm_max']:.3f} N·m")
        print(f"Overload Capacity Factor: {results['OCF']:.3f}")
        print()
        print("=" * 80)


def main():
    """Main function for standalone execution"""
    print("\nAdvanced Induction Motor Calculator")
    print("Solving Example 6.2...\n")

    calc = InductionMotorCalculator()
    results = calc.solve_example_6_2()
    calc.print_results(results)

    print("\n✓ Calculation completed successfully!")
    print("\nNote: For full GUI features, run: python3 induction_motor_simulator.py")


if __name__ == "__main__":
    main()

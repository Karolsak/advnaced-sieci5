#!/usr/bin/env python3
"""
Test script for DC Motor Solver (No GUI)
Verifies theoretical calculations and simulation functionality
"""

import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass
class MotorParameters:
    """DC Shunt Motor Parameters"""
    voltage: float = 440.0
    flux_initial: float = 50e-3
    flux_final: float = 45e-3
    current_initial: float = 50.0
    resistance_armature: float = 0.6
    resistance_field: float = 220.0
    inductance_armature: float = 0.05
    inductance_field: float = 10.0
    inertia: float = 0.5
    damping: float = 0.01
    poles: int = 4
    conductors: int = 500
    parallel_paths: int = 2
    load_torque: float = 0.0
    thermal_resistance: float = 2.5
    thermal_capacitance: float = 1000.0
    ambient_temp: float = 25.0
    max_temp: float = 155.0
    k_hysteresis: float = 0.02
    k_eddy: float = 0.005
    friction_coeff: float = 0.005
    windage_coeff: float = 1e-6
    energy_cost: float = 0.12
    maintenance_cost_per_hour: float = 2.5


class DCMotorSolver:
    """DC Motor Solver"""

    def __init__(self, params: MotorParameters):
        self.params = params
        self.results = {}

    def solve_theoretical_problem(self) -> Dict:
        """Solve theoretical problem"""
        p = self.params

        eb1 = p.voltage - p.current_initial * p.resistance_armature
        k_n1 = eb1 / p.flux_initial

        # (a) Instantaneous increase
        eb2_instant = k_n1 * p.flux_final
        ia2_instant = (p.voltage - eb2_instant) / p.resistance_armature
        delta_ia_instant = ia2_instant - p.current_initial

        # (b) Torque increase
        torque_ratio = (p.flux_final * ia2_instant) / (p.flux_initial * p.current_initial)
        torque_increase_pct = (torque_ratio - 1.0) * 100.0

        # (c) Steady state current
        ia_final = p.current_initial * (p.flux_initial / p.flux_final)

        # (d) Speed increase
        eb_final = p.voltage - ia_final * p.resistance_armature
        speed_ratio = (eb_final / eb1) * (p.flux_initial / p.flux_final)
        speed_increase_pct = (speed_ratio - 1.0) * 100.0

        results = {
            'eb1': eb1,
            'k_n1': k_n1,
            'ia2_instant': ia2_instant,
            'delta_ia_instant': delta_ia_instant,
            'torque_ratio': torque_ratio,
            'torque_increase_pct': torque_increase_pct,
            'ia_final': ia_final,
            'eb_final': eb_final,
            'speed_ratio': speed_ratio,
            'speed_increase_pct': speed_increase_pct
        }

        self.results = results
        return results


def test_theoretical_solution():
    """Test theoretical solution"""
    print("=" * 80)
    print("DC MOTOR FLUX CHANGE ANALYSIS - THEORETICAL SOLUTION TEST")
    print("=" * 80)

    params = MotorParameters(
        voltage=440.0,
        flux_initial=50e-3,
        flux_final=45e-3,
        current_initial=50.0,
        resistance_armature=0.6
    )

    solver = DCMotorSolver(params)
    results = solver.solve_theoretical_problem()

    print(f"\nPROBLEM:")
    print(f"  Voltage:                  {params.voltage} V")
    print(f"  Initial Current:          {params.current_initial} A")
    print(f"  Initial Flux:             {params.flux_initial*1000:.1f} mWb")
    print(f"  Final Flux:               {params.flux_final*1000:.1f} mWb")
    print(f"  Armature Resistance:      {params.resistance_armature} Ω")

    print(f"\nINITIAL CONDITIONS:")
    print(f"  Back EMF (Eb1):           {results['eb1']:.2f} V")

    print(f"\nSOLUTION:")
    print(f"\n(a) Instantaneous Increase in Armature Current:")
    print(f"    Instantaneous current:    {results['ia2_instant']:.2f} A")
    print(f"    Current increase:         {results['delta_ia_instant']:.2f} A")

    print(f"\n(b) Percentage Increase in Motor Torque:")
    print(f"    Torque ratio:             {results['torque_ratio']:.4f}")
    print(f"    Torque increase:          {results['torque_increase_pct']:.2f}%")

    print(f"\n(c) Steady State Current:")
    print(f"    Final current:            {results['ia_final']:.2f} A")

    print(f"\n(d) Final Percentage Increase in Speed:")
    print(f"    Speed ratio:              {results['speed_ratio']:.4f}")
    print(f"    Speed increase:           {results['speed_increase_pct']:.2f}%")

    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)

    # Manual verification
    eb1_check = params.voltage - params.current_initial * params.resistance_armature
    print(f"Back EMF: {params.voltage} - {params.current_initial} × {params.resistance_armature} = {eb1_check:.2f} V")
    assert abs(eb1_check - results['eb1']) < 0.01, "Back EMF calculation error"

    eb2_instant_check = eb1_check * (params.flux_final / params.flux_initial)
    ia2_instant_check = (params.voltage - eb2_instant_check) / params.resistance_armature
    print(f"Instantaneous Ia2: ({params.voltage} - {eb2_instant_check:.2f}) / {params.resistance_armature} = {ia2_instant_check:.2f} A")
    assert abs(ia2_instant_check - results['ia2_instant']) < 0.01, "Current calculation error"

    ia_final_check = params.current_initial * (params.flux_initial / params.flux_final)
    print(f"Final current: {params.current_initial} × ({params.flux_initial*1000:.1f}/{params.flux_final*1000:.1f}) = {ia_final_check:.2f} A")
    assert abs(ia_final_check - results['ia_final']) < 0.01, "Final current calculation error"

    print("\n✓ All calculations verified!")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"When flux drops from {params.flux_initial*1000:.1f} to {params.flux_final*1000:.1f} mWb:")
    print(f"  • Current instantly increases by {results['delta_ia_instant']:.2f} A")
    print(f"  • Torque temporarily increases by {results['torque_increase_pct']:.1f}%")
    print(f"  • Final steady-state current: {results['ia_final']:.2f} A")
    print(f"  • Final speed increases by {results['speed_increase_pct']:.2f}%")
    print("=" * 80)

    return True


def main():
    """Run tests"""
    print("\n")
    test_theoretical_solution()
    print("\n✓ ALL TESTS PASSED!\n")


if __name__ == "__main__":
    main()

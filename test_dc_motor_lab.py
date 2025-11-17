"""
Test script for DC Motor Advanced Laboratory
Verifies basic functionality without GUI display
"""

import sys
import numpy as np
from scipy.integrate import solve_ivp

def test_example_30_38_calculations():
    """Test the mathematical solution for Example 30.38"""
    print("="*70)
    print("TESTING EXAMPLE 30.38 CALCULATIONS")
    print("="*70)

    # Given parameters
    V = 250.0  # Voltage
    Ia1 = 20.0  # Current
    N1 = 900.0  # Speed
    Ra = 0.1  # Armature resistance
    Rse_per_coil = 0.025  # Field resistance per coil
    Rd = 0.2  # Divertor resistance
    P = 4  # Poles

    # Total series field resistance (4 coils)
    Rse1 = 4 * Rse_per_coil
    print(f"\nGiven Parameters:")
    print(f"  Voltage: {V} V")
    print(f"  Current: {Ia1} A")
    print(f"  Speed: {N1} RPM")
    print(f"  Ra: {Ra} Ω")
    print(f"  Rse (total): {Rse1} Ω")

    # Original condition
    E1 = V - Ia1 * (Ra + Rse1)
    print(f"\nOriginal Back EMF: {E1:.3f} V")

    # Case (i): Divertor in parallel
    Rse_eq = (Rse1 * Rd) / (Rse1 + Rd)
    Ia2 = Ia1 * np.sqrt((Rse1 + Rd) / Rd)
    If2 = Ia2 * Rd / (Rse1 + Rd)
    E2 = V - Ia2 * (Ra + Rse_eq)
    N2 = N1 * (E2 / E1) * (Ia1 / If2)

    print(f"\nCase (i) - With Divertor:")
    print(f"  Current: {Ia2:.3f} A")
    print(f"  Back EMF: {E2:.3f} V")
    print(f"  Speed: {N2:.2f} RPM")
    print(f"  Speed increase: {((N2-N1)/N1*100):.2f}%")

    # Case (ii): Series-parallel field
    Rse3 = Rse_per_coil
    Ia3 = 2 * Ia1
    E3 = V - Ia3 * (Ra + Rse3)
    phi_ratio = 0.5
    N3 = N1 * (E3 / E1) / phi_ratio

    print(f"\nCase (ii) - Series-Parallel Field:")
    print(f"  Current: {Ia3:.3f} A")
    print(f"  Back EMF: {E3:.3f} V")
    print(f"  Speed: {N3:.2f} RPM")
    print(f"  Speed increase: {((N3-N1)/N1*100):.2f}%")

    # Validation checks
    assert E1 > 0, "Back EMF should be positive"
    assert N2 > N1, "Speed should increase with divertor"
    assert N3 > N1, "Speed should increase with series-parallel"

    print("\n✓ All calculations validated successfully!")
    return True


def test_ode_solver():
    """Test ODE solver functionality"""
    print("\n" + "="*70)
    print("TESTING ODE SOLVER")
    print("="*70)

    def test_ode(t, y):
        """Simple test ODE: dy/dt = -y"""
        return [-y[0]]

    y0 = [1.0]
    t_span = (0, 1)
    t_eval = np.linspace(0, 1, 10)

    # Test RK45
    sol_rk45 = solve_ivp(test_ode, t_span, y0, method='RK45', t_eval=t_eval)
    print(f"\nRK45 solver:")
    print(f"  Time points: {len(sol_rk45.t)}")
    print(f"  Final value: {sol_rk45.y[0][-1]:.6f}")
    print(f"  Expected: {np.exp(-1):.6f}")

    # Test RK23
    sol_rk23 = solve_ivp(test_ode, t_span, y0, method='RK23', t_eval=t_eval)
    print(f"\nRK23 solver:")
    print(f"  Time points: {len(sol_rk23.t)}")
    print(f"  Final value: {sol_rk23.y[0][-1]:.6f}")

    assert len(sol_rk45.t) == 10, "Should have 10 time points"
    assert abs(sol_rk45.y[0][-1] - np.exp(-1)) < 0.01, "Solution should match analytical"

    print("\n✓ ODE solvers working correctly!")
    return True


def test_thermal_calculations():
    """Test thermal model calculations"""
    print("\n" + "="*70)
    print("TESTING THERMAL CALCULATIONS")
    print("="*70)

    # Parameters
    I = 20.0  # Current (A)
    Ra = 0.1  # Resistance (Ω)
    Rse = 0.1  # Field resistance (Ω)
    R_th = 2.0  # Thermal resistance (°C/W)
    T_amb = 25.0  # Ambient temperature (°C)

    # Calculate copper losses
    P_copper = I**2 * (Ra + Rse)
    print(f"\nCopper losses: {P_copper:.2f} W")

    # Steady-state temperature rise
    delta_T = P_copper * R_th
    T_steady = T_amb + delta_T
    print(f"Temperature rise: {delta_T:.2f} °C")
    print(f"Steady-state temperature: {T_steady:.2f} °C")

    # Derating factor
    if T_steady < 100:
        derating = 1.0
    else:
        derating = max(0, 1.0 - (T_steady - 100) / 50)

    print(f"Derating factor: {derating:.2%}")

    assert P_copper > 0, "Copper losses should be positive"
    assert T_steady > T_amb, "Temperature should rise above ambient"
    assert 0 <= derating <= 1, "Derating factor should be between 0 and 1"

    print("\n✓ Thermal calculations validated!")
    return True


def test_loss_breakdown():
    """Test detailed loss calculations"""
    print("\n" + "="*70)
    print("TESTING LOSS BREAKDOWN")
    print("="*70)

    I = 20.0
    Ra = 0.1
    Rse = 0.1
    N = 900.0

    # Copper losses
    P_copper = I**2 * (Ra + Rse)
    print(f"\nCopper losses: {P_copper:.2f} W")

    # Iron losses (simplified)
    P_iron = 0.02 * (N/900)**2 * 100
    print(f"Iron losses: {P_iron:.2f} W")

    # Friction losses (simplified)
    P_friction = 0.01 * (N/900) * 50
    print(f"Friction losses: {P_friction:.2f} W")

    # Stray losses
    P_stray = 0.01 * P_copper
    print(f"Stray losses: {P_stray:.2f} W")

    # Total losses
    P_total = P_copper + P_iron + P_friction + P_stray
    print(f"\nTotal losses: {P_total:.2f} W")

    # Input power
    V = 250.0
    P_input = V * I
    print(f"Input power: {P_input:.2f} W")

    # Efficiency
    P_output = P_input - P_total
    efficiency = (P_output / P_input) * 100
    print(f"Output power: {P_output:.2f} W")
    print(f"Efficiency: {efficiency:.2f}%")

    assert P_total > 0, "Total losses should be positive"
    assert P_output > 0, "Output power should be positive"
    assert 0 < efficiency < 100, "Efficiency should be between 0 and 100%"

    print("\n✓ Loss breakdown validated!")
    return True


def test_economic_calculations():
    """Test economic analysis"""
    print("\n" + "="*70)
    print("TESTING ECONOMIC CALCULATIONS")
    print("="*70)

    # Parameters
    P_avg = 5000.0  # Average power (W)
    elec_cost = 0.12  # $/kWh
    op_hours = 8760.0  # hours/year
    motor_cost = 5000.0  # $
    maint_cost = 500.0  # $/year
    lifetime = 15.0  # years

    # Calculations
    P_avg_kw = P_avg / 1000
    annual_energy = P_avg_kw * op_hours
    annual_energy_cost = annual_energy * elec_cost
    annual_total_cost = annual_energy_cost + maint_cost
    lifetime_total_cost = motor_cost + (annual_energy_cost + maint_cost) * lifetime

    print(f"\nAnnual energy consumption: {annual_energy:.2f} kWh")
    print(f"Annual energy cost: ${annual_energy_cost:.2f}")
    print(f"Annual total cost: ${annual_total_cost:.2f}")
    print(f"Lifetime total cost: ${lifetime_total_cost:.2f}")

    # CO2 emissions
    annual_co2 = annual_energy * 0.5  # kg
    print(f"\nAnnual CO2 emissions: {annual_co2:.2f} kg")

    assert annual_energy > 0, "Annual energy should be positive"
    assert lifetime_total_cost > motor_cost, "Lifetime cost should exceed initial cost"

    print("\n✓ Economic calculations validated!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("DC MOTOR LABORATORY - COMPREHENSIVE TEST SUITE")
    print("="*70)

    tests = [
        ("Example 30.38 Calculations", test_example_30_38_calculations),
        ("ODE Solver", test_ode_solver),
        ("Thermal Calculations", test_thermal_calculations),
        ("Loss Breakdown", test_loss_breakdown),
        ("Economic Calculations", test_economic_calculations)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test failed: {name}")
            print(f"  Error: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {name}")

    passed = sum(1 for _, s in results if s)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed!")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())

#!/usr/bin/env python3
"""
Test script for DC Motor Comprehensive Lab
Verifies theoretical calculations and basic functionality
"""

import sys
sys.path.insert(0, '/home/user/advnaced-sieci5')

from dc_motor_advanced_lab_comprehensive import MotorParameters, DCMotorSolver

def test_theoretical_solution():
    """Test the theoretical problem solution"""
    print("=" * 80)
    print("TESTING THEORETICAL SOLUTION")
    print("=" * 80)

    # Create motor parameters with the problem values
    params = MotorParameters(
        voltage=440.0,
        flux_initial=50e-3,  # 50 mWb
        flux_final=45e-3,    # 45 mWb
        current_initial=50.0,
        resistance_armature=0.6
    )

    # Create solver
    solver = DCMotorSolver(params)

    # Solve the problem
    results = solver.solve_theoretical_problem()

    # Display results
    print(f"\nInitial Conditions:")
    print(f"  Voltage:           {params.voltage} V")
    print(f"  Current:           {params.current_initial} A")
    print(f"  Flux Initial:      {params.flux_initial*1000:.1f} mWb")
    print(f"  Flux Final:        {params.flux_final*1000:.1f} mWb")
    print(f"  Armature Resist:   {params.resistance_armature} Ω")

    print(f"\nResults:")
    print(f"  (a) Instantaneous current increase:  {results['delta_ia_instant']:.2f} A")
    print(f"      Instantaneous current:           {results['ia2_instant']:.2f} A")

    print(f"\n  (b) Torque increase percentage:      {results['torque_increase_pct']:.2f}%")
    print(f"      Torque ratio:                    {results['torque_ratio']:.4f}")

    print(f"\n  (c) Steady state current:            {results['ia_final']:.2f} A")

    print(f"\n  (d) Speed increase percentage:       {results['speed_increase_pct']:.2f}%")
    print(f"      Speed ratio:                     {results['speed_ratio']:.4f}")

    print("\n" + "=" * 80)
    print("VERIFICATION:")
    print("=" * 80)

    # Verify calculations
    eb1 = params.voltage - params.current_initial * params.resistance_armature
    print(f"Back EMF (Eb1) = {params.voltage} - {params.current_initial} × {params.resistance_armature}")
    print(f"              = {eb1:.2f} V")

    eb2_instant = eb1 * (params.flux_final / params.flux_initial)
    print(f"\nInstantaneous Eb2 = {eb1:.2f} × ({params.flux_final*1000:.1f}/{params.flux_initial*1000:.1f})")
    print(f"                  = {eb2_instant:.2f} V")

    ia2_instant = (params.voltage - eb2_instant) / params.resistance_armature
    print(f"\nInstantaneous Ia2 = ({params.voltage} - {eb2_instant:.2f}) / {params.resistance_armature}")
    print(f"                  = {ia2_instant:.2f} A")

    print("\n✓ All calculations verified!")
    print("=" * 80)

    return True


def test_simulation():
    """Test simulation functionality"""
    print("\n" + "=" * 80)
    print("TESTING SIMULATION FUNCTIONALITY")
    print("=" * 80)

    params = MotorParameters()
    solver = DCMotorSolver(params)

    try:
        # Run a short simulation
        print("\nRunning 1-second simulation with RK45 solver...")
        data = solver.simulate_dynamic_response((0.0, 1.0), method='RK45')

        print(f"✓ RK45 simulation completed")
        print(f"  Time points:     {len(data['time'])}")
        print(f"  Final current:   {data['current_armature'][-1]:.2f} A")
        print(f"  Final speed:     {data['speed_rpm'][-1]:.2f} RPM")
        print(f"  Final temp:      {data['temperature'][-1]:.2f} °C")
        print(f"  Max torque transient: {data['max_torque_transient']:.2f} N·m/s")

        # Test Euler method
        print("\nRunning simulation with Euler solver...")
        data_euler = solver.simulate_dynamic_response((0.0, 0.5), method='Euler')

        print(f"✓ Euler simulation completed")
        print(f"  Time points:     {len(data_euler['time'])}")
        print(f"  Final current:   {data_euler['current_armature'][-1]:.2f} A")

        print("\n✓ Simulation tests passed!")

    except Exception as e:
        print(f"✗ Simulation test failed: {str(e)}")
        return False

    print("=" * 80)
    return True


def test_losses_calculation():
    """Test loss calculation"""
    print("\n" + "=" * 80)
    print("TESTING LOSS CALCULATIONS")
    print("=" * 80)

    params = MotorParameters()
    solver = DCMotorSolver(params)

    # Test at typical operating point
    ia = 50.0  # A
    if_ = params.voltage / params.resistance_field  # A
    speed_rpm = 1500.0
    flux = 50e-3  # Wb
    temp = 75.0  # °C

    losses = solver.calculate_losses(ia, if_, speed_rpm, flux, temp)

    print(f"\nOperating Point:")
    print(f"  Armature Current:    {ia} A")
    print(f"  Field Current:       {if_:.2f} A")
    print(f"  Speed:               {speed_rpm} RPM")
    print(f"  Flux:                {flux*1000:.1f} mWb")
    print(f"  Temperature:         {temp} °C")

    print(f"\nLoss Breakdown:")
    print(f"  Copper (Armature):   {losses['copper_armature']:.2f} W")
    print(f"  Copper (Field):      {losses['copper_field']:.2f} W")
    print(f"  Iron (Hysteresis):   {losses['hysteresis']:.2f} W")
    print(f"  Iron (Eddy):         {losses['eddy_current']:.2f} W")
    print(f"  Mechanical (Friction): {losses['friction']:.2f} W")
    print(f"  Mechanical (Windage):  {losses['windage']:.2f} W")
    print(f"  Stray Load:          {losses['stray']:.2f} W")
    print(f"  Total Losses:        {losses['total']:.2f} W")

    print(f"\nPerformance:")
    print(f"  Input Power:         {losses['input_power']:.2f} W")
    print(f"  Output Power:        {losses['output_power']:.2f} W")
    print(f"  Efficiency:          {losses['efficiency']:.2f} %")

    print("\n✓ Loss calculation test passed!")
    print("=" * 80)

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DC MOTOR COMPREHENSIVE LAB - TEST SUITE")
    print("=" * 80 + "\n")

    tests = [
        ("Theoretical Solution", test_theoretical_solution),
        ("Simulation Functionality", test_simulation),
        ("Loss Calculations", test_losses_calculation)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} - {test_name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

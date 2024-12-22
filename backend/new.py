import numpy as np
from sympy import symbols, Eq, solve, sympify

# Function to calculate fixed-end moments
def fixed_end_moments(load_type, load_params, length):
    if load_type == "point":
        P = load_params["P"]
        a = load_params["a"]
        b = length - a
        FEM_AB = -P * b**2 * a / length**2
        FEM_BA = P * a**2 * b / length**2
    elif load_type == "udl":
        w = load_params["w"]
        FEM_AB = -w * length**2 / 12
        FEM_BA = w * length**2 / 12
    elif load_type == "vdl":
        w = load_params["w"]
        FEM_AB = -w * length**2 / 20
        FEM_BA = w * length**2 / 20
    elif load_type == "none":
        FEM_AB, FEM_BA = 0, 0
    else:
        raise ValueError("Unsupported load type.")
    return FEM_AB, FEM_BA

# Function to collect user input
def get_user_input():
    num_supports = int(input("Enter the number of supports (minimum 2): "))
    supports = []
    for i in range(num_supports):
        support_type = input(f"Enter the type of support {i + 1} (hinged, fixed, roller): ").lower()
        position = float(input(f"Enter the position of support {i + 1}: "))
        supports.append({"type": support_type, "position": position})

    supports.sort(key=lambda x: x['position'])
    spans = []
    for i in range(len(supports) - 1):
        length = supports[i + 1]['position'] - supports[i]['position']
        EI = float(input(f"Enter EI for span {i + 1}: "))
        load_type = input(f"Enter load type for span {i + 1} (point, udl, vdl, none): ").lower()
        load_params = {}
        if load_type == 'point':
            load_params['P'] = float(input("Enter point load magnitude: "))
            load_params['a'] = float(input("Enter point load position from left: "))
        elif load_type == 'udl':
            load_params['w'] = float(input("Enter UDL magnitude: "))
        elif load_type == 'vdl':
            load_params['w'] = float(input("Enter VDL max magnitude: "))
        spans.append({"length": length, "EI": EI, "load_type": load_type, "load_params": load_params})
    return supports, spans

# Function to calculate fixed-end moments
from sympy import symbols, Eq, solve

def calculate_fixed_end_moments(supports, spans, loads):
    FEM = {}
    for i in range(len(supports)-1):
        span_length = spans[i]
        load_type = loads[i]["type"]
        if load_type == "point":
            point_position = loads[i]["position"]
            point_magnitude = loads[i]["magnitude"]
            FEM[f'FEM_{chr(65+i)}{chr(66+i)}'] = -point_magnitude * (span_length - point_position) * point_position / (2 * span_length)
            FEM[f'FEM_{chr(66+i)}{chr(65+i)}'] = -FEM[f'FEM_{chr(65+i)}{chr(66+i)}']
        elif load_type == "udl":
            udl_magnitude = loads[i]["magnitude"]
            FEM[f'FEM_{chr(65+i)}{chr(66+i)}'] = -udl_magnitude * span_length**2 / 12
            FEM[f'FEM_{chr(66+i)}{chr(65+i)}'] = -FEM[f'FEM_{chr(65+i)}{chr(66+i)}']
        elif load_type == "vdl":
            # Handle VDL if needed
            pass
    return FEM

def slope_deflection_equations(FEM, supports, spans):
    theta = symbols('θ_A θ_B θ_C θ_D')
    M_AB = 0.2 * theta[0] + 0.1 * theta[1] - FEM.get('FEM_AB', 0)
    M_BA = 0.1 * theta[0] + 0.2 * theta[1] + FEM.get('FEM_BA', 0)
    M_BC = 0.25 * theta[0] + 0.125 * theta[1] - FEM.get('FEM_BC', 0)
    M_CB = 0.125 * theta[0] + 0.25 * theta[1] + FEM.get('FEM_CB', 0)
    
    slope_deflection_results = {
        'M_AB': M_AB,
        'M_BA': M_BA,
        'M_BC': M_BC,
        'M_CB': M_CB
    }
    
    return slope_deflection_results

def boundary_equations(supports, slope_deflection_results):
    eqns = []
    for i, support in enumerate(supports):
        if support == 'hinged':
            if i == 0:  # First support, M_AB = 0
                eqns.append(Eq(slope_deflection_results['M_AB'], 0))
            elif i == 1:  # Middle support, M_BA + M_BC = 0
                eqns.append(Eq(slope_deflection_results['M_BA'] + slope_deflection_results['M_BC'], 0))
            elif i == len(supports) - 1:  # Last support, M_CB = 0
                eqns.append(Eq(slope_deflection_results['M_CB'], 0))
        elif support == 'fixed':
            # Skip boundary condition for fixed support
            continue
    return eqns

def main():
    print("Welcome to the Beam Analysis Program!")
    
    # Input for supports
    num_supports = int(input("Enter the number of supports (minimum 2): "))
    supports = []
    positions = []
    
    for i in range(num_supports):
        support_type = input(f"Enter the type of support {i+1} (hinged, fixed, roller): ").lower()
        position = float(input(f"Enter the position of support {i+1}: "))
        supports.append(support_type)
        positions.append(position)
    
    # Input for spans and loads
    spans = []
    loads = []
    for i in range(num_supports - 1):
        span_length = positions[i+1] - positions[i]
        spans.append(span_length)
        
        load_type = input(f"Enter load type for span {i+1} (point, udl, vdl, none): ").lower()
        load = {"type": load_type}
        
        if load_type == "point":
            load["magnitude"] = float(input("Enter point load magnitude: "))
            load["position"] = float(input("Enter point load position from left: "))
        elif load_type == "udl":
            load["magnitude"] = float(input("Enter UDL magnitude: "))
        # Add handling for "vdl" if needed
        
        loads.append(load)
    
    # Calculate Fixed-End Moments (FEM)
    FEM = calculate_fixed_end_moments(supports, spans, loads)
    print("\n--- Calculating Fixed-End Moments (FEM) ---")
    print("\n--- Displaying Fixed-End Moments ---")
    for key, value in FEM.items():
        print(f"{key}: {value} kNm")
    
    # Get slope deflection equations
    slope_deflection_results = slope_deflection_equations(FEM, supports, spans)
    print("\n--- Slope Deflection Equations ---")
    for key, value in slope_deflection_results.items():
        print(f"{key}: {value}")
    
    # Form boundary equations
    eqns = boundary_equations(supports, slope_deflection_results)
    print("\n--- Forming Boundary/Equilibrium Equations ---")
    for eqn in eqns:
        print(eqn)
    
    # Solve the system of equations
    unknowns = symbols('θ_A θ_B θ_C θ_D')
    solutions = solve(eqns, unknowns[:len(supports)-1])
    print("\n--- Solving the system of equations ---")
    print("\nSolutions for the unknowns:")
    print(solutions)

if __name__ == "__main__":
    main()

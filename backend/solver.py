import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, sympify, Eq, solve

def fixed_end_moments(load_type, load_params, length):
    """
    Calculate fixed-end moments for different loading conditions.

    Args:
        load_type (str): Type of load ("point", "udl", "vdl", "unequal_point", "cantilever").
        load_params (dict): Parameters specific to each load type:
            - For "point": {"P": load magnitude, "a": distance from left end}.
            - For "udl": {"w": load intensity}.
            - For "vdl": {"w": max intensity (vertex load)}.
            - For "unequal_point": {"loads": [(P1, a1), (P2, a2), ...]}.
        length (float): Length of the beam.

    Returns:
        tuple: Fixed-end moments (FEM_AB, FEM_BA).
    """
    if load_type == "point":
        # Point Load FEM
        P = load_params["P"]
        a = load_params["a"]
        b = length - a
        FEM_AB = -P * b**2 * a / length**2  # Negative moment at A
        FEM_BA = P * a**2 * b / length**2   # Positive moment at B

    elif load_type == "udl":
        # Uniformly Distributed Load FEM
        w = load_params["w"]
        FEM_AB = -w * length**2 / 12  # Negative at A
        FEM_BA = w * length**2 / 12   # Positive at B

    elif load_type == "vdl":
        # Triangular Distributed Load (VDL)
        w = load_params["w"]
        FEM_AB = -w * length**2 / 20  # Negative at A
        FEM_BA = w * length**2 / 30   # Positive at B

    elif load_type == "unequal_point":
        # Multiple Point Loads
        loads = load_params["loads"]  # List of (P, a) tuples
        FEM_AB, FEM_BA = 0, 0
        for P, a in loads:
            b = length - a
            FEM_AB += -P * b**2 * a / length**2  # Negative moment at A
            FEM_BA += P * a**2 * b / length**2   # Positive moment at B

    elif load_type == "cantilever":
        # Fixed at one end, free at the other (cantilever beam)
        P = load_params["P"]
        a = load_params["a"]
        FEM_AB = 0             # Free end moment is zero
        FEM_BA = -P * a        # Negative moment at fixed end

    else:
        raise ValueError("Unsupported load type.")

    return FEM_AB, FEM_BA

def get_user_input():
    """
    Get user input for beam configuration, including support types, positions, 
    span lengths, and loading conditions, including VDL, hinged supports, and unequal point loads.

    Returns:
        dict: A dictionary containing the support types, positions, spans, and loads.
    """
    def validate_float(prompt, min_value=None, max_value=None):
        """Helper function to validate float input."""
        while True:
            try:
                value = float(input(prompt))
                if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                    print(f"Value must be between {min_value} and {max_value}. Try again.")
                else:
                    return value
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def validate_int(prompt, min_value=None, max_value=None):
        """Helper function to validate integer input."""
        while True:
            try:
                value = int(input(prompt))
                if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                    print(f"Value must be between {min_value} and {max_value}. Try again.")
                else:
                    return value
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    # Get the number of supports
    num_supports = validate_int("Enter the number of supports (minimum 2): ", min_value=2)
    supports = []

    # Collect information for each support
    print("\nDefine support types and their positions:")
    for i in range(num_supports):
        support_type = input(f"Enter the type of support {i + 1} (e.g., 'hinged', 'fixed', 'roller'): ").lower()
        support_position = validate_float(f"Enter the position of support {i + 1} (in meters): ", min_value=0)
        supports.append({"type": support_type, "position": support_position})

    # Sort supports by position to ensure correct span calculations
    supports = sorted(supports, key=lambda s: s["position"])

    # Define spans based on support positions
    spans = []
    for i in range(num_supports - 1):
        print(f"\nSpan {i + 1}:")
        span_length = supports[i + 1]["position"] - supports[i]["position"]
        print(f"Length of Span {i + 1}: {span_length} meters (calculated from support positions).")

        # Load type selection
        print("Select load type:")
        print("1. Point Load")
        print("2. Uniformly Distributed Load (UDL)")
        print("3. Variable Distributed Load (VDL)")
        print("4. Unequal Point Loads")
        print("5. Combined Load")
        print("6. No Load")
        load_choice = validate_int("Enter your choice (1-6): ", min_value=1, max_value=6)
        
        load_details = {}
        if load_choice == 1:  # Point Load
            load_magnitude = validate_float("Enter the magnitude of the point load (in kN): ", min_value=0)
            load_position = validate_float("Enter the position of the point load from the start of this span (in meters): ", min_value=0, max_value=span_length)
            load_details = {"type": "point", "magnitude": load_magnitude, "position": load_position}

        elif load_choice == 2:  # Uniformly Distributed Load (UDL)
            load_magnitude = validate_float("Enter the magnitude of the UDL (in kN/m): ", min_value=0)
            load_details = {"type": "udl", "magnitude": load_magnitude}

        elif load_choice == 3:  # Variable Distributed Load (VDL)
            start_magnitude = validate_float("Enter the magnitude of the load at the start of the span (in kN/m): ", min_value=0)
            end_magnitude = validate_float("Enter the magnitude of the load at the end of the span (in kN/m): ", min_value=0)
            load_details = {"type": "vdl", "start_magnitude": start_magnitude, "end_magnitude": end_magnitude}

        elif load_choice == 4:  # Unequal Point Loads
            num_point_loads = validate_int("Enter the number of point loads on this span: ", min_value=1)
            point_loads = []
            for j in range(num_point_loads):
                magnitude = validate_float(f"Enter the magnitude of point load {j + 1} (in kN): ", min_value=0)
                position = validate_float(f"Enter the position of point load {j + 1} from the start of the span (in meters): ", min_value=0, max_value=span_length)
                point_loads.append({"magnitude": magnitude, "position": position})
            load_details = {"type": "unequal_point", "loads": point_loads}

        elif load_choice == 5:  # Combined Load
            udl_magnitude = validate_float("Enter the magnitude of the UDL (in kN/m): ", min_value=0)
            point_magnitude = validate_float("Enter the magnitude of the point load (in kN): ", min_value=0)
            point_position = validate_float("Enter the position of the point load from the start of this span (in meters): ", min_value=0, max_value=span_length)
            load_details = {
                "type": "combined",
                "udl": udl_magnitude,
                "point": {"magnitude": point_magnitude, "position": point_position}
            }

        spans.append({
            "start_support": supports[i],
            "end_support": supports[i + 1],
            "length": span_length,
            "load": load_details if load_choice != 6 else None
        })

    # Confirm inputs
    print("\nInput Summary:")
    print(f"  Number of Supports: {num_supports}")
    for i, support in enumerate(supports):
        print(f"  Support {i + 1}: Type = {support['type']}, Position = {support['position']} meters")
    print(f"  Number of Spans: {len(spans)}")
    for i, span in enumerate(spans):
        print(f"  Span {i + 1}: Length = {span['length']} meters, Start Support = {span['start_support']['type']} "
              f"at {span['start_support']['position']}m, End Support = {span['end_support']['type']} at {span['end_support']['position']}m, "
              f"Load = {span['load'] if span['load'] else 'None'}")

    return {"supports": supports, "EI": EI, "load_type": load_type, "load_params": load_params}


def calculate_fem(beam_data):
    """
    Calculate Fixed-End Moments (FEM) for all spans in the beam data.

    Args:
        beam_data (dict): Contains details about spans and their loading.

    Returns:
        dict: FEM results for all spans (e.g., {"FEM_AB": value, "FEM_BA": value}).
    """
    print("\n--- Calculating Fixed-End Moments (FEM) ---")
    spans = beam_data.get("spans", [])
    fem_results = {}

    for i, span in enumerate(spans):
        span_name_start = chr(65 + i)  # Convert 0, 1, 2... to A, B, C...
        span_name_end = chr(66 + i)    # Next letter
        FEM_forward_name = f"FEM_{span_name_start}{span_name_end}"
        FEM_backward_name = f"FEM_{span_name_end}{span_name_start}"

        print(f"\nSpan {i + 1} ({span_name_start} to {span_name_end}):")
        
        # Validate span properties
        length = span.get("length", None)
        load = span.get("load", None)
        if not length or length <= 0:
            print("  Invalid span length. Skipping...")
            continue

        if not load or not load.get("type"):
            print(f"  No load on this span. {FEM_forward_name} = 0 kNm, {FEM_backward_name} = 0 kNm.")
            fem_results[FEM_forward_name] = 0
            fem_results[FEM_backward_name] = 0
            continue

        # Extract load details
        load_type = load["type"]
        try:
            if load_type == "point":
                P = load["P"]
                a = load["a"]
                FEM_AB, FEM_BA = fixed_end_moments("point", {"P": P, "a": a}, length)

            elif load_type == "udl":
                w = load["w"]
                FEM_AB, FEM_BA = fixed_end_moments("udl", {"w": w}, length)

            elif load_type == "vdl":
                w = load["w"]
                FEM_AB, FEM_BA = fixed_end_moments("vdl", {"w": w}, length)

            elif load_type == "cantilever":
                P = load["P"]
                a = load["a"]
                FEM_AB, FEM_BA = fixed_end_moments("cantilever", {"P": P, "a": a}, length)

            else:
                raise ValueError(f"Unsupported load type: {load_type}")

            # Print and store results
            print(f"  {FEM_forward_name} = {FEM_AB:.2f} kNm, {FEM_backward_name} = {FEM_BA:.2f} kNm.")
            fem_results[FEM_forward_name] = FEM_AB
            fem_results[FEM_backward_name] = FEM_BA

        except KeyError as e:
            print(f"  Error: Missing parameter for load type '{load_type}': {e}")
        except Exception as e:
            print(f"  Error: Could not calculate FEM for span {i + 1}: {e}")

    return fem_results

def slope_deflection_equations(beam_data, fem_results):
    """
    Calculate Slope-Deflection Equations for all spans in the beam.

    Args:
        beam_data (dict): Contains details about spans, including lengths and EI values.
        fem_results (dict): Pre-computed Fixed-End Moments (FEM) for the spans.

    Returns:
        dict: Slope-Deflection Equations for each span in symbolic form.
    """
    print("\n--- Calculating Slope-Deflection Equations ---")
    spans = beam_data["spans"]
    slope_deflection_results = {}

    for i, span in enumerate(spans):
        span_name_start = chr(65 + i)  # Convert 0, 1, 2... to A, B, C...
        span_name_end = chr(66 + i)  # Next letter

        print(f"\nSpan {i + 1} ({span_name_start} to {span_name_end}):")

        # Validate input data
        length = span.get("length", None)
        if not length or length <= 0:
            print(f"  Error: Invalid span length for span {span_name_start}->{span_name_end}. Skipping...")
            continue

        EI = span.get("EI", None)
        if not EI or EI <= 0:
            print(f"  Error: Invalid EI value for span {span_name_start}->{span_name_end}. Skipping...")
            continue

        FEM_AB = fem_results.get(f"FEM_{span_name_start}{span_name_end}", 0)
        FEM_BA = fem_results.get(f"FEM_{span_name_end}{span_name_start}", 0)

        # Slope-deflection equations
        equation_forward = (
            f"(2*theta_{span_name_start} + theta_{span_name_end}) * EI/{length} + {FEM_AB:.2f}"
        )
        equation_backward = (
            f"(theta_{span_name_start} + 2*theta_{span_name_end}) * EI/{length} + {FEM_BA:.2f}"
        )

        # Store results
        slope_deflection_results[f"SDE_{span_name_start}{span_name_end}"] = equation_forward
        slope_deflection_results[f"SDE_{span_name_end}{span_name_start}"] = equation_backward

        # Print results for user feedback
        print(f"  Slope-Deflection Equation ({span_name_start}->{span_name_end}): {equation_forward}")
        print(f"  Slope-Deflection Equation ({span_name_end}->{span_name_start}): {equation_backward}")

    return slope_deflection_results

def apply_boundary_conditions(slope_deflection_results, boundary_conditions):
    """
    Apply boundary conditions to the slope-deflection equations.

    Args:
        slope_deflection_results (dict): Slope-deflection equations as symbolic expressions.
        boundary_conditions (dict): Dictionary of boundary conditions (e.g., {"theta_A": 0, "theta_C": 0}).

    Returns:
        dict: Adjusted slope-deflection equations with boundary conditions applied.
    """
    print("\n--- Applying Boundary Conditions ---")
    adjusted_results = {}

    # Convert boundary condition variables to symbolic form
    boundary_conditions_sym = {symbols(var): value for var, value in boundary_conditions.items()}

    for equation, expression in slope_deflection_results.items():
        try:
            # Convert the expression to symbolic form
            symbolic_expression = sympify(expression)

            # Substitute the boundary conditions
            adjusted_expression = symbolic_expression.subs(boundary_conditions_sym)

            # Simplify the resulting expression
            adjusted_expression = adjusted_expression.simplify()

            # Store the adjusted equation
            adjusted_results[equation] = adjusted_expression

            # Display user feedback
            print(f"  Adjusted {equation}: {adjusted_expression}")

        except Exception as e:
            print(f"  Error adjusting {equation}: {e}")

    return adjusted_results


def solve_equilibrium(adjusted_results, unknowns):
    """
    Solve the equilibrium equations to find unknowns.

    Args:
        adjusted_results (dict): Adjusted slope-deflection equations.
        unknowns (list): List of unknowns to solve for (e.g., ["theta_A", "theta_B"]).

    Returns:
        dict: Dictionary of solved values for unknowns.
    """
    print("\n--- Solving Equilibrium Equations ---")

    # Convert unknowns to symbolic variables
    unknown_symbols = [symbols(var) for var in unknowns]

    # Convert adjusted equations to symbolic form
    symbolic_equations = []
    for equation, expression in adjusted_results.items():
        try:
            # Convert the equation into a symbolic equality (set to zero)
            symbolic_equations.append(Eq(sympify(expression), 0))
        except Exception as e:
            print(f"  Error parsing {equation}: {e}")

    # Solve the system of equations
    try:
        solutions = solve(symbolic_equations, unknown_symbols, dict=True)
        if solutions:
            solutions = solutions[0]  # Get the first solution
            print(f"  Solutions: {solutions}")
            return {str(var): solutions[var] for var in unknown_symbols}
        else:
            print("  No solutions found.")
            return {}
    except Exception as e:
        print(f"  Error solving equilibrium equations: {e}")
        return {}

def calculate_reactions(load_type, load_params, length):
    """
    Calculate reactions for different load types.

    Args:
        load_type (str): Type of load ("point", "udl", "vdl").
        load_params (dict): Parameters specific to each load type.
        length (float): Length of the beam.

    Returns:
        tuple: Reactions at A and B.
    """
    # Validate load_params for each load type
    if load_type == "point":
        if "P" not in load_params or "a" not in load_params:
            raise ValueError("Missing parameters for point load: 'P' and 'a' are required.")
        P = load_params["P"]
        a = load_params["a"]
        # Reaction at A
        reaction_A = (P * (length - a)) / length
        # Reaction at B
        reaction_B = P - reaction_A
    
    elif load_type == "udl":
        if "w" not in load_params:
            raise ValueError("Missing parameter for UDL load: 'w' is required.")
        w = load_params["w"]
        # Total load due to UDL
        total_load = w * length
        # Reactions at A and B
        reaction_A = total_load / 2
        reaction_B = total_load / 2

    elif load_type == "vdl":
        if "w" not in load_params or "length" not in load_params:
            raise ValueError("Missing parameters for VDL load: 'w' and 'length' are required.")
        w = load_params["w"]  # Maximum value of the load
        length_vdl = load_params["length"]  # Span of the load
        # Total load due to VDL (triangular load)
        total_load = 1/2 * w * length_vdl
        
        # The centroid of a triangular load is 2/3 of the distance from the smaller end
        centroid = 2/3 * length_vdl
        
        # Reactions at A and B (assuming simply supported beam)
        # Taking moments about A to find reaction at B
        reaction_B = total_load * centroid / length_vdl
        
        # Reaction at A is found by equilibrium of vertical forces
        reaction_A = total_load - reaction_B

    else:
        raise ValueError("Unsupported load type for reactions.")
    
    return reaction_A, reaction_B


def shear_force_and_bending_moment(load_type, load_params, length, reaction_A, reaction_B):
    """
    Calculate shear force and bending moment for a given load type.

    Args:
        load_type (str): Type of load ("point", "udl").
        load_params (dict): Parameters specific to each load type.
        length (float): Length of the beam.
        reaction_A (float): Reaction at support A.
        reaction_B (float): Reaction at support B.

    Returns:
        tuple: Shear force and bending moment at points along the beam.
    """
    # Generate x points along the beam
    x = np.linspace(0, length, 100)
    
    shear_force = np.zeros_like(x)
    bending_moment = np.zeros_like(x)
    
    if load_type == "point":
        P = load_params["P"]
        a = load_params["a"]
        
        # Shear Force Calculation
        shear_force[x < a] = reaction_A  # Before the load
        shear_force[x >= a] = reaction_A - P  # After the load

        # Bending Moment Calculation
        bending_moment[x < a] = reaction_A * x[x < a]
        bending_moment[x >= a] = reaction_A * x[x >= a] - P * (x[x >= a] - a)
    
    elif load_type == "udl":
        w = load_params["w"]
        
        # Shear Force Calculation (no full overwrite, just update with the linear relationship)
        shear_force = reaction_A - w * x  # Shear force decreases linearly

        # Bending Moment Calculation
        bending_moment = reaction_A * x - (w * x**2) / 2

    else:
        raise ValueError("Unsupported load type for shear and bending moment calculation.")
    
    return shear_force, bending_moment, x

def plot_shear_bending(shear_force, bending_moment, x):
    """
    Plot the Shear Force and Bending Moment diagrams.
    """
    # Plot Shear Force
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(x, shear_force, label="Shear Force")
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Shear Force Diagram")
    plt.xlabel("Distance (m)")
    plt.ylabel("Shear Force (kN)")
    plt.legend()

    # Plot Bending Moment
    plt.subplot(2, 1, 2)
    plt.plot(x, bending_moment, label="Bending Moment", color="red")
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Bending Moment Diagram")
    plt.xlabel("Distance (m)")
    plt.ylabel("Bending Moment (kNm)")
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Get inputs from the user
    EI, length, load_type, load_params, supports = get_user_input()

    # Step 1: Calculate Fixed-End Moments (FEM)
    FEM_AB, FEM_BA = fixed_end_moments(load_type, load_params, length)
    print(f"Fixed-End Moments: FEM_AB = {FEM_AB:.2f} kNm, FEM_BA = {FEM_BA:.2f} kNm")

    # Step 2: Calculate Reactions
    reaction_A, reaction_B = calculate_reactions(load_type, load_params, length)
    print(f"Reactions: Reaction at A = {reaction_A:.2f} kN, Reaction at B = {reaction_B:.2f} kN")

    # Step 3: Calculate Shear Force and Bending Moment
    shear_force, bending_moment, x = shear_force_and_bending_moment(
        load_type, load_params, length, reaction_A, reaction_B
    )

    # Step 4: Plot the Shear Force and Bending Moment Diagrams
    plot_shear_bending(shear_force, bending_moment, x)

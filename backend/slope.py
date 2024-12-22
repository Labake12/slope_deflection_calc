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
def calculate_fem(supports, spans):
    fem_results = {}
    for i, span in enumerate(spans):
        span_name_start = chr(65 + i)
        span_name_end = chr(66 + i)
        FEM_forward_name = f"FEM_{span_name_start}{span_name_end}"
        FEM_backward_name = f"FEM_{span_name_end}{span_name_start}"

        length = span["length"]
        load_type = span["load_type"]
        load_params = span["load_params"]

        FEM_AB, FEM_BA = fixed_end_moments(load_type, load_params, length)

        fem_results[FEM_forward_name] = FEM_AB
        fem_results[FEM_backward_name] = FEM_BA

    return fem_results

# Slope deflection method
def slope_deflection_method(fem_results, spans):
    moments = {}
    for i, span in enumerate(spans):
        span_name_start = chr(65 + i)
        span_name_end = chr(66 + i)
        L = span["length"]
        EI = span["EI"]

        FEM_AB = fem_results.get(f"FEM_{span_name_start}{span_name_end}", 0)
        FEM_BA = fem_results.get(f"FEM_{span_name_end}{span_name_start}", 0)

        MAB = f"{FEM_AB} + {(EI / L)} * (2*θ_{span_name_start} + θ_{span_name_end})"
        MBA = f"{FEM_BA} + {(EI / L)} * (θ_{span_name_start} + 2*θ_{span_name_end})"

        moments[f"M_{span_name_start}{span_name_end}"] = MAB
        moments[f"M_{span_name_end}{span_name_start}"] = MBA

    return moments

# def apply_boundary_conditions(moments, supports):
#     """
#     Apply boundary conditions for a beam with supports.

#     Parameters:
#     moments (dict): Dictionary containing slope deflection equations for each span.
#     supports (list): List of support details, each containing the type and position.

#     Returns:
#     dict: Adjusted moments after applying boundary conditions.
#     """

#     from sympy import Eq, symbols, solve, sympify, simplify

#     adjusted_results = {}
#     equations = []

#     print("\n--- Boundary Conditions ---")

#     num_supports = len(supports)
#     num_spans = len(spans)

#     # Handle fixed ends
#     if num_supports == 2:  # Two fixed ends
#         eq_leftmost = Eq(symbols(f"M_{supports[0]['type']}"), 0)
#         eq_rightmost = Eq(symbols(f"{supports[-1]['type']}_M"), 0)
#         equations.extend([eq_leftmost, eq_rightmost])
#         print(eq_leftmost)
#         print(eq_rightmost)

#     elif num_supports > 2:  # At least one intermediate support
#         for i, support in enumerate(supports):
#             current_support = chr(65 + i)
            
#             if i == 0:  # Leftmost support
#                 if support["type"] in ["hinged", "roller"]:
#                     eq_leftmost = Eq(symbols(f"M_{supports[0]['type']}"), 0)
#                     equations.append(eq_leftmost)
#                     print(eq_leftmost)

#             elif i == num_supports - 1:  # Rightmost support
#                 if support["type"] in ["hinged", "roller"]:
#                     eq_rightmost = Eq(symbols(f"{supports[-1]['type']}_M"), 0)
#                     equations.append(eq_rightmost)
#                     print(eq_rightmost)

#             else:  # Intermediate supports
#                 prev_support = chr(65 + i - 1)
#                 next_support = chr(65 + i + 1)
#                 print (prev_support)

#                 if support["type"] == "hinged":
#                     eq_intermediate = Eq(
#                         symbols(f"M_{prev_support}{current_support}") + 
#                         symbols(f"M_{current_support}{next_support}"),
#                         0
#                     )
#                     equations.append(eq_intermediate)
#                     print(eq_intermediate)

#                 elif support["type"] == "fixed":
#                     eq_fixed = Eq(symbols(f"M_{prev_support}{current_support}") + 
#                                   symbols(f"M_{current_support}{next_support}"), 0)
#                     equations.append(eq_fixed)
#                     print(eq_fixed)

#     # Solve the system of equations
#     print("\n--- Solving Boundary Condition Equations ---")
    
#     all_symbols = [symbols(key) for key in moments.keys()]
#     solved_values = solve(equations, all_symbols)

#     # Substitute solved values into the moments dictionary
#     for moment_key, expression in moments.items():
#         symbolic_expression = sympify(expression)
#         adjusted_expression = symbolic_expression.subs(solved_values)
#         adjusted_results[moment_key] = simplify(adjusted_expression)

#     return adjusted_results
def apply_boundary_conditions(moments, supports, spans):
    """
    Apply boundary conditions for a beam with supports.

    Parameters:
    moments (dict): Dictionary containing slope deflection equations for each span.
    supports (list): List of support details, each containing the type and position.
    spans (list): List of span details, including length, EI, load type, and load parameters.

    Returns:
    dict: Adjusted moments after applying boundary conditions.
    """

    from sympy import Eq, symbols, solve, sympify, simplify

    adjusted_results = {}
    equations = []

    print("\n--- Boundary Conditions ---")

    num_supports = len(supports)
    num_spans = len(spans)

    # Handle fixed ends
    if num_supports == 2:  # Two fixed ends
        eq_leftmost = Eq(symbols(f"M_{supports[0]['type']}"), 0)
        eq_rightmost = Eq(symbols(f"{supports[-1]['type']}_M"), 0)
        equations.extend([eq_leftmost, eq_rightmost])
        print(eq_leftmost)
        print(eq_rightmost)

    elif num_supports > 2:  # At least one intermediate support
        for i, support in enumerate(supports):
            current_support = chr(65 + i)
            
            if i == 0:  # Leftmost support
                if support["type"] in ["hinged", "roller"]:
                    eq_leftmost = Eq(symbols(f"M_{supports[0]['type']}"), 0)
                    equations.append(eq_leftmost)
                    print(eq_leftmost)

            elif i == num_supports - 1:  # Rightmost support
                if support["type"] in ["hinged", "roller"]:
                    eq_rightmost = Eq(symbols(f"{supports[-1]['type']}_M"), 0)
                    equations.append(eq_rightmost)
                    print(eq_rightmost)

            else:  # Intermediate supports
                prev_support = chr(65 + i - 1)
                next_support = chr(65 + i + 1)
                print(prev_support)

                if support["type"] == "hinged":
                    eq_intermediate = Eq(
                        symbols(f"M_{prev_support}{current_support}") + 
                        symbols(f"M_{current_support}{next_support}"),
                        0
                    )
                    equations.append(eq_intermediate)
                    print(eq_intermediate)

                elif support["type"] == "fixed":
                    eq_fixed = Eq(symbols(f"M_{prev_support}{current_support}") + 
                                  symbols(f"M_{current_support}{next_support}"), 0)
                    equations.append(eq_fixed)
                    print(eq_fixed)

    # Solve the system of equations
    print("\n--- Solving Boundary Condition Equations ---")
    
    all_symbols = [symbols(key) for key in moments.keys()]
    solved_values = solve(equations, all_symbols)

    # Substitute solved values into the moments dictionary
    for moment_key, expression in moments.items():
        symbolic_expression = sympify(expression)
        adjusted_expression = symbolic_expression.subs(solved_values)
        adjusted_results[moment_key] = simplify(adjusted_expression)

    return adjusted_results


# Main
# if __name__ == "__main__":
#     print("Welcome to the Beam Analysis Program!")
#     supports, spans = get_user_input()

#     # Calculate Fixed-End Moments
#     print("\n--- Calculating Fixed-End Moments (FEM) ---")
#     fem_results = calculate_fem(supports, spans)
#     for key, value in fem_results.items():
#         print(f"{key}: {value} kNm")

#     # Perform Slope Deflection Analysis
#     print("\n--- Slope Deflection Equations ---")
#     slope_deflection_results = slope_deflection_method(fem_results, spans)
#     for eq, expression in slope_deflection_results.items():
#         print(f"{eq}: {expression}")

#     # Apply Boundary Conditions
#     adjusted_results = apply_boundary_conditions(slope_deflection_results, supports)

#     # Display Final Adjusted Results
#     print("\n--- Final Adjusted Results ---")
#     for eq, value in adjusted_results.items():
#         print(f"{eq}: {value}")

#     print("\nAnalysis Complete!")
# Main
# Main
if __name__ == "__main__":
    print("Welcome to the Beam Analysis Program!")

    # Collect User Input
    supports, spans = get_user_input()

    # Calculate Fixed-End Moments (FEM)
    print("\n--- Calculating Fixed-End Moments (FEM) ---")
    fem_results = calculate_fem(supports, spans)

    # Display Fixed-End Moments (FEM)
    print("\n--- Displaying Fixed-End Moments ---")
    for key, value in fem_results.items():
        print(f"{key}: {value} kNm")

    # Perform Slope Deflection Analysis (Calculate Slope Deflection Equations)
    print("\n--- Slope Deflection Equations ---")
    slope_deflection_results = slope_deflection_method(fem_results, spans)

    # Display Slope Deflection Equations
    for eq, expression in slope_deflection_results.items():
        print(f"{eq}: {expression}")

    # Apply Boundary Conditions and adjust results
    print("\n--- Applying Boundary Conditions ---")
    adjusted_results = apply_boundary_conditions(slope_deflection_results, supports, spans)

    # Display Final Adjusted Results (After applying Boundary Conditions)
    print("\n--- Final Adjusted Results ---")
    for eq, value in adjusted_results.items():
        print(f"{eq}: {value}")

    print("\nAnalysis Complete!")
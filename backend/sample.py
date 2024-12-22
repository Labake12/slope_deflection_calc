import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve, Matrix

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
        FEM_BA = w * length**2 / 30
    elif load_type == "none":
        FEM_AB = 0
        FEM_BA = 0
    else:
        raise ValueError("Unsupported load type.")
    return FEM_AB, FEM_BA

def calculate_reactions(load_type, load_params, length):
    if load_type == "point":
        P = load_params["P"]
        a = load_params["a"]
        reaction_A = (P * (length - a)) / length
        reaction_B = P - reaction_A
    elif load_type == "udl":
        w = load_params["w"]
        total_load = w * length
        reaction_A = total_load / 2
        reaction_B = total_load / 2
    elif load_type == "vdl":
        w = load_params["w"]
        total_load = 0.5 * w * length
        reaction_A = total_load / 3
        reaction_B = 2 * total_load / 3
    elif load_type == "none":
        reaction_A = 0
        reaction_B = 0
    else:
        raise ValueError("Unsupported load type for reactions.")
    return reaction_A, reaction_B

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
        length = supports[i+1]['position'] - supports[i]['position']
        EI = float(input(f"Enter EI for span {i+1}: "))
        load_type = input(f"Enter load type for span {i+1} (point, udl, vdl, none): ").lower()
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

def assemble_stiffness_matrix(supports, spans, fem_results):
    unknown_thetas = []
    for i in range(1, len(supports) - 1):
        if supports[i]['type'] != 'fixed':
            unknown_thetas.append(f"theta_{chr(65 + i)}")

    num_unknowns = len(unknown_thetas)
    stiffness_matrix = Matrix(np.zeros((num_unknowns, num_unknowns)))
    load_vector = Matrix(np.zeros((num_unknowns, 1)))

    for i in range(len(spans)):
        span_name_start = chr(65 + i)
        span_name_end = chr(66 + i)
        length = spans[i]['length']
        EI = spans[i]['EI']
        FEM_AB = fem_results.get(f"FEM_{span_name_start}{span_name_end}", 0)
        FEM_BA = fem_results.get(f"FEM_{span_name_end}{span_name_start}", 0)
        
        print(f"Processing span {span_name_start}-{span_name_end} with length {length}, EI={EI}")
        print(f"  FEM_AB: {FEM_AB}, FEM_BA: {FEM_BA}")
        
        if f"theta_{span_name_start}" in unknown_thetas:
            row_index = unknown_thetas.index(f"theta_{span_name_start}")
            stiffness_matrix[row_index, row_index] += 4 * EI / length
            load_vector[row_index] -= FEM_AB
        if f"theta_{span_name_end}" in unknown_thetas:
            row_index = unknown_thetas.index(f"theta_{span_name_end}")
            stiffness_matrix[row_index, row_index] += 4 * EI / length
            load_vector[row_index] -= FEM_BA

    print("\nStiffness Matrix (K):")
    print(stiffness_matrix)
    print("\nLoad Vector (Q):")
    print(load_vector)
    return stiffness_matrix, load_vector, unknown_thetas

def shear_force_and_bending_moment(load_type, load_params, length, moment_start, moment_end):
    x = np.linspace(0, length, 50)
    shear_force = np.zeros_like(x)
    bending_moment = np.zeros_like(x)

    if load_type == "point":
        P = load_params["P"]
        a = load_params["a"]
        reaction_A = (P * (length - a)) / length
        reaction_B = P - reaction_A
    elif load_type == "udl":
        w = load_params["w"]
        reaction_A = reaction_B = w * length / 2
    elif load_type == "vdl":
        w = load_params["w"]
        reaction_A = (w * length) / 3
        reaction_B = (2 * w * length) / 3
    else:
        reaction_A = reaction_B = 0

    adjusted_reaction_A = reaction_A + (moment_end - moment_start) / length

    if load_type == "point":
        shear_force[x < a] = adjusted_reaction_A
        shear_force[x >= a] = adjusted_reaction_A - P
        bending_moment[x < a] = moment_start + adjusted_reaction_A * x[x < a]
        bending_moment[x >= a] = moment_start + adjusted_reaction_A * x[x >= a] - P * (x[x >= a] - a)
    elif load_type == "udl":
        w = load_params["w"]
        shear_force = adjusted_reaction_A - w * x
        bending_moment = moment_start + adjusted_reaction_A * x - (w * x**2) / 2
    elif load_type == "vdl":
        w = load_params["w"]
        shear_force = adjusted_reaction_A - (w * x**2) / (2 * length)
        bending_moment = moment_start + adjusted_reaction_A * x - (w * x**3) / (6 * length)

    return shear_force, bending_moment, x

def plot_shear_bending(shear_force, bending_moment, x, start_node, end_node):
    plt.figure(figsize=(12, 6))
    plt.suptitle(f"Shear Force and Bending Moment Diagrams (Span {start_node}-{end_node})")

    plt.subplot(2, 1, 1)
    plt.plot(x, shear_force, label="Shear Force (kN)")
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Shear Force Diagram")
    plt.xlabel("Distance (m)")
    plt.ylabel("Shear Force (kN)")
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(x, bending_moment, label="Bending Moment (kNm)", color="red")
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Bending Moment Diagram")
    plt.xlabel("Distance (m)")
    plt.ylabel("Bending Moment (kNm)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    supports, spans = get_user_input()

    fem_results = {}
    for i, span in enumerate(spans):
        start_node = chr(65 + i)
        end_node = chr(66 + i)
        FEM_AB, FEM_BA = fixed_end_moments(span['load_type'], span['load_params'], span['length'])
        fem_results[f"FEM_{start_node}{end_node}"] = FEM_AB
        fem_results[f"FEM_{end_node}{start_node}"] = FEM_BA
        print(f"Span {start_node}-{end_node} Fixed End Moments:")
        print(f"  FEM_{start_node}{end_node}: {FEM_AB:.2f} kNm, FEM_{end_node}{start_node}: {FEM_BA:.2f} kNm")

    stiffness_matrix, load_vector, unknown_thetas = assemble_stiffness_matrix(supports, spans, fem_results)

    if unknown_thetas:
        theta_solutions = solve(Eq(stiffness_matrix * Matrix(symbols(unknown_thetas)), -load_vector), symbols(unknown_thetas), dict=True)
        print("\nTheta Solutions (Rotations at Supports):")
        for theta, value in theta_solutions[0].items():
            print(f"  {theta}: {value:.6f} radians")
    else:
        print("No unknown thetas (all supports are fixed).")
        theta_solutions = [{}]

    reactions = {}
    for i, support in enumerate(supports):
        reactions[chr(65 + i)] = 0

    for i, span in enumerate(spans):
        start_node = chr(65 + i)
        end_node = chr(66 + i)
        load_type = span["load_type"]
        load_params = span["load_params"]
        length = span["length"]
        reaction_start, reaction_end = calculate_reactions(load_type, load_params, length)

        theta_start_val = theta_solutions[0].get(symbols(f"theta_{start_node}"), 0)
        theta_end_val = theta_solutions[0].get(symbols(f"theta_{end_node}"), 0)
        EI = span["EI"]

        moment_start = (2 * theta_start_val + theta_end_val) * EI / length + fem_results[f"FEM_{start_node}{end_node}"]
        moment_end = (theta_start_val + 2 * theta_end_val) * EI / length + fem_results[f"FEM_{end_node}{start_node}"]

        reactions[start_node] += reaction_start + (moment_end - moment_start) / length
        reactions[end_node] += reaction_end - (moment_end - moment_start) / length

        shear_force, bending_moment, x = shear_force_and_bending_moment(load_type, load_params, length, moment_start, moment_end)
        plot_shear_bending(shear_force, bending_moment, x, start_node, end_node)

        print(f"\nSpan {start_node}-{end_node}:")
        print(f"  Initial Reactions (before moment distribution):")
        print(f"    R{start_node}: {reaction_start:.2f} kN, R{end_node}: {reaction_end:.2f} kN")
        print(f"  Moments:")
        print(f"    M{start_node}{end_node}: {moment_start:.2f} kNm, M{end_node}{start_node}: {moment_end:.2f} kNm")
        print("\nShear Force and Bending Moment along the span:")
        for j in range(len(x)):
            print(f"  x = {x[j]:.2f} m: SF = {shear_force[j]:.2f} kN, BM = {bending_moment[j]:.2f} kNm")

    print("\nFinal Support Reactions:")
    for support, reaction in reactions.items():
        print(f"  Reaction at {support}: {reaction:.2f} kN")
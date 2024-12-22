import numpy as np

def calculate_fem(load_type, load_magnitude, length, location):
    """Calculates fixed-end moments (FEMs) for different load types.

    Args:
        load_type: The type of load (e.g., 'uniform', 'point').
        load_magnitude: The magnitude of the load.
        length: The length of the member.
        location: The location of the load (relative to start of member).

    Returns:
        A tuple containing the FEM at the start and end of the member.
    """
    if load_type == 'uniform':
        FEM_start = -load_magnitude * length**2 / 12
        FEM_end = load_magnitude * length**2 / 12
    elif load_type == 'point':
        if location == 0:
            FEM_start = 0
            FEM_end = 0
        elif location == length:
            FEM_start = 0
            FEM_end = 0
        else:
            FEM_start = -load_magnitude * location * (length - location)**2 / length**2
            FEM_end = load_magnitude * location**2 * (length - location) / length**2
    else:
        raise ValueError("Invalid load type.")

    return FEM_start, FEM_end

def assemble_stiffness_matrix(structure):
    """Assembles the global stiffness matrix.

    Args:
        structure: A dictionary representing the structure.

    Returns:
        A NumPy array representing the global stiffness matrix.
    """
    num_nodes = len(set([node for member in structure.values() for node in member[:2]]))
    k_global = np.zeros((2 * num_nodes, 2 * num_nodes))

    for member_name, (start_node, end_node, length, E, I) in structure.items():
        k_local = (E * I / length) * np.array([
            [4, 2, -4, 2],
            [2, 4, -2, -2],
            [-4, -2, 4, -2],
            [2, -2, -2, 4]
        ])

        # Map local degrees of freedom to global degrees of freedom
        global_dof = [2 * (start_node - 1), 2 * (start_node - 1) + 1, 2 * (end_node - 1), 2 * (end_node - 1) + 1]

        # Assemble local stiffness matrix into global stiffness matrix
        for i in range(4):
            for j in range(4):
                k_global[global_dof[i], global_dof[j]] += k_local[i, j]

    return k_global

def assemble_load_vector(fems, supports):
    """Assembles the global load vector.

    Args:
        fems: A dictionary containing fixed-end moments for each member.
        supports: A dictionary representing the supports.

    Returns:
        A NumPy array representing the global load vector.
    """
    num_nodes = len(supports)
    f_global = np.zeros(2 * num_nodes)

    for member_name, (FEM_start, FEM_end) in fems.items():
        start_node = structure[member_name][0]
        end_node = structure[member_name][1]
        f_global[2 * (start_node - 1)] += FEM_start
        f_global[2 * (start_node - 1) + 1] += FEM_start
        f_global[2 * (end_node - 1)] += FEM_end
        f_global[2 * (end_node - 1) + 1] -= FEM_end

    # Apply support conditions
    for node, conditions in supports.items():
        if 'fixed' in conditions:
            f_global[2 * (node - 1)] = 0  # Fix rotation
            f_global[2 * (node - 1) + 1] = 0  # Fix displacement
        elif 'pinned' in conditions:
            f_global[2 * (node - 1) + 1] = 0  # Fix displacement

    return f_global

def calculate_member_end_moments(structure, fems, displacements):
    """Calculates member end moments using slope-deflection equations.

    Args:
        structure: A dictionary representing the structure.
        fems: A dictionary containing fixed-end moments for each member.
        displacements: A NumPy array containing joint rotations and displacements.

    Returns:
        A dictionary containing the member end moments.
    """
    member_end_moments = {}
    for member_name, (start_node, end_node, length, E, I) in structure.items():
        FEM_start, FEM_end = fems[member_name]
        theta_start = displacements[2 * (start_node - 1)]
        theta_end = displacements[2 * (end_node - 1)]
        delta = (displacements[2 * (end_node - 1) + 1] - displacements[2 * (start_node - 1) + 1]) / length

        M_start = FEM_start + (4 * E * I / length) * theta_start + (2 * E * I / length) * theta_end - (6 * E * I / length**2) * delta
        M_end = FEM_end + (2 * E * I / length) * theta_start + (4 * E * I / length) * theta_end + (6 * E * I / length**2) * delta

        member_end_moments[member_name] = (M_start, M_end)

    return member_end_moments

# Example usage
structure = {
    'AB': ('A', 'B', 10, 1, 200e9),
    'BC': ('B', 'C', 8, 1.5, 200e9),
}
loads = {
    'AB': [('uniform', 10, 0.5)],
    'BC': [('point', 20, 4)],
}
supports = {
    'A': ['fixed'],
    'B': ['fixed'],
    'C': ['pinned'],
}

# Calculate FEMs
fems = {}
for member_name, member_data in structure.items():
    length = member_data[2]
    member_loads = loads.get(member_name, [])
    member_fems = []
    for load_type, load_magnitude, load_location in member_loads:
        FEM_start, FEM_end = calculate_fem(load_type, load_magnitude, length, load_location)
        member_fems.append((FEM_start, FEM_end))
    fems[member_name] = sum(member_fems)  # Sum FEMs from all loads on the member

# Assemble stiffness matrix and load vector
k_matrix = assemble_stiffness_matrix(structure)
f_vector = assemble_load_vector(fems, supports)

# Solve for joint displacements
displacements = np.linalg.solve(k_matrix, f_vector)

# Calculate member end moments
member_end_moments = calculate_member_end_moments(structure, fems, displacements)

print("Member End Moments:")
for member_name, (M_start, M_end) in member_end_moments.items():
    print(f"{member_name}: M_start = {M_start:.2f} kNm, M_end = {M_end:.2f} kNm")
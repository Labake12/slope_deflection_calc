def get_user_input():
    print("=== Beam Analysis: Input Beam and Loading Details ===\n")
    
    # Get Flexural Rigidity and Length of Beam
    EI = float(input("Enter the flexural rigidity (EI) in kNm^2: "))
    length = float(input("Enter the length of the beam (m): "))
    
    # Choose load type
    load_type = input("Enter load type (point/udl/vdl/unequal_point/cantilever): ").strip().lower()
    
    load_params = {}
    
    if load_type == "point":
        load_params["P"] = float(input("Enter the point load magnitude (kN): "))
        load_params["a"] = float(input("Enter the distance of the point load from the left end (m): "))
    
    elif load_type == "udl":
        load_params["w"] = float(input("Enter the UDL intensity (kN/m): "))
    
    elif load_type == "vdl":
        load_params["w"] = float(input("Enter the maximum intensity of the triangular load (kN/m): "))
    
    elif load_type == "unequal_point":
        num_loads = int(input("Enter the number of point loads: "))
        loads = []
        for i in range(num_loads):
            P = float(input(f"Enter magnitude of load {i+1} (kN): "))
            a = float(input(f"Enter distance of load {i+1} from the left end (m): "))
            loads.append((P, a))
        load_params["loads"] = loads
    
    elif load_type == "cantilever":
        load_params["P"] = float(input("Enter the point load magnitude (kN): "))
        load_params["a"] = float(input("Enter the distance of the point load from the fixed end (m): "))
    
    else:
        raise ValueError("Invalid load type entered.")
    
    # Get support conditions
    supports = input("Enter the support conditions (e.g., fixed-fixed, fixed-hinged): ").strip().lower()
    return EI, length, load_type, load_params, supports

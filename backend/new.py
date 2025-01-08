# import numpy as np
# import matplotlib.pyplot as plt

# def calculate_shear_force_bending_moment(length, point_loads, udls=[]):
#     """
#     Calculate shear force and bending moment at various points along a beam.

#     Parameters:
#         length (float): Length of the beam in meters.
#         point_loads (list of tuples): Each tuple is (magnitude, position), where
#             - magnitude is the force in Newtons (positive is downward).
#             - position is the distance from the fixed end in meters.
#         udls (list of tuples): Each tuple is (start, end, intensity), where
#             - start and end define the span of the UDL in meters.
#             - intensity is the load per unit length in N/m (positive is downward).

#     Returns:
#         x (numpy array): Positions along the beam.
#         shear_force (numpy array): Shear force at each position.
#         bending_moment (numpy array): Bending moment at each position.
#     """
#     # Discretize the beam length
#     num_points = 1000
#     x = np.linspace(0, length, num_points)

#     # Initialize shear force and bending moment arrays
#     shear_force = np.zeros_like(x)
#     bending_moment = np.zeros_like(x)

#     # Apply point loads
#     for magnitude, position in point_loads:
#         shear_force[x >= position] += magnitude
#         bending_moment[x >= position] += magnitude * (x[x >= position] - position)

#     # Apply uniformly distributed loads (UDLs)
#     for start, end, intensity in udls:
#         udl_mask = (x >= start) & (x <= end)
#         shear_force[x >= start] += intensity * (end - start)
#         bending_moment[x >= start] += (
#             intensity * ((end - x[x >= start]) * (end - x[x >= start]) / 2)
#         )

#     # Convert shear force to cumulative distribution for bending moment
#     for i in range(1, len(x)):
#         bending_moment[i] += bending_moment[i - 1] - shear_force[i] * (x[i] - x[i - 1])

#     return x, shear_force, bending_moment


# def plot_sfd_bmd(x, shear_force, bending_moment):
#     """
#     Plot shear force and bending moment diagrams.

#     Parameters:
#         x (numpy array): Positions along the beam.
#         shear_force (numpy array): Shear force at each position.
#         bending_moment (numpy array): Bending moment at each position.
#     """
#     fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

#     # Shear Force Diagram (SFD)
#     axs[0].plot(x, shear_force, label="Shear Force", color="blue")
#     axs[0].axhline(0, color="black", linewidth=0.8, linestyle="--")
#     axs[0].set_ylabel("Shear Force (N)")
#     axs[0].set_title("Shear Force Diagram")
#     axs[0].legend()
#     axs[0].grid(True)

#     # Bending Moment Diagram (BMD)
#     axs[1].plot(x, bending_moment, label="Bending Moment", color="red")
#     axs[1].axhline(0, color="black", linewidth=0.8, linestyle="--")
#     axs[1].set_ylabel("Bending Moment (Nm)")
#     axs[1].set_xlabel("Position along the beam (m)")
#     axs[1].set_title("Bending Moment Diagram")
#     axs[1].legend()
#     axs[1].grid(True)

#     plt.tight_layout()
#     plt.show()

# # Example usage
# if __name__ == "__main__":
#     length = 2.0  # Length of the beam in meters
#     point_loads = [
#         (300, 0.5),  # 300 N at 0.5 m
#         (500, 0.7),  # 500 N at 0.7 m
#         (800, 0.8),  # 800 N at 0.8 m
#     ]
#     udls = []  # No UDLs in this example

#     # Calculate SFD and BMD
#     x, shear_force, bending_moment = calculate_shear_force_bending_moment(length, point_loads, udls)

#     # Plot the diagrams
#     plot_sfd_bmd(x, shear_force, bending_moment)
import matplotlib.pyplot as plt
import numpy as np

# Define beam parameters
length = 2.0  # Length of the beam in meters
point_loads = [
    (300, 0.5),  # 300 N at 0.5 m
    (500, 0.7),  # 500 N at 0.7 m
    (800, 0.8),  # 800 N at 0.8 m
]

# Step 1: Shear Force Calculation (starting from the free end)
sf_values = []
current_sf = 0  # Start with no force at the fixed end (cantilever beam)
sf_values.append(current_sf)

# Subtract loads as we encounter them (shear force increases as we move from free end)
for load, position in point_loads:
    current_sf += load  # Add load effect at position
    sf_values.append(current_sf)

# Step 2: Bending Moment Calculation (starting from the free end, negative for cantilever)
bm_values = [0]  # Moment at the free end is 0
for i, (load, position) in enumerate(point_loads):
    bm = 0
    for j, (prev_load, prev_position) in enumerate(point_loads[:i + 1]):
        bm += prev_load * (position - prev_position)
    bm_values.append(-bm)  # Negative for cantilever beam (counterclockwise moments are negative)

# Add fixed end bending moment (negative bending moment value)
fixed_bm = 0
for load, position in point_loads:
    fixed_bm += load * (length - position)
bm_values.append(-fixed_bm)  # Apply negative bending moment convention for cantilever

# Adjust positions for plotting and display
positions_sf = [0] + [load[1] for load in point_loads] + [length]
positions_bm = [0] + [load[1] for load in point_loads] + [length]

# Step 3: Plotting the diagrams
plt.figure(figsize=(12, 6))

# Shear Force Diagram (SFD)
plt.subplot(2, 1, 1)
plt.step(positions_sf, sf_values + [sf_values[-1]], where="post", color="blue", label="Shear Force")
plt.fill_between(positions_sf, sf_values + [sf_values[-1]], step="post", alpha=0.2, color="blue")
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.title("Shear Force Diagram (SFD)")
plt.xlabel("Position (m)")
plt.ylabel("Shear Force (N)")
plt.legend()
plt.grid(True)

# Bending Moment Diagram (BMD)
plt.subplot(2, 1, 2)
plt.plot(positions_bm, bm_values, color="red", marker="o", label="Bending Moment")
plt.fill_between(positions_bm, bm_values, step="pre", alpha=0.2, color="red")
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.title("Bending Moment Diagram (BMD)")
plt.xlabel("Position (m)")
plt.ylabel("Bending Moment (Nm)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Display values in terminal-friendly format
for i, (pos, sf, bm) in enumerate(zip(positions_sf, sf_values + [sf_values[-1]], bm_values)):
    print(f"Position: {pos:.2f} m, Shear Force: {sf:.2f} N, Bending Moment: {bm:.2f} Nm")

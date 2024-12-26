import numpy as np
import matplotlib.pyplot as plt

class BeamAnalysis:
    def __init__(self):
        self.supports = []
        self.spans = []
    
    def input_supports(self):
        num_supports = int(input("Enter the number of supports (minimum 2): "))
        for i in range(num_supports):
            support_type = input(f"Enter the type of support {i + 1} (hinged, fixed, roller): ").strip().lower()
            position = float(input(f"Enter the position of support {i + 1}: "))
            self.supports.append({"type": support_type, "position": position})
        print("Supports configured successfully.\n")
    
    def input_spans(self):
        num_spans = len(self.supports) - 1
        for i in range(num_spans):
            ei = float(input(f"Enter EI for span {i + 1}: "))
            load_type = input(f"Enter load type for span {i + 1} (point, udl, vdl, none): ").strip().lower()
            load_data = {}
            if load_type == "point":
                load_data["magnitude"] = float(input("Enter point load magnitude: "))
                load_data["position"] = float(input("Enter point load position from left: "))
            elif load_type == "udl":
                load_data["magnitude"] = float(input("Enter UDL magnitude: "))
            elif load_type == "vdl":
                load_data["magnitude"] = float(input("Enter varying load magnitude (max at mid-span): "))
            self.spans.append({"EI": ei, "load_type": load_type, "load_data": load_data})
        print("Spans configured successfully.\n")
    
    def calculate_fixed_end_moments(self):
        print("Calculating Fixed-End Moments (FEM)...")
        self.fixed_end_moments = []
        for i, span in enumerate(self.spans):
            fem = {}
            if span["load_type"] == "udl":
                w = span["load_data"]["magnitude"]
                l = self.supports[i + 1]["position"] - self.supports[i]["position"]
                fem["AB"] = -w * l**2 / 12
                fem["BA"] = w * l**2 / 12
            elif span["load_type"] == "point":
                p = span["load_data"]["magnitude"]
                a = span["load_data"]["position"]
                l = self.supports[i + 1]["position"] - self.supports[i]["position"]
                b = l - a
                fem["AB"] = -p * a * b**2 / (l**2)
                fem["BA"] = p * a**2 * b / (l**2)
            else:
                fem["AB"] = fem["BA"] = 0
            self.fixed_end_moments.append(fem)
        print("Fixed-End Moments (FEM):", self.fixed_end_moments, "\n")
    
    def solve_theta_values(self):
        print("Solving for Theta Values...")
        
        # Determine the number of unknowns (hinged or roller supports)
        num_supports = len(self.supports)
        unknown_indices = [
            i for i, support in enumerate(self.supports) if support["type"] in ("hinged", "roller")
        ]
        num_unknowns = len(unknown_indices)

        print(f"Number of unknowns (theta values): {num_unknowns}")
        
        # Initialize coefficient matrix and constants vector
        coeff_matrix = np.zeros((num_unknowns, num_unknowns))
        constants = np.zeros(num_unknowns)

        # Populate coefficients and constants
        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]

            # Indices of current and next supports in unknowns
            if self.supports[i]["type"] in ("hinged", "roller"):
                current_idx = unknown_indices.index(i)
                coeff_matrix[current_idx, current_idx] += 4 * ei / l
                constants[current_idx] += self.fixed_end_moments[i]["AB"]

                if self.supports[i + 1]["type"] in ("hinged", "roller"):
                    next_idx = unknown_indices.index(i + 1)
                    coeff_matrix[current_idx, next_idx] += 2 * ei / l

            if self.supports[i + 1]["type"] in ("hinged", "roller"):
                next_idx = unknown_indices.index(i + 1)
                coeff_matrix[next_idx, next_idx] += 4 * ei / l
                constants[next_idx] += self.fixed_end_moments[i]["BA"]

                if self.supports[i]["type"] in ("hinged", "roller"):
                    current_idx = unknown_indices.index(i)
                    coeff_matrix[next_idx, current_idx] += 2 * ei / l

        # Debug output
        print("Coefficient Matrix (stiffness):")
        print(coeff_matrix)
        print("Constants Vector (fixed end moments):")
        print(constants)

        # Solve the system of equations
        try:
            theta_unknowns = np.linalg.solve(coeff_matrix, constants)
        except np.linalg.LinAlgError:
            print("Error: Singular matrix. Check input data or boundary conditions.")
            return
        
        # Populate the full theta values for all supports
        self.theta_values = np.zeros(num_supports)
        for i, idx in enumerate(unknown_indices):
            self.theta_values[idx] = theta_unknowns[i]

        print("Theta Values (Slopes):", self.theta_values, "\n")

    def calculate_reactions(self):
        print("Calculating Reactions...")
        self.reactions = [0] * len(self.supports)

        for i in range(len(self.spans)):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            ei = self.spans[i]["EI"]
            theta_a = self.theta_values[i]
            theta_b = self.theta_values[i + 1]
            
            # Calculate moments using slope-deflection equations
            moment_a = (4 * ei / l) * theta_a - (2 * ei / l) * theta_b + self.fixed_end_moments[i]["AB"]
            moment_b = (4 * ei / l) * theta_b - (2 * ei / l) * theta_a + self.fixed_end_moments[i]["BA"]
            
            # Add moments to corresponding supports
            self.reactions[i] += moment_a
            self.reactions[i + 1] += moment_b

        print("Reactions:", self.reactions, "\n")

    def plot_shear_and_bending(self):
        print("Plotting Shear Force and Bending Moment Diagrams...")
        x_vals = []
        shear_vals = []
        moment_vals = []

        for i, span in enumerate(self.spans):
            l = self.supports[i + 1]["position"] - self.supports[i]["position"]
            if span["load_type"] == "udl":
                w = span["load_data"]["magnitude"]
                x = np.linspace(0, l, 100)
                shear = w * (l / 2 - x)
                moment = w * x * (l - x) / 2
                x_vals.extend(list(x + self.supports[i]["position"]))
                shear_vals.extend(list(shear))
                moment_vals.extend(list(moment))

        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(x_vals, shear_vals, label="Shear Force")
        plt.axhline(0, color="black", linewidth=0.5)
        plt.title("Shear Force Diagram")
        plt.xlabel("Position")
        plt.ylabel("Shear Force")
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(x_vals, moment_vals, label="Bending Moment", color="red")
        plt.axhline(0, color="black", linewidth=0.5)
        plt.title("Bending Moment Diagram")
        plt.xlabel("Position")
        plt.ylabel("Bending Moment")
        plt.grid()

        plt.tight_layout()
        plt.show()
    
    def analyze(self):
        self.input_supports()
        self.input_spans()
        self.calculate_fixed_end_moments()
        self.solve_theta_values()
        self.calculate_reactions()
        self.plot_shear_and_bending()


# Main program
beam = BeamAnalysis()
beam.analyze()
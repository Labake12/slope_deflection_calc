import numpy as np

class BeamReactions:
    def __init__(self):
        self.supports = []
        self.spans = []
        self.final_moments = {}
        self.reactions = []

    def calculate_reactions(self):
        """Calculate reactions at supports considering equilibrium conditions."""
        print("Calculating Reactions at Supports...")
        num_supports = len(self.supports)
        self.reactions = np.zeros(num_supports)  # Initialize reactions as zero

        for i in range(len(self.spans)):
            L = self.spans[i]["L"]
            loads = self.spans[i]["loads"]
            start_support = self.supports[i]["type"]
            end_support = self.supports[i + 1]["type"]

            start_letter = chr(65 + i)
            end_letter = chr(65 + i + 1)
            span_name_forward = f"{start_letter}{end_letter}"
            span_name_backward = f"{end_letter}{start_letter}"
            m_ab = self.final_moments.get(f"M_{span_name_forward}", 0)
            m_ba = self.final_moments.get(f"M_{span_name_backward}", 0)

            reaction_a, reaction_b = 0, 0  # Initialize reactions for the span

            # **Calculate Total Load for Span**
            total_load = 0
            load_position_sum = 0  # Used for moments
            for load in loads:
                if load["type"] == "udl":
                    w = load["magnitude"]
                    total_load += w * L
                    load_position_sum += (w * L * (L / 2))  # Moment due to UDL

                elif load["type"] == "point_center":
                    p = load["magnitude"]
                    total_load += p
                    load_position_sum += (p * (L / 2))  # Moment at center

                elif load["type"] == "vdl_right":
                    w = load["magnitude"]
                    total_load += 0.5 * w * L
                    load_position_sum += (0.5 * w * L * (2 * L / 3))  # Centroid at 2L/3

            # **Reaction Equilibrium: Sum of Forces = 0**
            if start_support == "none":
                # Assign all load directly to the first actual support
                reaction_b = total_load
                reaction_a = 0
            else:
                reaction_b = (m_ab + m_ba + load_position_sum) / L
                reaction_a = total_load - reaction_b

            # Update global reactions
            if start_support != "none":
                self.reactions[i] += reaction_a
            self.reactions[i + 1] += reaction_b  # The end support always takes reaction

        # Print calculated reactions
        print("\nReactions at Supports:")
        for i, reaction in enumerate(self.reactions):
            print(f"Support {chr(65 + i)} at {self.supports[i]['position']}m: {reaction:.3f} kN")

# ====== TEST CASE ======
if __name__ == "__main__":
    beam = BeamReactions()

    # Given question data
    beam.supports = [
        {"type": "none", "position": 0},  # A (Free End)
        {"type": "hinged", "position": 3},  # B (Hinged)
        {"type": "hinged", "position": 9},  # C (Hinged)
        {"type": "fixed", "position": 13}  # D (Fixed)
    ]
    beam.spans = [
        {"EI": 1, "L": 3, "loads": [{"type": "udl", "magnitude": 12}]},  # AB
        {"EI": 1, "L": 6, "loads": [{"type": "point_center", "magnitude": 48}]},  # BC
        {"EI": 1, "L": 4, "loads": [{"type": "vdl_right", "magnitude": 90}]}  # CD
    ]

    beam.final_moments = {
        "M_AB": 0.00,
        "M_BA": -54.00,
        "M_BC": -54.00,
        "M_CB": 34.00,
        "M_CD": -34.00,
        "M_DC": 79.00
    }

    # Run test
    beam.calculate_reactions()

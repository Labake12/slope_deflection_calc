from flask import Flask, render_template, request, jsonify
from sample import BeamAnalysis
import os

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static')

# Ensure a directory for images exists
IMAGE_DIR = 'static/images'
os.makedirs(IMAGE_DIR, exist_ok=True)

def clear_old_images():
    """Delete old images from the images directory."""
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle beam analysis."""
    try:
        total_supports = int(request.form['total_supports'])
        supports = [
            {
                "type": request.form[f'support_{i}_type'],
                "position": float(request.form[f'support_{i}_position'])
            } for i in range(1, total_supports + 1)
        ]

        total_spans = len(supports) - 1
        spans = []
        for i in range(1, total_spans + 1):
            ei = float(request.form[f'span_{i}_EI'])
            num_loads = int(request.form[f'span_{i}_num_loads'])
            loads = []
            for j in range(1, num_loads + 1):
                load_type = request.form[f'span_{i}_load_{j}_type']
                if load_type == 'point':
                    loads.append({
                        "type": load_type,
                        "magnitude": float(request.form[f'span_{i}_load_{j}_magnitude']),
                        "position": float(request.form[f'span_{i}_load_{j}_position'])
                    })
                elif load_type == 'udl':
                    loads.append({
                        "type": load_type,
                        "magnitude": float(request.form[f'span_{i}_load_{j}_magnitude'])
                    })
                elif load_type == 'vdl':
                    loads.append({
                        "type": load_type,
                        "magnitude_start": float(request.form[f'span_{i}_load_{j}_magnitude_start']),
                        "magnitude_end": float(request.form[f'span_{i}_load_{j}_magnitude_end'])
                    })
            spans.append({"EI": ei, "loads": loads})

        # Perform analysis
        beam = BeamAnalysis()
        beam.supports = supports
        beam.spans = spans
        beam.calculate_fixed_end_moments()
        beam.solve_theta_values()
        beam.calculate_final_moments()
        beam.calculate_reactions()

        # Generate diagrams
        clear_old_images()
        x_vals, shear_vals, moment_vals = beam.calculate_shear_and_bending()
        diagram_path = os.path.join(IMAGE_DIR, 'diagrams.png')
        beam.plot_diagrams(x_vals, shear_vals, moment_vals, diagram_path)

        return jsonify({
            "fixed_end_moments": beam.fixed_end_moments,
            "theta_values": beam.theta_values.tolist(),
            "final_moments": beam.final_moments,
            "reactions": beam.reactions,
            "diagram_path": '/' + diagram_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

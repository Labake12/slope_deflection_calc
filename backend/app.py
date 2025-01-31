from flask import Flask, render_template, request, jsonify
from beams import BeamAnalysis
import os
import logging
import numpy as np

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, template_folder='./templates', static_folder='./static')

IMAGE_DIR = 'static/images'
os.makedirs(IMAGE_DIR, exist_ok=True)

def clear_old_images():
    """Delete old images from the directory."""
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def convert_to_serializable(obj):
    """Recursively convert ndarrays to lists for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(value) for value in obj]
    return obj

@app.route('/')
def index():
    """Render the home page."""
    return render_template('home.html')

@app.route('/beam', methods=['GET'])
def beam():
    """Render the beam analysis page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_beam():
    """Handle beam analysis request and return results."""
    try:
        data = request.json
        supports = data.get('supports')
        spans = data.get('spans')

        # Convert load types from integers to descriptive strings
        load_type_mapping = {
            2: "point_center",
            3: "point_distance",
            6: "udl",
            7: "vdl_right",
            8: "vdl_left"
        }

        # Process spans and map load types
        for span in spans:
            converted_loads = []
            for load in span.get('loads', []):
                load_type = load.get('type')
                mapped_type = load_type_mapping.get(load_type, "unknown")
                
                new_load = {
                    'type': mapped_type,
                    'magnitude': load.get('magnitude')
                }
                
                if mapped_type == "point_distance":
                    new_load['a'] = load.get('distanceA')
                    new_load['b'] = load.get('distanceB')
                
                converted_loads.append(new_load)
            
            span['loads'] = converted_loads

        # Perform beam analysis
        analysis = BeamAnalysis()
        analysis.input_supports(supports)
        analysis.input_spans(spans)
        results = analysis.analyze()

        # Save diagram and return results
        diagram_path = os.path.join(IMAGE_DIR, 'diagram.png')
        analysis.plot_diagrams(results["shear_forces"], results["bending_moments"], diagram_path)

        return jsonify({
            "status": "success",
            "fixed_end_moments": [{"AB": fem["AB"], "BA": fem["BA"]} for fem in results["fixed_end_moments"]],
            "theta_values": convert_to_serializable(results["theta_values"]),
            "final_moments": convert_to_serializable(results["final_moments"]),
            "reactions": convert_to_serializable(results["reactions"]),
            "diagram_path": f"/{diagram_path}"
        })
    except Exception as e:
        logging.error(f"Error during beam analysis: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
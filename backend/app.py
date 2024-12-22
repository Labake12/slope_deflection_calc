from flask import Flask, render_template, request
from slope_deflection_calculations import calculate_fem, slope_deflection_method, apply_boundary_conditions

app = Flask(__name__,
            template_folder='../templates',  # Path to the templates folder
            static_folder='../static')       # Path to the static folder

# Route for the Home Page
@app.route('/home')
def home():
    return render_template('home.html')

# Route for the Beam Analysis Calculation Page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        total_spans = int(request.form['total_spans'])
        
        # Initialize the list of spans and supports
        spans = []
        supports = []

        for i in range(1, total_spans + 1):
            # Collect span details
            span_length = float(request.form[f'span_{i}_length'])
            EI = float(request.form[f'span_{i}_EI'])
            load_type = request.form[f'span_{i}_load_type']
            load_params = {}

            # Handle load parameters based on load type
            if load_type == 'point':
                load_params = {
                    'P': float(request.form[f'span_{i}_P']),
                    'a': float(request.form[f'span_{i}_a'])
                }
            elif load_type == 'udl':
                load_params = {'w': float(request.form[f'span_{i}_w'])}
            elif load_type == 'vdl':
                load_params = {'w': float(request.form[f'span_{i}_w_vdl'])}

            # Create span object
            spans.append({
                "length": span_length,
                "EI": EI,
                "load_type": load_type,
                "load_params": load_params
            })
            
            # Create support object (example: Hinged support at the end of each span)
            supports.append({"type": "hinged", "position": 0})  # Adjust as needed

        # Calculate Fixed-End Moments (FEM)
        fem_results = calculate_fem(supports, spans)

        # Perform Slope Deflection Analysis
        slope_deflection_results = slope_deflection_method(fem_results, spans)

        # Apply Boundary Conditions
        adjusted_results = apply_boundary_conditions(slope_deflection_results, supports, spans)

        return render_template('index.html', results=adjusted_results)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

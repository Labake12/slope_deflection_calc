document.addEventListener('DOMContentLoaded', function () {
    const totalSupportsInput = document.getElementById('total_supports'); // Number of supports input
    const spanDetailsContainer = document.getElementById('span_details_container'); // Container for spans and supports
    const calculateButton = document.getElementById('calculate_button'); // Calculate button

    // Hide the Calculate button initially
    calculateButton.style.display = 'none';

    totalSupportsInput.addEventListener('input', function () {
        const totalSupports = parseInt(totalSupportsInput.value);

        // Clear existing content and validate input
        spanDetailsContainer.innerHTML = '';
        if (isNaN(totalSupports) || totalSupports < 2) {
            spanDetailsContainer.innerHTML = '<p>Please enter a valid number of supports (at least 2).</p>';
            calculateButton.style.display = 'none';
            return;
        }

        const totalSpans = totalSupports - 1; // Spans = Supports - 1

        // Generate Support Fields
        for (let i = 1; i <= totalSupports; i++) {
            const supportDiv = document.createElement('div');
            supportDiv.classList.add('support-group');
            supportDiv.innerHTML = `
                <h3>Support ${i}</h3>
                <label for="support_${i}_position">Position of Support ${i}:</label>
                <input type="number" id="support_${i}_position" name="support_${i}_position" required><br><br>

                <label for="support_${i}_type">Support Type for Support ${i}:</label>
                <select name="support_${i}_type" id="support_${i}_type" required>
                    <option value="fixed">Fixed</option>
                    <option value="roller">Roller</option>
                    <option value="hinged">Hinged</option>
                </select><br><br>
            `;
            spanDetailsContainer.appendChild(supportDiv);
        }

        // Generate Span Fields
        for (let i = 1; i <= totalSpans; i++) {
            const spanDiv = document.createElement('div');
            spanDiv.classList.add('span-group');
            spanDiv.innerHTML = `
                <h3>Span ${i}</h3>
                <label for="span_${i}_length">Length of Span ${i} (L):</label>
                <input type="number" id="span_${i}_length" name="span_${i}_length" required><br><br>

                <label for="span_${i}_EI">Elasticity (EI):</label>
                <input type="number" id="span_${i}_EI" name="span_${i}_EI" required><br><br>

                <label for="span_${i}_load_type">Load Type for Span ${i}:</label>
                <select name="span_${i}_load_type" id="span_${i}_load_type" required>
                    <option value="point">Point Load</option>
                    <option value="udl">Uniformly Distributed Load</option>
                    <option value="vdl">Variable Distributed Load</option>
                    <option value="none">No Load</option>
                </select><br><br>

                <div id="span_${i}_load_params"></div>
            `;
            spanDetailsContainer.appendChild(spanDiv);

            // Add Event Listener for Load Type
            const loadTypeSelect = spanDiv.querySelector(`#span_${i}_load_type`);
            const loadParamsContainer = spanDiv.querySelector(`#span_${i}_load_params`);

            loadTypeSelect.addEventListener('change', function () {
                const loadType = loadTypeSelect.value;
                loadParamsContainer.innerHTML = ''; // Clear existing inputs

                if (loadType === 'point') {
                    loadParamsContainer.innerHTML = `
                        <label for="span_${i}_P">Load Magnitude (P):</label>
                        <input type="number" id="span_${i}_P" name="span_${i}_P" required><br><br>

                        <label for="span_${i}_a">Distance from Start (a):</label>
                        <input type="number" id="span_${i}_a" name="span_${i}_a" required><br><br>
                    `;
                } else if (loadType === 'udl') {
                    loadParamsContainer.innerHTML = `
                        <label for="span_${i}_w">Uniform Load (w):</label>
                        <input type="number" id="span_${i}_w" name="span_${i}_w" required><br><br>
                    `;
                } else if (loadType === 'vdl') {
                    loadParamsContainer.innerHTML = `
                        <label for="span_${i}_w_vdl">Variable Load (w):</label>
                        <input type="number" id="span_${i}_w_vdl" name="span_${i}_w_vdl" required><br><br>
                    `;
                }
            });
        }

        // Show the Calculate button after generating spans and supports
        calculateButton.style.display = 'block';
    });
});

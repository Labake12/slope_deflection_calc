document.addEventListener('DOMContentLoaded', function() {
    const totalSpansInput = document.getElementById('total_spans');
    const spanDetailsContainer = document.getElementById('span_details_container');

    totalSpansInput.addEventListener('input', function() {
        const totalSpans = parseInt(totalSpansInput.value);
        spanDetailsContainer.innerHTML = '';  // Clear existing fields

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

            // Add event listener for the load type dropdown
            const loadTypeSelect = spanDiv.querySelector(`#span_${i}_load_type`);
            const loadParamsContainer = spanDiv.querySelector(`#span_${i}_load_params`);

            loadTypeSelect.addEventListener('change', function() {
                const loadType = loadTypeSelect.value;
                loadParamsContainer.innerHTML = '';  // Clear existing inputs

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
    });
});
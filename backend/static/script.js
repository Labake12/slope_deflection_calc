document.addEventListener('DOMContentLoaded', function () {
    const totalSupportsInput = document.getElementById('total_supports');
    const spanDetailsContainer = document.getElementById('span_details_container');
    const calculateButton = document.getElementById('calculate_button');
    const resultsContainer = document.getElementById('results_container');

    // Hide calculate button initially
    calculateButton.style.display = 'none';

    totalSupportsInput.addEventListener('input', function () {
        const totalSupports = parseInt(totalSupportsInput.value);
        spanDetailsContainer.innerHTML = ''; // Clear existing fields

        if (isNaN(totalSupports) || totalSupports < 2) {
            spanDetailsContainer.innerHTML = '<p>Please enter at least 2 supports.</p>';
            calculateButton.style.display = 'none';
            return;
        }

        const totalSpans = totalSupports - 1;

        // Generate support fields
        for (let i = 1; i <= totalSupports; i++) {
            const supportDiv = document.createElement('div');
            supportDiv.innerHTML = `
                <h3>Support ${i}</h3>
                <label for="support_${i}_type">Type:</label>
                <select id="support_${i}_type" name="support_${i}_type">
                    <option value="fixed">Fixed</option>
                    <option value="roller">Roller</option>
                    <option value="hinged">Hinged</option>
                </select>
                <label for="support_${i}_position">Position:</label>
                <input type="number" id="support_${i}_position" name="support_${i}_position" required>
            `;
            spanDetailsContainer.appendChild(supportDiv);
        }

        // Generate span fields
        for (let i = 1; i <= totalSpans; i++) {
            const spanDiv = document.createElement('div');
            spanDiv.innerHTML = `
                <h3>Span ${i}</h3>
                <label for="span_${i}_EI">Elasticity (EI):</label>
                <input type="number" id="span_${i}_EI" name="span_${i}_EI" required>
                <label for="span_${i}_num_loads">Number of Loads:</label>
                <input type="number" id="span_${i}_num_loads" name="span_${i}_num_loads" required>
                <div id="span_${i}_loads"></div>
            `;
            spanDetailsContainer.appendChild(spanDiv);

            const numLoadsInput = spanDiv.querySelector(`#span_${i}_num_loads`);
            const loadsContainer = spanDiv.querySelector(`#span_${i}_loads`);

            numLoadsInput.addEventListener('input', function () {
                loadsContainer.innerHTML = '';
                const numLoads = parseInt(numLoadsInput.value);

                for (let j = 1; j <= numLoads; j++) {
                    const loadDiv = document.createElement('div');
                    loadDiv.innerHTML = `
                        <h4>Load ${j}</h4>
                        <label for="span_${i}_load_${j}_type">Type:</label>
                        <select id="span_${i}_load_${j}_type" name="span_${i}_load_${j}_type">
                            <option value="point">Point Load</option>
                            <option value="udl">Uniformly Distributed Load</option>
                            <option value="vdl">Variable Distributed Load</option>
                        </select>
                        <div id="span_${i}_load_${j}_params"></div>
                    `;
                    loadsContainer.appendChild(loadDiv);

                    const loadTypeSelect = loadDiv.querySelector(`#span_${i}_load_${j}_type`);
                    const loadParamsContainer = loadDiv.querySelector(`#span_${i}_load_${j}_params`);

                    loadTypeSelect.addEventListener('change', function () {
                        const loadType = loadTypeSelect.value;
                        loadParamsContainer.innerHTML = '';

                        if (loadType === 'point') {
                            loadParamsContainer.innerHTML = `
                                <label for="span_${i}_load_${j}_magnitude">Magnitude:</label>
                                <input type="number" id="span_${i}_load_${j}_magnitude" name="span_${i}_load_${j}_magnitude" required>
                                <label for="span_${i}_load_${j}_position">Position:</label>
                                <input type="number" id="span_${i}_load_${j}_position" name="span_${i}_load_${j}_position" required>
                            `;
                        } else if (loadType === 'udl') {
                            loadParamsContainer.innerHTML = `
                                <label for="span_${i}_load_${j}_magnitude">Magnitude:</label>
                                <input type="number" id="span_${i}_load_${j}_magnitude" name="span_${i}_load_${j}_magnitude" required>
                            `;
                        } else if (loadType === 'vdl') {
                            loadParamsContainer.innerHTML = `
                                <label for="span_${i}_load_${j}_magnitude_start">Start Magnitude:</label>
                                <input type="number" id="span_${i}_load_${j}_magnitude_start" name="span_${i}_load_${j}_magnitude_start" required>
                                <label for="span_${i}_load_${j}_magnitude_end">End Magnitude:</label>
                                <input type="number" id="span_${i}_load_${j}_magnitude_end" name="span_${i}_load_${j}_magnitude_end" required>
                            `;
                        }
                    });
                }
            });
        }

        calculateButton.style.display = 'block';
    });

    calculateButton.addEventListener('click', async function () {
        const form = document.getElementById('beam-analysis-form');
        const formData = new FormData(form);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            if (response.ok) {
                resultsContainer.innerHTML = `
                    <h3>Results</h3>
                    <pre>Fixed-End Moments: ${JSON.stringify(data.fixed_end_moments, null, 2)}</pre>
                    <pre>Reactions: ${JSON.stringify(data.reactions, null, 2)}</pre>
                    <img src="${data.diagram_path}" alt="Beam Diagrams">
                `;
            } else {
                resultsContainer.innerHTML = `<p>Error: ${data.error}</p>`;
            }
        } catch (error) {
            resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    });
});

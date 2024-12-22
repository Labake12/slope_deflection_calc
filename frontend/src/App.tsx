import React, { useState } from "react";
// import axios from "axios";
import "./App.css";

const App: React.FC = () => {
    const [numSupports, setNumSupports] = useState<number | ''>('');
    const [supports, setSupports] = useState<{ type: string; position: number }[]>([]);
    const [currentSupport, setCurrentSupport] = useState<{ type: string; position: number }>({
        type: '',
        position: 0,
    });
    const [spans, setSpans] = useState<{ EI: number; loadType: string; loadParams: any }[]>([]);
    const [currentSpan, setCurrentSpan] = useState<{ EI: number; loadType: string; loadParams: any }>({
        EI: 0,
        loadType: '',
        loadParams: {},
    });

    const handleAddSupport = () => {
        if (currentSupport.type && currentSupport.position > 0) {
            setSupports((prev) => [...prev, currentSupport].sort((a, b) => a.position - b.position));
            setCurrentSupport({ type: '', position: 0 });
        } else {
            alert('Please provide valid support details.');
        }
    };

    const handleAddSpan = () => {
        if (currentSpan.EI && currentSpan.loadType) {
            setSpans((prev) => [...prev, currentSpan]);
            setCurrentSpan({ EI: 0, loadType: '', loadParams: {} });
        } else {
            alert('Please provide valid span details.');
        }
    };

    const handleAddLoadParams = (paramName: string, value: any) => {
        setCurrentSpan((prev) => ({
            ...prev,
            loadParams: { ...prev.loadParams, [paramName]: value },
        }));
    };

    return (
        <div style={{ fontFamily: 'Arial, sans-serif', margin: '20px' }}>
            <h1>Slope Deflection Calculator</h1>

            {/* Step 1: Number of Supports */}
            {numSupports === '' ? (
                <div>
                    <label>Enter the number of supports (minimum 2):</label>
                    <input
                        type="number"
                        value={numSupports}
                        onChange={(e) => setNumSupports(Number(e.target.value))}
                        min={2}
                        required
                    />
                </div>
            ) : (
                <>
                    {/* Step 2: Add Supports */}
                    {supports.length < numSupports && (
                        <div>
                            <h2>Add Supports</h2>
                            <label>Type of Support:</label>
                            <select
                                value={currentSupport.type}
                                onChange={(e) =>
                                    setCurrentSupport((prev) => ({ ...prev, type: e.target.value }))
                                }
                            >
                                <option value="">Select support type</option>
                                <option value="hinged">Hinged</option>
                                <option value="fixed">Fixed</option>
                                <option value="roller">Roller</option>
                            </select>
                            <label>Position:</label>
                            <input
                                type="number"
                                value={currentSupport.position}
                                onChange={(e) =>
                                    setCurrentSupport((prev) => ({
                                        ...prev,
                                        position: Number(e.target.value),
                                    }))
                                }
                                required
                            />
                            <button type="button" onClick={handleAddSupport}>
                                Add Support
                            </button>
                        </div>
                    )}

                    {/* Step 3: Add Spans */}
                    {supports.length === numSupports && (
                        <>
                            <h2>Add Spans</h2>
                            {spans.length < numSupports - 1 && (
                                <div>
                                    <h3>Span {spans.length + 1}</h3>
                                    <label>Enter EI for this span:</label>
                                    <input
                                        type="number"
                                        value={currentSpan.EI}
                                        onChange={(e) =>
                                            setCurrentSpan((prev) => ({
                                                ...prev,
                                                EI: Number(e.target.value),
                                            }))
                                        }
                                        required
                                    />
                                    <label>Load Type:</label>
                                    <select
                                        value={currentSpan.loadType}
                                        onChange={(e) =>
                                            setCurrentSpan((prev) => ({
                                                ...prev,
                                                loadType: e.target.value,
                                            }))
                                        }
                                    >
                                        <option value="">Select load type</option>
                                        <option value="point">Point Load</option>
                                        <option value="udl">Uniformly Distributed Load (UDL)</option>
                                        <option value="vdl">Variable Distributed Load (VDL)</option>
                                        <option value="none">No Load</option>
                                    </select>

                                    {currentSpan.loadType === 'point' && (
                                        <div>
                                            <label>Point Load Magnitude:</label>
                                            <input
                                                type="number"
                                                onChange={(e) => handleAddLoadParams('P', Number(e.target.value))}
                                                required
                                            />
                                            <label>Position from Left:</label>
                                            <input
                                                type="number"
                                                onChange={(e) =>
                                                    handleAddLoadParams('a', Number(e.target.value))
                                                }
                                                required
                                            />
                                        </div>
                                    )}

                                    {currentSpan.loadType === 'udl' && (
                                        <div>
                                            <label>UDL Magnitude:</label>
                                            <input
                                                type="number"
                                                onChange={(e) =>
                                                    handleAddLoadParams('w', Number(e.target.value))
                                                }
                                                required
                                            />
                                        </div>
                                    )}

                                    {currentSpan.loadType === 'vdl' && (
                                        <div>
                                            <label>VDL Max Magnitude:</label>
                                            <input
                                                type="number"
                                                onChange={(e) =>
                                                    handleAddLoadParams('w', Number(e.target.value))
                                                }
                                                required
                                            />
                                        </div>
                                    )}

                                    <button type="button" onClick={handleAddSpan}>
                                        Add Span
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </>
            )}
        </div>
    );
};

export default App;

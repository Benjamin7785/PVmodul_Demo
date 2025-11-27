/**
 * Client-Side Dash Callbacks for PV Module Visualization
 * 
 * Uses LUT interpolation for instant updates without server round-trips.
 * Performs physics calculations in browser and updates visualizations directly.
 * 
 * Performance: 10-20ms per update (vs. 650ms server-side)
 */

// Global interpolator instance (initialized when LUT data is loaded)
let globalInterpolator = null;
let lutLoadingPromise = null; // Track if we're already loading

// OPTION B: Fetch LUT from Flask API endpoint
async function fetchLUTFromAPI() {
    if (lutLoadingPromise) {
        return lutLoadingPromise; // Already loading, return existing promise
    }
    
    console.log("[API] Fetching LUT from /api/lut...");
    lutLoadingPromise = fetch('/api/lut')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(lutData => {
            console.log("[API] LUT data received, initializing interpolator...");
            if (initializeInterpolator(lutData)) {
                console.log("[OK] LUT loaded successfully from API!");
                return true;
            } else {
                console.error("[ERROR] Failed to initialize interpolator");
                return false;
            }
        })
        .catch(error => {
            console.error("[ERROR] Failed to fetch LUT from API:", error);
            lutLoadingPromise = null; // Reset so we can retry
            return false;
        });
    
    return lutLoadingPromise;
}

// Initialize interpolator when LUT data is available
function initializeInterpolator(lutData) {
    if (!lutData || !lutData.voltage_lut) {
        console.warn("[LUT] No LUT data available, client-side mode disabled");
        return false;
    }
    
    // Reconstruct 4D array from flattened data
    const shape = lutData.shape;
    const flat = lutData.voltage_lut;
    const lut4D = [];
    
    let idx = 0;
    for (let i = 0; i < shape[0]; i++) {
        lut4D[i] = [];
        for (let j = 0; j < shape[1]; j++) {
            lut4D[i][j] = [];
            for (let k = 0; k < shape[2]; k++) {
                lut4D[i][j][k] = [];
                for (let m = 0; m < shape[3]; m++) {
                    lut4D[i][j][k][m] = flat[idx++];
                }
            }
        }
    }
    
    // Create interpolator with reconstructed 4D array
    const lutDataReconstructed = {
        irradiance: lutData.irradiance,
        temperature: lutData.temperature,
        shading: lutData.shading,
        current: lutData.current,
        voltage_lut: lut4D.flat()  // LUTInterpolator expects flat array with shape info
    };
    
    globalInterpolator = new window.LUTInterpolator(lutDataReconstructed);
    console.log("[OK] Client-side interpolator initialized!");
    return true;
}


/**
 * Client-Side Callback: Update Voltage Distribution Visualizations
 * 
 * This replaces the server-side Python callback with pure JavaScript.
 * Uses LUT interpolation for instant physics calculations.
 */
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        /**
         * Update voltage distribution page
         * 
         * This is the MAIN performance-critical callback.
         * Replaces ~650ms server callback with ~10-20ms client calculation.
         */
        update_voltage_distribution: function(
            scenario_id,
            irradiance,
            temperature,
            shading_percent,
            display_options,
            lutData
        ) {
            console.time('[PERF] Client-side update');
            
            // OPTION B: Try to fetch LUT from API if not available
            if (!globalInterpolator) {
                // Try to initialize from dcc.Store first (if available)
                if (lutData && !globalInterpolator) {
                    initializeInterpolator(lutData);
                }
                
                // If still not available, fetch from API (async)
                if (!globalInterpolator) {
                    console.log("[FETCH] Attempting to load LUT from API...");
                    
                    // Start loading in background
                    fetchLUTFromAPI().then(() => {
                        // Add a small delay to ensure the interpolator is fully ready
                        setTimeout(() => {
                            if (globalInterpolator) {
                                console.log("[OK] LUT ready, triggering page refresh...");
                                // Trigger a small input change to re-run the callback
                                // We'll use the irradiance slider to re-trigger the callback
                                const irradianceSlider = document.getElementById('irradiance-slider');
                                console.log("[DEBUG] Irradiance slider element:", irradianceSlider);
                                
                                if (irradianceSlider) {
                                    console.log("[OK] Triggering irradiance slider change event...");
                                    // Get the current value and set it again to trigger the callback
                                    const currentValue = irradianceSlider.value;
                                    const newValue = currentValue === '1000' ? '999' : '1000';
                                    
                                    // Trigger the change
                                    irradianceSlider.value = newValue;
                                    irradianceSlider.dispatchEvent(new Event('input', { bubbles: true }));
                                    irradianceSlider.dispatchEvent(new Event('change', { bubbles: true }));
                                    
                                    // Reset to original value after a small delay
                                    setTimeout(() => {
                                        irradianceSlider.value = currentValue;
                                        irradianceSlider.dispatchEvent(new Event('input', { bubbles: true }));
                                        irradianceSlider.dispatchEvent(new Event('change', { bubbles: true }));
                                        console.log("[OK] Slider reset to original value");
                                    }, 200);
                                } else {
                                    console.error("[ERROR] Irradiance slider element not found!");
                                }
                            } else {
                                console.error("[ERROR] globalInterpolator still null after LUT load!");
                            }
                        }, 200); // Wait 200ms to ensure interpolator is fully initialized
                    });
                    
                    // Return loading state while fetching
                    return [
                        {data: [], layout: {title: 'Loading LUT from API...'}},
                        {data: [], layout: {title: 'Loading LUT from API...'}},
                        {data: [], layout: {title: 'Loading LUT from API...'}},
                        'Loading LUT...',
                        'Loading...',
                        'Loading...'
                    ];
                }
            }
            
            // Convert shading percent to factor
            const shadingIntensity = shading_percent / 100.0;
            
            // Create module with shading scenario
            const module = window.applyShadingScenario(
                scenario_id || 'none',
                shadingIntensity,
                globalInterpolator,
                irradiance,
                temperature
            );
            
            // Find MPP (fast!)
            const mpp = module.findMPP(30);
            const current = mpp.current;
            
            // Calculate module state at operating point
            const moduleState = module.calculateVoltage(current);
            
            // Extract cell voltages for visualization
            const cellVoltages = [];
            const cellPowers = [];
            const cellShading = [];
            
            for (const string of module.strings) {
                for (const cell of string.cells) {
                    const voltage = cell.findVoltage(current);
                    const power = Math.abs(voltage * current);
                    cellVoltages.push(voltage);
                    cellPowers.push(power);
                    cellShading.push(cell.shadingFactor);
                }
            }
            
            // ================================================================
            // VISUALIZATION 1: Circuit Diagram (Simplified SVG update)
            // ================================================================
            // For now, return a simple Plotly heatmap-like visualization
            // Full SVG circuit diagram would require more complex JS
            
            const circuitFig = createCircuitDiagram(
                cellVoltages,
                moduleState,
                current,
                display_options
            );
            
            // ================================================================
            // VISUALIZATION 2: Voltage Heatmap
            // ================================================================
            
            const voltageHeatmap = createVoltageHeatmap(cellVoltages);
            
            // ================================================================
            // VISUALIZATION 3: Power Dissipation Heatmap
            // ================================================================
            
            const powerHeatmap = createPowerHeatmap(cellPowers);
            
            // ================================================================
            // INFO PANELS: Hotspots, Operating Point, Shading Info
            // ================================================================
            
            // Hotspot analysis
            const hotspots = analyzeHotspots(cellVoltages, cellPowers, current);
            const hotspotInfo = formatHotspotInfo(hotspots);
            
            // Operating point info
            const opInfo = formatOperatingPointInfo(moduleState, current, mpp);
            
            // Shading intensity info
            const shadingInfo = formatShadingInfo(
                shading_percent,
                shadingIntensity,
                cellShading,
                current,
                mpp
            );
            
            console.timeEnd('[PERF] Client-side update');
            
            return [
                circuitFig,
                voltageHeatmap,
                powerHeatmap,
                hotspotInfo,
                opInfo,
                shadingInfo
            ];
        },
        
        /**
         * Initialize LUT when data becomes available
         */
        initialize_lut: function(lutData) {
            if (lutData) {
                initializeInterpolator(lutData);
                return 'LUT Initialized';
            }
            return 'Waiting for LUT...';
        }
    }
});


// ============================================================================
// VISUALIZATION HELPER FUNCTIONS
// ============================================================================

/**
 * Create circuit diagram visualization
 * Simplified version using Plotly heatmap (full SVG would be more complex)
 */
function createCircuitDiagram(cellVoltages, moduleState, current, displayOptions) {
    // Reshape cell voltages to 6x18 grid (6 columns, 18 rows)
    const voltageGrid = [];
    for (let row = 0; row < 18; row++) {
        voltageGrid[row] = [];
        for (let col = 0; col < 6; col++) {
            const cellIdx = col * 18 + row;
            voltageGrid[row][col] = cellVoltages[cellIdx];
        }
    }
    
    // Create heatmap
    return {
        data: [{
            z: voltageGrid,
            type: 'heatmap',
            colorscale: [
                [0, 'rgb(165,0,38)'],      // Dark red (negative)
                [0.4, 'rgb(244,109,67)'],  // Orange
                [0.5, 'rgb(253,174,97)'],  // Light orange
                [0.7, 'rgb(254,224,139)'], // Yellow
                [0.9, 'rgb(217,239,139)'], // Light green
                [1, 'rgb(102,189,99)']     // Green (positive)
            ],
            colorbar: {
                title: 'Voltage (V)',
                titleside: 'right'
            },
            showscale: true,
            hovertemplate: 'Col: %{x}<br>Row: %{y}<br>Voltage: %{z:.3f} V<extra></extra>'
        }],
        layout: {
            title: `PV Module Circuit (I = ${current.toFixed(2)} A)`,
            xaxis: {title: 'Column', dtick: 1},
            yaxis: {title: 'Row', dtick: 1, autorange: 'reversed'},
            height: 600,
            margin: {t: 50, b: 50, l: 50, r: 100}
        }
    };
}

/**
 * Create voltage heatmap (WebGL-accelerated)
 */
function createVoltageHeatmap(cellVoltages) {
    // Check if WebGL heatmap renderer is available
    if (typeof window.WebGLHeatmap !== 'undefined' && window.webglVoltageHeatmap) {
        // Use WebGL renderer (GPU-accelerated, 60 FPS)
        window.webglVoltageHeatmap.render(cellVoltages);
        
        // Return placeholder Plotly figure (WebGL renders to canvas separately)
        return {
            data: [],
            layout: {
                title: 'Cell Voltage Distribution (WebGL)',
                annotations: [{
                    text: 'Rendered with WebGL (GPU)',
                    xref: 'paper',
                    yref: 'paper',
                    x: 0.5,
                    y: 0.5,
                    showarrow: false
                }],
                height: 400
            }
        };
    } else {
        // Fallback to Plotly heatmap
        const voltageGrid = [];
        for (let row = 0; row < 18; row++) {
            voltageGrid[row] = [];
            for (let col = 0; col < 6; col++) {
                const cellIdx = col * 18 + row;
                voltageGrid[row][col] = cellVoltages[cellIdx];
            }
        }
        
        return {
            data: [{
                z: voltageGrid,
                type: 'heatmap',
                colorscale: 'RdYlGn',
                reversescale: false,
                colorbar: {title: 'V'},
                hovertemplate: 'Voltage: %{z:.3f} V<extra></extra>'
            }],
            layout: {
                title: 'Cell Voltage Distribution',
                xaxis: {title: 'Column'},
                yaxis: {title: 'Row', autorange: 'reversed'},
                height: 400
            }
        };
    }
}

/**
 * Create power dissipation heatmap (WebGL-accelerated)
 */
function createPowerHeatmap(cellPowers) {
    // Check if WebGL heatmap renderer is available
    if (typeof window.WebGLHeatmap !== 'undefined' && window.webglPowerHeatmap) {
        // Use WebGL renderer (GPU-accelerated, 60 FPS)
        window.webglPowerHeatmap.render(cellPowers);
        
        // Return placeholder Plotly figure
        return {
            data: [],
            layout: {
                title: 'Power Dissipation (WebGL)',
                annotations: [{
                    text: 'Rendered with WebGL (GPU)',
                    xref: 'paper',
                    yref: 'paper',
                    x: 0.5,
                    y: 0.5,
                    showarrow: false
                }],
                height: 400
            }
        };
    } else {
        // Fallback to Plotly heatmap
        const powerGrid = [];
        for (let row = 0; row < 18; row++) {
            powerGrid[row] = [];
            for (let col = 0; col < 6; col++) {
                const cellIdx = col * 18 + row;
                powerGrid[row][col] = cellPowers[cellIdx];
            }
        }
        
        return {
            data: [{
                z: powerGrid,
                type: 'heatmap',
                colorscale: 'Reds',
                colorbar: {title: 'W'},
                hovertemplate: 'Power: %{z:.2f} W<extra></extra>'
            }],
            layout: {
                title: 'Power Dissipation',
                xaxis: {title: 'Column'},
                yaxis: {title: 'Row', autorange: 'reversed'},
                height: 400
            }
        };
    }
}

/**
 * Analyze hotspots (cells in reverse bias dissipating power)
 */
function analyzeHotspots(voltages, powers, current) {
    const hotspots = [];
    const threshold = -0.2; // Voltage threshold for hotspot
    
    for (let i = 0; i < voltages.length; i++) {
        if (voltages[i] < threshold && powers[i] > 0.1) {
            hotspots.push({
                cellIdx: i,
                voltage: voltages[i],
                power: powers[i]
            });
        }
    }
    
    return hotspots;
}

/**
 * Format hotspot info as HTML
 */
function formatHotspotInfo(hotspots) {
    if (hotspots.length === 0) {
        return {
            props: {
                children: '✓ Keine Hot-Spots detektiert',
                className: 'text-success'
            },
            type: 'P',
            namespace: 'dash_html_components'
        };
    }
    
    const totalPower = hotspots.reduce((sum, hs) => sum + hs.power, 0);
    
    return {
        props: {
            children: [
                {
                    props: {
                        children: `⚠️ ${hotspots.length} Hot-Spots erkannt`,
                        className: 'text-danger'
                    },
                    type: 'H5',
                    namespace: 'dash_html_components'
                },
                {
                    props: {
                        children: `Gesamte Hot-Spot-Leistung: ${totalPower.toFixed(1)} W`
                    },
                    type: 'P',
                    namespace: 'dash_html_components'
                }
            ]
        },
        type: 'Div',
        namespace: 'dash_html_components'
    };
}

/**
 * Format operating point info
 */
function formatOperatingPointInfo(moduleState, current, mpp) {
    return {
        props: {
            children: [
                {
                    props: {children: 'Betriebspunkt:'},
                    type: 'Strong',
                    namespace: 'dash_html_components'
                },
                {
                    props: {},  // FIX: Br elements must not have children
                    type: 'Br',
                    namespace: 'dash_html_components'
                },
                {
                    props: {children: `Spannung: ${moduleState.voltage.toFixed(2)} V`},
                    type: 'P',
                    namespace: 'dash_html_components'
                },
                {
                    props: {children: `Strom: ${current.toFixed(2)} A`},
                    type: 'P',
                    namespace: 'dash_html_components'
                },
                {
                    props: {children: `Leistung: ${moduleState.power.toFixed(1)} W`},
                    type: 'P',
                    namespace: 'dash_html_components'
                },
                {
                    props: {children: `Aktive Bypass-Dioden: ${moduleState.numBypassed}/3`},
                    type: 'P',
                    namespace: 'dash_html_components'
                }
            ]
        },
        type: 'Div',
        namespace: 'dash_html_components'
    };
}

/**
 * Format shading intensity info
 */
function formatShadingInfo(percent, intensity, cellShading, current, mpp) {
    const numShaded = cellShading.filter(s => s > 0.01).length;
    
    return {
        props: {
            children: [
                {
                    props: {children: `Verschattungsgrad: ${percent}%`},
                    type: 'Strong',
                    namespace: 'dash_html_components'
                },
                {
                    props: {},  // FIX: Br elements must not have children
                    type: 'Br',
                    namespace: 'dash_html_components'
                },
                {
                    props: {children: `Anzahl verschatteter Zellen: ${numShaded} von 108`},
                    type: 'P',
                    namespace: 'dash_html_components'
                },
                {
                    props: {
                        children: `MPP: ${current.toFixed(2)} A, ${mpp.voltage.toFixed(2)} V, ${mpp.power.toFixed(1)} W`,
                        className: 'text-muted'
                    },
                    type: 'Small',
                    namespace: 'dash_html_components'
                }
            ]
        },
        type: 'Div',
        namespace: 'dash_html_components'
    };
}

// Initialize WebGL heatmap renderers when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if canvas elements exist
    if (document.getElementById('webgl-voltage-canvas')) {
        window.webglVoltageHeatmap = new window.WebGLHeatmap('webgl-voltage-canvas', 600, 1800);
        console.log('[OK] WebGL Voltage Heatmap initialized');
    }
    
    if (document.getElementById('webgl-power-canvas')) {
        window.webglPowerHeatmap = new window.WebGLHeatmap('webgl-power-canvas', 600, 1800);
        console.log('[OK] WebGL Power Heatmap initialized');
    }
});

console.log("[OK] Client-side callbacks module loaded!");


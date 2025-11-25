/**
 * Client-Side LUT Interpolator for Solar Cell I-V Characteristics
 * 
 * Performs fast 4D linear interpolation on pre-computed Look-up Table
 * enabling instant visualization updates without server round-trips.
 * 
 * Performance: ~0.01ms per interpolation (vs. 3-4ms server-side scipy)
 * 
 * @author PV Module Shading Analyzer
 * @version 1.0.0
 */

// ============================================================================
// 4D LINEAR INTERPOLATION ENGINE
// ============================================================================

class LUTInterpolator {
    constructor(lutData) {
        console.log("[LUT] Initializing client-side interpolator...");
        
        // Store grid arrays
        this.irrGrid = lutData.irradiance;
        this.tempGrid = lutData.temperature;
        this.shadeGrid = lutData.shading;
        this.currentGrid = lutData.current;
        
        // Store 4D voltage LUT
        // Shape: [irr, temp, shade, current]
        this.lut = lutData.voltage_lut;
        
        // Pre-compute grid sizes for faster indexing
        this.ni = this.irrGrid.length;
        this.nj = this.tempGrid.length;
        this.nk = this.shadeGrid.length;
        this.nm = this.currentGrid.length;
        
        console.log(`[LUT] Grid loaded: ${this.ni}×${this.nj}×${this.nk}×${this.nm} = ${this.ni*this.nj*this.nk*this.nm} points`);
        console.log("[OK] LUT interpolator ready!");
    }
    
    /**
     * Find index and weight for 1D linear interpolation
     * 
     * @param {number} value - Target value
     * @param {Array<number>} grid - Grid array
     * @returns {{idx: number, weight: number}} - Index and interpolation weight
     */
    findIndexAndWeight(value, grid) {
        const n = grid.length;
        
        // Clamp value to grid bounds
        if (value <= grid[0]) return {idx: 0, weight: 0.0};
        if (value >= grid[n-1]) return {idx: n-2, weight: 1.0};
        
        // Binary search for the correct interval
        let left = 0;
        let right = n - 1;
        
        while (right - left > 1) {
            const mid = Math.floor((left + right) / 2);
            if (grid[mid] <= value) {
                left = mid;
            } else {
                right = mid;
            }
        }
        
        // Linear interpolation weight
        const idx = left;
        const weight = (value - grid[idx]) / (grid[idx + 1] - grid[idx]);
        
        return {idx, weight};
    }
    
    /**
     * Perform 4D linear interpolation on the LUT
     * 
     * @param {number} irradiance - Irradiance in W/m² (200-1000)
     * @param {number} temperature - Temperature in °C (-20 to 90)
     * @param {number} shading - Shading factor (0.0 to 1.0)
     * @param {number} current - Current in A (0 to 15)
     * @returns {number} - Interpolated voltage in V
     */
    interpolate(irradiance, temperature, shading, current) {
        // Find indices and weights for each dimension
        const {idx: i0, weight: wi} = this.findIndexAndWeight(irradiance, this.irrGrid);
        const {idx: j0, weight: wj} = this.findIndexAndWeight(temperature, this.tempGrid);
        const {idx: k0, weight: wk} = this.findIndexAndWeight(shading, this.shadeGrid);
        const {idx: m0, weight: wm} = this.findIndexAndWeight(current, this.currentGrid);
        
        const i1 = Math.min(i0 + 1, this.ni - 1);
        const j1 = Math.min(j0 + 1, this.nj - 1);
        const k1 = Math.min(k0 + 1, this.nk - 1);
        const m1 = Math.min(m0 + 1, this.nm - 1);
        
        // Perform 4D linear interpolation (16 corners of hypercube)
        // V(i,j,k,m) = ∑ V[corners] × weights
        
        // Helper function to get LUT value
        const getLUT = (i, j, k, m) => {
            const idx = i * (this.nj * this.nk * this.nm) + 
                        j * (this.nk * this.nm) + 
                        k * this.nm + 
                        m;
            return this.lut[idx];
        };
        
        // Interpolate along current dimension (m) first
        const v0000 = getLUT(i0, j0, k0, m0);
        const v0001 = getLUT(i0, j0, k0, m1);
        const v0010 = getLUT(i0, j0, k1, m0);
        const v0011 = getLUT(i0, j0, k1, m1);
        const v0100 = getLUT(i0, j1, k0, m0);
        const v0101 = getLUT(i0, j1, k0, m1);
        const v0110 = getLUT(i0, j1, k1, m0);
        const v0111 = getLUT(i0, j1, k1, m1);
        const v1000 = getLUT(i1, j0, k0, m0);
        const v1001 = getLUT(i1, j0, k0, m1);
        const v1010 = getLUT(i1, j0, k1, m0);
        const v1011 = getLUT(i1, j0, k1, m1);
        const v1100 = getLUT(i1, j1, k0, m0);
        const v1101 = getLUT(i1, j1, k0, m1);
        const v1110 = getLUT(i1, j1, k1, m0);
        const v1111 = getLUT(i1, j1, k1, m1);
        
        // Interpolate along m
        const v000 = v0000 * (1 - wm) + v0001 * wm;
        const v001 = v0010 * (1 - wm) + v0011 * wm;
        const v010 = v0100 * (1 - wm) + v0101 * wm;
        const v011 = v0110 * (1 - wm) + v0111 * wm;
        const v100 = v1000 * (1 - wm) + v1001 * wm;
        const v101 = v1010 * (1 - wm) + v1011 * wm;
        const v110 = v1100 * (1 - wm) + v1101 * wm;
        const v111 = v1110 * (1 - wm) + v1111 * wm;
        
        // Interpolate along k
        const v00 = v000 * (1 - wk) + v001 * wk;
        const v01 = v010 * (1 - wk) + v011 * wk;
        const v10 = v100 * (1 - wk) + v101 * wk;
        const v11 = v110 * (1 - wk) + v111 * wk;
        
        // Interpolate along j
        const v0 = v00 * (1 - wj) + v01 * wj;
        const v1 = v10 * (1 - wj) + v11 * wj;
        
        // Interpolate along i
        const voltage = v0 * (1 - wi) + v1 * wi;
        
        return voltage;
    }
    
    /**
     * Batch interpolation for multiple currents (for I-V curves)
     * 
     * @param {number} irradiance
     * @param {number} temperature
     * @param {number} shading
     * @param {Array<number>} currents - Array of current values
     * @returns {Array<number>} - Array of voltages
     */
    interpolateBatch(irradiance, temperature, shading, currents) {
        return currents.map(current => 
            this.interpolate(irradiance, temperature, shading, current)
        );
    }
}


// ============================================================================
// SOLAR CELL & MODULE PHYSICS (Client-Side)
// ============================================================================

class ClientSideCell {
    constructor(irradiance, temperature, shadingFactor, interpolator) {
        this.irradiance = irradiance;
        this.temperature = temperature;
        this.shadingFactor = shadingFactor;
        this.interpolator = interpolator;
    }
    
    /**
     * Find voltage for a given current using LUT interpolation
     */
    findVoltage(current) {
        return this.interpolator.interpolate(
            this.irradiance,
            this.temperature,
            this.shadingFactor,
            current
        );
    }
    
    /**
     * Get I-V curve data
     */
    getIVCurve(numPoints = 30) {
        const currents = [];
        const voltages = [];
        
        const maxCurrent = 15.0;
        for (let i = 0; i <= numPoints; i++) {
            const current = (maxCurrent * i) / numPoints;
            const voltage = this.findVoltage(current);
            currents.push(current);
            voltages.push(voltage);
        }
        
        return {currents, voltages};
    }
}


class ClientSideString {
    constructor(cells, bypassThreshold = -0.5) {
        this.cells = cells;
        this.bypassThreshold = bypassThreshold;
    }
    
    /**
     * Calculate string voltage at given current
     */
    calculateVoltage(current) {
        let totalVoltage = 0;
        let rawVoltage = 0;
        let isBypassed = false;
        
        for (const cell of this.cells) {
            const cellVoltage = cell.findVoltage(current);
            rawVoltage += cellVoltage;
            
            // Check if cell should be bypassed
            if (cellVoltage < this.bypassThreshold) {
                isBypassed = true;
                // Bypass diode activated (Schottky: ~0.3V drop)
                totalVoltage += 0.3;
            } else {
                totalVoltage += cellVoltage;
            }
        }
        
        return {
            voltage: totalVoltage,
            rawVoltage: rawVoltage,
            isBypassed: isBypassed
        };
    }
}


class ClientSideModule {
    constructor(strings) {
        this.strings = strings;
    }
    
    /**
     * Calculate module voltage at given current
     */
    calculateVoltage(current) {
        let totalVoltage = 0;
        let numBypassed = 0;
        const stringDetails = [];
        
        for (const string of this.strings) {
            const result = string.calculateVoltage(current);
            totalVoltage += result.voltage;
            if (result.isBypassed) numBypassed++;
            stringDetails.push(result);
        }
        
        return {
            voltage: totalVoltage,
            current: current,
            power: totalVoltage * current,
            numBypassed: numBypassed,
            stringDetails: stringDetails
        };
    }
    
    /**
     * Find Maximum Power Point using simple search
     */
    findMPP(numPoints = 30) {
        let maxPower = 0;
        let mppCurrent = 0;
        let mppVoltage = 0;
        
        const maxCurrent = 15.0;
        for (let i = 0; i <= numPoints; i++) {
            const current = (maxCurrent * i) / numPoints;
            const result = this.calculateVoltage(current);
            
            if (result.power > maxPower) {
                maxPower = result.power;
                mppCurrent = current;
                mppVoltage = result.voltage;
            }
        }
        
        return {
            current: mppCurrent,
            voltage: mppVoltage,
            power: maxPower
        };
    }
}


// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Convert shading scenario to cell configuration
 */
function applyShadingScenario(scenarioId, intensity, interpolator, irradiance, temperature) {
    // Default: 3 strings × 36 cells = 108 total cells
    const cellsPerString = 36;
    const numStrings = 3;
    
    // Create cells for each string
    const strings = [];
    
    for (let s = 0; s < numStrings; s++) {
        const cells = [];
        
        for (let c = 0; c < cellsPerString; c++) {
            let shadingFactor = 0.0;
            
            // Apply shading based on scenario
            // This is a simplified version - full logic would match Python scenarios
            if (scenarioId === 'single_cell') {
                // Shade one cell in first string
                if (s === 0 && c === 17) shadingFactor = intensity;
            } else if (scenarioId === 'partial_string') {
                // Shade bottom third of first string
                if (s === 0 && c >= 24) shadingFactor = intensity;
            } else if (scenarioId === 'full_string') {
                // Shade entire first string
                if (s === 0) shadingFactor = intensity;
            } else if (scenarioId === 'diagonal') {
                // Diagonal shading pattern
                const cellRow = Math.floor(c / 2); // 18 rows
                const cellCol = (c % 2) + s * 2; // 6 columns
                if (cellRow >= cellCol * 3) shadingFactor = intensity;
            } else if (scenarioId === 'mixed') {
                // Mixed shading
                if (s === 0 && c >= 18) shadingFactor = intensity;
                if (s === 1 && c >= 27) shadingFactor = intensity * 0.5;
            }
            
            const cell = new ClientSideCell(irradiance, temperature, shadingFactor, interpolator);
            cells.push(cell);
        }
        
        const string = new ClientSideString(cells);
        strings.push(string);
    }
    
    return new ClientSideModule(strings);
}


/**
 * Format voltage for display
 */
function formatVoltage(v) {
    if (Math.abs(v) < 0.01) return '0.00 V';
    return v.toFixed(2) + ' V';
}

/**
 * Format current for display
 */
function formatCurrent(i) {
    if (Math.abs(i) < 0.01) return '0.00 A';
    return i.toFixed(2) + ' A';
}

/**
 * Format power for display
 */
function formatPower(p) {
    if (Math.abs(p) < 0.1) return '0.0 W';
    return p.toFixed(1) + ' W';
}


// Export for use in Dash clientside callbacks
if (typeof window !== 'undefined') {
    window.LUTInterpolator = LUTInterpolator;
    window.ClientSideModule = ClientSideModule;
    window.applyShadingScenario = applyShadingScenario;
    window.formatVoltage = formatVoltage;
    window.formatCurrent = formatCurrent;
    window.formatPower = formatPower;
    
    console.log("[OK] LUT Interpolator module loaded!");
}


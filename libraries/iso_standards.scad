// =================================================================
// ISO STANDARDS LIBRARY FOR OPENSCAD
// Optimized for AI code generation and automated engineering
// =================================================================

// =================================================================
// SECTION 1: DATABASE (The Arrays)
// =================================================================

// ISO 273: [Nominal, Fine(H12), Medium(H13), Coarse(H14)]
ISO_273_DATA = [
    [1.6, 1.7, 1.8, 2.0], [2, 2.2, 2.4, 2.6], [2.5, 2.7, 2.9, 3.1],
    [3, 3.2, 3.4, 3.6], [4, 4.3, 4.5, 4.8], [5, 5.3, 5.5, 5.8],
    [6, 6.4, 6.6, 7.0], [8, 8.4, 9.0, 10.0], [10, 10.5, 11.0, 12.0],
    [12, 13.0, 13.5, 14.5], [16, 17.0, 17.5, 18.5], [20, 21.0, 22.0, 24.0]
];

// ISO 4762 SHCS: [Nominal, Head_Dia(dk), Head_Height(k), Hex_Size(s)]
ISO_4762_DATA = [
    [1.6, 3.0, 1.6, 1.5], [2, 3.8, 2.0, 1.5], [2.5, 4.5, 2.5, 2.0],
    [3, 5.5, 3.0, 2.5], [4, 7.0, 4.0, 3.0], [5, 8.5, 5.0, 4.0],
    [6, 10.0, 6.0, 5.0], [8, 13.0, 8.0, 6.0], [10, 16.0, 10.0, 8.0],
    [12, 18.0, 12.0, 10.0], [16, 24.0, 16.0, 14.0], [20, 30.0, 20.0, 17.0]
];

// ISO 7380 Button Head: [Nominal, Head_Dia(dk), Head_Height(k)]
ISO_7380_DATA = [
    [3, 5.7, 1.65], [4, 7.6, 2.2], [5, 9.5, 2.75], 
    [6, 10.5, 3.3], [8, 14.0, 4.4], [10, 17.5, 5.5], [12, 21.0, 6.6]
];

// ISO 4032 Nut: [Nominal, Width_Across_Flats(s), Height(m)]
ISO_4032_DATA = [
    [1.6, 3.2, 1.3], [2, 4.0, 1.6], [2.5, 5.0, 2.0],
    [3, 5.5, 2.4], [4, 7.0, 3.2], [5, 8.0, 4.7],
    [6, 10.0, 5.2], [8, 13.0, 6.8], [10, 16.0, 8.4],
    [12, 18.0, 10.8], [16, 24.0, 14.8], [20, 30.0, 18.0]
];

// DIN 985 Nyloc Nut (Taller than standard): [Nominal, s, Height(m)]
DIN_985_DATA = [
    [3, 5.5, 4.0], [4, 7.0, 5.0], [5, 8.0, 5.0], 
    [6, 10.0, 6.0], [8, 13.0, 8.0], [10, 16.0, 10.0], [12, 18.0, 12.0]
];

// ISO 7046 Countersunk: [Nominal, Head_Dia(dk)_Max, Head_Height(k)_Max]
ISO_7046_DATA = [
    [2, 3.8, 1.2], [2.5, 4.7, 1.5], [3, 5.5, 1.65],
    [4, 8.4, 2.7], [5, 9.3, 2.7],   [6, 11.3, 3.3],
    [8, 15.8, 4.65], [10, 18.3, 5.0]
];

// ISO 7093 Fender Washer: [Nominal_Bolt, Inside_Dia, Outside_Dia, Thickness]
ISO_7093_DATA = [
    [3, 3.2, 9, 0.8], [4, 4.3, 12, 1.0], [5, 5.3, 15, 1.2], 
    [6, 6.4, 18, 1.6], [8, 8.4, 24, 2.0], [10, 10.5, 30, 2.5]
];

// ISO 262 Metric Coarse Threads: [Nominal, Pitch, Tap_Drill_Dia]
ISO_262_TAP_DATA = [
    [1.6, 0.35, 1.25], [2, 0.4, 1.6], [2.5, 0.45, 2.05],
    [3, 0.5, 2.5], [4, 0.7, 3.3], [5, 0.8, 4.2],
    [6, 1.0, 5.0], [8, 1.25, 6.8], [10, 1.5, 8.5],
    [12, 1.75, 10.2], [16, 2.0, 14.0], [20, 2.5, 17.5]
];

// ISO 15 Rolling Bearings (6000 Series): [Nominal_ID, Inside, Outside, Width]
BEARING_6000_DATA = [
    [608, 8, 22, 7], [6000, 10, 26, 8], [6001, 12, 28, 8], 
    [6002, 15, 32, 9], [6003, 17, 35, 10], [6004, 20, 42, 12]
];

// =================================================================
// SECTION 2: LOGIC (Fixed Index-Based Search)
// =================================================================

// Helper to find the row index for a specific diameter/type
function _find_row(key, data) = search([key], data)[0];

function iso273_hole(d, fit="medium") = 
    let(row = _find_row(d, ISO_273_DATA))
    let(col = (fit=="fine" ? 1 : (fit=="coarse" ? 3 : 2)))
    ISO_273_DATA[row][col];

function iso4762_head_dia(d)    = ISO_4762_DATA[_find_row(d, ISO_4762_DATA)][1];
function iso4762_head_height(d) = ISO_4762_DATA[_find_row(d, ISO_4762_DATA)][2];

function iso7380_head_dia(d)    = ISO_7380_DATA[_find_row(d, ISO_7380_DATA)][1];
function iso7380_head_height(d) = ISO_7380_DATA[_find_row(d, ISO_7380_DATA)][2];

function iso4032_nut_width(d)   = ISO_4032_DATA[_find_row(d, ISO_4032_DATA)][1];
function iso4032_nut_height(d)  = ISO_4032_DATA[_find_row(d, ISO_4032_DATA)][2];

function din985_nut_width(d)    = DIN_985_DATA[_find_row(d, DIN_985_DATA)][1];
function din985_nut_height(d)   = DIN_985_DATA[_find_row(d, DIN_985_DATA)][2];

function iso7046_head_dia(d)    = ISO_7046_DATA[_find_row(d, ISO_7046_DATA)][1];
function iso7046_head_height(d) = ISO_7046_DATA[_find_row(d, ISO_7046_DATA)][2];

function iso7093_fender_dia(d)  = ISO_7093_DATA[_find_row(d, ISO_7093_DATA)][2];
function iso7093_thickness(d)   = ISO_7093_DATA[_find_row(d, ISO_7093_DATA)][3];

function iso262_tap_drill(d)    = ISO_262_TAP_DATA[_find_row(d, ISO_262_TAP_DATA)][2];

function bearing_od(type)       = BEARING_6000_DATA[_find_row(type, BEARING_6000_DATA)][2];
function bearing_width(type)    = BEARING_6000_DATA[_find_row(type, BEARING_6000_DATA)][3];

// =================================================================
// SECTION 3: UTILITY MODULES (Physical Implementation - PRECISION TOP-DOWN)
// =================================================================

// 1. SIMPLE CLEARANCE HOLE
module iso_273_clearance(d, h, fit="medium") {
    h_dia = iso273_hole(d, fit);
    // Entry point: +0.5mm above surface to ensure clean cut
    // Total height: h + 0.5 to keep the 'tip' exactly at h depth
    translate([0, 0, 0.5]) 
        mirror([0,0,1]) cylinder(d = h_dia, h = h + 0.5, center = false, $fn = 64);
}

// 2. SOCKET HEAD CAP SCREW (ISO 4762)
module hole_socket_head(d, h_total, fit="medium", extra_depth=0) {
    h_dia = iso273_hole(d, fit);
    dk = iso4762_head_dia(d);
    k = iso4762_head_height(d);
    union() {
        // Main Shaft (The hole)
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d = h_dia, h = h_total + 0.5, center = false, $fn = 64);
        // Head Recess
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d = dk, h = k + extra_depth + 0.5, $fn = 64);
    }
}

// 3. BUTTON HEAD SCREW (ISO 7380)
module hole_button_head(d, h_total, fit="medium", extra_depth=0) {
    h_dia = iso273_hole(d, fit);
    dk = iso7380_head_dia(d);
    k = iso7380_head_height(d);
    union() {
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d = h_dia, h = h_total + 0.5, center = false, $fn = 64);
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d = dk, h = k + extra_depth + 0.5, $fn = 64);
    }
}

// 4. COUNTERSUNK SCREW (ISO 7046)
module hole_countersunk(d, h_total, fit="medium") {
    h_dia = iso273_hole(d, fit);
    dk = iso7046_head_dia(d);
    k = iso7046_head_height(d);
    union() {
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d = h_dia, h = h_total + 0.5, center = false, $fn = 64);
        translate([0, 0, 0.5]) 
            mirror([0,0,1]) cylinder(d1 = dk, d2 = h_dia, h = k + 0.5, $fn = 64);
    }
}

// 5. HEX NUT TRAP
module hole_nut_trap(d, depth_extra=0, nyloc=false) {
    s = nyloc ? din985_nut_width(d) : iso4032_nut_width(d);
    m = nyloc ? din985_nut_height(d) : iso4032_nut_height(d);
    translate([0,0,0.5])
        mirror([0,0,1]) rotate([0, 0, 30]) 
            cylinder(d = s / cos(30), h = m + depth_extra + 0.5, $fn = 6);
}

// 6. FENDER WASHER RECESS
module hole_fender_washer(d, depth_extra=0) {
    dw = iso7093_fender_dia(d);
    hw = iso7093_thickness(d);
    translate([0,0,0.5])
        mirror([0,0,1]) cylinder(d = dw, h = hw + depth_extra + 0.5, $fn = 64);
}

// 7. THREADED TAP DRILL
module hole_threaded_tap(d, h_total) {
    drill_dia = iso262_tap_drill(d);
    translate([0, 0, 0.5]) 
        mirror([0,0,1]) cylinder(d = drill_dia, h = h_total + 0.5, center = false, $fn = 64);
}

// 8. BEARING HOUSING
module bearing_housing(type, depth_extra=0, clearance_3dp=0.15) {
    od = bearing_od(type);
    w = bearing_width(type);
    translate([0,0,0.5])
        mirror([0,0,1]) cylinder(d = od + (clearance_3dp * 2), h = w + depth_extra + 0.5, $fn = 120);
}
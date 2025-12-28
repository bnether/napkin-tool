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

// ISO 4032 Nut: [Nominal, Width_Across_Flats(s), Height(m)]
ISO_4032_DATA = [
    [1.6, 3.2, 1.3], [2, 4.0, 1.6], [2.5, 5.0, 2.0],
    [3, 5.5, 2.4], [4, 7.0, 3.2], [5, 8.0, 4.7],
    [6, 10.0, 5.2], [8, 13.0, 6.8], [10, 16.0, 8.4],
    [12, 18.0, 10.8], [16, 24.0, 14.8], [20, 30.0, 18.0]
];

// ISO 7046 Countersunk: [Nominal, Head_Dia(dk)_Max, Head_Height(k)_Max]
ISO_7046_DATA = [
    [2, 3.8, 1.2], [2.5, 4.7, 1.5], [3, 5.5, 1.65],
    [4, 8.4, 2.7], [5, 9.3, 2.7],   [6, 11.3, 3.3],
    [8, 15.8, 4.65], [10, 18.3, 5.0]
];

// ISO 7089 Washer: [Nominal_Bolt, Inside_Dia(d1), Outside_Dia(d2), Thickness(h)]
ISO_7089_DATA = [
    [3, 3.2, 7, 0.5], [4, 4.3, 9, 0.8], [5, 5.3, 10, 1.0],
    [6, 6.4, 12, 1.6], [8, 8.4, 16, 1.6], [10, 10.5, 20, 2.0],
    [12, 13, 24, 2.5], [16, 17, 30, 3.0], [20, 21, 37, 3.0]
];

// =================================================================
// SECTION 2: LOGIC (Getter Functions)
// =================================================================

function iso273_hole(d, fit="medium") = 
    let(col = (fit=="fine" ? 1 : (fit=="coarse" ? 3 : 2)))
    lookup(d, ISO_273_DATA, col);

function iso4762_head_dia(d)    = lookup(d, ISO_4762_DATA, 1);
function iso4762_head_height(d) = lookup(d, ISO_4762_DATA, 2);
function iso4762_hex_key(d)     = lookup(d, ISO_4762_DATA, 3);

function iso4032_nut_width(d)   = lookup(d, ISO_4032_DATA, 1);
function iso4032_nut_height(d)  = lookup(d, ISO_4032_DATA, 2);

function iso7046_head_dia(d)    = lookup(d, ISO_7046_DATA, 1);
function iso7046_head_height(d) = lookup(d, ISO_7046_DATA, 2);

function iso7089_outer_dia(d)   = lookup(d, ISO_7089_DATA, 2);
function iso7089_thickness(d)   = lookup(d, ISO_7089_DATA, 3);

// =================================================================
// SECTION 3: UTILITY MODULES (Physical Implementation)
// =================================================================

// SOCKET HEAD COUNTERBORE (ISO 4762 + ISO 273)
module hole_socket_head(d, h_total, fit="medium", extra_depth=0) {
    h_dia = iso273_hole(d, fit);
    dk = iso4762_head_dia(d);
    k = iso4762_head_height(d);
    union() {
        cylinder(d = h_dia, h = h_total * 3, center = true, $fn = 32);
        translate([0, 0, -0.01]) 
            cylinder(d = dk, h = k + extra_depth, $fn = 32);
    }
}

// COUNTERSINK HOLE (ISO 7046 + ISO 273)
module hole_countersunk(d, h_total, fit="medium") {
    h_dia = iso273_hole(d, fit);
    dk = iso7046_head_dia(d);
    k = iso7046_head_height(d);
    union() {
        cylinder(d = h_dia, h = h_total * 3, center = true, $fn = 32);
        translate([0, 0, -0.01])
            cylinder(d1 = dk, d2 = h_dia, h = k, $fn = 32);
    }
}

// NUT TRAP (ISO 4032)
module hole_nut_trap(d, depth_extra=0) {
    s = iso4032_nut_width(d);
    m = iso4032_nut_height(d);
    rotate([0, 0, 30])
        cylinder(d = s / cos(30), h = m + depth_extra, $fn = 6);
}

/* ===========================================================
[USER PROMPT]: "50mm cube, with an M8 clearance hole through the centre"
[DECODED LOGIC]: Boolean Difference. Uses 'iso_standards.scad' for ISO 273 Medium fit. 
Logic: Center cube at origin. Subtract centered iso_273_clearance(8).
[RESULT CODE]:
include <libraries/iso_standards.scad>;

// Note: High resolution for printable standard holes
$fn = 64;

difference() {
    // 1. The main body
    cube(50, center = true);
    
    // 2. ISO 273 Standard Clearance Hole
    // M8 Medium fit results in a 9.0mm diameter via the library lookup
    iso_273_clearance(8, 60); 
}
=========================================================== */
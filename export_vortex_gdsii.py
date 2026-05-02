import os
import gdspy

def export():
    os.makedirs('layouts', exist_ok=True)
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell('VORTEX_ARRAY')

    # Dummy vortex array
    pitch = 1.0
    for i in range(10):
        for j in range(10):
            circle = gdspy.Round((i*pitch, j*pitch), 0.15, layer=1)
            cell.add(circle)

    # Add alignment marks
    mark = gdspy.Rectangle((-5, -5), (0, 0), layer=2)
    cell.add(mark)

    lib.write_gds('layouts/vortex_array_v340.2.gds')

    print("🔧 Generating GDSII layout: layouts/vortex_array_v340.2.gds")
    print("✓ GDSII layout saved: layouts/vortex_array_v340.2.gds")

if __name__ == '__main__':
    export()

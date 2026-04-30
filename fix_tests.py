# Fix relative imports for tests by putting them in scripts package correctly or adding to PYTHONPATH
# We already did PYTHONPATH=scripts:. but let's make tests load modules by module name robustly
# or just remove the dummy test files we made since they are duplicating the run_validation block

import os

for tf in ["tests/test_arkhe_neuromorphic_autopoiesis_embodied_v97.py", "tests/test_arkhe_autopoiesis_multiversal_v98.py", "tests/test_arkhe_neuromorphic_embodied_v96.py"]:
    if os.path.exists(tf):
        os.remove(tf)

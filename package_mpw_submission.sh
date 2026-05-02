#!/bin/bash
echo "Packaging MPW submission v∞.340.3..."

./run_validation_suite.sh
python analyze_validation_results.py
python export_to_lumerical.py
python export_to_meep.py
python export_vortex_gdsii.py
./validate_drc.py

echo "Creating package directory..."
mkdir -p mpw_submission_v340.3/layouts mpw_submission_v340.3/docs mpw_submission_v340.3/exports

cp layouts/vortex_array_v340.2.gds mpw_submission_v340.3/layouts/
cp reports/fabrication_specification_v340.2.json mpw_submission_v340.3/docs/
cp exports/vortex_index_profile.npy mpw_submission_v340.3/exports/
cp exports/meep/simulation_config.json mpw_submission_v340.3/exports/
cp docs/experimental_setup_v340.3.md mpw_submission_v340.3/docs/

echo "MPW Submission package ready at mpw_submission_v340.3/"

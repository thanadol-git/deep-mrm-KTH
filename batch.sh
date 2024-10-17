#!/bin/bash
# Directory containing .mzML files
MZML_DIR="./sample_data/Andrea"
# Directory containing target files (CSV)
TARGET_DIR="./sample_data/Andrea"
# Target file (assuming it’s the same for all .mzML files)
TARGET_FILE="$TARGET_DIR/Transitions-ApoEdge.csv"
# Calculate half of the available cores (rounded down)
TOTAL_CORES=$(nproc)
#CORES=$((TOTAL_CORES / 2))
CORES=1
# Ensure at least one core is used
if [ $CORES -lt 1 ]; then
    CORES=1
fi
# Function to process a single .mzML file
process_mzml() {
    mzml_file="$1"
    python deepmrm/predict/make_prediction.py -target "$TARGET_FILE" -input "$mzml_file"
    echo "Prediction completed for $mzml_file"
}
# Export the function so it’s available to parallel
export -f process_mzml
# Export the TARGET_FILE variable so it’s available in the parallel execution environment
export TARGET_FILE
# Run the command in parallel for all .mzML files in the directory
find "$MZML_DIR" -name "*.mzML" | parallel -j "$CORES" process_mzml
#echo “All predictions have been completed for all .mzML files using $CORES out of $TOTAL_CORES cores.”
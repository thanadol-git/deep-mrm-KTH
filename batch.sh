#!/bin/bash
# Directory containing .mzML files
MZML_DIR="./2024 Khue temp"
# Directory containing target files is same as mzmldir
TARGET_DIR=$MZML_DIR

# Target file (assuming it’s the same for all .mzML files)
TARGET_FILE="$TARGET_DIR/Vebios_ComplemEdge_deepmrm_20241108.csv"
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
# Run the command in parallel for all .mzML files in the directory by sorting the file names
# and passing them to parallel
find "$MZML_DIR" -name "*.mzML" | sort | parallel -j "$CORES" process_mzml

# find "$MZML_DIR" -name "*.mzML" | parallel -j "$CORES" process_mzml

# Inform the user that all predictions have been completed after the last mzml 
# file has been processed
echo "All predictions completed"
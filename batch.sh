#!/bin/bash

# Default values
CORES=1
MZML_DIR=""
TARGET_FILE=""

# Parse command-line options
while getopts "c:t:i:" opt; do
  case $opt in
    c)
      CORES=$OPTARG
      ;;
    t)
      TARGET_FILE=$OPTARG
      ;;
    i)
      MZML_DIR=$OPTARG
      ;;
    *)
      echo "Usage: $0 [-c number_of_cores] [-t target_file] [-i input_directory]"
      exit 1
      ;;
  esac
done

# Ensure at least one core is used
if [ $CORES -lt 1 ]; then
    CORES=1
fi

# Ensure target file and input directory are provided
if [ -z "$TARGET_FILE" ] || [ -z "$MZML_DIR" ]; then
  echo "Both target file and input directory must be specified."
  echo "Usage: $0 [-c number_of_cores] [-t target_file] [-i input_directory]"
  exit 1
fi

# Initialize the counter
PROCESSED_COUNT=0

# Function to process a single .mzML file
process_mzml() {
    mzml_file="$1"
    python deepmrm/predict/make_prediction.py -target "$TARGET_FILE" -input "$mzml_file"
    echo "Prediction completed for $mzml_file"
    ((PROCESSED_COUNT++))
}

# Export the function and variables so they are available to parallel
export -f process_mzml
export TARGET_FILE
export -n PROCESSED_COUNT

# Run the command in parallel for all .mzML files in the directory
find "$MZML_DIR" -name "*.mzML" | parallel -j "$CORES" process_mzml

# Inform the user that all predictions have been completed
echo "All predictions completed"
echo "Total number of files processed: $PROCESSED_COUNT"


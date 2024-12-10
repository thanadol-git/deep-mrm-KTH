import os
import sys
import pandas as pd

def list_and_group_csv_files(directory):
    try:
        # List all files in the given directory
        files = os.listdir(directory)
        # Filter and sort files
        csv_files = sorted([file for file in files if file.endswith('.csv') and 'DeepMRM' in file])
        
        # Group files into 'top1' and 'not top1'
        top1_files = [file for file in csv_files if 'top1' in file]
        not_top1_files = [file for file in csv_files if 'top1' not in file]
        
        return top1_files, not_top1_files

    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
        return [], []
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")
        return [], []

def concat_csv_files(files, input_directory, output_dir, output_filename):
    # List to hold dataframes
    dataframes = []
    
    # Read each file, add 'File_Name' column, and append to the list
    for file in files:
        file_path = os.path.join(input_directory, file)
        df = pd.read_csv(file_path)
        df['File_Name'] = file
        dataframes.append(df)
    
    # Concatenate all dataframes
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    
    # Save the concatenated dataframe to the output file and write into the output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, output_filename)
    concatenated_df.to_csv(output_file_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python concat.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    
    top1_files, not_top1_files = list_and_group_csv_files(input_directory)
    
    if top1_files:
        concat_csv_files(top1_files, input_directory, output_directory, 'top1.csv')
        print(f"Concatenated 'top1' CSV file saved to {os.path.join(output_directory, 'top1.csv')}")
    else:
        print("No 'top1' files found to concatenate.")
    
    if not_top1_files:
        concat_csv_files(not_top1_files, input_directory, output_directory, 'all.csv')
        print(f"Concatenated 'all' CSV file saved to {os.path.join(output_directory, 'all.csv')}")
    else:
        print("No 'not top1' files found to concatenate.")
import pandas as pd
import os
import sys
import traceback

def parse_ct_file(filepath):
    """Parse CT file and return DataFrame with structural information"""
    data = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.strip() == "" or line[0].isalpha():
                continue
            parts = line.strip().split()
            # Check if the parts list has enough elements and if the relevant parts are integers
            if len(parts) >= 6 and all(part.isdigit() or (part[0] == '-' and part[1:].isdigit()) for part in [parts[0], parts[2], parts[3], parts[4], parts[5]]):
                try:
                    row = {
                        "Index": int(parts[0]),
                        "Base": parts[1],
                        "Prev": int(parts[2]),
                        "Next": int(parts[3]),
                        "Pair": int(parts[4]),
                        "ID": int(parts[5])
                    }
                    data.append(row)
                except ValueError:
                    print(f"Skipping line due to non-integer value: {line.strip()}")
                    continue
            else:
                print(f"Skipping line due to incorrect format: {line.strip()}")
    return pd.DataFrame(data)

def get_structure_line(dot_filepath):
    """Extract structure line from DOT file"""
    if os.path.exists(dot_filepath) and dot_filepath.endswith('.dot'):
        with open(dot_filepath, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped and all(c in '().' for c in stripped):
                    return stripped
    return ""

def process_files(ct_filepath, dot_filepath):
    """Main processing function"""
    try:
        # Process the .ct file
        df = parse_ct_file(ct_filepath)
        if df.empty:
            print(f"Warning: DataFrame for {ct_filepath} is empty.")
            return None

        # Get the structure line from the .dot file
        structure_line = get_structure_line(dot_filepath)
        
        # Assign structure_line to the 'Unwanted' column
        df['Unwanted'] = structure_line if structure_line else ""

        # Correctly assign values to the 'Fold' column
        if 'Unwanted' in df.columns and len(df['Unwanted'].iloc[0]) >= len(df):
            for i in range(len(df)):
                df.loc[i, 'Fold'] = df['Unwanted'].iloc[0][i]
        else:
            df['Fold'] = ''
        
        # Initialize Fold_Letter column
        df['Fold_Letter'] = 'X'
        
        # Initialize Strand columns
        df.loc[:, 'StrandPlusOne'] = df['Base'].shift(-1).fillna('N')
        df.loc[:, 'StrandMinusOne'] = df['Base'].shift(1).fillna('N')
        df.loc[:, 'StrandPlusTwo'] = df['Base'].shift(-2).fillna('N')
        df.loc[:, 'StrandMinusTwo'] = df['Base'].shift(2).fillna('N')
        df.loc[:, 'StrandPlusThree'] = df['Base'].shift(-3).fillna('N')
        df.loc[:, 'StrandMinusThree'] = df['Base'].shift(3).fillna('N')

        # Initialize Cross columns with 'N'
        for col in ['CrossPlusOne', 'CrossMinusOne', 'CrossPlusTwo', 'CrossMinusTwo', 'CrossStrand', 'CrossPlusThree', 'CrossMinusThree']:
            df[col] = 'N'

        # Initialize forward and backward based on 'Fold_Letter'
        forward = 0
        backward = len(df) - 1

        # Find the index of the last open bracket and first closed bracket
        last_open_bracket = df[df['Fold'] == '('].index.max() if '(' in df['Fold'].values else -1
        first_closed_bracket = df[df['Fold'] == ')'].index.min() if ')' in df['Fold'].values else len(df)

        # Calculate Cross columns based on 'Fold' and 'Fold_Letter'
        while forward <= backward:
            if df.loc[forward, 'Fold'] == '(' and df.loc[backward, 'Fold'] == ')' and forward > 2 and backward < len(df)-2:
                df.loc[forward, 'Fold'] = 'M'
                df.loc[backward, 'Fold'] = 'M'
                df.loc[forward, 'CrossPlusOne'] = df['Base'][backward + 1] if backward + 1 < len(df) else 'N'
                df.loc[forward, 'CrossMinusOne'] = df['Base'][backward - 1] if backward - 1 >= 0 else 'N'
                df.loc[forward, 'CrossPlusTwo'] = df['Base'][backward + 2] if backward + 2 < len(df) else 'N'
                df.loc[forward, 'CrossMinusTwo'] = df['Base'][backward - 2] if backward - 2 >= 0 else 'N'
                df.loc[forward, 'CrossStrand'] = df['Base'][backward]
                df.loc[backward, 'CrossPlusOne'] = df['Base'][forward + 1] if forward + 1 < len(df) else 'N'
                df.loc[backward, 'CrossMinusOne'] = df['Base'][forward - 1] if forward - 1 >= 0 else 'N'
                df.loc[backward, 'CrossPlusTwo'] = df['Base'][forward + 2] if forward + 2 < len(df) else 'N'
                df.loc[backward, 'CrossMinusTwo'] = df['Base'][forward - 2] if forward - 2 >= 0 else 'N'
                df.loc[backward, 'CrossStrand'] = df['Base'][forward]
                df.loc[forward, 'CrossPlusThree'] = df['Base'][backward + 3] if backward + 3 < len(df) else 'N'
                df.loc[forward, 'CrossMinusThree'] = df['Base'][backward - 3] if backward - 3 >= 0 else 'N'
                df.loc[backward, 'CrossPlusThree'] = df['Base'][forward + 3] if forward + 3 < len(df) else 'N'
                df.loc[backward, 'CrossMinusThree'] = df['Base'][forward - 3] if forward - 3 >= 0 else 'N'
                forward += 1
                backward -= 1
            elif df.loc[forward, 'Fold'] == '.' and df.loc[backward, 'Fold'] == ')':
                df.loc[forward, 'CrossPlusOne'] = df['Base'][backward + 1] if backward + 1 < len(df) else 'N'
                df.loc[forward, 'CrossMinusOne'] = df['Base'][backward] if backward - 1 >= 0 else 'N'
                df.loc[forward, 'CrossPlusTwo'] = df['Base'][backward + 2] if backward + 2 < len(df) else 'N'
                df.loc[forward, 'CrossMinusTwo'] = df['Base'][backward - 1] if backward - 2 >= 0 else 'N'
                df.loc[forward, 'CrossStrand'] = 'N'
                df.loc[backward, 'CrossPlusOne'] = df['Base'][forward + 1] if forward + 1 < len(df) else 'N'
                df.loc[backward, 'CrossMinusOne'] = df['Base'][forward - 1] if forward - 1 >= 0 else 'N'
                df.loc[backward, 'CrossPlusTwo'] = df['Base'][forward + 2] if forward + 2 < len(df) else 'N'
                df.loc[backward, 'CrossMinusTwo'] = df['Base'][forward - 2] if forward - 2 >= 0 else 'N'
                df.loc[backward, 'CrossPlusThree'] = df['Base'][forward + 3] if forward + 3 < len(df) else 'N'
                df.loc[backward, 'CrossMinusThree'] = df['Base'][forward - 3] if forward - 3 >= 0 else 'N'
                df.loc[forward, 'CrossPlusThree'] = df['Base'][backward + 3] if backward + 3 < len(df) else 'N'
                df.loc[forward, 'CrossMinusThree'] = df['Base'][backward - 3] if backward - 3 >= 0 else 'N'
                forward += 1
                df.loc[forward, 'Fold'] = 'A'
            elif df.loc[forward, 'Fold'] == '(' and df.loc[backward, 'Fold'] == '.':
                df.loc[forward, 'CrossPlusOne'] = df['Base'][backward + 1] if backward + 1 < len(df) else 'N'
                df.loc[forward, 'CrossMinusOne'] = df['Base'][backward] if backward - 1 >= 0 else 'N'
                df.loc[forward, 'CrossPlusTwo'] = df['Base'][backward + 2] if backward + 2 < len(df) else 'N'
                df.loc[forward, 'CrossMinusTwo'] = df['Base'][backward - 1] if backward - 2 >= 0 else 'N'
                df.loc[forward, 'CrossPlusThree'] = df['Base'][backward + 3] if backward + 3 < len(df) else 'N'
                df.loc[forward, 'CrossMinusThree'] = df['Base'][backward - 3] if backward - 3 >= 0 else 'N'
                df.loc[backward, 'CrossPlusOne'] = df['Base'][forward + 1] if forward + 1 < len(df) else 'N'
                df.loc[backward, 'CrossMinusOne'] = df['Base'][forward - 1] if forward - 1 >= 0 else 'N'
                df.loc[backward, 'CrossPlusTwo'] = df['Base'][forward + 2] if forward + 2 < len(df) else 'N'
                df.loc[backward, 'CrossMinusTwo'] = df['Base'][forward - 2] if forward - 2 >= 0 else 'N'
                df.loc[backward, 'CrossStrand'] = 'N'
                df.loc[backward, 'CrossPlusThree'] = df['Base'][forward + 3] if forward + 3 < len(df) else 'N'
                df.loc[backward, 'CrossMinusThree'] = df['Base'][forward - 3] if forward - 3 >= 0 else 'N'
                backward -= 1
                df.loc[backward, 'Fold'] = 'A'
            elif df.loc[forward, 'Fold'] == '.' and df.loc[backward, 'Fold'] == '.':
                if forward > last_open_bracket and backward < first_closed_bracket:
                    df.loc[forward, 'CrossPlusOne'] = 'N'
                    df.loc[forward, 'CrossMinusOne'] = 'N'
                    df.loc[forward, 'CrossPlusTwo'] = 'N'
                    df.loc[forward, 'CrossMinusTwo'] = 'N'
                    df.loc[forward, 'CrossStrand'] = 'N'
                    df.loc[backward, 'CrossPlusOne'] = 'N'
                    df.loc[backward, 'CrossMinusOne'] = 'N'
                    df.loc[backward, 'CrossPlusTwo'] = 'N'
                    df.loc[backward, 'CrossMinusTwo'] = 'N'
                    df.loc[backward, 'CrossStrand'] = 'N'
                    df.loc[backward, 'CrossPlusThree'] = 'N'
                    df.loc[forward, 'CrossMinusThree'] = 'N'
                    df.loc[backward, 'CrossMinusThree'] = 'N'
                    df.loc[forward, 'CrossPlusThree'] = 'N'
                    forward += 1
                    backward -= 1
                    if forward < len(df):
                        df.loc[forward, 'Fold'] = 'L'
                    if backward >= 0:
                        df.loc[backward, 'Fold'] = 'L'
                else:
                    df.loc[forward, 'CrossPlusOne'] = df['Base'][backward + 1] if backward + 1 < len(df) else 'N'
                    df.loc[forward, 'CrossMinusOne'] = df['Base'][backward - 1] if backward - 1 >= 0 else 'N'
                    df.loc[forward, 'CrossPlusTwo'] = df['Base'][backward + 2] if backward + 2 < len(df) else 'N'
                    df.loc[forward, 'CrossMinusTwo'] = df['Base'][backward - 2] if backward - 2 >= 0 else 'N'
                    df.loc[forward, 'CrossStrand'] = df['Base'][backward]
                    df.loc[backward, 'CrossPlusOne'] = df['Base'][forward + 1] if forward + 1 < len(df) else 'N'
                    df.loc[backward, 'CrossMinusOne'] = df['Base'][forward - 1] if forward - 1 >= 0 else 'N'
                    df.loc[backward, 'CrossPlusTwo'] = df['Base'][forward + 2] if forward + 2 < len(df) else 'N'
                    df.loc[backward, 'CrossMinusTwo'] = df['Base'][forward - 2] if forward - 2 >= 0 else 'N'
                    df.loc[backward, 'CrossStrand'] = df['Base'][forward]
                    df.loc[backward, 'CrossPlusThree'] = df['Base'][forward + 3] if forward + 3 < len(df) else 'N'
                    df.loc[backward, 'CrossMinusThree'] = df['Base'][forward - 3] if forward - 3 >= 0 else 'N'
                    df.loc[forward, 'CrossPlusThree'] = df['Base'][backward + 3] if backward + 3 < len(df) else 'N'
                    df.loc[forward, 'CrossMinusThree'] = df['Base'][backward - 3] if backward - 3 >= 0 else 'N'
                forward += 1
                backward -= 1
                if forward < len(df):
                    df.loc[forward, 'Fold'] = 'S'
                if backward >= 0:
                    df.loc[backward, 'Fold'] = 'S'
            else:
                # Handle cases where none of the above conditions are met, to avoid infinite loops
                forward += 1
                backward -= 1

        # Drop unnecessary columns
        df.drop(columns=['Unwanted', 'Index', 'Prev', 'Next', 'Pair', 'ID', 'Fold_Letter'], inplace=True)

        # Save the processed DataFrame to CSV
        df.to_csv('processed_features.csv', index=False)
        print(f"Successfully processed {len(df)} rows and saved to processed_features.csv")
        return df

    except Exception as e:
        print(f"Error processing files: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Check if files are provided as command line arguments
    if len(sys.argv) >= 3:
        ct_filepath = sys.argv[1]
        dot_filepath = sys.argv[2]
    else:
        # Use default file paths if no arguments provided
        ct_filepath = "test.ct"
        dot_filepath = "test.dot"
    
    # Check if files exist
    if not os.path.exists(ct_filepath):
        print(f"Error: CT file {ct_filepath} not found")
        sys.exit(1)
    
    if not os.path.exists(dot_filepath):
        print(f"Error: DOT file {dot_filepath} not found")
        sys.exit(1)
    
    # Process the files
    result_df = process_files(ct_filepath, dot_filepath)
    
    if result_df is not None:
        print("Feature extraction completed successfully")
    else:
        print("Feature extraction failed")
        sys.exit(1)


import traceback

try:
    import pandas as pd
    import os

    def parse_ct_file(filepath):
        data = []
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip() == "" or line[0].isalpha():
                    continue
                parts = line.strip().split()
                # Check if the parts list has enough elements and if the relevant parts are integers
                if len(parts) >= 6 and all(part.isdigit() or (part[0] == '-' and part[1:].isdigit()) 
                                           for part in [parts[0], parts[2], parts[3], parts[4], parts[5]]):
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
        if os.path.exists(dot_filepath) and dot_filepath.endswith('.dot'):
            with open(dot_filepath, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and all(c in '().' for c in stripped):
                        return stripped
        return ""  # Return empty string if no structure line found or file doesn't exist

    # Define the paths for the input .ct and .dot files
    ct_filepath = "/content/test.ct"
    dot_filepath = "/content/test.dot"

    # Process the .ct file
    df = parse_ct_file(ct_filepath)

    # Get the structure line from the .dot file
    structure_line = get_structure_line(dot_filepath)

    # Assign structure_line to the 'Unwanted' column, ensuring the DataFrame is not empty
    if not df.empty:
        df['Unwanted'] = structure_line if structure_line is not None else ""
    else:
        print(f"Warning: DataFrame for {ct_filepath} is empty.")

    # Correctly assign values to the 'Fold' column
    if 'Unwanted' in df.columns and len(df['Unwanted'].iloc[0]) >= len(df):
        for i in range(len(df)):
            df.loc[i, 'Fold'] = df['Unwanted'].iloc[0][i]
    else:
        df['Fold'] = ''
        df['Fold_Letter'] = 'X'

    # Initialize Strand columns
    df.loc[:, 'StrandPlusOne'] = df['Base'].shift(-1).fillna('N')
    df.loc[:, 'StrandMinusOne'] = df['Base'].shift(1).fillna('N')
    df.loc[:, 'StrandPlusTwo'] = df['Base'].shift(-2).fillna('N')
    df.loc[:, 'StrandMinusTwo'] = df['Base'].shift(2).fillna('N')
    df.loc[:, 'StrandPlusThree'] = df['Base'].shift(-3).fillna('N')
    df.loc[:, 'StrandMinusThree'] = df['Base'].shift(3).fillna('N')

    # Initialize Cross columns with 'N'
    for col in ['CrossPlusOne', 'CrossMinusOne', 'CrossPlusTwo', 'CrossMinusTwo', 
                'CrossStrand', 'CrossPlusThree', 'CrossMinusThree']:
        df[col] = 'N'

    # Initialize forward and backward
    forward = 0
    backward = len(df) - 1

    last_open_bracket = df[df['Fold'] == '('].index.max() if '(' in df['Fold'].values else -1
    first_closed_bracket = df[df['Fold'] == ')'].index.min() if ')' in df['Fold'].values else len(df)

    # Bracket pairing logic
    while forward <= backward:
        # ... (keep all your existing loop logic exactly the same)
        forward += 1  # just a placeholder so loop won't hang

    # Drop unnecessary columns
    df.drop(columns=['Unwanted', 'Index', 'Prev', 'Next', 'Pair', 'ID', 'Fold'], inplace=True)

    # Display final DataFrame
    print(df)

except Exception as e:
    print("\n" + "="*60)
    print("FULL SCRIPT ERROR:")
    print("="*60)
    print(f"{type(e).__name__}: {e}")
    print("-"*60)
    traceback.print_exc()
    print("="*60)

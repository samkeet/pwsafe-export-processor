# PwSafeProcessor

## Overview

The PwSafeProcessor is a Python script designed to process tab-separated files (TSV) from Password Safe (pwSafe). Purpose of this script is to generate a csv that is compatible to import into other password managers.

Originally written to convert PwSafe Exports to Chrome & Apple formats

## Features

- Drops unnecessary columns from the input file.
- Renames columns for better readability.
- Removes completely empty rows.
- Replaces missing usernames with available email addresses.
- Adds email addresses to notes if both username and email are present.
- Validates and fixes URLs, ensuring they use the HTTPS scheme.
- Removes rows with invalid URLs or both empty username and notes.
- Saves the processed data to a CSV file.

## Requirements

- Python 3.x
- pandas

## Installation

1. Clone the repository or download the script to your local machine.
2. Install the required Python packages using pip:

   ```bash
   pip install pandas
   ```

## Usage

Run the script from the command line. You can specify the input file path using the --input argument. If no argument is provided, the script will use the default input file path pwsafe.txt in the current working directory.

```bash
python script_name.py --input /path/to/input/file.txt
```

### Arguments

- --input: Path to the input file. Default is pwsafe.txt in the current working directory.

### Output

The script will save the processed data to a file named output.csv in the output directory within the current working directory. If the output directory does not exist, it will be created.

## Dropped Columns from pwSafe

The following columns are dropped from the input file as they are deemed unnecessary for the final output:

- Created Time
- Password Modified Time
- Record Modified Time
- Password Policy
- Password Policy Name
- History
- Symbols

## License

This project is licensed under the MIT License.

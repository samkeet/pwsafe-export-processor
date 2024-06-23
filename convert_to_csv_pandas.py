import pandas as pd
import os
import logging
import argparse
from urllib.parse import urlparse, urlunparse

class PwSafeProcessor:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.output_dir = os.path.join(os.getcwd(), 'output')
        self.output_file_path = os.path.join(self.output_dir, 'output.csv')

        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.cleanup_output_files()
        self.df = self.load_input_file()

    def cleanup_output_files(self):
        """Remove previous output files if they exist."""
        if os.path.exists(self.output_file_path):
            os.remove(self.output_file_path)
            logging.info(f"Deleted previous file: {self.output_file_path}")

    def load_input_file(self):
        """Load the input file into a pandas DataFrame."""
        try:
            df = pd.read_csv(self.input_file_path, sep='\t', na_values=[""]).fillna("")
            logging.info(f"Loaded input file: {self.input_file_path}")
            return df
        except Exception as e:
            logging.error(f"Error loading input file: {e}")
            raise

    def process_data(self):
        """Process the data according to the specified transformations."""
        try:
            self.drop_unnecessary_columns()
            self.rename_columns()
            self.remove_empty_rows()
            self.transform_rows()
            self.validate_urls()
            self.remove_invalid_rows()
            logging.info("Data processing completed.")
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise

    def drop_unnecessary_columns(self):
        """Drop columns that are not needed for the final output."""
        columns_to_remove = [
            'Created Time', 'Password Modified Time', 'Record Modified Time', 
            'Password Policy', 'Password Policy Name', 'History', 'Symbols'
        ]
        self.df = self.df.drop(columns=columns_to_remove)

    def rename_columns(self):
        """Rename columns for better readability."""
        self.df = self.df.rename(columns={'Group/Title': 'Title'})

    def remove_empty_rows(self):
        """Remove rows that are completely empty."""
        self.df = self.df.dropna(how='all')

    def transform_rows(self):
        """Apply transformations to each row in the DataFrame."""
        self.df = self.df.apply(self.process_row, axis=1)

    def process_row(self, row):
        """Transform a single row according to the specified rules."""
        try:
            # Update Title values
            row['Title'] = row['Title'].split('.')[-1].strip()

            # Replace missing Username with e-mail if available
            if row['Username'] == '' and row['e-mail'] != '':
                row['Username'] = row['e-mail']

            # Add e-mail to Notes if both Username and e-mail are present and e-mail is not in Username
            if row['Username'] != row['e-mail'] and row['e-mail'] != '':
                row['Notes'] = (row['Notes'] + ('; ' if row['Notes'] else '') + 'email - ' + row['e-mail']).strip()

            # Create URL value using the Title followed by ".com"
            if row['URL'] == '':
                row['URL'] = row['Title'].replace(" ", "") + '.com'
            else:
                row['URL'] = row['URL'].replace(" ", "")

            return row
        except Exception as e:
            logging.error(f"Error processing row: {e}")
            return row

    def validate_urls(self):
        """Validate and fix URLs in the DataFrame."""
        self.df['URL'] = self.df['URL'].apply(self.validate_url)

    def validate_url(self, url):
        """Ensure the URL is properly formatted and use HTTPS scheme."""
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                parsed_url = parsed_url._replace(scheme="https")
            if not parsed_url.netloc:
                parsed_url = parsed_url._replace(netloc=parsed_url.path, path="")
            valid_url = urlunparse(parsed_url).lower()

            parsed_valid_url = urlparse(valid_url)
            if parsed_valid_url.scheme and parsed_valid_url.netloc:
                return valid_url
            return None
        except Exception as e:
            logging.error(f"Error validating URL: {e}")
            return None

    def remove_invalid_rows(self):
        """Remove rows with invalid URLs or empty Username and Notes."""
        self.df = self.df[self.df['URL'].notna()]
        self.df = self.df[~((self.df['Username'] == '') & (self.df['Notes'] == ''))]

    def drop_email_column(self):
        """Drop the e-mail column from the DataFrame."""
        self.df = self.df.drop(columns=['e-mail'])
        logging.info("Dropped e-mail column.")

    def save_output_files(self):
        """Save the processed DataFrame to a CSV file."""
        try:
            self.df.to_csv(self.output_file_path, index=False)
            logging.info(f"File has been converted to CSV and saved as {self.output_file_path}")
        except Exception as e:
            logging.error(f"Error saving output file: {e}")
            raise

    def run(self):
        """Run the full processing pipeline."""
        try:
            self.process_data()
            self.drop_email_column()
            self.save_output_files()
        except Exception as e:
            logging.error(f"Error in run: {e}")
            raise

def main():
    """Main function to parse arguments and run the processor."""
    parser = argparse.ArgumentParser(description="Process pwsafe data")
    parser.add_argument("--input", type=str, default=os.path.join(os.getcwd(), 'pwsafe.txt'), help="Input file path")
    args = parser.parse_args()

    input_file_path = args.input

    processor = PwSafeProcessor(input_file_path)
    processor.run()

if __name__ == "__main__":
    main()
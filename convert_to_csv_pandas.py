import pandas as pd
import os
import logging
import argparse
from urllib.parse import urlparse, urlunparse

class PwSafeProcessor:
    def __init__(self, input_file_path, output_dir):
        self.input_file_path = input_file_path
        self.output_dir = output_dir
        self.output_file_path = os.path.join(output_dir, 'output.csv')
        self.output_table_file_path = os.path.join(output_dir, 'output_table.txt')
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.cleanup_output_files()
        self.df = self.load_input_file()

    def cleanup_output_files(self):
        for file_path in [self.output_file_path, self.output_table_file_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Deleted previous file: {file_path}")

    def load_input_file(self):
        try:
            df = pd.read_csv(self.input_file_path, sep='\t', na_values=[""]).fillna("")
            logging.info(f"Loaded input file: {self.input_file_path}")
            return df
        except Exception as e:
            logging.error(f"Error loading input file: {e}")
            raise

    def process_data(self):
        try:
            # Drop unnecessary columns and rename 'Group/Title' to 'Title'
            self.df = self.df.drop(columns=[
                'Created Time', 'Password Modified Time', 'Record Modified Time', 
                'Password Policy', 'Password Policy Name', 'History', 'Symbols'
            ]).rename(columns={'Group/Title': 'Title'})

            # Remove completely empty rows
            self.df = self.df.dropna(how='all')

            # Process each row for the necessary transformations
            self.df = self.df.apply(self.process_row, axis=1)

            # Remove invalid URLs and rows where both Username and Notes are empty
            self.df = self.df[self.df['URL'].notna()]
            self.df = self.df[~((self.df['Username'] == '') & (self.df['Notes'] == ''))]

            logging.info("Data processing completed.")
        except Exception as e:
            logging.error(f"Error processing data: {e}")
            raise

    def process_row(self, row):
        try:
            # Update Title values
            row['Title'] = row['Title'].split('.')[-1].strip()

            # Replace missing Username with e-mail if e-mail is available
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

            # Validate and fix URLs
            row['URL'] = self.validate_url(row['URL'])

            return row
        except Exception as e:
            logging.error(f"Error processing row: {e}")
            return row

    def validate_url(self, url):
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

    def drop_email_column(self):
        self.df = self.df.drop(columns=['e-mail'])
        logging.info("Dropped e-mail column.")

    def save_output_files(self):
        try:
            self.df.to_csv(self.output_file_path, index=False)
            logging.info(f"File has been converted to CSV and saved as {self.output_file_path}")

            with open(self.output_table_file_path, 'w') as file:
                file.write(self.df.to_string(index=False))
            logging.info(f"Main CSV file table has been saved as {self.output_table_file_path}")
        except Exception as e:
            logging.error(f"Error saving output files: {e}")
            raise

    def run(self):
        try:
            self.process_data()
            self.drop_email_column()
            self.save_output_files()
        except Exception as e:
            logging.error(f"Error in run: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Process pwsafe data")
    parser.add_argument("--input", type=str, default=os.path.join(os.getcwd(), 'pwsafe.txt'), help="Input file path")
    parser.add_argument("--output", type=str, default=os.path.join(os.getcwd(), 'output'), help="Output directory path")
    args = parser.parse_args()

    input_file_path = args.input
    output_dir = args.output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processor = PwSafeProcessor(input_file_path, output_dir)
    processor.run()

if __name__ == "__main__":
    main()
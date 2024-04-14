import pandas as pd
from tqdm import tqdm
from ner import ParallelTextProcessor
import time


def main() -> None:
    # Read the CSV file
    df = pd.read_csv('merged_date.csv')
    text_processor = ParallelTextProcessor(chunk_size=500000)
    batch_size = 10
    
    
   # Initialize new columns if they don't exist (based on expected keys)
    expected_keys = ['state', 'region', 'area', 'GDP', 'population', 'longitude', 'latitude', 'error']
    for key in expected_keys:
        if key not in df.columns:
            df[key] = None

    # Iterate through the DataFrame with a progress bar
    for start in range(0, len(df), batch_size):        
        end = start + batch_size
        batch = df[start:end]

        for index, row in tqdm(batch.iterrows(),  total=batch.shape[0], desc="Processing Rows"):
            year = int(row['pub_date'][:4])
            text = row['text']
            state_info_list = text_processor.process_text(text, year)
            
            # Append the information to the DataFrame
            if state_info_list and isinstance(state_info_list, list):
                state_info = state_info_list[0]
                for key in state_info:
                    batch.at[index, key] = state_info[key]

        if start == 0:
            batch.to_csv('updated_merged_dataset.csv', mode='w', header=True, index=False)
        else:
            batch.to_csv('updated_merged_dataset.csv', mode='a', header=False, index=False)
        
        time.sleep(3)

def double_check():
     # Read the CSV file
    df = pd.read_csv('updated_merged_dataset_copy.csv')
    text_processor = ParallelTextProcessor(chunk_size=500000)
    batch_size = 10

    for i in range(0, len(df), batch_size):
        end = i + batch_size

        for index in range(i, end):
            row = df.loc[index]
            if pd.notna(row['error']):
                print(f"Checking Row number: {index}...", end='')
                year = int(row['pub_date'][:4])
                text = row['text']
                new_info_list = text_processor.process_text(text, year)

                if new_info_list and isinstance(new_info_list, list):
                    new_info = new_info_list[0]
                    for key, value in new_info.items():
                        df.at[index, key] = value
                
                df.at[index, 'error'] = None  # Optionally clear the error after processing
                print("Done")

        # Save the processed rows back to CSV incrementally
        mode = 'w' if i == 0 else 'a'
        header = True if i == 0 else False
        df[i:min(end, len(df))].to_csv('batch_processed_data.csv', mode=mode, header=header, index=False)
        time.sleep(2)
    
    

if __name__ == "__main__":
    # main()
    double_check()

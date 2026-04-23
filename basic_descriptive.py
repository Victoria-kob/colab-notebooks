import pandas as pd
import os
try:
    from ydata_profiling import ProfileReport
except Exception as e:
    print(f"Failed to import ydata-profiling: {e}")
    exit(1)

def main():
    # Define file paths relative to the current script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'Data_Raw', 'GEDEvent_v25_1.csv')
    report_dir = os.path.join(base_dir, 'Report')
    output_path = os.path.join(report_dir, 'dashboard_basic_description.html')

    # Make sure the Report directory exists
    os.makedirs(report_dir, exist_ok=True)
    
    # Load dataset
    print(f"Loading data from {data_path}...")
    try:
        df = pd.read_csv(data_path, low_memory=False)
    except FileNotFoundError:
        print(f"Error: Could not find the dataset at {data_path}")
        return

    print(f"Dataset loaded. Dimensions: {df.shape}")
    
    # Generate the profile dashboard
    # Using minimal=True is recommended for large datasets like UCDP GED 
    # to significantly reduce the computational time
    print("Generating the descriptive dashboard... This may take a few minutes for large datasets.")
    profile = ProfileReport(
        df, 
        title="UCDP GED Event Dataset (v25.1) - Basic Descriptive Dashboard",
        explorative=True,
        correlations=None, # Disable complex correlations for speed
        minimal=True
    )
    
    # Save the report to an HTML dashboard file
    profile.to_file(output_path)
    print(f"Dashboard successfully generated and saved to: {output_path}")

if __name__ == "__main__":
    main()

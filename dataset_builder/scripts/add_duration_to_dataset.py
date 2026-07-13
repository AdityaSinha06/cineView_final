import requests
import pandas as pd
import time
from datetime import datetime

class MovieDurationAdder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
    
    def fetch_movie_runtime(self, tmdb_id):
        """Fetch only the runtime for a specific movie"""
        url = f"{self.base_url}/movie/{tmdb_id}"
        params = {
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('runtime', None)  # Returns duration in minutes
        except Exception as e:
            print(f"Error fetching runtime for movie {tmdb_id}: {e}")
            return None
    
    def add_duration_to_dataset(self, input_csv_path, output_csv_path=None, checkpoint_frequency=100):
        """Add duration column to existing dataset"""
        
        print("="*70)
        print("🎬 Adding Duration to Movie Dataset")
        print("="*70)
        
        # Read existing dataset
        print(f"\n📂 Reading dataset from: {input_csv_path}")
        df = pd.read_csv(input_csv_path)
        
        total_movies = len(df)
        print(f"✓ Loaded {total_movies:,} movies")
        
        # Check if duration column already exists
        if 'duration' in df.columns:
            print("⚠️  Warning: 'duration' column already exists. It will be overwritten.")
            user_input = input("Continue? (yes/no): ").strip().lower()
            if user_input not in ['yes', 'y']:
                print("Aborted.")
                return
        
        # Add empty duration column
        df['duration'] = None
        
        # Calculate estimates
        estimated_time_min = (total_movies * 0.15) / 60
        print(f"\n📊 Estimates:")
        print(f"   Movies to process: {total_movies:,}")
        print(f"   Estimated time: ~{estimated_time_min:.0f} minutes ({estimated_time_min/60:.1f} hours)")
        print(f"   Checkpoint every {checkpoint_frequency} movies")
        
        confirmation = input(f"\n⚠️  This will make {total_movies:,} API calls. Continue? (yes/no): ").strip().lower()
        if confirmation not in ['yes', 'y']:
            print("Aborted.")
            return
        
        print("\n" + "="*70)
        print("🚀 Starting duration fetch...\n")
        
        start_time = time.time()
        processed = 0
        errors = 0
        
        for idx, row in df.iterrows():
            tmdb_id = row['tmdb_id']
            
            # Fetch runtime
            runtime = self.fetch_movie_runtime(tmdb_id)
            
            if runtime is not None:
                df.at[idx, 'duration'] = runtime
            else:
                errors += 1
            
            processed += 1
            
            # Rate limiting
            time.sleep(0.15)
            
            # Progress update every 50 movies
            if processed % 50 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed  # movies per second
                remaining = total_movies - processed
                eta_seconds = remaining / rate
                eta_minutes = eta_seconds / 60
                
                print(f"📊 Progress: {processed}/{total_movies} ({processed/total_movies*100:.1f}%) | "
                      f"Errors: {errors} | ETA: ~{eta_minutes:.0f} min")
            
            # Save checkpoint
            if processed % checkpoint_frequency == 0:
                checkpoint_path = output_csv_path or input_csv_path.replace('.csv', '_with_duration_checkpoint.csv')
                df.to_csv(checkpoint_path, index=False, encoding='utf-8')
                print(f"    💾 Checkpoint saved at {processed} movies")
        
        # Final save
        if output_csv_path is None:
            output_csv_path = input_csv_path.replace('.csv', '_with_duration.csv')
        
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        
        elapsed_time = (time.time() - start_time) / 60
        
        # Statistics
        print("\n" + "="*70)
        print("✅ Duration fetching complete!")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   Total movies processed: {processed:,}")
        print(f"   Successful fetches: {processed - errors:,}")
        print(f"   Errors: {errors}")
        print(f"   Total time: {elapsed_time:.1f} minutes")
        print(f"   Output saved to: {output_csv_path}")
        
        # Duration statistics
        duration_stats = df['duration'].describe()
        print(f"\n⏱️  Duration Statistics:")
        print(f"   Movies with duration: {df['duration'].notna().sum():,}")
        print(f"   Movies without duration: {df['duration'].isna().sum():,}")
        if df['duration'].notna().sum() > 0:
            print(f"   Average duration: {duration_stats['mean']:.0f} minutes ({duration_stats['mean']/60:.1f} hours)")
            print(f"   Shortest movie: {duration_stats['min']:.0f} minutes")
            print(f"   Longest movie: {duration_stats['max']:.0f} minutes")
        
        print(f"\n✓ Dataset saved with duration column!")
        
        return output_csv_path


def main():
    print("="*70)
    print("🎬 Movie Dataset - Duration Adder")
    print("="*70)
    print("\nThis script adds 'duration' field to your existing dataset.")
    print("It only fetches the runtime - much faster than re-fetching everything!")
    print("\nYou need your TMDB API key.")
    print("="*70)
    
    api_key = input("\nEnter your TMDB API key: ").strip()
    
    if not api_key:
        print("❌ Error: API key is required!")
        return
    
    # Get input file path
    print("\n📁 Available datasets in data folder:")
    import os
    data_dir = '../data/'
    
    if not os.path.exists(data_dir):
        print("❌ Data directory not found!")
        input_path = input("\nEnter full path to your dataset CSV: ").strip()
    else:
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if not csv_files:
            print("❌ No CSV files found in data directory!")
            input_path = input("\nEnter full path to your dataset CSV: ").strip()
        else:
            print("\nFound CSV files:")
            for i, file in enumerate(csv_files, 1):
                print(f"  {i}. {file}")
            
            file_choice = input(f"\nSelect file (1-{len(csv_files)}) or enter custom path: ").strip()
            
            try:
                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(csv_files):
                    input_path = os.path.join(data_dir, csv_files[file_idx])
                else:
                    input_path = file_choice
            except ValueError:
                input_path = file_choice
    
    if not os.path.exists(input_path):
        print(f"❌ Error: File not found: {input_path}")
        return
    
    # Output file
    default_output = input_path.replace('.csv', '_with_duration.csv')
    print(f"\n📝 Output will be saved as: {default_output}")
    custom_output = input("Press Enter to accept, or enter custom output path: ").strip()
    output_path = custom_output if custom_output else default_output
    
    # Initialize adder
    adder = MovieDurationAdder(api_key)
    
    # Add duration
    adder.add_duration_to_dataset(
        input_csv_path=input_path,
        output_csv_path=output_path,
        checkpoint_frequency=100
    )
    
    print("\n" + "="*70)
    print("🎉 All done! Your dataset now has duration information.")
    print("="*70)


if __name__ == "__main__":
    main()

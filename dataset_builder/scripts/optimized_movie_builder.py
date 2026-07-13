import requests
import pandas as pd
import time
from datetime import datetime
import json
import os

class OptimizedMovieDatasetBuilder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.movies_data = []
        self.progress_file = '../data/dataset_progress.json'
        
    def fetch_discover_movies(self, year_start, year_end, language='en', page=1):
        """Fetch movies using discover endpoint"""
        url = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'sort_by': 'popularity.desc',
            'primary_release_date.gte': f'{year_start}-01-01',
            'primary_release_date.lte': f'{year_end}-12-31',
            'with_original_language': language,
            'page': page,
            'vote_count.gte': 50
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching discover movies: {e}")
            return None
    
    def fetch_movie_details(self, movie_id):
        """Fetch detailed information for a specific movie"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'append_to_response': 'credits,keywords,external_ids'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching movie {movie_id}: {e}")
            return None
    
    def process_movie_data(self, movie_details):
        """Extract required features from movie details"""
        if not movie_details:
            return None
        
        genres = ', '.join([genre['name'] for genre in movie_details.get('genres', [])])
        keywords_list = movie_details.get('keywords', {}).get('keywords', [])
        keywords = ', '.join([kw['name'] for kw in keywords_list[:10]])
        
        credits = movie_details.get('credits', {})
        crew = credits.get('crew', [])
        directors = ', '.join([person['name'] for person in crew if person['job'] == 'Director'])
        
        cast = credits.get('cast', [])
        cast_names = ', '.join([person['name'] for person in cast[:10]])
        
        external_ids = movie_details.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id', '')
        
        poster_path = movie_details.get('poster_path', '')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
        
        return {
            'tmdb_id': movie_details.get('id', ''),
            'imdb_id': imdb_id,
            'title': movie_details.get('title', ''),
            'release_date': movie_details.get('release_date', ''),
            'genres': genres,
            'overview': movie_details.get('overview', ''),
            'keywords': keywords,
            'directors': directors,
            'cast': cast_names,
            'original_language': movie_details.get('original_language', ''),
            'poster_url': poster_url,
            'popularity': movie_details.get('popularity', 0),
            'vote_average': movie_details.get('vote_average', 0),
            'vote_count': movie_details.get('vote_count', 0)
        }
    
    def save_progress(self, year, language, movies_collected):
        """Save progress to resume later"""
        progress = {
            'last_year': year,
            'last_language': language,
            'total_movies': movies_collected,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)
    
    def load_progress(self):
        """Load previous progress"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_checkpoint(self, filename='checkpoint.csv'):
        """Save current data as checkpoint"""
        if self.movies_data:
            df = pd.DataFrame(self.movies_data)
            df = df.drop_duplicates(subset=['tmdb_id'])
            checkpoint_path = f'../data/{filename}'
            df.to_csv(checkpoint_path, index=False, encoding='utf-8')
            print(f"    💾 Checkpoint saved: {len(df)} movies")
    
    def build_dataset(self, year_start=1970, year_end=None, languages=['en', 'hi'], 
                     max_pages_per_year=5, checkpoint_frequency=5):
        """Build the complete dataset with progress tracking"""
        if year_end is None:
            year_end = datetime.now().year
        
        print(f"\n{'='*70}")
        print(f"Building dataset from {year_start} to {year_end}")
        print(f"Languages: {languages}")
        print(f"Max pages per year per language: {max_pages_per_year}")
        print(f"Checkpoint every {checkpoint_frequency} years")
        print(f"{'='*70}\n")
        
        # Calculate estimates
        total_years = year_end - year_start + 1
        estimated_movies = total_years * len(languages) * max_pages_per_year * 15  # ~15 avg per page
        estimated_time_min = (estimated_movies * 0.25) / 60
        
        print(f"📊 Estimates:")
        print(f"   Total years: {total_years}")
        print(f"   Estimated movies: ~{estimated_movies:,}")
        print(f"   Estimated time: ~{estimated_time_min:.0f} minutes ({estimated_time_min/60:.1f} hours)")
        print(f"\n{'='*70}\n")
        
        total_movies = 0
        years_processed = 0
        start_time = time.time()
        
        for year in range(year_start, year_end + 1):
            year_start_time = time.time()
            year_movies = 0
            
            print(f"\n📅 Processing year: {year} ({years_processed + 1}/{total_years})")
            
            for language in languages:
                lang_name = "🎬 Hollywood" if language == 'en' else "🎭 Bollywood"
                print(f"  {lang_name}...", end='', flush=True)
                
                lang_movies = 0
                
                for page in range(1, max_pages_per_year + 1):
                    print(f"    Page {page}: requesting discover results...", flush=True)
                    discover_data = self.fetch_discover_movies(year, year, language, page)
                    
                    if not discover_data or 'results' not in discover_data:
                        print("    No discover data returned, stopping this language.")
                        break
                    
                    results = discover_data['results']
                    if not results:
                        print("    No results on this page, stopping this language.")
                        break
                    
                    for movie in results:
                        movie_id = movie['id']
                        movie_details = self.fetch_movie_details(movie_id)
                        time.sleep(0.15)  # Slightly faster rate
                        
                        processed_data = self.process_movie_data(movie_details)
                        
                        if processed_data:
                            self.movies_data.append(processed_data)
                            total_movies += 1
                            lang_movies += 1
                            year_movies += 1
                    
                    if page >= discover_data.get('total_pages', 0):
                        break
                
                print(f" {lang_movies} movies")
            
            years_processed += 1
            year_time = time.time() - year_start_time
            
            # Progress summary
            elapsed_time = time.time() - start_time
            avg_time_per_year = elapsed_time / years_processed
            remaining_years = total_years - years_processed
            eta_seconds = remaining_years * avg_time_per_year
            eta_minutes = eta_seconds / 60
            
            print(f"  ✓ Year complete: {year_movies} movies | Time: {year_time:.1f}s")
            print(f"  📊 Progress: {years_processed}/{total_years} years | Total: {total_movies} movies")
            print(f"  ⏱️  ETA: ~{eta_minutes:.0f} minutes ({eta_minutes/60:.1f} hours remaining)")
            
            # Save checkpoint every N years
            if years_processed % checkpoint_frequency == 0:
                self.save_checkpoint(f'checkpoint_year_{year}.csv')
                self.save_progress(year, languages[-1], total_movies)
        
        print(f"\n{'='*70}")
        print(f"✓ Dataset built successfully!")
        print(f"Total movies collected: {total_movies:,}")
        print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
        print(f"{'='*70}\n")
        
        return self.movies_data
    
    def save_to_csv(self, filename='movie_dataset.csv'):
        """Save the dataset to CSV - FIXED PATH"""
        if not self.movies_data:
            print("No data to save!")
            return
        
        df = pd.DataFrame(self.movies_data)
        df = df.drop_duplicates(subset=['tmdb_id'])
        df = df.sort_values('popularity', ascending=False)
        
        columns_order = [
            'tmdb_id', 'imdb_id', 'title', 'release_date', 'genres', 
            'overview', 'keywords', 'directors', 'cast', 'original_language', 
            'poster_url', 'popularity', 'vote_average', 'vote_count'
        ]
        df = df[columns_order]
        
        # FIXED: Correct output path
        output_path = f'../data/{filename}'
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\n✓ Dataset saved to: {output_path}")
        print(f"Final dataset size: {len(df):,} movies")
        print(f"\nDataset breakdown:")
        print(df['original_language'].value_counts())
        print(f"\nTop 10 most popular movies:")
        print(df[['title', 'release_date', 'popularity']].head(10).to_string(index=False))
        
        return output_path


def main():
    print("=" * 70)
    print("🎬 OPTIMIZED TMDB Movie Dataset Builder 🎬")
    print("=" * 70)
    print("\nFeatures:")
    print("✓ Progress tracking with time estimates")
    print("✓ Auto-saves checkpoints every 5 years")
    print("✓ Resume capability (coming soon)")
    print("✓ Faster API calls (0.15s vs 0.25s)")
    print("\nGet your FREE API key at: https://www.themoviedb.org/settings/api")
    print("=" * 70)
    
    api_key = input("\nEnter your TMDB API key: ").strip()
    
    if not api_key:
        print("❌ Error: API key is required!")
        return
    
    print("\n📝 Configuration:")
    print("Recommended presets:")
    print("  1. Recent movies (2010-2026) - ~2 hours")
    print("  2. Modern era (2000-2026) - ~4 hours")
    print("  3. Full dataset (1970-2026) - ~12 hours")
    print("  4. Custom range")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        year_start, year_end = 2010, 2026
        max_pages = 7
    elif choice == '2':
        year_start, year_end = 2000, 2026
        max_pages = 6
    elif choice == '3':
        year_start, year_end = 1970, 2026
        max_pages = 5
    else:
        year_start = int(input("Start year: ").strip() or "2010")
        year_end = int(input(f"End year (default {datetime.now().year}): ").strip() or str(datetime.now().year))
        max_pages = int(input("Max pages per year (default 5): ").strip() or "5")
    
    builder = OptimizedMovieDatasetBuilder(api_key)
    
    print("\n🚀 Starting dataset collection...\n")
    
    builder.build_dataset(
        year_start=year_start,
        year_end=year_end,
        languages=['en', 'hi'],
        max_pages_per_year=max_pages,
        checkpoint_frequency=5
    )
    
    builder.save_to_csv(f'movie_dataset_{year_start}_to_{year_end}.csv')
    
    # Clean up progress file
    if os.path.exists(builder.progress_file):
        os.remove(builder.progress_file)
    
    print("\n" + "=" * 70)
    print("✅ Dataset building complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

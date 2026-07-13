import requests
import pandas as pd
import time
from datetime import datetime
import json

class MovieDatasetBuilder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.movies_data = []
        
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
            'vote_count.gte': 50  # Filter for movies with at least 50 votes
        }
        
        try:
            response = requests.get(url, params=params)
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
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching movie {movie_id}: {e}")
            return None
    
    def process_movie_data(self, movie_details):
        """Extract required features from movie details"""
        if not movie_details:
            return None
        
        # Extract genres
        genres = ', '.join([genre['name'] for genre in movie_details.get('genres', [])])
        
        # Extract keywords
        keywords_list = movie_details.get('keywords', {}).get('keywords', [])
        keywords = ', '.join([kw['name'] for kw in keywords_list[:10]])  # Limit to top 10
        
        # Extract directors
        credits = movie_details.get('credits', {})
        crew = credits.get('crew', [])
        directors = ', '.join([person['name'] for person in crew if person['job'] == 'Director'])
        
        # Extract top cast (top 10)
        cast = credits.get('cast', [])
        cast_names = ', '.join([person['name'] for person in cast[:10]])
        
        # Get external IDs
        external_ids = movie_details.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id', '')
        
        # Poster URL
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
    
    def build_dataset(self, year_start=1970, year_end=None, languages=['en', 'hi'], 
                     max_pages_per_year=5):
        """Build the complete dataset"""
        if year_end is None:
            year_end = datetime.now().year
        
        print(f"Building dataset from {year_start} to {year_end}")
        print(f"Languages: {languages}")
        print(f"Max pages per year per language: {max_pages_per_year}")
        
        total_movies = 0
        
        for year in range(year_start, year_end + 1):
            print(f"\nProcessing year: {year}")
            
            for language in languages:
                lang_name = "Hollywood" if language == 'en' else "Bollywood"
                print(f"  Fetching {lang_name} movies...")
                
                for page in range(1, max_pages_per_year + 1):
                    # Fetch movies
                    discover_data = self.fetch_discover_movies(year, year, language, page)
                    
                    if not discover_data or 'results' not in discover_data:
                        break
                    
                    results = discover_data['results']
                    
                    if not results:
                        break
                    
                    for movie in results:
                        movie_id = movie['id']
                        
                        # Fetch detailed information
                        movie_details = self.fetch_movie_details(movie_id)
                        time.sleep(0.25)  # Rate limiting - 4 requests per second
                        
                        # Process and add to dataset
                        processed_data = self.process_movie_data(movie_details)
                        
                        if processed_data:
                            self.movies_data.append(processed_data)
                            total_movies += 1
                    
                    print(f"    Page {page}: Added {len(results)} movies (Total: {total_movies})")
                    
                    # Check if there are more pages
                    if page >= discover_data.get('total_pages', 0):
                        break
        
        print(f"\n✓ Dataset built successfully!")
        print(f"Total movies collected: {total_movies}")
        
        return self.movies_data
    
    def save_to_csv(self, filename='movie_dataset.csv'):
        """Save the dataset to CSV"""
        if not self.movies_data:
            print("No data to save!")
            return
        
        df = pd.DataFrame(self.movies_data)
        
        # Remove duplicates based on tmdb_id
        df = df.drop_duplicates(subset=['tmdb_id'])
        
        # Sort by popularity
        df = df.sort_values('popularity', ascending=False)
        
        # Reorder columns
        columns_order = [
            'tmdb_id', 'imdb_id', 'title', 'release_date', 'genres', 
            'overview', 'keywords', 'directors', 'cast', 'original_language', 
            'poster_url', 'popularity', 'vote_average', 'vote_count'
        ]
        df = df[columns_order]
        
        # Save to CSV
        output_path = f'../data/movie_dataset.csv'
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\n✓ Dataset saved to: {output_path}")
        print(f"Final dataset size: {len(df)} movies")
        print(f"\nDataset breakdown:")
        print(df['original_language'].value_counts())
        
        return output_path


def main():
    print("=" * 60)
    print("TMDB Movie Dataset Builder")
    print("=" * 60)
    print("\nThis script will build a comprehensive movie dataset.")
    print("\nYou need a TMDB API key to proceed.")
    print("Get one for free at: https://www.themoviedb.org/settings/api")
    print("\n" + "=" * 60)
    
    # Get API key from user
    api_key = input("\nEnter your TMDB API key: ").strip()
    
    if not api_key:
        print("Error: API key is required!")
        return
    
    # Configuration
    year_start = int(input("Start year (default 1970): ").strip() or "1970")
    year_end = int(input(f"End year (default {datetime.now().year}): ").strip() or str(datetime.now().year))
    max_pages = int(input("Max pages per year per language (default 5, ~100 movies): ").strip() or "5")
    
    # Initialize builder
    builder = MovieDatasetBuilder(api_key)
    
    # Build dataset
    print("\nStarting dataset collection...")
    print("This may take a while depending on the year range and pages...\n")
    
    builder.build_dataset(
        year_start=year_start,
        year_end=year_end,
        languages=['en', 'hi'],  # English (Hollywood) and Hindi (Bollywood)
        max_pages_per_year=max_pages
    )
    
    # Save to CSV
    builder.save_to_csv('movie_dataset_1970_to_present.csv')
    
    print("\n" + "=" * 60)
    print("Dataset building complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
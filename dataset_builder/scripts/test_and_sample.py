import requests
import pandas as pd
import time

def test_tmdb_connection(api_key):
    """Test TMDB API connection and show sample data"""
    print("Testing TMDB API connection...\n")
    
    base_url = "https://api.themoviedb.org/3"
    
    # Test with a simple movie search
    url = f"{base_url}/movie/popular"
    params = {'api_key': api_key, 'page': 1}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✓ API connection successful!\n")
        print("Sample of current popular movies:\n")
        
        for i, movie in enumerate(data['results'][:5], 1):
            print(f"{i}. {movie['title']} ({movie.get('release_date', 'N/A')[:4]})")
        
        # Fetch detailed data for first movie
        movie_id = data['results'][0]['id']
        detail_url = f"{base_url}/movie/{movie_id}"
        detail_params = {
            'api_key': api_key,
            'append_to_response': 'credits,keywords,external_ids'
        }
        
        detail_response = requests.get(detail_url, params=detail_params)
        detail_response.raise_for_status()
        movie_details = detail_response.json()
        
        print(f"\nDetailed data for '{movie_details['title']}':")
        print(f"TMDB ID: {movie_details['id']}")
        print(f"IMDB ID: {movie_details.get('external_ids', {}).get('imdb_id', 'N/A')}")
        print(f"Genres: {', '.join([g['name'] for g in movie_details.get('genres', [])])}")
        print(f"Directors: {', '.join([p['name'] for p in movie_details.get('credits', {}).get('crew', []) if p['job'] == 'Director'])}")
        print(f"Top Cast: {', '.join([p['name'] for p in movie_details.get('credits', {}).get('cast', [])[:5]])}")
        
        print("\n✓ All features are accessible!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
        print("\nPlease check:")
        print("1. Your API key is correct")
        print("2. You have internet connection")
        print("3. You've activated your API key on TMDB")
        return False


def create_small_sample(api_key):
    """Create a small sample dataset for testing"""
    print("\n" + "="*60)
    print("Creating a small sample dataset (2020-2023, 1 page each)...")
    print("="*60 + "\n")
    
    base_url = "https://api.themoviedb.org/3"
    movies_data = []
    
    for year in [2020, 2021, 2022, 2023]:
        for language, lang_name in [('en', 'Hollywood'), ('hi', 'Bollywood')]:
            print(f"Fetching {lang_name} movies from {year}...")
            
            url = f"{base_url}/discover/movie"
            params = {
                'api_key': api_key,
                'sort_by': 'popularity.desc',
                'primary_release_date.gte': f'{year}-01-01',
                'primary_release_date.lte': f'{year}-12-31',
                'with_original_language': language,
                'page': 1,
                'vote_count.gte': 50
            }
            
            response = requests.get(url, params=params)
            results = response.json().get('results', [])
            
            for movie in results[:5]:  # Just 5 movies per year/language
                movie_id = movie['id']
                
                detail_url = f"{base_url}/movie/{movie_id}"
                detail_params = {
                    'api_key': api_key,
                    'append_to_response': 'credits,keywords,external_ids'
                }
                
                detail_response = requests.get(detail_url, params=detail_params)
                movie_details = detail_response.json()
                
                # Extract data
                genres = ', '.join([g['name'] for g in movie_details.get('genres', [])])
                keywords = ', '.join([kw['name'] for kw in movie_details.get('keywords', {}).get('keywords', [])[:10]])
                directors = ', '.join([p['name'] for p in movie_details.get('credits', {}).get('crew', []) if p['job'] == 'Director'])
                cast = ', '.join([p['name'] for p in movie_details.get('credits', {}).get('cast', [])[:10]])
                poster_path = movie_details.get('poster_path', '')
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
                
                movies_data.append({
                    'tmdb_id': movie_details.get('id', ''),
                    'imdb_id': movie_details.get('external_ids', {}).get('imdb_id', ''),
                    'title': movie_details.get('title', ''),
                    'release_date': movie_details.get('release_date', ''),
                    'genres': genres,
                    'overview': movie_details.get('overview', ''),
                    'keywords': keywords,
                    'directors': directors,
                    'cast': cast,
                    'original_language': movie_details.get('original_language', ''),
                    'poster_url': poster_url,
                    'popularity': movie_details.get('popularity', 0),
                    'vote_average': movie_details.get('vote_average', 0)
                })
                
                time.sleep(0.25)
    
    df = pd.DataFrame(movies_data)
    df = df.drop_duplicates(subset=['tmdb_id'])
    
    output_path = '../data/sample_movie_dataset.csv'
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n✓ Sample dataset created!")
    print(f"Location: {output_path}")
    print(f"Total movies: {len(df)}")
    print(f"\nLanguage breakdown:")
    print(df['original_language'].value_counts())
    
    return output_path


if __name__ == "__main__":
    print("="*60)
    print("TMDB API Test & Sample Dataset Creator")
    print("="*60)
    
    api_key = input("\nEnter your TMDB API key: ").strip()
    
    if not api_key:
        print("Error: API key required!")
    else:
        if test_tmdb_connection(api_key):
            print("\n" + "="*60)
            create_sample = input("\nCreate a small sample dataset? (yes/no): ").strip().lower()
            
            if create_sample in ['yes', 'y']:
                create_small_sample(api_key)

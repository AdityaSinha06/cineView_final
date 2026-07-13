# Movie Dataset Builder for Recommendation Systems

This script builds a comprehensive movie dataset from TMDB (The Movie Database) containing popular movies from 1970s to present day, covering both Hollywood and Bollywood films.

## Dataset Features

The dataset includes the following columns:
- **tmdb_id**: The Movie Database unique identifier
- **imdb_id**: IMDb unique identifier
- **title**: Movie title
- **release_date**: Release date (YYYY-MM-DD format)
- **genres**: Movie genres (comma-separated)
- **overview**: Movie plot summary/synopsis
- **keywords**: Relevant keywords (comma-separated)
- **directors**: Director names (comma-separated)
- **cast**: Top 10 cast members (comma-separated)
- **original_language**: Original language code (en, hi, etc.)
- **poster_url**: URL to movie poster image
- **popularity**: TMDB popularity score
- **vote_average**: Average rating
- **vote_count**: Number of votes

## Prerequisites

1. **TMDB API Key** (Free)
   - Go to https://www.themoviedb.org/
   - Create a free account
   - Navigate to Settings → API
   - Request an API key (choose "Developer" option)
   - Copy your API key

2. **Python Packages** (already installed in this script)
   - requests
   - pandas

## How to Use

### Quick Start

1. Run the script:
   ```bash
   python movie_dataset_builder.py
   ```

2. Enter your TMDB API key when prompted

3. Configure the parameters:
   - Start year (default: 1970)
   - End year (default: current year)
   - Pages per year per language (default: 5)
     - Each page contains ~20 movies
     - 5 pages = ~100 movies per year per language

4. Wait for the script to complete (this may take 15-30 minutes depending on your settings)

5. Find your dataset in: `/mnt/user-data/outputs/movie_dataset_1970_to_present.csv`

### Advanced Configuration

You can modify the script to customize:

**Languages**: Currently set to English (Hollywood) and Hindi (Bollywood)
```python
languages=['en', 'hi']
```

Add more languages:
- 'ta' - Tamil
- 'te' - Telugu
- 'ml' - Malayalam
- 'kn' - Kannada
- 'es' - Spanish
- 'fr' - French
- etc.

**Vote Count Filter**: Movies with at least 50 votes (adjustable)
```python
'vote_count.gte': 50
```

**Cast/Keywords Limit**: Currently top 10 cast members and keywords
```python
cast[:10]
keywords[:10]
```

## Expected Dataset Size

With default settings (1970-2024, 5 pages/year):
- ~54 years × 2 languages × 5 pages × 20 movies = ~10,800 movies
- Actual size may vary based on availability

## Rate Limiting

The script includes automatic rate limiting:
- 4 requests per second (0.25s delay)
- Complies with TMDB API guidelines

## Tips for Recommendation Systems

This dataset is well-suited for:

1. **Content-Based Filtering**
   - Use: genres, keywords, directors, cast, overview
   - Create feature vectors from text data

2. **Collaborative Filtering**
   - Use: vote_average, vote_count, popularity
   - Combine with user ratings data

3. **Hybrid Systems**
   - Combine content features with collaborative signals
   - Use metadata for cold-start problems

4. **Natural Language Processing**
   - overview: for semantic similarity
   - keywords: for topic modeling
   - genres: for categorical features

## Troubleshooting

**Error: "Invalid API key"**
- Check your API key is correct
- Ensure you've activated it in TMDB settings

**Error: "Rate limit exceeded"**
- The script includes delays, but if you still hit limits:
- Increase the sleep time: `time.sleep(0.5)`

**Missing data for some movies**
- Some movies may not have all fields (e.g., no keywords, missing cast)
- This is normal - filter or handle missing data in your preprocessing

**Dataset is too large/small**
- Adjust `max_pages_per_year` parameter
- Modify `vote_count.gte` to be more/less selective
- Adjust year range

## Data Quality Notes

- Movies are sorted by popularity within each year
- Duplicates are automatically removed
- Only movies with sufficient vote counts are included
- Both released and upcoming movies may be included

## License

This script uses TMDB API. Please review TMDB's terms of service:
https://www.themoviedb.org/terms-of-use

## Support

For issues with:
- **The script**: Check the error messages and troubleshooting section
- **TMDB API**: Visit https://www.themoviedb.org/talk
- **Missing movies**: TMDB may not have complete data for all films

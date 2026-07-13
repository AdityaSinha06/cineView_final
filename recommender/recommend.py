import argparse
import json
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity


def load_data(base_dir):
    with open(os.path.join(base_dir, "df.pkl"), "rb") as f:
        df = pickle.load(f)
    with open(os.path.join(base_dir, "tfidf_matrix.pkl"), "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open(os.path.join(base_dir, "indices.pkl"), "rb") as f:
        indices = pickle.load(f)
    return df, tfidf_matrix, indices


def normalize_title(title):
    return str(title).strip().lower()


def normalize_index_value(value):
    if hasattr(value, "iloc"):
        try:
            return [int(x) for x in value.tolist()]
        except Exception:
            pass
    if isinstance(value, (list, tuple)):
        return [int(x) for x in value]
    return [int(value)]


def main():
    parser = argparse.ArgumentParser(description="Get movie recommendations from the recommender pickle files.")
    parser.add_argument("title", help="Movie title to get recommendations for")
    parser.add_argument("n", nargs="?", type=int, default=20, help="Number of recommendations")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        df, tfidf_matrix, indices = load_data(base_dir)
    except Exception as exc:
        print(json.dumps({"error": f"Failed to load recommender data: {exc}"}))
        return

    title_key = normalize_title(args.title)
    indices_map = {}
    for key, value in indices.items():
        if key is None or str(key).strip() == "":
            continue
        normalized_key = normalize_title(key)
        values = normalize_index_value(value)
        if normalized_key in indices_map:
            indices_map[normalized_key].extend(values)
        else:
            indices_map[normalized_key] = values

    if title_key not in indices_map:
        print(json.dumps({"error": "Movie not found. Use exact title casing or check the dataset title."}))
        return

    idx_list = sorted(set(indices_map[title_key]))
    if not idx_list:
        print(json.dumps({"error": "Movie index list is empty for this title."}))
        return

    idx = idx_list[0]
    if idx < 0 or idx >= len(df):
        print(json.dumps({"error": "Movie index is invalid in the recommend dataset."}))
        return

    sim_score = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    ranked = sim_score.argsort()[::-1]
    ranked = [i for i in ranked if i != idx]
    limit = min(args.n, len(ranked))
    similar_idx = ranked[:limit]
    recommendations = df["title"].iloc[similar_idx].tolist()
    print(json.dumps({"recommendations": recommendations}))


if __name__ == "__main__":
    main()

const mongoose = require("mongoose");

async function main() {
    await mongoose.connect("mongodb://127.0.0.1:27017/cineView");
}

main()
    .then(() => {console.log("connection successfull!")})
    .catch((err) => {console.log(err);})

const movieSchema = new mongoose.Schema({
    tmdb_id: Number,
    imdb_id: String,
    title: String,
    release_date: String,  // Stored as YYYY-MM-DD (e.g., "1975-08-13")
    genres: [String],
    overview: String,
    keywords: [String],
    directors: [String],
    cast: [String],
    original_language: String,
    poster_url: String,
    popularity: Number,
    vote_average: Number,
    vote_count: Number,
});

const movie = mongoose.model("Movie" , movieSchema);

module.exports = movie;
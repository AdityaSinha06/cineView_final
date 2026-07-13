const fs = require("fs");
const csvParser = require("csv-parser");
const mongoose = require("mongoose");
const Movie = require("../models/moviesModel.js");

async function main() {
    await mongoose.connect("mongodb://127.0.0.1:27017/cineView");
}

main().catch((err) => { console.log("Error: ", err.message); });

async function insertMovies() {
    const movies = []; //first add all the movies to [] as forming [] of objects
    fs.createReadStream("../dataset_builder/data/movies_dataset.csv")
        .pipe(csvParser())
        .on("data", (row) => {
            // Preprocessing the rows
            const processedRow = {
                tmdb_id: parseInt(row.tmdb_id),
                imdb_id: row.imdb_id,
                title: row.title,
                release_date: row.release_date,
                genres: row.genres ? row.genres.split(', ') : [], //splitting the genres/strings by using ',' as de-limiter
                overview: row.overview,
                keywords: row.keywords ? row.keywords.split(', ') : [],
                directors: row.directors ? row.directors.split(', ') : [],
                cast: row.cast ? row.cast.split(', ') : [],
                original_language: row.original_language,
                poster_url: row.poster_url,
                popularity: parseFloat(row.popularity),
                vote_average: parseFloat(row.vote_average),
                vote_count: parseInt(row.vote_count)
            };
            movies.push(processedRow);
        })
        .on("end", async () => {
            try {
                await Movie.deleteMany({});
                console.log("DB reset successfull!");
                await Movie.insertMany(movies);
                console.log("Data has been inserted successfully!");
                mongoose.connection.close();
            } catch (err) {
                console.log("Error inserting data:", err.message);
                mongoose.connection.close();
            }
        })
        .on("error", (err) => {
            console.log("Error reading CSV:", err.message);
        });
}

insertMovies();
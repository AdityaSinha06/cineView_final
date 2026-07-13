const express = require("express");
const { spawn } = require("child_process");
const path = require("path");
const router = express.Router({ mergeParams: true });
const Movie = require("../models/moviesModel.js");

function getRecommendations(movieName, n = 20) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(__dirname, "../recommender/recommend.py");
        const pythonCommand = process.env.PYTHON || "python";
        const child = spawn(pythonCommand, [scriptPath, movieName, n.toString()]);

        let stdout = "";
        let stderr = "";

        child.stdout.on("data", (data) => {
            stdout += data.toString();
        });

        child.stderr.on("data", (data) => {
            stderr += data.toString();
        });

        child.on("close", (code) => {
            if (code !== 0) {
                return reject(new Error(stderr || `Python exited with code ${code}`));
            }
            try {
                const parsed = JSON.parse(stdout);
                resolve(parsed);
            } catch (err) {
                reject(new Error("Invalid recommender response: " + err.message));
            }
        });
    });
}

router.get("/", async (req, res) => {
    const movieName = (req.query.name).trim();
    
    try {
        const recommendations = await getRecommendations(movieName, 20);
        if (recommendations.error) {
            req.flash("error", recommendations.error);
            return res.redirect(`/movies/getrecommendations/form?name=${encodeURIComponent(movieName)}`);
        }
        // console.log(recommendations.recommendations);
        let allMovies = [];
        for (title of recommendations.recommendations) {
            let movie = await Movie.find({title: title});
            // allMovies.push(movie[0]);
            for(mObj of movie) allMovies.push(mObj);
        }
        // console.log(allMovies)
        // need to create all the movie cards like allMovies
        return res.render("./listings/recommendationForm.ejs", {
            query: movieName,
            allMovies
        });
    } catch (err) {
        console.error(err);
        req.flash("error", err.message);
        return res.redirect(`/movies/getrecommendations/form?name=${encodeURIComponent(movieName)}`);
    }
});

router.get("/form", (req, res) => {
    res.render("./listings/recommendationForm.ejs", {
        query: req.query.name || "",
        allMovies: []
    });
});

module.exports = router;

// all movies ::> vectorize , then for the given movie name , 
// calculate the cosine similarity bw the given movie and all other movies

// Intuition: 
// Content Based Recommendation System: 
// - uses attributes such as genre, director, description, actors, etc  for a movie to make suggestions for the users
// - if a user liked a particular movie or show, he/she might like a movie or a show similar to it.

const express = require("express");
const router = express.Router({mergeParams: true});
const Movie = require("../models/moviesModel.js")


// Index-route
router.get('/', async (req, res) => {
    const moviesPerPage = 70;
    let page = parseInt(req.query.page) || 1;

    try {
        const totalMovies = await Movie.countDocuments();
        const totalPages = Math.ceil(totalMovies / moviesPerPage);

        // Safety: Ensure page is within valid range
        if (page < 1) page = 1;
        if (page > totalPages) page = totalPages;

        const allMovies = await Movie.find({})
            .skip((moviesPerPage * page) - moviesPerPage)
            .limit(moviesPerPage);

        res.render('./listings/index.ejs', {
            allMovies,
            currentPage: page,
            totalPages: totalPages
        });
    } catch (err) {
        res.status(500).send("Error loading movies");
    }
});


// Filter route : specific searching
router.get("/filter", async (req, res) => {
    try {
        const filterData = req.query;
        console.log("Raw filter data:", filterData);

        let query = {};

        if (filterData.title && filterData.title.trim()) {
            // regex: Allows partials matchings, checks whether the txt i/p is present in any portion of movies title
            // i : ensures case-insensitiveness
            query.title = { $regex: filterData.title.trim(), $options: 'i' };
        }

        if (filterData.release_date_from || filterData.release_date_to) {
            query.release_date = {};
            if (filterData.release_date_from) {
                query.release_date.$gte = filterData.release_date_from;
            }
            if (filterData.release_date_to) {
                query.release_date.$lte = filterData.release_date_to;
            }
        }

        if (filterData.original_language) {
            // in express, when used a checkbox or multiple i/p with same name:
            // if >= 2 items are selected, that field(filterData.original_language) is a array
            // else : if only 1 item is selected, the field is string: "en" or "hi"
            const languages = Array.isArray(filterData.original_language) 
                ? filterData.original_language 
                : [filterData.original_language];
            query.original_language = { $in: languages };
        }

        // All genres must match in the selected movies
        if (filterData.genres) {
            // same logic, as above
            const genres = Array.isArray(filterData.genres)  
                ? filterData.genres 
                : [filterData.genres];
            query.genres = { $all: genres };
        }

        // At least one keyword matches
        if (filterData.keywords && filterData.keywords.length > 0) {
            query.keywords = { $in: filterData.keywords.map(k => k.toLowerCase()).join(', ') };
        }

        // at least one director matches
        if (filterData.directors && filterData.directors.length > 0) {
            query.directors = { $in: filterData.directors };
        }

        // at least one cast : actor / actress matches
        if (filterData.cast && filterData.cast.length > 0) {
            query.cast = { $in: filterData.cast };
        }

        console.log("MongoDB Query:", query);

        // Executed with Claude from below -----------------------------
        // Execute query with pagination
        const moviesPerPage = 70;
        let page = parseInt(req.query.page) || 1;

        const totalMovies = await Movie.countDocuments(query);
        const totalPages = Math.ceil(totalMovies / moviesPerPage);

        if (page < 1) page = 1;
        if (page > totalPages && totalPages > 0) page = totalPages;

        const filteredMovies = await Movie.find(query)
            .skip((moviesPerPage * page) - moviesPerPage)
            .limit(moviesPerPage);

        console.log(`Found ${totalMovies} movies matching filters`);

        
        res.render('./listings/filtered_index.ejs', {
            allMovies: filteredMovies,
            currentPage: page,
            totalPages: totalPages,
            appliedFilters: filterData,
            moviesFound: totalMovies
            
        });

    } catch (err) {
        console.error("Filter error:", err);
        res.status(500).send("Error filtering movies: " + err.message);
    }
});


router.get("/filter/form" , async (req , res) => {
    const genres = await Movie.distinct("genres");
    const original_languages = await Movie.distinct("original_language");
    res.render("./listings/filter.ejs" , {genres , original_languages});
});


// show route : for a particular movie
router.get("/:id" , async (req , res) => {
    let {id} = req.params;
    const movie = await Movie.findById(id);
    res.render("./listings/show.ejs" , {movie});
});

module.exports = router;
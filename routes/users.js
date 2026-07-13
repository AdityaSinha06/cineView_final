const express = require("express");
const router = express.Router({mergeParams: true});
const passport = require('passport');
const User = require("../models/usersModel.js");
const { isLoggedIn } = require("../middleware.js");
const Movie = require("../models/moviesModel.js");

// user route: 
router.get("/auth" , (req , res) => {
    res.render("./listings/userForm.ejs");
});

router.post("/login" , passport.authenticate("local" , {failureRedirect: "/user/auth" , failureFlash: true}), async (req , res) => {
    req.flash("success" , "welcome back to Cine-View, You are now logged in!");
    res.redirect("/movies");
});

router.post("/signup" , async (req , res) => {
    try {
        let {username , email , password} = req.body.users;
        const newUser = new User({email , username});
        const registeredUser = await User.register(newUser , password);
        // console.log(registeredUser);
        req.login(registeredUser , (er) => {
            if(er) return next(er);
            
            req.flash("success" , "Welcome to Cine-View");
            res.redirect("/movies");
        });
    } catch(err) {
        req.flash("error" , err.message);
        res.redirect("/user/auth");
    }
});

router.get("/logout" , (req , res , next) => {
    req.logout((err) => {
        if(err) return next(err);

        req.flash("success" , "You are now logged out");
        res.redirect("/movies");
    });
})

router.get("/watchlist" , isLoggedIn, async (req , res) => {
    const user = await req.user.populate("watchLaterList");
    const allMovies = user.watchLaterList;
    // console.log(allMovies);

    const moviesPerPage = 70;
    let page = parseInt(req.query.page) || 1;

    const totalMovies = allMovies.length;
    const totalPages = Math.ceil(totalMovies / moviesPerPage);

    // Safety: Ensure page is within valid range
    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;

    res.render("./listings/watchlist.ejs" , {allMovies, currentPage: page , totalPages: totalPages});
});


router.post("/:id/addtoList" , isLoggedIn , async (req , res) => {
    let {id: movieId} = req.params;
    // console.log(movieId);
    
    // add this movie Id to user's watchlaterlist
    // console.log(req.user);
    if(req.user.watchLaterList.includes(movieId)) {
        req.flash("error" , "Movie already exists in the list");
    } else {
        req.user.watchLaterList.push(movieId);

        // console.log(req.user);
        
        await req.user.save();
        req.flash("success" , "Movie added to watch-later list");
    }
    // console.log(req.get("Referer"));
    res.redirect(req.get("Referer"));
});

router.put("/:id/remove" , async (req , res) => {
    let {id: movieId} = req.params;
    const userId = req.user._id;
    await User.findByIdAndUpdate(userId , {$pull: {watchLaterList: movieId}});

    req.flash("success" , "Movie Removed from watch-later list");
    res.redirect("/user/watchlist");
})

module.exports = router;
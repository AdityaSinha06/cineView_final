const express = require("express");
const mongoose = require("mongoose");
const Movie = require("./models/moviesModel.js");
const User = require("./models/usersModel.js");
const path = require("path");
const ejsMate = require('ejs-mate');
const { getSystemErrorMessage } = require("util");
const movieRouter = require("./routes/movies.js");
const userRouter = require("./routes/users.js");
const recommendationRouter = require("./routes/recommendations.js");
const session = require("express-session");
const flash = require("connect-flash");
const passport = require("passport");
const LocalStrategy = require("passport-local");
const app = express();
const port = 8080;
const ExpressError = require("./utils/ExpressError.js");
const methodOverride = require("method-override");
const sessionOptions = require("./utils/sessionConfig.js");

app.set("view engine" , "ejs");
app.set("views" , path.join(__dirname , "views"));
app.engine('ejs', ejsMate);
app.use(express.urlencoded({extended: true})); 
app.use(express.static(path.join(__dirname , "/public")));
app.use(methodOverride("_method"));

app.use(session(sessionOptions));
app.use(flash());

// configuring passport:
app.use(passport.initialize());
app.use(passport.session());
passport.use(new LocalStrategy(User.authenticate()));

passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

// configuring flash : 
app.use((req , res , next) => {
    res.locals.success = req.flash("success");
    res.locals.error = req.flash("error");
    res.locals.currUser = req.user;
    next();
});

async function main() {
    await mongoose.connect("mongodb://127.0.0.1:27017/cineView");
}

main().then(() => {console.log("Connection to DB via mongoose success");})
    .catch(err => {console.log("Error: " , err.message);})


app.get("/" , (req , res) => {
    res.send("Welcome to Server");
});

app.use("/movies/getrecommendations" , recommendationRouter);
app.use("/movies" , movieRouter);
app.use("/user" , userRouter);

app.use((req , res , next) => {
    next(new ExpressError(404 , "Page not found!"));
});

app.use((err , req , res , next) => {
    let {statusCode , message} = err;
    res.render("error.ejs" , {message});
});

app.listen(port , (req , res) => {
    console.log("Server is listening at port: " , port);
});
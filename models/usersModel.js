const mongoose = require("mongoose");
const {Schema} = mongoose;
const passportLocalMongoose = require("passport-local-mongoose").default;

const userSchema = new Schema({
    email: {
        type: String, 
        required: true,
    } , 
    watchLaterList : [
        {
            type: Schema.Types.ObjectId,
            ref: "Movie"
        }
    ]
});

userSchema.plugin(passportLocalMongoose);

module.exports = mongoose.model("User" , userSchema);
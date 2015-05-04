
/**
 * Module dependencies.
 */

var mongoose = require('mongoose');

var Schema = mongoose.Schema;

/**
 * Recipe Schema
 */

var RecipeSchema = new Schema({
  name: { type: String, default: '' }, // name of recipe
  ingrs: { type: String, default: '' }, // ingredients in recipe
  lastCooked: { type: String, default: '' }, // last time recipe was cooked
  other: { type: String, default: '' }, // ingredients whose amounts could not be transformed in gms
  steps: { type: String, default: '' }, // steps of recipe
  time: { type: String, default: '' }, // timing details regarding recipe steps
  image: { type: String, default: '' }, // URL of the recipe image
  rating: { type: String, default: '' }, // Rating of recipe from allrecipes.com
  orderedIngrs: { type: String, default: '' } // Ingredients required stepwise
});

mongoose.model('Recipe', RecipeSchema);


/**
 * Module dependencies.
 */

var mongoose = require('mongoose');

var Schema = mongoose.Schema;

/**
 * Ingredient Schema
 */

/* We are storing name and amount of ingredient in the database. */
var IngredientSchema = new Schema({
  name: { type: String, default: '' },
  amount: { type: String, default: '' }
});

mongoose.model('Ingredient', IngredientSchema);


/**
 * Module dependencies.
 */

var mongoose = require('mongoose');
var Ingredient = mongoose.model('Ingredient');

/**
 * Load All Ingredients
 */

exports.loadAll = function (req, res, next) {
  var options = {};
  Ingredient.find(options, function (err, ingredients) {
    if (err) return next(err);
    if (!ingredients) return next(new Error('Failed to load Ingredients'));
    //console.log(ingredients);

    ingredient_names = [];
    amounts = [];
    ingredients.forEach(function(ingr){
    	ingredient_names.push(ingr['name'].toString());
    	amounts.push(ingr['amount'].toString());
    });
    res.render("inventory",{ingredient_names:ingredient_names,amounts:amounts});
  });
};

/**
 * Add an ingredient
 */

exports.add = function(req,res,next) {

  var ingr_name = req.body.ingr_name;
  var ingr_amount = req.body.ingr_amount;

  var ingr = new Ingredient({name:ingr_name,amount:ingr_amount});
  
  ingr.save(function(err) {
    if(err) {
      var msg = "Could not add inventory";
      res.redirect("/inventory");
    }
    else
    {
      var msg = "Inventory added successfully!";
      res.redirect("/inventory"); 
    }
  });
};

/**
 * Update an ingredient
 */
exports.update = function(req,res,next) {

  var ingr_name = req.body.ingr_name;
  var ingr_amount = req.body.ingr_amount;
  var query = {name: ingr_name}
  
  Ingredient.update(query,{ $set: { amount: ingr_amount }},function(err) {
    if(err) {
      var msg = "Could not update inventory";
      res.redirect("/inventory");
    }
    else
    {
      var msg = "Inventory updated successfully!";
      res.redirect("/inventory"); 
    }
  });
};



/*!
 * Module dependencies.
 */

var recipes = require('recipes');
var ingredients = require('ingredients');

/**
 * Expose routes
 */

module.exports = function (app) {

  // home route
  app.get('/',function(req,res){
    res.render("home");
  });

  // ingredients route
  app.get('/inventory',ingredients.loadAll);
  app.post('/inventory/add_ingr',ingredients.add);
  app.post('/inventory/update_ingr',ingredients.update);
  
  // recipes route
  app.get('/recipes',recipes.loadAll);
  
  app.get('/recipes/getWeight',recipes.getWeight); // Get value of weight scale - RPC call
  app.get('/recipes/fillFluid',recipes.fillFluid); // Fill liquid - RPC call
  app.get('/recipes/ingrDone',recipes.ingr_done); // Rotate motor - RPC call
  app.get('/recipes/orderIngredients',recipes.orderIngredients); // Show ingredients required in recipe step - RPC call
  app.get('/recipes/resetScale',recipes.resetScale); // Tare the weighing scale - RPC call

  app.post('/recipes/recipeContents',recipes.getRecipeDetails);
  app.post('/recipes/fillBox',recipes.fillBox);
  app.post('/recipes/cook',recipes.cookRecipe);
  app.post('/add_recipe',recipes.addRecipe);
  app.post('/recipes/recipeDone',recipes.recipeDone);

  /* This request is for adding sitemap urls */
  //app.get('/add_sitemap_recipe',recipes.addSitemapRecipe);
  //app.get('/add_sitemap',function(req,res,next){res.render('recipes/add_sitemap')});

  //timer notification
  app.get('/recipes/sendAlert', recipes.sendAlert);
  /**
   * Error handling
   */

  app.use(function (err, req, res, next) {
    // treat as 404
    if (err.message
      && (~err.message.indexOf('not found')
      || (~err.message.indexOf('Cast to ObjectId failed')))) {
      return next();
    }
    console.error(err.stack);
    // error page
    res.status(500).render('500', { error: err.stack });
  });

  // assume 404 since no middleware responded
  app.use(function (req, res, next) {
    res.status(404).render('404', {
      url: req.originalUrl,
      error: 'Not found'
    });
  });
}

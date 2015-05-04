
/**
 * Module dependencies.
 */

var mongoose = require('mongoose');
var Recipe = mongoose.model('Recipe');
var Ingredient = mongoose.model('Ingredient');
var IngrImage  = mongoose.model('Image');
var querystring = require('querystring');
var http = require('http');
var url = require('url');

var zerorpc = require("zerorpc");

// Your accountSid and authToken from twilio.com/user/account
var accountSid = 'AC96ac54628e12f5ddd3bc717083fbc229'; 
var authToken = '986fefc5ff26f6612c8c8d9ee47c01f3';
var client = require('twilio')(accountSid, authToken);

var rpc_ip = "158.130.170.3";
var rpcclient = new zerorpc.Client();
rpcclient.connect("tcp://" + rpc_ip + ":4242");

/**
 * Get Recipe Details - Route for /recipes/recipeContents
 */

exports.getRecipeDetails = function (req, res, next) {

  var options = {};
  var ingr_names = [];
  var ingr_amounts = [];
  var ingr_images = [];
  var selected_images = [];

  /* Get all ingredients from database */
  Ingredient.find(options, function (err, ingredients) {
    if (err) return next(err);
    if (!ingredients) return next(new Error('Failed to load Ingredients'));

    ingr_amounts = [];
    ingredients.forEach(function(ingr){
      ingr_names.push(ingr['name']);
      ingr_amounts.push(ingr['amount']);
    });

  });
  
  /* Get list of all images of ingredients in database */
  IngrImage.find(options, function (err, images) {
    if (err) return next(err);
    if (!images) return next(new Error('Failed to load Ingredients'));

    ingr_images = [];
    images.forEach(function(img){
      ingr_images.push(img['ingr']);
    });
  });

  var recipe_name = req.body.recipe_name;

  /* Get recipe details from database by recipe name */
  Recipe.find({name:recipe_name}, function (err, recipe) {
    if (err) return next(err);
    if (!recipe) return next(new Error('Failed to load Recipe'));
    var solids_with_amounts = recipe[0]['ingrs'].split("@");

    var ingrs = [];               // Ingredients list
    var amounts = [];             // Amount of ingredient
    var liquid_vector = [];       // Indicate if ingredient is liquid or not
    var other = recipe[0]['other'];
    var recipe_image = recipe[0]['image'];
    var recipe_rating = recipe[0]['rating'];
    var ingrs_in_inventory = [];
    var ingrs_in_inventory_amount = [];

    //console.log(solids_with_amounts);
    
    for(var i=0; i < solids_with_amounts.length;i+=3)
    {
      /* Check if ingredient is also in inventory */

      /* First: check for exact match and then check for contains */
      var solid_in_inventory = 0;
      var ingr_to_push = "";
      var amount_to_push = "";
      var inv_ingr_to_push = "";
      var inv_amount_to_push = "";

      /* Check if ingredient required is in inventory */
      for(var j=0;j<ingr_names.length;j++)
      {
        if(solids_with_amounts[i].toLowerCase().indexOf(ingr_names[j].toLowerCase()) != -1)
        //if(ingr_names[j].indexOf(solids_with_amounts[i]) != -1)
        {
          ingr_to_push = solids_with_amounts[i];
          amount_to_push = solids_with_amounts[i+1];
          inv_ingr_to_push = ingr_names[j];
          inv_amount_to_push = ingr_amounts[j];
          
          solid_in_inventory = 1;

          if(ingr_names[j] == solids_with_amounts[i])
            break;
        }
      }

      if(solid_in_inventory)
      {
        ingrs.push(ingr_to_push);
        amounts.push(amount_to_push);
        ingrs_in_inventory.push(inv_ingr_to_push);
        ingrs_in_inventory_amount.push(inv_amount_to_push);
      }
      else
      {
        /* If item is not in inventory, add to other*/
        if (other == "")
          other = solids_with_amounts[i]
        else
          other = other + ", " + solids_with_amounts[i];
      }
    }

    //console.log(ingr_names);
    //console.log(ingr_amounts);

    /* Check if any ingredient has corresponding image in our database */
    selected_images = [];
    for(var i=0; i < ingrs.length;i++)
    {
      var img_match_found = 0;
      for(var j=0;j < ingr_images.length;j++)
      {
        if(ingrs[i].toLowerCase().indexOf(ingr_images[j].toLowerCase()) != -1)
        {
          selected_images.push(ingr_images[j]);
          img_match_found = 1;
          break;
        }
      }
      if(img_match_found == 0)
        selected_images.push("0")
    }
    res.render("recipes/recipeContents",{recipe_name:recipe_name,ingrs:ingrs.join("@"),amounts:amounts.join("@"),
      inv_names:ingrs_in_inventory.join("@"),inv_amounts:ingrs_in_inventory_amount.join("@"),other:other,
      recipe_image:recipe_image,recipe_rating:recipe_rating,ingr_images:selected_images.join("@")});
  });
};

/**
 * Fill Ingredient Box - route for /recipes/fillBox
 */

exports.fillBox = function (req, res, next) {

  var recipe_name = req.body.recipe_name;

  Recipe.find({name:recipe_name}, function (err, recipe) {
    if (err) return next(err);
    if (!recipe) return next(new Error('Failed to load Recipe'));
    var solids = recipe[0]['ingrs'].split("@");

    var ingrs = [];
    var amounts = [];
    var bit_vector = [];
    var other = recipe[0]['other'];

    solids.forEach(function(ingr,index){
      if(index % 3 == 0)
        ingrs.push(ingr);
      else if((index-1) % 3 == 0 )
        amounts.push(ingr);
      else
        bit_vector.push(ingr);
    });

    res.render("recipes/fillBox",{recipe_name:recipe_name,ingrs:ingrs.join("@"),
      amounts:amounts.join("@"),bit_vector:bit_vector.join("@"),other:other});
  });
};

/**
 * Get Weight Sensor Values by RPC call
 */
exports.getWeight = function (req, res, next) {

  rpcclient.invoke("get_sensor_value", function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });

}

/**
 * Ingredient Done - RPC call
 */
exports.ingr_done = function (req, res, next) {

  var url_parts = url.parse(req.url, true);
  var ingr_name = url_parts.query.ingrName; // Pass ingredient name as argument

  rpcclient.invoke("ingredient_done", ingr_name ,function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });
}

/**
 * Order Ingredients - RPC call
 */
exports.orderIngredients = function (req, res, next) {

  var url_parts = url.parse(req.url, true);
  var orderedIngrs = url_parts.query.orderedIngrs; // Pass list of ingredients in current step as argument

  rpcclient.invoke("order", orderedIngrs ,function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });
}

/**
 * Fill Liquid - Route for /recipes/fillFluid - RPC call
 */
exports.fillFluid = function (req, res, next) {

  var url_parts = url.parse(req.url, true);
  var lq_vol = url_parts.query.liquid_volume; // pass liquid volume as argument
  
  rpcclient.invoke("fluidMotor",lq_vol,function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });
}

/**
 * Reset Weight Scale - RPC call
 */
exports.resetScale = function (req, res, next) {

  rpcclient.invoke("tare", function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });
}



/**
 * Cook Recipe - route for /recipes/cook
 */

exports.cookRecipe = function (req, res, next) {

  var recipe_name = req.body.recipe_name;

  Recipe.find({name:recipe_name}, function (err, recipe) {
    if (err) return next(err);
    if (!recipe) return next(new Error('Failed to load Recipe'));
    
    var steps = recipe[0]['steps'];
    var timer_vals = recipe[0]['time'];
    var orderedIngrs = recipe[0]['orderedIngrs'];
    //console.log(steps);
    //console.log(timer_vals);
    res.render("recipes/cook",{recipe_name:recipe_name,steps:steps,timer_vals:timer_vals,orderedIngrs:orderedIngrs})
  });
};


/**
 * Load All Recipes - Route for /recipes
 */

exports.loadAll = function (req, res, next) {
  var options = {};
  Recipe.find(options, function (err, recipes) {
    if (err) return next(err);
    if (!recipes) return next(new Error('Failed to load Recipes'));
    recipe_names = [];
    timestamps = [];
    ratings = [];
    recipes.forEach(function(recipe){
    	recipe_names.push(recipe['name']);
    	timestamps.push(recipe['lastCooked']);
      ratings.push(recipe['rating'])
    });
    res.render("recipes",{recipe_names:recipe_names,timestamps:timestamps,ratings:ratings});
  });
};

/**
 * Add New Recipe - Route for /add_recipe
 */

exports.addRecipe = function (req, res, next) {

  var url = req.body.recipe_url;
  var post_data = querystring.stringify({
      //'recipe_url' : 'http://allrecipes.com/recipe/tangy-honey-glazed-ham/?prop24=hn_slide1_Tangy-Honey-Glazed-Ham&evt19=1'
      'recipe_url' : url
  });

  var options = {
    host: "localhost",
    port: 4567,
    path: '/recipe',
    method: 'POST'
  };

  /* Preparing request for ruby server */
  var post_request = http.request(options, function(res) {
      res.setEncoding('utf8');
      res.on('data', function (chunk) {
        //console.log('BODY: ' + chunk);
        console.log(chunk);
        var recipe_data = chunk, obj = JSON.parse(recipe_data);
        var recipename = obj.recipename;
        var ingrs = obj.ingrs;
        var other = obj.other;
        var steps = obj.steps;
        var time = obj.time;
        var image = obj.image;
        var rating = obj.rating;
        var orderedIngrs = obj.orderedIngrs;

        //console.log(obj.recipename);
        var recipe = new Recipe({name:recipename,ingrs:ingrs,other:other,steps:steps,time:time,
          image:image,rating:rating,lastCooked:"0",orderedIngrs:orderedIngrs});
        recipe.save(function(err) {
          if(err) {
            var msg = "Could not add recipe.";
            //res.redirect("/recipes");
          }
          else
          {
            var msg = "Recipe added successfully!";
            //res.redirect("/recipes"); 
          }
        });
      });
      //res.redirect("/recipes");
    });

  /* Make call to Ruby Server */
  post_request.write(post_data);
  post_request.end("test");
  res.redirect('/');
}

/**
 * Update Done Recipe - Route for /recipes/recipeDone
 */

exports.recipeDone = function (req, res, next) {
    var recipe_name = req.body.recipe_name;
    var query = { name: recipe_name };

    /* Code to update timestamp of recipe last cooked */
    var lastCooked = (new Date()).toString();
    Recipe.update(query,{lastCooked:lastCooked},function(err) {
      if(err) {
        var msg = "Could not update recipe.";
        res.redirect("/recipes");
      }
      else
      {
        var msg = "Recipe added successfully!";
        res.redirect("/recipes"); 
      }
    });
} 

/**
 * Send alerts to phone.
 */
exports.sendAlert = function (req, res, next) {
    /* Send alert to phone using Twilio */
    client.messages.create({ 
      to: "+12152859314", 
      from: "+14843620689", 
      body: "Alert: The current step will be done in a minute.",   
    }, function(err, message) { 
      console.log(message.sid); 
    });
    //res.write("Message Sent..!");
    
  //console.log("before rpc call..");
  //var rpcclient = new zerorpc.Client();
  //rpcclient.connect("tcp://" + rpc_ip + ":4242");

  // Make RPC call to buzz
  rpcclient.invoke("sound", function(error, res1, more) {  
    console.log(res1);
    res.write(res1);
    res.end();
  });
  //res.end();
}
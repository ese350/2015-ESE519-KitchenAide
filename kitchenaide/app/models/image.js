
/**
 * Module dependencies.
 */

var mongoose = require('mongoose');

var Schema = mongoose.Schema;

/**
 * Image Schema - This collection holds URLs of images stored to show ingredient image to user
 */

var ImageSchema = new Schema({
  ingr: { type: String, default: '' }
});

mongoose.model('Image', ImageSchema);

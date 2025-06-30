const mongoose = require('mongoose');
delete mongoose.connection.models['listings']; // 💀 flush the old model
const ListingSchema = new mongoose.Schema({
  Global_Room_ID: {
    type: String,
    required: true
  },
  Host_ID: {
    type: Number,
    required: true
  },
  is_Active: {
    type: Boolean,
    required: true
  },
  Price_by_type: {
    type: String,
    required: true
  },
  Property_ID: {
    type: Number,
    required: true
  },
  Property_Name: {
    type: String,
    required: true
  },
  Room_types: {
    type: String,
    required: true
  }
});

module.exports = mongoose.model('listings', ListingSchema);



const mongoose = require('mongoose');

const ListingSchema = new mongoose.Schema({
  Price_by_type: {
    type: String,
    required: true
  },
  Property_address: {
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
  },
  Total_rooms_for_type: {
    type: String,
    required: true
  },
  User_ID: {
    type: Number,
    required: true
  }
});

module.exports = mongoose.model('Listing', ListingSchema, 'listings'); // 💥 collection name forced

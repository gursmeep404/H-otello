const mongoose = require('mongoose');

const BookingSchema = new mongoose.Schema({
  booked_by: {
    type: String,
    required: true
  },
  booked_for_dates: {
    type: String,
    required: true
  },
  property_id: {
    type: Number,
    required: true
  },
  room_type: {
    type: String,
    required: true
  },
  user_id: {
    type: Number,
    required: true
  }
});

module.exports = mongoose.model('bookings', BookingSchema);
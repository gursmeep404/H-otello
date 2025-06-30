const mongoose = require('mongoose');

const BookingSchema = new mongoose.Schema({
  Amount_paid: {
    type: Number,
    required: true
  },
  booked_by: {
    type: String,
    required: true
  },
  check_in: {
    type: Date,
    required: true
  },
  check_out: {
    type: Date,
    required: true
  },
  Guest_name: {
    type: String,
    required: true
  },
  owner_id: {
    type: Number,
    required: true
  },
  property_id: {
    type: String,
    required: true
  },
  room_id: {
    type: String,
    required: true
  },
  room_type: {
    type: String,
    required: true
  }
}, { timestamps: true }); // optional: adds createdAt and updatedAt

module.exports = mongoose.model('bookings', BookingSchema);

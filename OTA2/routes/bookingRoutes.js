const express = require('express');
const router = express.Router();
const Booking = require('../models/bookings');

router.post('/', async (req, res) => {
  try {
    const booking = new Booking(req.body);
    await booking.save();
    res.status(201).json(booking);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get('/', async (req, res) => {
  try {
    const bookings = await Booking.find();
    res.json(bookings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const booking = await Booking.findById(req.params.id);
    if (!booking) return res.status(404).send("Not found");
    res.json(booking);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const updated = await Booking.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(updated);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.delete('/', async (req, res) => {
  try {
    const { room_id } = req.query;

    if (!room_id) {
      return res.status(400).json({ message: "room_id is required in query." });
    }

    const result = await Booking.deleteOne({ room_id });

    if (result.deletedCount === 0) {
      return res.status(404).json({ message: "No booking found with that room_id." });
    }

    res.json({ message: `Booking with room_id ${room_id} deleted.` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;

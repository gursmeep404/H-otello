const express = require('express');
const router = express.Router();
const Listing = require('../models/listings');

router.post('/', async (req, res) => {
  try {
    const listing = new Listing(req.body);
    await listing.save();
    res.status(201).json(listing);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get('/', async (req, res) => {
  try {
    const listings = await Listing.find();
    res.json(listings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const listing = await Listing.findById(req.params.id);
    if (!listing) return res.status(404).send("Not found");
    res.json(listing);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.put('/', async (req, res) => {
  try {
    const { Global_Room_ID } = req.query;
    const updateData = req.body;

    if (!Global_Room_ID) {
      return res.status(400).json({ message: "Global_Room_ID is required in query." });
    }

    const updatedListing = await Listing.findOneAndUpdate(
      { Global_Room_ID }, // filter
      updateData,         // what to update
      { new: true }       // return updated doc
    );

    if (!updatedListing) {
      return res.status(404).json({ message: "Listing not found." });
    }

    res.json({ message: "Listing updated successfully", data: updatedListing });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


router.delete('/', async (req, res) => {
  try {
    const { Global_Room_ID } = req.query;

    if (!Global_Room_ID) {
      return res.status(400).json({ message: "Global_Room_ID is required in query." });
    }

    const result = await Listing.deleteOne({ Global_Room_ID });

    if (result.deletedCount === 0) {
      return res.status(404).json({ message: "No listing found with that Global_Room_ID." });
    }

    res.json({ message: `Listing with Global_Room_ID ${Global_Room_ID} deleted.` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


module.exports = router;
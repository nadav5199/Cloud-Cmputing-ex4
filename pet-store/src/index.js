import express from "express";
import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { connectDB, getCollection } from './db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// Configuration from environment variables
const PORT = process.env.PORT || 5001;
const NINJA_API_KEY = process.env.NINJA_API_KEY || "LTdiBLKLgYtxViDRO8yNjA==5WsW9gTJ1AMC9FnD";
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const MONGO_COLLECTION = process.env.MONGO_COLLECTION || 'pet-store1';

let collection;

// Pictures directory
const picturesDir = path.join(__dirname, "pictures");
if (!fs.existsSync(picturesDir)) {
  fs.mkdirSync(picturesDir, { recursive: true });
}

// Helper functions
function parseLifespan(lifespanStr) {
  if (!lifespanStr) return null;

  // Extract numbers from the string
  const numbers = lifespanStr.match(/\d+/g);
  if (!numbers || numbers.length === 0) return null;

  // Return the lowest number
  return parseInt(numbers[0]);
}

function parseAttributes(temperament, groupBehavior) {
  // Prefer temperament over group_behavior
  const source = temperament || groupBehavior;
  if (!source) return [];

  // Split by common delimiters and filter out punctuation
  return source
    .split(/[\s,]+/)
    .map(word => word.replace(/[.,;:!?]/g, ''))
    .filter(word => word.length > 0);
}

function compareDates(dateStr1, dateStr2) {
  // Convert DD-MM-YYYY to comparable format
  const [d1, m1, y1] = dateStr1.split('-').map(Number);
  const [d2, m2, y2] = dateStr2.split('-').map(Number);

  const date1 = new Date(y1, m1 - 1, d1);
  const date2 = new Date(y2, m2 - 1, d2);

  return date1 - date2;
}

async function fetchFromNinjaAPI(animalType) {
  try {
    const response = await axios.get('https://api.api-ninjas.com/v1/animals', {
      params: { name: animalType },
      headers: { 'X-Api-Key': NINJA_API_KEY }
    });

    if (response.status !== 200) {
      throw new Error(`API response code ${response.status}`);
    }

    if (!response.data || response.data.length === 0) {
      return null;
    }

    // Find exact match (case insensitive)
    const exactMatch = response.data.find(
      animal => animal.name.toLowerCase() === animalType.toLowerCase()
    );

    return exactMatch || response.data[0];
  } catch (error) {
    if (error.response) {
      throw new Error(`API response code ${error.response.status}`);
    }
    throw error;
  }
}

async function downloadImage(url, filename) {
  try {
    const response = await axios.get(url, { responseType: 'arraybuffer' });
    const filepath = path.join(picturesDir, filename);
    fs.writeFileSync(filepath, response.data);
    return filename;
  } catch (error) {
    throw error;
  }
}

// Transform MongoDB document to API format
function mongoToApi(doc) {
  const petsData = doc.petsData || {};
  return {
    id: doc.id,
    type: doc.type,
    family: doc.family,
    genus: doc.genus,
    attributes: doc.attributes,
    lifespan: doc.lifespan,
    pets: Object.values(petsData).map(pet => pet.name)
  };
}

// Root endpoint
app.get("/", (req, res) => {
  res.send("Initial connection");
});

// POST /pet-types - Create a new pet type
app.post("/pet-types", async (req, res) => {
  try {
    // Validate content type
    if (!req.is('application/json')) {
      return res.status(415).json({ error: "Expected application/json media type" });
    }

    const { type } = req.body;

    if (!type) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Check if pet type already exists (case-insensitive)
    const existing = await collection.findOne({
      type: { $regex: new RegExp(`^${type}$`, 'i') }
    });

    if (existing) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Fetch from Ninja API
    let animalData;
    try {
      animalData = await fetchFromNinjaAPI(type);
    } catch (error) {
      if (error.message.startsWith('API response code')) {
        return res.status(500).json({ "server error": error.message });
      }
      return res.status(500).json({ "server error": "API error" });
    }

    if (!animalData) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Generate unique ID (find max ID and increment)
    const maxDoc = await collection.find().sort({ id: -1 }).limit(1).toArray();
    const id = maxDoc.length > 0 ? String(parseInt(maxDoc[0].id) + 1) : "1";

    // Extract data from Ninja API
    const family = animalData.taxonomy?.family || "";
    const genus = animalData.taxonomy?.genus || "";
    const lifespan = parseLifespan(animalData.characteristics?.lifespan);
    const attributes = parseAttributes(
      animalData.characteristics?.temperament,
      animalData.characteristics?.group_behavior
    );

    const petTypeDoc = {
      id,
      type: animalData.name,
      family,
      genus,
      attributes,
      lifespan,
      petsData: {}
    };

    await collection.insertOne(petTypeDoc);

    res.status(201).json(mongoToApi(petTypeDoc));
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// GET /pet-types - Get all pet types with optional filters
app.get("/pet-types", async (req, res) => {
  try {
    const query = {};

    // Apply filters
    const { id, type, family, genus, lifespan, hasAttribute } = req.query;

    if (id) {
      query.id = id;
    }

    if (type) {
      query.type = { $regex: new RegExp(`^${type}$`, 'i') };
    }

    if (family) {
      query.family = { $regex: new RegExp(`^${family}$`, 'i') };
    }

    if (genus) {
      query.genus = { $regex: new RegExp(`^${genus}$`, 'i') };
    }

    if (lifespan) {
      query.lifespan = parseInt(lifespan);
    }

    if (hasAttribute) {
      query.attributes = {
        $regex: new RegExp(`^${hasAttribute}$`, 'i')
      };
    }

    const results = await collection.find(query).toArray();
    const formatted = results.map(doc => mongoToApi(doc));

    res.status(200).json(formatted);
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// GET /pet-types/:id - Get a specific pet type
app.get("/pet-types/:id", async (req, res) => {
  try {
    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    res.status(200).json(mongoToApi(petType));
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// DELETE /pet-types/:id - Delete a pet type
app.delete("/pet-types/:id", async (req, res) => {
  try {
    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    // Check if there are any pets
    const petsData = petType.petsData || {};
    if (Object.keys(petsData).length > 0) {
      return res.status(400).json({ error: "Malformed data" });
    }

    await collection.deleteOne({ id: req.params.id });

    res.status(204).send();
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// POST /pet-types/:id/pets - Add a pet to a pet type
app.post("/pet-types/:id/pets", async (req, res) => {
  try {
    // Validate content type
    if (!req.is('application/json')) {
      return res.status(415).json({ error: "Expected application/json media type" });
    }

    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    const { name, birthdate, "picture-url": pictureUrl } = req.body;

    if (!name) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Check if pet name already exists for this type
    const petsData = petType.petsData || {};
    if (petsData[name.toLowerCase()]) {
      return res.status(400).json({ error: "Malformed data" });
    }

    const pet = {
      name,
      birthdate: birthdate || "NA",
      picture: "NA"
    };

    // Download picture if URL provided
    if (pictureUrl) {
      try {
        const extension = pictureUrl.split('.').pop().split('?')[0];
        const filename = `${name}-${petType.type}.${extension}`;
        await downloadImage(pictureUrl, filename);
        pet.picture = filename;
      } catch (error) {
        // If download fails, picture remains "NA"
      }
    }

    // Add pet to MongoDB
    await collection.updateOne(
      { id: req.params.id },
      { $set: { [`petsData.${name.toLowerCase()}`]: pet } }
    );

    res.status(201).json(pet);
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// GET /pet-types/:id/pets - Get all pets of a type with optional filters
app.get("/pet-types/:id/pets", async (req, res) => {
  try {
    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    const petsData = petType.petsData || {};
    let results = Object.values(petsData);

    // Apply birthdate filters
    const { birthdateGT, birthdateLT } = req.query;

    if (birthdateGT) {
      results = results.filter(pet => {
        if (pet.birthdate === "NA") return false;
        return compareDates(pet.birthdate, birthdateGT) > 0;
      });
    }

    if (birthdateLT) {
      results = results.filter(pet => {
        if (pet.birthdate === "NA") return false;
        return compareDates(pet.birthdate, birthdateLT) < 0;
      });
    }

    res.status(200).json(results);
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// GET /pet-types/:id/pets/:name - Get a specific pet
app.get("/pet-types/:id/pets/:name", async (req, res) => {
  try {
    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    const petsData = petType.petsData || {};
    const pet = petsData[req.params.name.toLowerCase()];

    if (!pet) {
      return res.status(404).json({ error: "Not found" });
    }

    res.status(200).json(pet);
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// PUT /pet-types/:id/pets/:name - Update a pet
app.put("/pet-types/:id/pets/:name", async (req, res) => {
  try {
    // Validate content type
    if (!req.is('application/json')) {
      return res.status(415).json({ error: "Expected application/json media type" });
    }

    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    const petsData = petType.petsData || {};
    const existingPet = petsData[req.params.name.toLowerCase()];

    if (!existingPet) {
      return res.status(404).json({ error: "Not found" });
    }

    const { name, birthdate, "picture-url": pictureUrl } = req.body;

    if (!name) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Create updated pet object
    const updatedPet = {
      name,
      birthdate: birthdate !== undefined ? (birthdate || "NA") : existingPet.birthdate,
      picture: existingPet.picture
    };

    // Download picture if URL provided
    if (pictureUrl) {
      const extension = pictureUrl.split('.').pop().split('?')[0];
      const filename = `${name}-${petType.type}.${extension}`;

      // Only download if URL is different
      if (existingPet.picture !== filename) {
        try {
          await downloadImage(pictureUrl, filename);

          // Delete old picture if it exists
          if (existingPet.picture !== "NA") {
            const oldPath = path.join(picturesDir, existingPet.picture);
            if (fs.existsSync(oldPath)) {
              fs.unlinkSync(oldPath);
            }
          }

          updatedPet.picture = filename;
        } catch (error) {
          // If download fails, keep existing picture
        }
      }
    }

    // Update MongoDB
    const updateOps = {};

    // If name changed, remove old entry and add new one
    if (name.toLowerCase() !== req.params.name.toLowerCase()) {
      updateOps[`$unset`] = { [`petsData.${req.params.name.toLowerCase()}`]: "" };
      await collection.updateOne({ id: req.params.id }, updateOps);

      await collection.updateOne(
        { id: req.params.id },
        { $set: { [`petsData.${name.toLowerCase()}`]: updatedPet } }
      );
    } else {
      // Just update the existing entry
      await collection.updateOne(
        { id: req.params.id },
        { $set: { [`petsData.${name.toLowerCase()}`]: updatedPet } }
      );
    }

    res.status(200).json(updatedPet);
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// DELETE /pet-types/:id/pets/:name - Delete a pet
app.delete("/pet-types/:id/pets/:name", async (req, res) => {
  try {
    const petType = await collection.findOne({ id: req.params.id });

    if (!petType) {
      return res.status(404).json({ error: "Not found" });
    }

    const petsData = petType.petsData || {};
    const pet = petsData[req.params.name.toLowerCase()];

    if (!pet) {
      return res.status(404).json({ error: "Not found" });
    }

    // Delete picture file if it exists
    if (pet.picture !== "NA") {
      const picturePath = path.join(picturesDir, pet.picture);
      if (fs.existsSync(picturePath)) {
        fs.unlinkSync(picturePath);
      }
    }

    // Remove pet from MongoDB
    await collection.updateOne(
      { id: req.params.id },
      { $unset: { [`petsData.${req.params.name.toLowerCase()}`]: "" } }
    );

    res.status(204).send();
  } catch (error) {
    res.status(500).json({ "server error": error.message });
  }
});

// GET /pictures/:filename - Get a picture
app.get("/pictures/:filename", (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(picturesDir, filename);

  if (!fs.existsSync(filepath)) {
    return res.status(404).json({ error: "Not found" });
  }

  // Determine content type based on extension
  const ext = path.extname(filename).toLowerCase();
  let contentType = "image/jpg";

  if (ext === ".png") {
    contentType = "image/png";
  } else if (ext === ".jpg" || ext === ".jpeg") {
    contentType = "image/jpg";
  }

  res.setHeader("Content-Type", contentType);
  res.sendFile(filepath);
});

// GET /kill - Testing endpoint for Docker restart
app.get("/kill", (req, res) => {
  res.status(200).send("Pet-store shutting down...");
  setTimeout(() => process.exit(1), 100);
});

// Connect to MongoDB and start server
(async () => {
  try {
    collection = await connectDB(MONGO_URI, 'petstore', MONGO_COLLECTION);
    app.listen(PORT, () => console.log(`Pet-store running on port ${PORT}`));
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
})();

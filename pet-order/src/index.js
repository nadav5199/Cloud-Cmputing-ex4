import express from "express";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { connectDB } from './db.js';

const app = express();
app.use(express.json());

// Configuration from environment variables
const PORT = process.env.PORT || 5003;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017';
const PET_STORE_1_URL = process.env.PET_STORE_1_URL || 'http://pet-store1:5001';
const PET_STORE_2_URL = process.env.PET_STORE_2_URL || 'http://pet-store2:5002';
const OWNER_PASSWORD = 'LovesPetsL2M3n4';

let collection;

// POST /purchases - Customer purchases pet
app.post("/purchases", async (req, res) => {
  try {
    const { purchaser, "pet-type": petType, store, "pet-name": petName } = req.body;

    // Validation
    if (!purchaser || !petType) {
      return res.status(400).json({ error: "Malformed data" });
    }

    if (petName && !store) {
      return res.status(400).json({ error: "Malformed data" });
    }

    if (store && (store !== 1 && store !== 2)) {
      return res.status(400).json({ error: "Malformed data" });
    }

    // Determine stores to query
    const storesToQuery = store ? [store] : [1, 2];
    let availablePets = [];

    // Query each store
    for (const storeId of storesToQuery) {
      const storeUrl = storeId === 1 ? PET_STORE_1_URL : PET_STORE_2_URL;

      try {
        // Find pet-type by name
        const typesRes = await axios.get(`${storeUrl}/pet-types`, {
          params: { type: petType },
          timeout: 5000
        });

        if (typesRes.data.length === 0) continue;

        // Check ALL matching pet-types (there may be multiple with same name)
        for (const petTypeData of typesRes.data) {
          // Get pets of this type
          const petsRes = await axios.get(
            `${storeUrl}/pet-types/${petTypeData.id}/pets`,
            { timeout: 5000 }
          );

          // Filter by pet-name if specified
          for (const pet of petsRes.data) {
            if (petName && pet.name.toLowerCase() !== petName.toLowerCase()) {
              continue;
            }

            availablePets.push({
              store: storeId,
              petTypeId: petTypeData.id,
              pet: pet
            });
          }
        }
      } catch (error) {
        // Store down or pet-type doesn't exist
        console.error(`Failed to query store ${storeId}:`, error.message);
      }
    }

    // Check if any pets found
    if (availablePets.length === 0) {
      return res.status(400).json({ error: "No pet of this type is available" });
    }

    // Randomly select pet
    const selected = availablePets[Math.floor(Math.random() * availablePets.length)];
    const storeUrl = selected.store === 1 ? PET_STORE_1_URL : PET_STORE_2_URL;

    // Delete pet from store
    try {
      await axios.delete(
        `${storeUrl}/pet-types/${selected.petTypeId}/pets/${selected.pet.name}`,
        { timeout: 5000 }
      );
    } catch (error) {
      return res.status(500).json({ "server error": "Failed to remove pet from store" });
    }

    // Create transaction
    const purchaseId = uuidv4();
    const transaction = {
      "purchase-id": purchaseId,
      purchaser: purchaser,
      "pet-type": petType,
      "pet-name": selected.pet.name,
      store: selected.store,
      timestamp: new Date()
    };

    await collection.insertOne(transaction);

    // Return response (without timestamp)
    res.status(201).json({
      "purchase-id": transaction["purchase-id"],
      purchaser: transaction.purchaser,
      "pet-type": transaction["pet-type"],
      "pet-name": transaction["pet-name"],
      store: transaction.store
    });

  } catch (error) {
    console.error("Purchase error:", error);
    res.status(500).json({ "server error": error.message });
  }
});

// GET /transactions - Owner views purchases
app.get("/transactions", async (req, res) => {
  try {
    // Check authorization
    const ownerPC = req.headers['ownerpc'];
    if (ownerPC !== OWNER_PASSWORD) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    // Build query from filters
    const query = {};

    if (req.query.store) {
      query.store = parseInt(req.query.store);
    }

    if (req.query['pet-type']) {
      query["pet-type"] = {
        $regex: new RegExp(`^${req.query['pet-type']}$`, 'i')
      };
    }

    if (req.query.purchaser) {
      query.purchaser = {
        $regex: new RegExp(`^${req.query.purchaser}$`, 'i')
      };
    }

    if (req.query['purchase-id']) {
      query["purchase-id"] = req.query['purchase-id'];
    }

    // Query MongoDB
    const transactions = await collection.find(query).toArray();

    // Format response (remove _id and timestamp)
    const response = transactions.map(t => ({
      "purchase-id": t["purchase-id"],
      purchaser: t.purchaser,
      "pet-type": t["pet-type"],
      store: t.store
    }));

    res.status(200).json(response);

  } catch (error) {
    console.error("Transactions error:", error);
    res.status(500).json({ "server error": error.message });
  }
});

// GET /kill - Testing endpoint
app.get("/kill", (req, res) => {
  res.status(200).send("Pet-order shutting down...");
  setTimeout(() => process.exit(1), 100);
});

// Connect to MongoDB and start server
(async () => {
  try {
    collection = await connectDB(MONGO_URI, 'petstore', 'transactions');

    // Create indexes
    await collection.createIndex({ "purchase-id": 1 }, { unique: true });
    await collection.createIndex({ store: 1 });
    await collection.createIndex({ "pet-type": 1 });

    app.listen(PORT, () => console.log(`Pet-order running on port ${PORT}`));
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
})();

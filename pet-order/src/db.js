import { MongoClient } from 'mongodb';

let client = null;
let collection = null;

export async function connectDB(uri, dbName, collectionName) {
  if (client) return collection;

  client = new MongoClient(uri);
  await client.connect();

  const db = client.db(dbName);
  collection = db.collection(collectionName);

  // Create indexes for transactions
  await collection.createIndex({ "purchase-id": 1 }, { unique: true });
  await collection.createIndex({ store: 1 });
  await collection.createIndex({ "pet-type": 1 });

  console.log(`Connected to ${dbName}.${collectionName}`);
  return collection;
}

export function getCollection() {
  if (!collection) throw new Error('DB not connected');
  return collection;
}

export async function closeDB() {
  if (client) {
    await client.close();
    client = null;
    collection = null;
  }
}

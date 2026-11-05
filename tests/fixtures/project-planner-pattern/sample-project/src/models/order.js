const Database = require("better-sqlite3");
const db = new Database("orders.db");

exports.find = (id) => db.prepare("SELECT * FROM orders WHERE id = ?").get(id);

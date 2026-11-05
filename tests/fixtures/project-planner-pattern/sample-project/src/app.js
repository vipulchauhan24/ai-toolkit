const express = require("express");
const orders = require("./controllers/orderController");

const app = express();
app.set("view engine", "ejs");
app.set("views", __dirname + "/views");
app.get("/orders/:id", orders.show);
app.listen(3000);

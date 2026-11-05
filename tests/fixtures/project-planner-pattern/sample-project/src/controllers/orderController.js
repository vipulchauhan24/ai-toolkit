const Order = require("../models/order");

exports.show = (req, res) => {
  const order = Order.find(req.params.id);
  if (!order) return res.status(404).send("Not found");
  res.render("order", { order });
};

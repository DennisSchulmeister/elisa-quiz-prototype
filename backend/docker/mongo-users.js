db = db.getSiblingDB("elisa");

db.createUser({
    user:  "mongo",
    pwd:   "mongo",
    roles: [{role: "readWrite", db: "elisa"}],
});

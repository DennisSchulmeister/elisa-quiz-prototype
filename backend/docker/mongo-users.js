// Switch to "admin" database and create the new users there. This saves us
// from passing "?authSource=other_db" in the connection string.
db = db.getSiblingDB("admin");

db.createUser({
    user:  "mongo",
    pwd:   "mongo",
    roles: [
        {role: "readWrite", db: "analytics"},
        {role: "readWrite", db: "error"},
        {role: "readWrite", db: "user"},
    ],
});

conn = new Mongo();
db = conn.getDB("bloomberg");
print(db.articles.find().count());

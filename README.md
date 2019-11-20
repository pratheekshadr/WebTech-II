
1. to start server  - open command prompt
mongod

2. 	Connect to mongoDB -- open new command prompt
"C:\Program Files\MongoDB\Server\3.4\bin\mongo.exe

3. to run flask - open command prompt
    python app.py  
    (runs on port 5000)


1. On normla terminal(not in mongo shell) -  to create table from csv
Syntax:     mongoimport -d [dbName] -c [tableName] --type CSV --file [csvName] --headerline
    mongoimport -d wt -c users --type CSV --file users.csv --headerline
    mongoimport -d wt -c offer --type CSV --file offer.csv --headerline

Extra:
Queries on mongo shell
1 use wt     (switches to wt db)

2. show db   (shows dbs)

3. show collections   ( shows tables)

4. db.users.find({})  		(shows data inside users table)
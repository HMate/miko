#Miko - micro library application 

To start the application run `docker-compose up` from the root directory. 
This will start the web service. 
By default it will listen for requests on the url http://127.0.0.1:5000 

### REST api: 

 - **/books** : Returns all the book acquisitions in the database.
   Use query parameters to filter for specific books. The following attributes can be used for filtering:
   - uid
   - author
   - title
   - publisher
   - publish_year
   - acquire_date
   - issue_count
 - **/books/insert** : Inserts a new book acquisition. Have to include the properties in a json body 
 - **/stat/**: Can query various statistics about the contained books
   - **/stat/average_books_age** : Average age of all the books inside the library
   - **/stat/author_book_count** : Count of books from the same author
   - **/stat/publisher_book_count** : Count of books from the same publisher
   - **/stat/oldest_youngest_books** : The oldest and the youngest books in the library
   - **/stat/author_books_until_year** : How many books we had for an author until the given year
   - **/stat/author_average_acquire** : How much time did it took the library to acquire a book from an author on average
   - **/stat/author_third_book_issues** : How many copies do we have from the third published book of an author. 

### Examples :

Query books with curl whose author is Brad and the library acquired them in 2015:
```
curl "http://127.0.0.1:5000/books?author=Brad&acquire_date=2015"
```

Query the author_books_until_year statistic:
```
curl "http://127.0.0.1:5000/stat/author_books_until_year"
```

Insert new book through curl
```
curl -H "Content-Type: application/json" -d '{
"title": "Ghost",
"publisher": "Atheneum/Caitlyn Dlouhy Books",
"publish_year": 2016,
"author": "Jason Reynolds",
"acquire_date": "2019-04-30",
"issue_count": 1}' "http://127.0.0.1:5000/books/insert"
```

Insert new book through powershell:
```
PS C:\> $body = [System.Text.Encoding]::UTF8.GetBytes(@"
 {
 "title": "Good Omens",
 "publisher": "William Morrow",
 "publish_year": "2006",
 "author": "Neil Gaiman, Terry Pratchett",
 "acquire_date": "2020-08-20",
 "issue_count": "4"
 }
"@)
PS C:\> Invoke-RestMethod http://127.0.0.1:5000/books/insert -Method POST -Body $body -ContentType 'application/json'
```

###For developers:

####Architecture
The application consists of 4 docker images: miko-app, miko-dal, miko-datastore and rabbitmq.<br>
miko-app is a web service which implements the miko rest api. 
It communicates with the database through the rabbitmq message broker server. 
The image miko-dal contains the python app which listens for requests from the rmq queues and 
creates the concrete queries to the postgres database contained in miko-datastore. 

To setup the whole system, run `docker-compose up` from the root directory.<br>
To start in development mode, run it with `docker-compose -f docker-compose.dev.yml up`. 
In development mode the ports of the postgres and rabbitmq servers are exposed 
to the host machine, so its easier to manage them with pgadmin, rabbitmq-manager etc. 
This also enables to run the python applications on the host, and connect to the images network.
Volumes are also shared between the host and the containers, so its easier to restart the 
apps after code change.


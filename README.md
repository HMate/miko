Miko - micro library application

### REST api: 

http://127.0.0.1:5000/books : Returns all the book acquisitions in the database
http://127.0.0.1:5000/books/9 : Returns book acquisition with unique identifier 9  
http://127.0.0.1:5000/books/insert : Inserts a new book acquisition. Have to include the properties in a json body 

http://127.0.0.1:5000/stat/average_books_age
http://127.0.0.1:5000/stat/author_book_count
http://127.0.0.1:5000/stat/publisher_book_count
http://127.0.0.1:5000/stat/oldest_youngest_books
http://127.0.0.1:5000/stat/author_books_until_year
http://127.0.0.1:5000/stat/author_average_acquire
http://127.0.0.1:5000/stat/author_third_book_issues


### Exmaple to insert book through the rest api:

In powershell:
```
PS C:\> $body = @"
 {
 "title": "Good Omens",
 "publisher": "William Morrow",
 "publish_year": "2006",
 "author": "Neil Gaiman, Terry Pratchett",
 "acquire_date": "2020-08-20",
 "issue_count": "4"
 }
 "@
PS C:\> Invoke-RestMethod http://127.0.0.1:5000/books/insert -Method POST -Body $body -ContentType 'application/json'
```
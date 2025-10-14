import pytest
from library_service import (
    add_book_to_catalog, borrow_book_by_patron, get_book_by_isbn,
    return_book_by_patron,calculate_late_fee_for_book, search_books_in_catalog, get_patron_status_report
)
from database import(
    get_all_books
)

#R1 Test Cases
def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567990125", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_title_too_long():
    """Test adding a book with a title too long"""
    success, message =add_book_to_catalog("TestBoooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooook"
                                           , "Test Author", "1234567890129", 5)
    assert success == False
    assert "200 or Less Characters" in message
    

def test_add_book_invalid_author_too_long():
    """Test adding a bOok with a author name too long"""
    success, message = add_book_to_catalog("Test Book", "Test Authorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", "1234567890127", 5)
    assert success == False
    assert "100 or Less Characters" in message

def test_add_book_invalid_totalcopies_negative():
    """Test adding a how many copies wanted being a negative or zero"""

    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890128", -5)
    
    assert success == False
    assert "Must be a positive Integer" in message

def test_add_book_valid_input_2():
    """Test adding numbers in the title"""

    success, message = add_book_to_catalog("Test Book23", "Test Author", "8234567890128", 3)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_ISBN():
    """Testing putting an invalid ISBN"""
    success, message = add_book_to_catalog("Test Book23", "Test Author", "abcdefghijklm", 3)
    
    assert success == False
    assert "Must only be digits" in message.lower()







#R2 Test Cases
"""Visual Test done on the `http://localhost:5000` to ensure that the system displays all books in the catalog in a table
format showing the following: Book ID, Title, Author, ISBN, Available copies / Total copies as well as the actions(Burrow Button)"""

def test_get_all_books_valid():
    add_book_to_catalog("Glass", "Onion", "8374659283745", 2)
    books = get_all_books()
    assert books["title"] == "Glass"


#R3 Test Cases
def test_book_borrowing_valid():
    """Test borrowing a book with valid input"""
    isbn = "2123456789876"
    success, message = add_book_to_catalog("TestBook23", "TestAuthor23", isbn, 3)
    assert success == True
    assert "successfully added" in message.lower()

    book = get_book_by_isbn(isbn)
    assert book is not None
    book_id = book["id"]

    success, message = borrow_book_by_patron("012345", book_id)
    assert success == True
    assert "book borrowed" in message.lower()

def test_book_borrowing_invalid_patron_id():
    """Test borrowing a book when patron ID is not 6 digits"""
    isbn = "2222222222222"
    success, _ = add_book_to_catalog("Journal12", "Journal12Author", isbn, 2)
    assert success == True

    book = get_book_by_isbn(isbn)
    assert book is not None
    success, message = borrow_book_by_patron("12345", book["id"]) 
    assert success == False
    assert "invalid patron id" in message.lower()

def test_borrow_max_5_books_same_patron():
    """Test the max borrowing limit of 5"""
    isbn = "9000000000000"

    add_book_to_catalog("PercyJackson", "JK", isbn, 6)
    book = get_book_by_isbn(isbn)
    for i in range(5):
        success, message = borrow_book_by_patron("000000", book["id"])
        assert success == True
    success, message = borrow_book_by_patron("000000", book["id"])
    assert success == False
    assert "max" in message.lower() 


def test_book_borrowing_book_not_found():
    """Testng if the the book does not exist"""
    success, message = borrow_book_by_patron("123456", 500000)  
    assert success == False

    assert "not found" in message.lower()

def test_borrow_invalid_6_books():
    """Test the max borrowing by borrowing 6"""
    isbn = "6767454523231"

    add_book_to_catalog("Location", "David", isbn, 6)
    book = get_book_by_isbn(isbn)
    for i in range(6):
        success, message = borrow_book_by_patron("824343", book["id"])
        if i<5:
            assert success == True
        else:
            assert success == False
            assert "max" in message.lower() 


#R4 Test Cases
def test_return_book_valid():
    """Test the returning a book with a valid input"""
    isbn = "3333333333333"
    success, message = add_book_to_catalog("BobMarley", "Dave", isbn, 1)
    assert success == True

    book = get_book_by_isbn(isbn)
    borrow,message = borrow_book_by_patron("876876",book["id"])

    assert borrow == True

    returnbook, message = return_book_by_patron("876876", book["id"])
    assert returnbook == True
    assert "book successfully returned" in message.lower()


def test_return_book_invalid_patron_id():
    """Test if the patron ID in corelation to the book is invalid"""
    isbn = "4444444444444"
    add_book_to_catalog("VybzKartel", "Spice", isbn, 1)
    book = get_book_by_isbn(isbn)
    borrow_book_by_patron("222222", book["id"])

    success, message = return_book_by_patron("0023", book["id"]) 
    assert success == False
    assert "invalid patron id" in message.lower()

def test_return_updates_available_copies():
    """Test the update of Copies of books"""
    isbn = "8768768768768"
    add_book_to_catalog("SoSick", "Neyo",isbn, 1)
    book = get_book_by_isbn(isbn)


    borrow_book_by_patron("989898", book["id"])
    assert get_book_by_isbn(isbn)["available_copies"] == 0  
    return_book_by_patron("989898", book["id"])
    assert get_book_by_isbn(isbn)["available_copies"] == 1  


def test_return_book_twice_invalid():
    """Test if someone tries to return a book twice"""
    isbn = "7666566666661"
    add_book_to_catalog("LilBaby", "Gunna", isbn, 1)
    book = get_book_by_isbn(isbn)


    borrow_book_by_patron("676767", book["id"])
    return_book_by_patron("676767", book["id"])


    success, message = return_book_by_patron("676767",book["id"])
    assert success == False

    assert "no active borrow" in message.lower() 

def test_return_book_different_patron():
    """Test when a different patron ID tries to return a book"""
    isbn = "7666566664661"
    add_book_to_catalog("BTS", "BlackPink", isbn, 1)
    book = get_book_by_isbn(isbn)
    success,message =borrow_book_by_patron("848848", book["id"])
    assert success == True
    success,message = return_book_by_patron("888888", book["id"])
    assert success == False
    assert "Different patron ID" in message.lower()



#R5 Test Cases
def test_no_late_fees():
    """Test if book is returnd before due date"""
    result = calculate_late_fee_for_book("242424",1)
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] ==0
    assert "status" in result

def test_late_fee_four_days_overdue():
    """Test the correct amount being charged after 4 days"""
    result = calculate_late_fee_for_book("984575",2)
    assert result["days_overdue"] == 4
    assert result["fee_amount"] ==2.00
    assert "status" in result

def test_late_fee_seven_days_overdue():
    """Test correct amount being charged afer 7 days"""
    result = calculate_late_fee_for_book("436743",3)
    assert result["days_overdue"] == 7
    assert result["fee_amount"] ==3.50
    assert "status" in result

def test_late_fee_ten_days_overdue():
    """Test correct amount being charged after 10 days"""
    result = calculate_late_fee_for_book("436748",4)
    assert result["days_overdue"] == 10
    assert result["fee_amount"] ==6.50
    assert "status" in result

def test_late_fee_max_per_book():
    """Test the maximim of $15 per book"""
    result = calculate_late_fee_for_book("857439", 5)
    assert result["days_overdue"] >= 19
    assert result["fee_amount"]>= 15.00
    assert "status" in result



#R6 Test Cases
def test_search_title_name():
    """Test searching for the title of a book"""
    add_book_to_catalog("Unwritten Love Story","Natasha", "7436293409885",1)
    result = search_books_in_catalog("Love", "title")
    assert result[0]["title"] == "Unwritten Love Story"

def test_search_author_name():
    """Test searching for the title of an author"""
    add_book_to_catalog("Work", "Rihanna","6644664466447",1)
    result = search_books_in_catalog("Rihanna", "author")
    assert result[0]["author"] == "Rihanna"

def test_search_isbn_number():
    """Test searching for the isbn number"""
    add_book_to_catalog("Too Much", "Drake", "1333333333333",1)
    result = search_books_in_catalog("1333333333333", "isbn")
    assert result[0]["isbn"] == "1333333333333"

def test_search_not_found():
    """Test searching for a title but not found"""
    add_book_to_catalog("Sky Priority", "Rod Wave", "2333333333333",1)
    result = search_books_in_catalog("Let", "title")
    assert result == []

def test_invalid_search_of_ISBN_using_title():
    """Test searching for a book with wrong search type"""
    isbn = "2333333333334"
    add_book_to_catalog("King and the Pawns","Queen", isbn,3)
    success,message = search_books_in_catalog("King", isbn)
    assert success == False
    assert "invalid search for an isbn" in message.lower()

#R7 Test Cases
def test_patron_status_borrowed_books():
    """Test display of patron status for borrowed books"""
    report = get_patron_status_report("012345")
    assert "borrowed_books" in report

def test_patron_status_total_fees():
    """Test display of patron status for total fees"""
    report = get_patron_status_report("012345")
    assert "total_fees" in report

def test_patron_status_num_books():
    """Test display of patron status for numbe of books borrowed"""
    report = get_patron_status_report("012345")
    assert "books_borrowed_count" in report

def test_patron_status_history():
    """Test display of patron status for borow history"""
    report = get_patron_status_report("012345")
    assert "borrowing_history" in report

def test_patron_id_invalid():
    """Test that the patron id is invalid"""
    success = get_patron_status_report("abcdef")
    assert success == False 

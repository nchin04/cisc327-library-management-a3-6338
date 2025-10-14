"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books, get_db_connection
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    if not isbn.isdigit():
        return False,"ISBN must be only digits"
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:

    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_ids = [borrowed["book_id"] for borrowed in borrowed_books]

    if book_id not in borrowed_ids:
        return False, f"Patron ID {patron_id} did not borrow Book ID {book_id} or has been retrned try again"
    

    return_date = datetime.now()

    update_borrow_record_return_date(patron_id, book_id, return_date)
    update_book_availability(book_id, +1)
    return True, f"Book {book_id} returned sucessfully by patron ID:{patron_id}"


    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    return False, "Book return functionality is not yet implemented."

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    
    simulated_days_overdue = { #for test script
        1: 0,    
        2: 4,   
        3: 7,    
        4: 10,   
        5: 20    
    }

    days_overdue = simulated_days_overdue.get(book_id, 0)

    if days_overdue <= 7:
        fee = days_overdue * 0.5
    else:
        fee = (7 * 0.5) + ((days_overdue - 7) * 1.0)

    if fee > 15:
        fee = 15.0

    status = "Retrned on time" if days_overdue == 0 else f"{days_overdue} days overdue"

    return {
        "fee_amount":fee,
        "days_overdue": days_overdue,
        "status": status
    }
   

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
   

    results = []

    if search_type not in ["isbn", "title", "author"]:
        return False, "Invalid search for an isbn"


    if not search_term or not search_type:
        return results

    if search_type == "isbn":
        book = get_book_by_isbn(search_term)
        if book:
            results.append(book)


    elif search_type == "title":
        books = get_all_books()
        for book in books:
            if search_term.lower() in book["title"].lower():
                results.append(book)


    elif search_type == "author":
        books = get_all_books()
        for book in books:
            if search_term.lower() in book["author"].lower():
                results.append(book)

    return results


    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    


def get_patron_status_report(patron_id: str) -> Dict:

    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    borrowed_books =get_patron_borrowed_books(patron_id)
    total_fees = 0.0

    for book in borrowed_books:
        
        fee_info= calculate_late_fee_for_book(patron_id, book["book_id"])
        total_fees += fee_info["fee_amount"]

        
    conn = get_db_connection()
    records = conn.execute('''
        SELECT br.book_id, b.title, b.author
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date
    ''', (patron_id,)).fetchall()
    conn.close()

    borrow_history = []
    for record in records:
        borrow_history.append({
            "book_id": record["book_id"],
            "title": record["title"],
            "author":record["author"],


        })

    report = {
        "patron_id":patron_id,
        "borrowed_books": borrowed_books,
        "books_borrowed_count":len(borrowed_books),
        "total_fees":total_fees,
        "borrowing_history": borrow_history

    }

    return report
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
  

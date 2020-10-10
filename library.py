from prettytable import PrettyTable
import sys

import sqlite3
import datetime
conn = sqlite3.connect('library.db')

## PICK WHICH LIBRARY YOU WANT 
def intro():
    
    cur = conn.cursor()
    cur.execute("SELECT libraryName FROM Library")
    rows = cur.fetchall()
    if rows:
        print("Please select from the following libraries:\n")
    else:
        print("There are no libraries.")
    
    for row in rows:
        print('\t'+row[0])
    print("\n")
    library = input("Which library would you like to visit?\n")
    print("\n")
    check = libraryCheck(library)
    if (check == 1):
        print("ERROR: Such library does not exist.")
        print("Please reselect an existing library.\n")
        return intro()
    else:
        print("Succesfully connected to: " + library + '\n')
        return library

## CHECK LIBRARY
def libraryCheck(library):
    cur = conn.cursor()
    query = "SELECT COUNT(*) FROM Library WHERE libraryName=:nameOfLibrary"
    cur.execute(query,{"nameOfLibrary":library})
    count = cur.fetchall()
    if (count[0][0]<=0):
        return 1
    else:
        return 0

## LOGIN
def login():
    personID = input("Please enter your personID number: ")
    cur = conn.cursor()

    myQuery = "SELECT * FROM Person WHERE personID=:myID"
    cur.execute(myQuery, {"myID": personID})
    rows = cur.fetchall()
    
    for row in rows:
        if personID == str(row[0]):
            print("Welcome " + row[1] + ' ' + row[2] + "\n")
            return personID

    print("ERROR: Invalid ID\n")
    return login()

## SELECTION 
def select():
    print("What task would you like to do?")
    print("1. Find an item")
    print("2. Borrow an item")
    print("3. Donate an item")
    print("4. Find event(s)")
    print("5. Register for an event")
    print("6. Volunteer for the Library")
    print("7. Ask for help from a librarian")
    print("8. Reselect Library")
    print("9. Return item")
    print("10. Exit application")
    print("\n")

    task = input("Enter the number: ")

    choices = ('1','2','3','4','5','6','7','8','9','10')

    if task in choices:
        return task

    else:
        print("Please choose a valid number\n")
        return select()


## FIND ITEM IN LIBRARY
def findItem(library):
    cur = conn.cursor()
    title = input("Please input the title of the item or press enter to list all items: ")

    if title == '':
        myQuery = "SELECT * FROM Item WHERE libraryName =:myLibrary"
        cur.execute(myQuery,{"myLibrary":library})
        rows = cur.fetchall()
    else:
        myQuery = "SELECT * FROM Item WHERE libraryName =:myLibrary AND title =:myTitle"
        cur.execute(myQuery,{"myLibrary":library, "myTitle":title})
        rows = cur.fetchall()

    t = PrettyTable(['itemID', 'library name', 'title', 'type', 'author', 'stock'])

    for row in rows:
        t.add_row([row[0], row[1], row[2], row[3], row[4], row[5]])

    print(t)
    print("\n")

    choice = input("Would you like to seach for a different item? (Y/N): ")

    if choice == 'y' or choice == 'Y':
        return findItem(library)
    else:
        return select()


## BORROW ITEM
def borrowItem(library,person):
    cur = conn.cursor()
    itemID = input("Please input the itemID of the item or press enter to list all items: ")

    if itemID == '':
        myQuery = "SELECT * FROM Item WHERE libraryName =:myLibrary"
        cur.execute(myQuery,{"myLibrary":library})
        rows = cur.fetchall()

        t = PrettyTable(['itemID', 'library name', 'title', 'type', 'author', 'stock'])

        for row in rows:
            t.add_row([row[0], row[1], row[2], row[3], row[4], row[5]])

        print(t)
        print("\n")
        
        itemID = input("Please input the itemID of the item: ")
    
    myQuery = "SELECT * FROM Item WHERE libraryName =:myLibrary AND itemID =:myID"
    cur.execute(myQuery,{"myLibrary":library, "myID":itemID})
    rows = cur.fetchall()

    if rows:
        for row in rows:
            if row[5] == 0:
                print("This item is not in stock at the moment")
                choice = input("Would you like to borrow another item? (Y/N): ")
                if choice == 'y' or choice == 'Y':
                    return borrowItem(library,person)
                else:
                    return select()
            else:
                newStock = row[5] - 1
                myQuery = "UPDATE Item SET instock =:myStock WHERE libraryName =:myLibrary AND itemID =:myID"
                cur.execute(myQuery, {"myStock": newStock, "myLibrary":library, "myID":itemID})
                dueDate = (datetime.date.today() + datetime.timedelta(365/12)).isoformat()
                myQuery = "INSERT INTO Borrows (itemID, libraryName, personID, dueDate) VALUES ( ?, ?, ?, ? )"
                values = (itemID, library, person, dueDate)
                cur.execute(myQuery, values)
                print("Item successfully borrowed")
                choice = input("Would you like to borrow another item? (Y/N): ")
                if choice == 'y' or choice == 'Y':
                    return borrowItem(library,person)
                else:
                    return select()
    
    else:
        print("Please enter a valid itemID\n")
        return borrowItem(library,person)


## DONATE ITEM
def donateItem(library):

    title = input("Please enter the title of the item: ")
    itemType = input("Please enter the type of the item: ")
    author = input("Please enter the author of the item: ")
    stock = input("Please enter the amount of this item you are donating: ")

    if stock.isdigit() == False:
        print("Invalid input, please try again\n")
        return donateItem(library)

    cur = conn.cursor()

    myQuery = "INSERT INTO Item (libraryName, title, type, author, inStock) VALUES (?,?,?,?,?)"
    values = (library, title, itemType, author, stock)
    cur.execute(myQuery,values)

    print("Donation success!")
    print("Thank you for your donation!\n")
    choice = input("Would you like to donate another item? (Y/N): ")
    
    if choice == 'y' or choice == 'Y':
        return donateItem(library)
    else:
        print("Returning to main menu\n")
        return select()

def findEvent(library):
    cur = conn.cursor()

    eventName = input("Please enter the name of the event or press enter to list all events at this library: ")
    if eventName == '':
        myQuery = "SELECT * FROM Event WHERE libraryName =:myLibrary"
        cur.execute(myQuery,{"myLibrary":library})
        rows = cur.fetchall()
        t= PrettyTable(['eventName', 'eventDate', 'startTime', 'endTime', 'eventType', 'recommended_Audience', 'roomNumber'])

        for row in rows:
            t.add_row([row[2], row[3], row[4], row[5], row[6], row[7], row[8]])
        print(t)
        print("\n")
        
    else:
        myQuery = "SELECT * FROM Event WHERE libraryName =:myLibrary AND eventName =:myEvent"
        cur.execute(myQuery,{"myLibrary":library, "myEvent":eventName})
        rows = cur.fetchall()
        t= PrettyTable(['eventName', 'eventDate', 'startTime', 'endTime', 'eventType', 'recommended_Audience', 'roomNumber'])

        for row in rows:
            t.add_row([row[2], row[3], row[4], row[5], row[6], row[7], row[8]])
        print(t)
        print("\n")
    
    choice = input("Would you like to search for a different event? (Y/N): ")

    if choice == 'y' or choice == 'Y':
        return findEvent(library)
    else:
        print("Returning to main menu\n")
        return select()

## REGISTER FOR EVENT
def registerEvent(library,person):
    cur = conn.cursor()
    myQuery = "SELECT * FROM Event WHERE libraryName =:myLibrary"
    cur.execute(myQuery,{"myLibrary":library})
    rows = cur.fetchall()
    if (rows):
        print("You can register for the following events at your designated library: ")
        t= PrettyTable(['eventID', 'eventName', 'eventDate', 'startTime', 'endTime', 'eventType', 'recommended_Audience', 'roomNumber'])
        
        for row in rows:
            t.add_row([row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8]])
        print(t)
        return checkEvent(library,person)

    else:
        print("\nThere are no events at your designated library.\n")
        print("Returning to the menu\n")
        return select()

## CHECK EVENT
def checkEvent(library,person):
    cur = conn.cursor()
    idOfEvent= input("Please input the ID of the event you want to register for: ")
    query = "SELECT * FROM Event where eventID= " + idOfEvent + " AND libraryName = '" + library +"';"
    cur.execute(query)
    result = cur.fetchall()
    if not(result):
        print ("Invalid ID entered.\n")
        return registerEvent(library,person)

    myQuery = "SELECT COUNT(*) FROM Attends WHERE eventID=" + idOfEvent + " AND libraryName= '" + library + "' and personID= " + person + ";"
    cur.execute(myQuery)
    count= cur.fetchall()
    if(count[0][0]>0):
        print("You are already registered for the selected event!")
        print("Returning to the main menu.\n")
        return select()

    ## Registering for the Event 
    myQuery= 'INSERT INTO Attends(eventID,libraryName,personID) VALUES(?,?,?);'
    values=(idOfEvent,library,person)
    cur.execute(myQuery,values)
                    
    print("Event Registered!")
    print("Returning to the main menu.")
    return select()

## VOLUNTEER FOR LIBRARY
def volunteer(libary,person):
    check = input("Do you want to volunteer for the current library? (Y/N)")
    if (check == "Y" or check == "y"):
        cur= conn.cursor()
        myQuery= "SELECT COUNT(*) FROM Volunteers WHERE libraryName= '"+ library + "' AND personID= " + person + ";"
        cur.execute(myQuery)
        count = cur.fetchall()
        if (count[0][0]>0):
            print("You already volunteer for this library!")
            print("Returning to the main menu.\n")
            return select()
        else:
            myQuery= "INSERT INTO Volunteers(libraryName,personID) VALUES(?,?);"
            values= (library,person)
            cur.execute(myQuery,values)

            print("You now volunteer for the current library!")
            print("Returning to the main menu.\n")
            return select()
    if (check =="N"):
        print("Returning to the main menu.\n")
        return select()

## ASK FOR HELP
def help(library,helper):

    if helper != '':
        print("It looks like someone is already helping you!\n")
        return select(), helper
            
    print("Looking for a librarian to help you at your library!")
    cur= conn.cursor()
    countQuery= "SELECT COUNT(*) FROM Personnel WHERE available=1 AND libraryName= " + "'" + library + "'"
    cur.execute(countQuery)
    count = cur.fetchall()
    if (count[0][0] <= 0):
        print("No librarians are available to help you right now! Please try again later.\n")
        print("Returning to the main menu.\n")
        return select(), helper

    myQuery= "SELECT employeeID,firstName,lastName FROM Personnel WHERE available=1 AND libraryName= " + "'" + library + "'"
    cur.execute(myQuery)
    results = cur.fetchall()
    eid= results[0][0]
    firstName = results[0][1]
    lastName= results[0][2]
    print(firstName + " " + lastName + " will help you now.\n")

    myQuery= "UPDATE Personnel SET available = 0 WHERE employeeID = " + str(eid)
    cur.execute(myQuery)
    print("Returning to the main menu.\n")
    return select(), eid

## RETURN ITEM
def returnItem(library,person):
    cur = conn.cursor()
    myQuery = "SELECT * FROM Borrows WHERE personID =:myPerson AND libraryName =:myLibrary"
    cur.execute(myQuery, {"myPerson":person, "myLibrary":library})
    rows = cur.fetchall()

    t = PrettyTable(['itemID', 'title', 'dueDate'])

    borrowed = []

    for row in rows:
        myQuery = "SELECT title FROM Item WHERE itemID =:myItem AND libraryName =:myLibrary"
        cur.execute(myQuery, {'myItem':row[0], 'myLibrary':library})
        title = cur.fetchall()
        t.add_row([row[0],title,row[3]])
        borrowed.append(str(row[0]))
    
    if rows:
        print(t)
        print('\n')

        itemID = input("Enter the itemID of the item you would like to return: ")

        if itemID not in borrowed:
            print("ERROR: Please enter a valid ID\n")
            return returnItem(library,person)

        myQuery = "DELETE FROM Borrows WHERE personID =:myPerson AND itemID =:myItem"
        cur.execute(myQuery, {"myPerson":person, "myItem":itemID})
        
        myQuery = "SELECT * FROM Item WHERE libraryName =:myLibrary AND itemID =:myID"
        cur.execute(myQuery,{"myLibrary":library, "myID":itemID})
        rows = cur.fetchall()
        
        for row in rows:
            stock = row[5] + 1

        myQuery = "UPDATE Item SET inStock =:newStock WHERE itemID =:myItem"
        cur.execute(myQuery, {"newStock":stock, "myItem":itemID})

        print("Successfully returned item\n")

        choice = input("Would you like to return another item? (Y/N): ")

        if choice == 'Y' or choice == 'y':
            return returnItem(library,person)
        else:
            print("Returning to the main menu.")
            return select()

    else:
        print("You have no items to return\n")
        print("Returning to main menu\n")
        return select()

conn = sqlite3.connect('library.db')
with conn:
    print("Welcome to the Library application!")
    library = intro()
    person = login()
    task = select()
    helper = ''
    while True:
        if task == '1':
            task = findItem(library)
        elif task == '2':
            task = borrowItem(library, person)
        elif task == '3':
            task = donateItem(library)
        elif task == '4':
            task = findEvent(library)
        elif task == '5':
            task = registerEvent(library,person)
        elif task == '6':
            task = volunteer(library,person)
        elif task == '7':
            task, helper = help(library,helper)
        elif task == '8':
            library = intro()
            task = select()
        elif task == '9':
            task = returnItem(library,person)
        else:
            if helper.isdigit():
                cur = conn.cursor()
                myQuery= "UPDATE Personnel SET available = 1 WHERE employeeID = " + str(helper)
                cur.execute(myQuery)
            print("Exiting application")
            break

conn.close()


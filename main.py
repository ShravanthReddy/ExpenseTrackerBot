import mysql.connector
import logging as NULL
import datetime
import time as t
from telebot import types, apihelper
from settings import API_KEY, HOST, PASSWORD
import telebot
from telegramcalendar import create_calendar

while True:
    
    bot = telebot.TeleBot(API_KEY)
    apihelper.SESSION_TIME_TO_LIVE = 60 * 5

    current_shown_dates = {}
    expense_dict = {}

    class expense:
        def __init__(self, name):
            self.customerid = name
            self.description = None
            self.amount = None
            self.dateOfExpense = None
            self.expenseIdDict = list()
            self.serialNumDict = list()

    optionA = 'Record Expense'
    optionB = 'Track Expenses'
    optionC = 'Sum of all Expenses'
    optionD = 'Go to Main menu'
    optionE = 'Exit'
    optionF = 'Delete Expenses'
    optionG = 'Edit Expenses'
    optionH = 'Edit Description'
    optionI = 'Edit Amount'
    optionJ = 'Edit Date'
    optionK = 'Go Back'

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    markup1 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    markup2 = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton(optionA)
    itembtn2 = types.KeyboardButton(optionB)
    itembtn3 = types.KeyboardButton(optionC)
    itembtn4 = types.KeyboardButton(optionD)
    itembtn5 = types.KeyboardButton(optionE)
    itembtn6 = types.KeyboardButton(optionF)
    itembtn7 = types.KeyboardButton(optionG)
    itembtn8 = types.KeyboardButton(optionH)
    itembtn9 = types.KeyboardButton(optionI)
    itembtn10 = types.KeyboardButton(optionJ)
    itembtn11 = types.KeyboardButton(optionK)
    markup.add(itembtn1, itembtn2, itembtn5)
    markup1.add(itembtn3, itembtn6, itembtn7, itembtn4, itembtn5)
    markup2.add(itembtn8, itembtn9, itembtn10, itembtn11, itembtn5)

    mydb = mysql.connector.connect(user='root', password=PASSWORD, host=HOST, database='sql_expensebot')
    mycursor = mydb.cursor()

    #start command handler
    @bot.message_handler(commands=['start'])
    def start(message):
        username = message.chat.first_name 
        bot.send_message(message.chat.id, "Hello " +str(username)+ ", welcome! I'm your personal expense tracker. Hope you are doing well.\nAre you tired of forgetting where you spent your money? you're not alone. ;)\n")
        bot.send_chat_action(message.chat.id, action='typing')
        bot.send_message(message.chat.id, "I am here to help you. You will be able to track and record your expenses as you wish. It's just like texting a friend. Trust me it's that easy.")
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.2)
        reply = bot.send_message(message.chat.id, "So let's begin. Choose an option to continue: ", reply_markup=markup)
        bot.register_next_step_handler(reply, check)

    #continue command handler
    @bot.message_handler(commands=['continue'])
    def cont(message):
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        reply = bot.send_message(message.chat.id, 'Select any option below to continue:', reply_markup=markup)
        bot.register_next_step_handler(reply, check)

    #other commands handler
    @bot.message_handler(func=lambda message: True)
    def all(message):
        bot.send_message(message.chat.id, 'Wrong input, please try again. \ntap /continue or /start to record or track your expenses.')

    #check1
    def check(message):
        if message.text == optionA:
            recordExpense(message)
        elif message.text == optionB:
            trackExpense(message)
        elif message.text == optionE:
            exitFunc(message)
        else:
            bot.send_message(message.chat.id, 'Wrong option selected, please try again')
            cont(message)

    #record expense initiation
    def recordExpense(message):
        customerid = customeridExtraction(message)
        if customerid == 0:
            customerRegistration(message)
        customerid = customeridExtraction(message)
        chat_id = message.chat.id
        initiation(customerid, chat_id)
        expenseDetailsRecorderDescription(message)

    #function to initialize class expense
    def initiation(mainvar, chat_id):
        initvar = expense(mainvar)
        expense_dict[chat_id] = initvar
        expense.customerid = mainvar

    #extracting customer id function
    def customeridExtraction(message):
        username = message.chat.id
        mycursor.execute("select customer_chatid, customer_id from customer_details")
        customerid = 0
        for i in mycursor.fetchall():
            result = i[0]
            if result == username:
                customerid = i[1]
        return customerid

    #customer registration
    def customerRegistration(message):
        username = str(message.chat.username)
        chat_id = message.chat.id
        firstname = str(message.chat.first_name)
        sqlform = "Insert into customer_details(customer_chatid, customer_username, customer_firstname, date_created) values (%s, %s, %s, %s)"
        details = [(chat_id, username, firstname, datetime.date.today())]
        mycursor.executemany(sqlform, details)

    #expense data description recorder function
    def expenseDetailsRecorderDescription(message):
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        bot.send_message(message.chat.id, 'Enter a short description of your expense (For ex: Movie Tickets)')
        bot.register_next_step_handler(message, expenseDetailsRecorderAmount)

    #expense data amount recorder function
    def expenseDetailsRecorderAmount(message):
        chat_id = message.chat.id
        description = message.text
        expense = expense_dict[chat_id]
        expense.description = description 
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)           
        bot.send_message(message.chat.id, 'Enter the amount in rupees (Please only enter numbers, for ex: 20000)')
        bot.register_next_step_handler(message, expenseDetailsRecorderDate)

    #expense data date recorder function
    def expenseDetailsRecorderDate(message):
        chat_id = message.chat.id
        amount = message.text
        expense = expense_dict[chat_id]
        try:
            expense.amount = int(amount)
            expense.dateId = 0
            datecalendar(message)
        except Exception as e:
            bot.send_message(message.chat.id, 'Please enter the amount in rupees and use only numbers, for Ex: 2000')
            bot.register_next_step_handler(message, expenseDetailsRecorderDate)

    #date output function
    def calendarDatefunction(message, date):
        chat_id = message.chat.id
        expense = expense_dict[chat_id]
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        if expense.dateId == 0:
            expenseDetailsRecorder(message, date)
        elif expense.dateId == 1:
            editDate(message, date)

    #expense data insert function into mysql database
    def expenseDetailsRecorder(message, date):
        if date <= datetime.date.today():
            chat_id = message.chat.id
            dateOfExpense = date
            expense = expense_dict[chat_id]
            expense.dateOfExpense = dateOfExpense
            sqlform = "Insert into expense_details(customer_id, expense_details, expense_amt, date_of_expense, date_of_entry) values (%s, %s, %s, %s, %s)"
            details = [(expense.customerid, expense.description, expense.amount, expense.dateOfExpense, datetime.date.today())]
            try:
                mycursor.executemany(sqlform, details)
                mydb.commit()
                bot.send_chat_action(message.chat.id, action='typing')
                t.sleep(0.3)
                bot.send_message(message.chat.id, 'Your expense has been recorded. To record another expense or track your expenses.')
                cont(message)
            except Exception as e:
                bot.send_message(message.chat.id, 'Oops! you have used the wrong format while entering your information, please follow the format mentioned and try again')
                cont(message)
        else:
            bot.send_message(message.chat.id, 'Oops! you have entered a date in the future, please try again')
            expense = expense_dict[message.chat.id]
            expense.dateId = 0
            datecalendar(message)

    #track expense function
    def trackExpense(message):
        chat_id = message.chat.id
        mycursor.execute("select customer_chatid, customer_id from customer_details")
        count = 0
        for i in mycursor.fetchall():
            result = i[0]
            customerid = i[1]
            if result == chat_id:
                count = count + 1
                customerExpenses(message, customerid)

    #expense id recorder function for delete operation
    def expenseIdExtractor(message):
        bot.send_message(message.chat.id, "Enter the serial number of the expense record to continue:\n(Please note: This action is not reversible)")
        bot.register_next_step_handler(message, deleteRecords)

    #delete records function
    def deleteRecords(message):
        chat_id = message.chat.id
        identifier(message)
        expense = expense_dict[chat_id]
        count = 0
        try:
            serialno = int(message.text)
            for i in range(1, len(expense.serialNumDict)+1):
                if i == serialno:
                    expenseid = expense.expenseIdDict[i-1]
                    query = "delete from expense_details where expense_id = {} order by date_of_expense".format(expenseid)
                    mycursor.execute(query)
                    mydb.commit()
                    bot.send_message(message.chat.id, 'Deleting..')
                    bot.send_chat_action(message.chat.id, action='typing')
                    t.sleep(0.2)
                    bot.send_message(message.chat.id, "Expense has been deleted.")
                    cont(message)
                    count = count+1

            if count == 0:
                bot.send_message(message.chat.id, 'Oops! wrong serial number entered. Please try again')
                expenseIdExtractor(message)

        except Exception as e:
            bot.send_message(message.chat.id, 'Oops! wrong serial number entered. Please try again and enter only numbers')
            expenseIdExtractor(message)

    #edit records function
    def expenseIdForEdit(message):
        bot.send_message(message.chat.id, "Please choose what you want to edit:)")
        bot.register_next_step_handler(message, check3)

    #date recorder function from calendar
    def editDateRecorder(message):
        chat_id = message.chat.id
        expenseid = message.text
        initiation(expenseid, chat_id)
        expense = expense_dict[chat_id]
        expense.dateId = 1
        datecalendar(message)

    #date edit in mysql database function
    def editDate(message, date):
        chat_id = message.chat.id
        expense = expense_dict[chat_id]
        try:
            serialno = int(expense.customerid)
            count = 0
            if date <= datetime.date.today():
                identifier(message)
                expense = expense_dict[chat_id]
                expense.dateOfExpense = date 
                for i in range(1, len(expense.serialNumDict)+1):
                    if i == serialno:
                        expenseid = expense.expenseIdDict[i-1]
                        sqlform = "update expense_details SET date_of_expense = %s WHERE expense_id = %s order by date_of_expense"
                        form = (expense.dateOfExpense, int(expenseid))
                        mycursor.execute(sqlform, form)
                        mydb.commit()
                        count = count + 1
                        bot.send_message(message.chat.id, 'Updating..')
                        bot.send_chat_action(message.chat.id, action='typing')
                        t.sleep(0.2)
                        bot.send_message(message.chat.id, 'Your expense date has been updated.')
                        cont(message)
            else:
                count = count + 1
                bot.send_message(message.chat.id, 'Oops! you have entered a date in the future, please try again')
                expense.dateId = 1
                datecalendar(message)

            if count == 0:
                bot.send_message(message.chat.id, 'Oops! Wrong serial number entered. Please try again, enter the serial number to continue:')
                bot.register_next_step_handler(message, editDateRecorder)

        except Exception as e:
            bot.send_message(message.chat.id, 'Oops! Wrong serial number entered. Please try again and enter only numbers')
            bot.register_next_step_handler(message, editDateRecorder)       

    #Recorded expense display function
    def customerExpenses(message, customerid):
        chat_id = message.chat.id
        count = 1
        initiation(count, chat_id)
        mycursor.execute("select customer_id, expense_details, expense_amt, date_of_expense, expense_id from expense_details order by date_of_expense")
        for i in mycursor.fetchall():
            if i[0] == customerid:
                description = i[1]
                amount = i[2]
                dateOfExpense = i[3]
                bot.send_message(message.chat.id, str(count) + ') Expense description: '+ description +'\nAmount Spent: ₹'+ str(amount) +'\nDate Spent(YY-MM-DD): '+ str(dateOfExpense))
                count = count + 1
        if count > 1:
            bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
            bot.register_next_step_handler(message, check2)
        else:
            bot.send_chat_action(message.chat.id, action='typing')
            t.sleep(0.5)
            bot.send_message(message.chat.id, 'You do not have any expenses recorded. Please start recording an expense first.')
            cont(message)

    #Function to link expense id and serial number
    def identifier(message): 
        chat_id = message.chat.id
        count = 1
        initiation(count, chat_id)
        expense = expense_dict[chat_id]
        customerid = customeridExtraction(message)
        mycursor.execute("select customer_id, expense_details, expense_amt, date_of_expense, expense_id from expense_details order by date_of_expense")
        for i in mycursor.fetchall():
            if i[0] == customerid:
                expense.serialNumDict.append(count)
                expense.expenseIdDict.append(int(i[4]))
                count = count+1
        return

    #check2
    def check2(message):
        if message.text == optionC:
            sum = 0
            customerid = customeridExtraction(message)
            mycursor.execute("select customer_id, expense_details, expense_amt from expense_details")
            for i in mycursor.fetchall():
                if i[0] == customerid:
                    amount = i[2]
                    sum = sum + amount
            if sum > 0:
                bot.send_chat_action(message.chat.id, action='typing')
                t.sleep(0.3)
                bot.send_message(message.chat.id, 'Sum of your recorded expenses: ₹'+ str(sum))
                bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
                bot.register_next_step_handler(message, check2)
            else:
                bot.send_message(message.chat.id, 'You do not have any expenses recorded. Please start recording an expense first.')
                cont(message) 
        elif message.text == optionD:
            cont(message)
        elif message.text == optionF:
            expenseIdExtractor(message)
        elif message.text == optionG:
            bot.send_message(message.chat.id, "Please choose what you want to edit:", reply_markup=markup2)
            bot.register_next_step_handler(message, check3)
        elif message.text == optionE:
            exitFunc(message)
        else:
            bot.send_message(message.chat.id, 'Wrong option selected, please try again')
            bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
            bot.register_next_step_handler(message, check2)

    #exit function
    def exitFunc(message):
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        bot.send_message(message.chat.id, 'Thank you for your time. Hope I was helpful. You can always come back and tap /continue or /start to record or track your expenses. Have a nice day! Good bye, see you soon.')

    #check3 function
    def check3(message):
        if message.text == optionH:
            bot.send_message(message.chat.id, 'Enter the new description so that I can update it in the records:')
            bot.register_next_step_handler(message, editDescriptionRecorder)
        elif message.text == optionI:
            bot.send_message(message.chat.id, 'Enter the new amount so that I can update it in the records:')
            bot.register_next_step_handler(message, editAmountRecorder)
        elif message.text == optionJ:
            bot.send_message(message.chat.id, 'Enter the serial number of the record to edit it:')
            bot.register_next_step_handler(message, editDateRecorder)
        elif message.text == optionE:
            exitFunc(message)
        elif message.text == optionK:
            bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
            bot.register_next_step_handler(message, check2)
        else:
            bot.send_message(message.chat.id, 'Wrong option selected, please try again')
            bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup2)
            bot.register_next_step_handler(message, check3)

    #description recorder from user
    def editDescriptionRecorder(message):
        chat_id = message.chat.id
        description = message.text
        initiation(description, chat_id)
        bot.send_message(message.chat.id, 'Now, enter the serial number of the record to edit it:')
        bot.register_next_step_handler(message, editDescription)

    #description edit in mysql database
    def editDescription(message):
        chat_id = message.chat.id
        expense = expense_dict[chat_id]
        description = expense.customerid
        try:
            serialno = int(message.text)
            identifier(message)
            expense = expense_dict[chat_id]
            count = 0
            for i in range(1, len(expense.serialNumDict)+1):
                if i == serialno:
                    expenseid = expense.expenseIdDict[i-1]
                    sqlform = "update expense_details SET expense_details = %s WHERE expense_id = %s order by date_of_expense"
                    form = (description, int(expenseid))
                    mycursor.execute(sqlform, form)
                    mydb.commit()
                    count = count+1
                    bot.send_message(message.chat.id, 'Updating..')
                    bot.send_chat_action(message.chat.id, action='typing')
                    t.sleep(0.2)
                    bot.send_message(message.chat.id, 'Your expense description has been updated.')
                    bot.send_message(message.chat.id, 'Select an option below to continue', reply_markup = markup1)
                    bot.register_next_step_handler(message, check2)
                    
            if count == 0:
                bot.send_message(message.chat.id, 'Oops! Wrong Expense ID entered. Please try again.', reply_markup = markup1)
                bot.register_next_step_handler(message, check2)
                
        except Exception as e:
            bot.send_message(message.chat.id, 'Oops! Wrong Expense ID entered. Please try again and enter only numbers:')
            bot.register_next_step_handler(message, editDescription)

    #amount recorder from user
    def editAmountRecorder(message):
        chat_id = message.chat.id
        try:
            amount = int(message.text)
            initiation(amount, chat_id)
            bot.send_message(message.chat.id, 'Now, enter the serial number of the record to edit it:')
            bot.register_next_step_handler(message, editAmount)
        except Exception as e:
            bot.send_message(message.chat.id, 'Wrong input, please enter the new amount in numbers so that I can update it in the records:')
            bot.register_next_step_handler(message, editAmountRecorder)

    #amount edit in mysql database
    def editAmount(message):
        chat_id = message.chat.id
        expense = expense_dict[chat_id]
        try:
            amount = expense.customerid
            serialno = int(message.text)
            identifier(message)
            expense = expense_dict[chat_id]
            count = 0
            for i in range(1, len(expense.serialNumDict)+1):
                if i == serialno:
                    expenseid = expense.expenseIdDict[i-1]
                    sqlform = "update expense_details SET expense_amt = %s WHERE expense_id = %s order by date_of_expense"
                    form = (amount, int(expenseid))
                    mycursor.execute(sqlform, form)
                    mydb.commit()
                    count = count + 1
                    bot.send_message(message.chat.id, 'Updating..')
                    bot.send_chat_action(message.chat.id, action='typing')
                    t.sleep(0.2)
                    bot.send_message(message.chat.id, 'Your expense amount has been updated.')
                    bot.send_message(message.chat.id, 'Select an option below to continue', reply_markup = markup1)
                    bot.register_next_step_handler(message, check2)

            if count == 0:
                bot.send_message(message.chat.id, 'Oops! Wrong serial number entered. Please try again', reply_markup = markup1)
                bot.register_next_step_handler(message, check2)

        except Exception as e:
            bot.send_message(message.chat.id, 'Oops! serial number entered. Please try again and enter only numbers:')
            bot.register_next_step_handler(message, editAmount)

    #calendar inline keyboard function
    def datecalendar(message):
        now = datetime.datetime.now()
        chat_id = message.chat.id

        date = (now.year, now.month)
        current_shown_dates[chat_id] = date

        markup = create_calendar(now.year, now.month)

        bot.send_message(message.chat.id, "Select the day of expense", reply_markup=markup)

    #date command handler after user selects date on calendar inline keyboard
    @bot.callback_query_handler(func=lambda call: 'DAY' in call.data[0:13])
    def handle_day_query(call):
        chat_id = call.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        last_sep = call.data.rfind(';') + 1

        if saved_date is not None:

            day = call.data[last_sep:]
            date = datetime.date(int(saved_date[0]), int(saved_date[1]), int(day))
            calendarDatefunction(call.message, date)
        else:
            bot.send_message(chat_id, "Please select correct date from the calendar to continue: ")

    #month change handler
    @bot.callback_query_handler(func=lambda call: 'MONTH' in call.data)
    def handle_month_query(call):

        info = call.data.split(';')
        month_opt = info[0].split('-')[0]
        year, month = int(info[1]), int(info[2])
        chat_id = call.message.chat.id

        if month_opt == 'PREV':
            month -= 1

        elif month_opt == 'NEXT':
            month += 1

        if month < 1:
            month = 12
            year -= 1

        if month > 12:
            month = 1
            year += 1

        date = (year, month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
    
    try:
        bot.polling()
    except Exception as e:
        t.sleep(5)

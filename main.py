import mysql.connector
import logging as NULL
import datetime
import time as t
from telebot import types, apihelper
from settings import API_KEY, HOST, PASSWORD
import telebot
from telegramcalendar import create_calendar

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

optionA = 'Record Expense'
optionB = 'Track Expenses'
optionC = 'Sum of all Expenses'
optionD = 'Go to Main menu'
optionE = 'Exit'
optionF = 'Delete Expenses'

markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
markup1 = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
itembtn1 = types.KeyboardButton(optionA)
itembtn2 = types.KeyboardButton(optionB)
itembtn3 = types.KeyboardButton(optionC)
itembtn4 = types.KeyboardButton(optionD)
itembtn5 = types.KeyboardButton(optionE)
itembtn6 = types.KeyboardButton(optionF)
markup.add(itembtn1, itembtn2, itembtn5)
markup1.add(itembtn3, itembtn6, itembtn4, itembtn5)

mydb = mysql.connector.connect(user='root', password="ilml@$600", host="34.133.159.110", database='sql_expensebot')
mycursor = mydb.cursor()

#start command handler
@bot.message_handler(commands=['start'])
def start(message):
  username = message.chat.username
  if username == None:
    bot.send_message(message.chat.id, "Hello, welcome! I'm your personal expense tracker. Hope you are doing well :)\nAre you tired of forgetting where you spent your money? you're not alone. ;)\n")
    bot.send_chat_action(message.chat.id, action='typing')
    bot.send_message(message.chat.id, "I am here to help you now. You will be able to track and record your expenses as you wish. It's just like texting your friend. Trust me it's that easy.")
    bot.send_chat_action(message.chat.id, action='typing')
    t.sleep(0.5)
    reply = bot.send_message(message.chat.id, "So let's begin. Choose an option to continue: ", reply_markup=markup)
  else:
    bot.send_message(message.chat.id, "Hello " +str(username)+ ", welcome! I'm your personal expense tracker. Hope you are doing well :)\nAre you tired of forgetting where you spent your money? you're not alone. ;)\n")
    bot.send_chat_action(message.chat.id, action='typing')
    bot.send_message(message.chat.id, "I am here to help you now. You will be able to track and record your expenses as you wish. It's just like texting your friend. Trust me it's that easy.")
    bot.send_chat_action(message.chat.id, action='typing')
    t.sleep(0.5)
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
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        bot.send_message(message.chat.id, 'Thank you for using the Expense tracker Bot. You can always come back and tap /continue or /start to record or track your expenses. Have a nice day! Good bye')
    else:
        bot.send_message(message.chat.id, 'Wrong option selected please try again:')
        cont(message)

#record expense initiation
def recordExpense(message):
    customerid = customeridExtraction(message)
    if customerid == 0:
        customerRegistration(message)
    customerid = customeridExtraction(message)
    chat_id = message.chat.id
    customer_id = expense(customerid)
    expense_dict[chat_id] = customer_id
    expense.customerid = customerid
    expenseDetailsRecorderDescription(message)

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
    sqlform = "Insert into customer_details(customer_chatid, customer_username, date_created) values (%s, %s, %s)"
    details = [(chat_id, username, datetime.date.today())]
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
    expense.amount = amount
    datecalendar(message)

#expense data insert function into mysql database
def expenseDetailsRecorder(message, date):
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
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

#expense id extractor function
def expenseIdExtractor(message):
    bot.send_message(message.chat.id, "Enter the Expense ID to continue:\n(Please note: This action is not reversible)")
    bot.register_next_step_handler(message, deleteRecords)

#delete records function
def deleteRecords(message):
    try:
        expenseid = int(message.text)
        count = 0
        customerid = customeridExtraction(message)
        mycursor.execute("select expense_id, customer_id from expense_details")
        for i in mycursor.fetchall():
            if i[0] == expenseid and i[1] == customerid:     
                query = "delete from expense_details where expense_id = {}".format(expenseid)
                mycursor.execute(query)
                mydb.commit()
                count = count+1
                bot.send_message(message.chat.id, "Expense has been deleted.")
                bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
                bot.register_next_step_handler(message, check2)
        if count == 0:
            bot.send_message(message.chat.id, 'Oops! Wrong Expense ID entered. Please try again', reply_markup = markup1)
            bot.register_next_step_handler(message, check2)
    except Exception as e:
        bot.send_message(message.chat.id, 'Oops! Wrong Expense ID entered. Please try again and enter only numbers', reply_markup = markup1)
        bot.register_next_step_handler(message, check2)

#Recorded expense display function
def customerExpenses(message, customerid):
    count = 0
    mycursor.execute("select customer_id, expense_details, expense_amt, date_of_expense, expense_id from expense_details")
    for i in mycursor.fetchall():
        if i[0] == customerid:
            count = count + 1
            description = i[1]
            amount = i[2]
            dateOfExpense = i[3]
            expenseid = i[4]
            bot.send_message(message.chat.id, 'Expense ID: '+ str(expenseid) +'\nExpense description: '+ description +'\nAmount Spent: ₹'+ str(amount) +'\nDate Spent: '+ str(dateOfExpense))
            bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
            bot.register_next_step_handler(message, check2)

    if count == 0:
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.5)
        bot.send_message(message.chat.id, 'You do not have any expenses recorded. Please start recording an expense first.')
        cont(message)

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
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        bot.send_message(message.chat.id, 'Sum of your recorded expenses: ₹'+ str(sum))
        bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
        bot.register_next_step_handler(message, check2)
    elif message.text == optionD:
        cont(message)
    elif message.text == optionF:
        expenseIdExtractor(message)
    elif message.text == optionE:
        bot.send_chat_action(message.chat.id, action='typing')
        t.sleep(0.3)
        bot.send_message(message.chat.id, 'Thank you for using the Expense tracker Bot. You can always come back and tap /continue or /start to record or track your expenses. Have a nice day! Good bye')
    else:
        bot.send_message(message.chat.id, 'Wrong option selected, please try again')
        bot.send_message(message.chat.id, 'Select an option below to continue: ', reply_markup = markup1)
        bot.register_next_step_handler(message, check2)

def datecalendar(message):
    now = datetime.datetime.now()
    chat_id = message.chat.id

    date = (now.year, now.month)
    current_shown_dates[chat_id] = date

    markup = create_calendar(now.year, now.month)

    bot.send_message(message.chat.id, "Select the day of expense", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: 'DAY' in call.data[0:13])
def handle_day_query(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    last_sep = call.data.rfind(';') + 1

    if saved_date is not None:

        day = call.data[last_sep:]
        date = datetime.date(int(saved_date[0]), int(saved_date[1]), int(day))
        expenseDetailsRecorder(call.message, date)
    else:
        bot.send_message(chat_id, "Please select correct date from the calendar to continue: ")
        pass

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

@bot.callback_query_handler(func=lambda call: "IGNORE" in call.data)
def ignore(call):
    bot.answer_callback_query(call.id, text="OOPS... something went wrong")

bot.polling()

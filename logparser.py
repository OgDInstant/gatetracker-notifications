import csv
import os
import base64
import smtplib
import ssl
import bs4
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_PASSWORD = 
SMTP_USER = 
SMTP_HOST = 
SMTP_PORT = 

MAIL_FROM = 
MAIL_TO = 
MAIL_TO = 

COL_TIME_FINISH = 0
COL_TIME_START = 1
COL_GATE_NAME = 2
COL_CHIP_ID = 3
COL_BAR_CODE = 4
COL_BOOK_NAME = 5
COL_STATUS = 6
COL_CHARGE_DATE = 7
COL_ALEPH_STATUS = 8

LOG_PATH = "logs"
LOG_ARCHIVE_PATH = "logs_archive"
htmlbody = '<table border="1" style="border-collapse:collapse" cellspacing="3" cellpadding="3">\n'
htmlbody += '<tr><th>Datum</th><th>Čas</th><th>Brána</th><th>Čárový kód</th><th>Název knihy</th></tr>'
processed_files = []
rowcount = 0
# Zde vytvarime tabulku
for filename in os.listdir(LOG_PATH):  # vylistujeme sei soubory
    if filename.startswith('saved-') and not filename.startswith('saved-' + time.strftime("%Y-%m-%d")):  # Vybereme soubory saved-
        print("Zpracovava se " + filename + " ...")
        csvfile = open(LOG_PATH + os.sep + filename)
        csvdata = csv.reader(csvfile, delimiter=',', quotechar='"')  # Nacteme CSV
        
        manulu=False
        for row in csvdata:
                # print(len(row))
                if len(row) > COL_BAR_CODE:  # Kdyz obsahuje sloupec barcode, resp. kdyz pocet sloupcu je alespon tolik, ze je tam i cislo slopce BAR_CODE
                    if row[COL_BAR_CODE] != '' and row[COL_STATUS] == "0":  # Jestli BARCODE neni prazdny
                        if row[COL_BAR_CODE].startswith("266") or row[COL_BAR_CODE].startswith("3198") or row[COL_BAR_CODE].startswith("42340"): 
                            htmlbody += '<tr>\n'
                            htmlbody += "\t<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>\n".format(
                                row[COL_TIME_START].partition(" ")[0], row[COL_TIME_START].partition(" ")[2], row[COL_GATE_NAME],
                                row[COL_BAR_CODE], row[COL_BOOK_NAME])
                            htmlbody += '</tr>\n'  # Radek tabulky
                            rowcount += 1  # Zvysime pocet zpracovanych radku abychom vedeli, jestli ma smysl posilat mail:-)
                            manulu=True

        if not manulu:
            processed_files.append(filename)  # Zapamutejme si, ktere soubory jmse zpracovavali, budeme je mazat az pozdeji

htmlbody += '</table>\n'

if rowcount:  # Jestli mame nejake radky
    print(htmlbody)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Neprověřené incidenty"
    message["From"] = MAIL_FROM
    message["To"] = MAIL_TO

    part1 = MIMEText(bs4.BeautifulSoup(htmlbody, features="html.parser").get_text(), "plain")
    part2 = MIMEText(htmlbody, "html")    
    message.attach(part1)
    message.attach(part2)

    mailsent = False
    # Zde bude odesilani mailu
    smtp_connection = None
    try:
        # Create a secure SSL context
        context = ssl._create_unverified_context()
        smtp_connection = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context)
        smtp_connection.ehlo()  # Can be omitted
        SMTP_PASSWORD = base64.b64decode(SMTP_PASSWORD).decode()
        # print("'"+SMTP_PASSWORD+"'")
        smtp_connection.login(SMTP_USER, SMTP_PASSWORD)
        print("Sending Email.....")
        smtp_connection.sendmail(MAIL_FROM, MAIL_TO, message.as_string())
        print("Mail sent")
        mailsent = True
    except Exception as e:
    # Print any error messages to stdout
        print(e)
        mailsent = False
    finally:
        if smtp_connection:
            smtp_connection.quit() 
        
    if mailsent:
    
        if not (os.path.exists(LOG_ARCHIVE_PATH) and os.path.isdir(LOG_ARCHIVE_PATH)):  # Pokud neeexistuje adresar pro uchovani zpracovanych logu, vytvori se
            os.makedirs(LOG_ARCHIVE_PATH)

        for filename in processed_files:  # pokud vse probehlo v poradku, provede se presun
            print("Presouva se: " + filename)
            try:
                os.rename(LOG_PATH + os.sep + filename, LOG_ARCHIVE_PATH + os.sep + filename)
            except Exception as e:
                print(e)
    # print("--------------Message-----------")
    # print(message.as_string())
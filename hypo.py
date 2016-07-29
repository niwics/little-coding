#!/usr/bin/python

from sys import argv

def main():
    
    if len(argv) < 4 or (len(argv) > 1 and argv[1] == "-h"):
        print "Usage: %s interest initial_debt month_payment" % argv[0]
        return 1
    
    interest = float(argv[1]) / 100
    initial_debt = int(argv[2])
    years = 30
    months = years * 12
    month_interest = interest / 12
    month_payment = int(argv[3]) #initial_debt * ((month_interest*(1+month_interest)**months) / (((1+month_interest)**months) - 1))
    assurance_monthly = int(argv[4]) if len(argv) > 4 else 0
    print "Month payment: %s" % month_payment
    #fixes = ((5, 12*10000))
    
    print "Year\tdebt\tinterest"
    
    month = 1
    debt = initial_debt
    total_interest_payed = year_interest_payed = 0
    while debt > 0:
        interest_payed = debt*month_interest
        year_interest_payed += interest_payed
        total_interest_payed += interest_payed 
        if month % 12 == 0:
            print "%d:\t%d\t%d" % (month/12, debt, year_interest_payed)
            year_interest_payed = 0
        debt -= month_payment - interest_payed
        if month == 5*12:
            break
        month += 1
    print "Total interest payed: %d + %d = %d" % (total_interest_payed, month*assurance_monthly, total_interest_payed+month*assurance_monthly)
    print "Final debt: %d" % debt
    
    # 12*mp + interest*()


if __name__ == "__main__":
    exit(main())

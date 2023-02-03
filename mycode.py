import sys
import pandas as pd


ERROR_CODES = dict(
    POINTS_NEGATIVE=1,
    NO_ENOUGH_POINTS=2
)


def calc_effective_points_by_payer(df):
    """
    To calculate effective points by payer (eliminate negative points in transaction records),
    iterate through the dataframe and
    add the negative points to the oldest available positive points.
    """
    # effective_transaction_records is a dictionary stores the effective records by payer
    # e.g. {payer0: [[time0, payer0, points0], [time1, payer0, points1], ...],
    #       payer1: [[time0, payer1, points0], [time1, payer1, points1], ...],
    #       ...}
    effective_transaction_records = {}
    # result is the final output of the program and
    # is a dictionary stores the total points by payer after spending the points,
    # e.g. {payer0: total_points_of_payer0,
    #       payer1: total_points_of_payer1,
    #       ...}
    result = {}

    # iterate through the dataframe
    for index, row in df.iterrows():
        payer = row['payer']
        points = row['points']
        timestamp = row['timestamp']
        # if points is 0, do nothing
        if points == 0:
            continue
        # if points is negative, balance it with its payer's previous points
        elif points < 0:
            while points < 0:
                if payer not in effective_transaction_records.keys():
                    print("Error: Points can't go negative.", file=sys.stderr)
                    exit(ERROR_CODES["POINTS_NEGATIVE"])
                if effective_transaction_records[payer][0][2] <= -points:
                    points += effective_transaction_records[payer][0][2]
                    effective_transaction_records[payer].pop(0)
                else:
                    effective_transaction_records[payer][0][2] += points
                    points = 0
                if len(effective_transaction_records[payer]) == 0:
                    effective_transaction_records.pop(payer)
        # if points is positive, put it into its corresponding payer's list
        else:
            if payer not in effective_transaction_records.keys():
                effective_transaction_records[payer] = [[timestamp, payer, points]]
                result[payer] = 0
            else:
                effective_transaction_records[payer].append([timestamp, payer, points])
    return effective_transaction_records, result


def spend_points():
    """
    Find all payer point balances after spending points.
    """
    # read in the amount to spend
    to_spend = int(sys.argv[1])

    # read in transactions.csv and sort it by time
    df = pd.read_csv("transactions.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    effective_transaction_records, result = calc_effective_points_by_payer(df)

    # put all the points records together and sort by time
    total = []
    for key in effective_transaction_records.keys():
        total += effective_transaction_records[key]
    total = sorted(total, key=lambda l: l[0])

    # spend the points by time order
    while to_spend > 0 and len(total) != 0:
        if total[0][2] <= to_spend:
            to_spend -= total[0][2]
            total.pop(0)
        else:
            total[0][2] -= to_spend
            to_spend = 0

    # check if there is enough points for the user to spend
    if to_spend > 0:
        print("Error: Not enough points to be spent", file=sys.stderr)
        exit(ERROR_CODES["NO_ENOUGH_POINTS"])

    # find points for each payer after spending points
    for record in total:
        payer = record[1]
        points = record[2]
        result[payer] += points

    print(result)


if __name__ == '__main__':
    spend_points()

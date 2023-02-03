import sys
import pandas as pd


def main():
    # read in the amount to spend
    toSpend = int(sys.argv[1])
    # read in transactions.csv and sort it by time
    df = pd.read_csv("transactions.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')
    # iterate through dataframe and classify by payers to check the balance
    cnt = {}
    result = {}
    for index, row in df.iterrows():
        payer = row['payer']
        points = row['points']
        timestamp = row['timestamp']
        # if points is 0, do nothing
        if points == 0:
            continue
        # if points is negative, balance it with its payer's previous points
        elif points < 0:
            if payer not in cnt.keys():
                print("Error: Points can't go negative.")
                return
            else:
                while points < 0:
                    if payer not in cnt.keys():
                        print("Error: Points can't go negative.")
                        return
                    if cnt[payer][0][2] <= -points:
                        points += cnt[payer][0][2]
                        cnt[payer].pop(0)
                        if len(cnt[payer]) == 0:
                            cnt.pop(payer)
                    else:
                        cnt[payer][0][2] += points
                        points = 0
        # if points is positive, put it into its corresponding payer's list
        else:
            if payer not in cnt.keys():
                cnt[payer] = [[timestamp, payer, points]]
                result[payer] = 0
            else:
                cnt[payer].append([timestamp, payer, points])
    # put all the points records together and sort by time
    total = []
    for key in cnt.keys():
        total += cnt[key]
    total = sorted(total, key=lambda l: l[0])
    # spend the points by time order
    while toSpend > 0 and len(total) != 0:
        if total[0][2] <= toSpend:
            toSpend -= total[0][2]
            total.pop(0)
        else:
            total[0][2] -= toSpend
            toSpend = 0
    # check if there is enough points to be spent
    if toSpend > 0:
        print("Error: No more points to be spent")
        return
    # find points for each payer after spending points
    for record in total:
        payer = record[1]
        points = record[2]
        result[payer] += points
    print(result)


if __name__ == '__main__':
    main()

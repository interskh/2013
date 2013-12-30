import argparse

from datetime import datetime
from datetime import timedelta
from jiffy_record import JiffyRecord

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='input CSV file')
    args = parser.parse_args()

    records = []
    with open(args.input) as f:
        f.readline() #skip first line
        for line in f:
            r = JiffyRecord(line)
            records.append(r)

    start_work_time_list = [r.stop for r in records if r.is_commute_to_work()]
    print("========== start work ===========")
    for t in start_work_time_list:
        print(t.strftime('%Y-%m-%d %H:%M:%S'))
    avg_start_work_time = timedelta(seconds=
                sum(map(lambda t: t.hour*3600 + t.minute*60 + t.second, start_work_time_list))
                    / len(start_work_time_list))

    print("========== finish work ===========")
    finish_work_time_list = [r.start for r in records if r.is_commute_after_work()]
    for t in finish_work_time_list:
        print(t.strftime('%Y-%m-%d %H:%M:%S'))
    avg_finish_work_time = timedelta(seconds=
                sum(map(lambda t: t.hour*3600 + t.minute*60 + t.second, finish_work_time_list))
                    / len(finish_work_time_list))

    print("========== commute ===========")
    morning_commute_list = [r.stop - r.start for r in records if r.is_commute_to_work()]
    avg_morning_commute_time = sum(morning_commute_list, timedelta(0)) / len(morning_commute_list)

    evening_commute_list = [r.stop - r.start for r in records if r.is_commute_after_work()]
    avg_evening_commute_time = sum(evening_commute_list, timedelta(0)) / len(morning_commute_list)

    print("========== work ===========")
    working_days = {}
    total = 0
    for r in records:
        if r.is_houzz():
            total += r.duration
            date = r.start.strftime('%Y-%m-%d')
            if date in working_days:
                working_days[date] += r.duration
            else:
                working_days[date] = r.duration
    avg_work_time_per_day = total / len([d for d,t in working_days.items() if t > 300]) # working day if I work for longer than 5 hours

    print("========= summary =========")
    print("Average time to start work: %s" % str(avg_start_work_time))
    print("Average time to finish work: %s" % str(avg_finish_work_time))
    print("Average morning commute time: %s" % str(avg_morning_commute_time))
    print("Average evening commute time: %s" % str(avg_evening_commute_time))
    print("Average working mins per day: %s" % str(avg_work_time_per_day))
    #import ipdb; ipdb.set_trace()

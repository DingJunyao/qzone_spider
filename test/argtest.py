import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('-u', type=str, default=None)
parser.add_argument('-p', type=str, default=None)
parser.add_argument('-q', type=int, default=20)
args = parser.parse_args()

QQ = args.u
password = args.p
quantity = args.q

if QQ is None and password is None:
    print('Usage: ./test-spider.py -u your_QQ_number -p your_password -q quantity')

print(args.u, args.p, args.q)
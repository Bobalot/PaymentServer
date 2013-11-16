from flask import Flask, render_template, request, json
from pybitcointools import deterministic
from redis import Redis
from config import *

app = Flask(__name__)
r = Redis()

@app.route('/')
@app.route('/donate')
def index():
    address = get_btc_address()
    bitcoinuri = "bitcoin:" + address
    return render_template("index.html", header=header, address=address, bitcoinuri=bitcoinuri)


@app.route('/getnewaddress')
def donate():
    return get_btc_address()


def get_btc_address():
    # Check for X-Real-IP header added by proxy
    ip_address = request.headers.get("X-Real-IP") or request.remote_addr

    address = r.get(redis_prefix + ip_address)
    if address is None:
        n = r.incr(redis_prefix + index_key)
        address = deterministic.electrum_address(mpk, n)
        r.setex(redis_prefix + ip_address, address, timeout)

    return address


if __name__ == '__main__':
    app.run()

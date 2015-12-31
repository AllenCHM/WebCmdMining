
# import websocket
#
# ws = websocket.WebSocket(u'ws://primsg-live.bilibili.com:8090/sub')
# print ws.receive()
# ws.close()


import websocket
import thread
import time
import json

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    op = {
        u'ver':1,
        u'op':7,
        u'seq':1,
        u'body':{
            u'data':{}
        }
    }
    ws.send(json.dump(op))

    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://primsg-live.bilibili.com:8090/sub",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
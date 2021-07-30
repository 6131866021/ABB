from trainpanel import *
from testpanel import *
from optimizepanel import *
from executepanel import *

# Main Function
# Adjust params used in the program at param.py

def main():
    train_subscriber = TrainSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    try:
        if train_subscriber.subscribe():
            train_subscriber.start_recv_events()
    except KeyboardInterrupt:
        train_subscriber.close()
        predict()

    test_subsciber = TestSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    try:
        if test_subsciber.subscribe():
            test_subsciber.start_recv_events()
    except KeyboardInterrupt:
        test_subsciber.close()
        optimize()

    execute_subscriber = ExecuteSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    try:
        if execute_subscriber.subscribe():
            execute_subscriber.start_recv_events()
    except KeyboardInterrupt:
        execute_subscriber.close()
        efficiency()

if __name__ == "__main__":
    main()

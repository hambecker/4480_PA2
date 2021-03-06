from StudentNetworkSimulator import StudentNetworkSimulator
import sys
import time


def main():
    n_sim = -1
    loss = -1.0
    corrupt = -1.0
    delay = -1.0
    trace = -1
    seed = -1
    _buffer = ""

    print("Network Simulator v1.0")
    while n_sim < 1:
        try:
            _buffer = input("Enter number of messages to simulate (> 0):[10] ")
        except Exception:
            print("Error reading input")
            sys.exit(0)

        if _buffer == "":
            n_sim = 10
        else:
            try:
                n_sim=int(_buffer)
            except Exception:
                print("Please enter a valid value.")
                n_sim = -1

    while loss < 0.0:
        try:
            _buffer= input("Enter the paceket loss probablity (0.0 for no loss): [0.0] ")
        except Exception:
            print("Error reading your input")
            sys.exit(0)

        if _buffer == "":
            loss = 0.0
        else:
            try:
                loss = float(_buffer)
            except Exception:
                print("Please enter a valid value.")
                loss = -1.0

    while corrupt < 0.0:
        try:
            _buffer = input("Enter the packet corruption probablity (0.0 for no corruption):[0.0] ")
        except Exception:
            print("Error reading your input")
            sys.exit(0)
        if _buffer == "":
            corrupt = 0.0
        else:
            try:
                corrupt = float(_buffer)
            except Exception:
                print("Please enter a valid value.")
                corrupt = -1.0

    while delay <= 0.0:
        try:
            _buffer = input("Enter the average time between messages from sender's layer 5 (> 0.0): [1000] ")
        except Exception:
            print("Error reading your input")
            sys.exit(0)
        if _buffer == "":
            delay = 1000.0
        else:
            try:
                delay = float(_buffer)
            except Exception:
                print("Please enter a valid value.")
                delay = -1.0

    while trace<0:
        try:
            _buffer = input("Enter trace level (>=0): [0] ")
        except Exception:
            print("Error reading your input" )
            sys.exit(0)

        if _buffer == "":
            trace = 0
        else:
            try:
                trace = int(_buffer)
            except Exception:
                print("Please enter a valid value.")
                trace = -1

    while seed <1:
        try:
            _buffer = input("Enter random seed: [random] ")
        except Exception:
            print("Error reading your input")
            sys.exit(0)

        if _buffer == "":
            seed = int(round(time.time() * 1000))
        else:
            try:
                seed = int(_buffer)
            except Exception:
                print("Please enter a valid value.")
                seed = -1

    simulator = StudentNetworkSimulator(n_sim, loss, corrupt, delay, trace, seed)
    simulator.run_simulator()

    # A Output
    print('received messages from layer 5:', '\t', simulator.received_messages)
    print('sent packets to b: ', '\t', simulator.sent_packets)
    print('messages discarded because buffer is full: ', '\t', simulator.message_discarded)

    # B input
    print('received packets from a: ', '\t', simulator.received_packets_from_a)
    print('corrupt_packets_from_a: ', '\t', simulator.corrupt_packets_from_a)
    print('correct sequence numbers: ', '\t', simulator.correct_sequence_nums)
    print('incorrect sequence numbers: ', '\t', simulator.incorrect_sequence_nums)
    print('Sent acks: ', '\t', simulator.sent_acks)

    # Timeout
    print('Lost retransmission happening: ', '\t', simulator.lost_packets_or_acks)
    print('Resent packets because of loss: ', '\t', simulator.resent_messages)

    # A input
    print('received acks: ', '\t', simulator.received_acks)
    print('Successful acks: ', '\t', simulator.successful_acks)
    print('Corrupt acks: ', '\t', simulator.corrupt_acks)
    print('incorrect acks: ', '\t', simulator.incorrect_acks)
    print('buffer used: ', '\t', simulator.buffer_used)
    print('messages still in buffer: ', '\t', len(simulator.buffer))



main()

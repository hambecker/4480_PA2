from NetworkSimulator import NetworkSimulator
from queue import Queue
import random
from Event import Event
from Packet import Packet
from message import Message
from EventListImpl import EventListImpl
import random
import math



class StudentNetworkSimulator(NetworkSimulator, object):


	"""
	* Predefined Constants (static member variables):
	 *
	 *   int MAXDATASIZE : the maximum size of the Message data and
	 *                     Packet payload
	 *
	 *   int A           : a predefined integer that represents entity A
	 *   int B           : a predefined integer that represents entity B
	 *
	 *
	 * Predefined Member Methods:
	 *
	 *  stopTimer(int entity):
	 *       Stops the timer running at "entity" [A or B]
	 *  startTimer(int entity, double increment):
	 *       Starts a timer running at "entity" [A or B], which will expire in
	 *       "increment" time units, causing the interrupt handler to be
	 *       called.  You should only call this with A.
	 *  toLayer3(int callingEntity, Packet p)
	 *       Puts the packet "p" into the network from "callingEntity" [A or B]
	 *  toLayer5(int entity, String dataSent)
	 *       Passes "dataSent" up to layer 5 from "entity" [A or B]
	 *  getTime()
	 *       Returns the current time in the simulator.  Might be useful for
	 *       debugging.
	 *  printEventList()
	 *       Prints the current event list to stdout.  Might be useful for
	 *       debugging, but probably not.
	 *
	 *
	 *  Predefined Classes:
	 *
	 *  Message: Used to encapsulate a message coming from layer 5
	 *    Constructor:
	 *      Message(String inputData):
	 *          creates a new Message containing "inputData"
	 *    Methods:
	 *      boolean setData(String inputData):
	 *          sets an existing Message's data to "inputData"
	 *          returns true on success, false otherwise
	 *      String getData():
	 *          returns the data contained in the message
	 *  Packet: Used to encapsulate a packet
	 *    Constructors:
	 *      Packet (Packet p):
	 *          creates a new Packet that is a copy of "p"
	 *      Packet (int seq, int ack, int check, String newPayload)
	 *          creates a new Packet with a sequence field of "seq", an
	 *          ack field of "ack", a checksum field of "check", and a
	 *          payload of "newPayload"
	 *      Packet (int seq, int ack, int check)
	 *          chreate a new Packet with a sequence field of "seq", an
	 *          ack field of "ack", a checksum field of "check", and
	 *          an empty payload
	 *    Methods:
	 *      boolean setSeqnum(int n)
	 *          sets the Packet's sequence field to "n"
	 *          returns true on success, false otherwise
	 *      boolean setAcknum(int n)
	 *          sets the Packet's ack field to "n"
	 *          returns true on success, false otherwise
	 *      boolean setChecksum(int n)
	 *          sets the Packet's checksum to "n"
	 *          returns true on success, false otherwise
	 *      boolean setPayload(String newPayload)
	 *          sets the Packet's payload to "newPayload"
	 *          returns true on success, false otherwise
	 *      int getSeqnum()
	 *          returns the contents of the Packet's sequence field
	 *      int getAcknum()
	 *          returns the contents of the Packet's ack field
	 *      int getChecksum()
	 *          returns the checksum of the Packet
	 *      int getPayload()
	 *          returns the Packet's payload
	 *

	"""
	# Add any necessary class/static variables here.  Remember, you cannot use
	# these variables to send messages error free!  They can only hold
	# state information for A or B.
	# Also add any necessary methods (e.g. checksum of a String)

	# alternating bit set-up
	# message_in_transit = False
	# global_message = ""
	# alternating_bit_a = 0
	# alternating_bit_b = 0
	# send_packet_b = Packet(0, 0, 0, "")
	# message_to_5 = ""

	# GBN set up
	next_sequence_num = 0
	base = 0
	N = 8
	buffer = []
	send_packets = {}
	expected_sequence_num = 0
	message_to_5 = Message("")
	send_packet_b = Packet(0, 0, 0, "")
	timer_amount = 10
	buffer_used = 0

	# Stats in A
	received_messages = 0
	sent_packets = 0
	received_acks = 0
	successful_acks = 0
	corrupt_acks = 0
	incorrect_acks = 0
	resent_messages = 0
	resent_message = False
	message_discarded = 0

	# IN B
	received_packets_from_a = 0
	corrupt_packets_from_a = 0
	sent_acks = 0
	correct_sequence_nums = 0
	incorrect_sequence_nums = 0

	# Shared
	lost_packets_or_acks = 0

	# This is the constructor.  Don't touch!
	def __init__(self, num_messages, loss, corrupt, avg_delay, trace, seed):
		super(StudentNetworkSimulator, self).__init__(num_messages, loss, corrupt, avg_delay, trace, seed)

	# This routine will be called whenever the upper layer at the sender [A]
	# has a message to send.  It is the job of your protocol to insure that
	# the data in such a message is delivered in-order, and correctly, to
	# the receiving upper layer.
	def a_output(self, message):
		"""
		args[0]=sequence number
		args[1]=acknowledgement number
		args[2]=checksum
		args[3]=payload string
		"""
		# statistic for output
		self.received_messages = self.received_messages + 1

		# reject any calls from layer 5 if there is a packet already being sent and waiting for an awk
		if self.next_sequence_num < self.base + self.N:

			# checksum to check for corruption when it gets to b
			checksum = 0
			for char in message.get_data():
				checksum += ord(char)
			checksum = checksum + self.next_sequence_num + self.next_sequence_num

			# create the packet to send to the transport layer
			packet2 = Packet(self.next_sequence_num, self.next_sequence_num, checksum, message.get_data())

			# add to send packets data
			if self.next_sequence_num in self.send_packets:
				print("ERROR: SEQUENCE NUMBER ALREADY IN USE!")
			else:
				self.send_packets[self.next_sequence_num] = packet2

			# send the packet to the transport layer
			self.to_layer3(0, packet2)

			# start timer to check for a timeout
			if self.base == self.next_sequence_num:
				self.start_timer(0, self.timer_amount)

			# increment sequence number
			self.next_sequence_num = self.next_sequence_num + 1

			# statistic for output
			self.sent_packets = self.sent_packets + 1
		else:
			if len(self.buffer) < 50:
				self.buffer.append(message)
				self.buffer_used = self.buffer_used + 1
			else:
				print("message discarded because a current message is in progress")
				print('message: ', message.get_data())
				self.message_discarded = self.message_discarded + 1
		return

	# This routine will be called whenever a packet sent from the B-side
	# (i.e. as a result of a toLayer3() being done by a B-side procedure)
	# arrives at the A-side.  "packet" is the (possibly corrupted) packet
	# sent from the B-side.

	def a_input(self, packet):
		"""
		args[0]=sequence number
		args[1]=acknowledgement number
		args[2]=checksum
		args[3]=payload string
		"""

		self.received_acks = self.received_acks + 1

		# extract the payload from the packet received from layer 3 and turn it into a message
		message_from_b = Message(packet.get_payload())

		# corruption calculation
		checksum_check = 0
		for char in message_from_b.get_data():
			checksum_check += ord(char)

		checksum_check = checksum_check + packet.get_acknum() + packet.get_seqnum()

		# check if checksum is correct
		if packet.get_checksum() != checksum_check or packet.get_seqnum() != packet.get_acknum():
			print("Corruption detected: bad checksum for ack")
			self.corrupt_acks = self.corrupt_acks + 1
			return

		print("ack number received: ", packet.get_acknum())

		if self.successful_acks + 1 != self.base:
			# awk received okay, change the base to ack + 1
			self.successful_acks = self.successful_acks + 1

			# increment the timer amount
			if self.timer_amount == 10:
				self.timer_amount = 15
			elif self.timer_amount == 15:
				self.timer_amount = 20
			elif self.timer_amount == 20:
				self.timer_amount = 25
			elif self.timer_amount == 25:
				self.timer_amount = 30
			elif self.timer_amount == 30:
				self.timer_amount = 35
			elif self.timer_amount == 35:
				self.timer_amount = 40

		self.base = packet.get_acknum() + 1
		print("base number: ", self.base)
		delete_nums = []
		for seq_num, packet_stored in self.send_packets.items():
			if packet.get_acknum() >= seq_num:
				delete_nums.append(seq_num)
		for x in delete_nums:
			del self.send_packets[x]

		if self.base == self.next_sequence_num:
			self.stop_timer(0)
			while len(self.buffer) > 0:
				self.a_output(self.buffer.pop(0))
		elif self.next_sequence_num - self.base < self.N:
			self.stop_timer(0)
			if len(self.buffer) > 0:
				while len(self.buffer) > 0 and self.next_sequence_num - self.base < self.N:
					self.a_output(self.buffer.pop(0))
			self.start_timer(0, self.timer_amount)
			return

	# This routine will be called when A's timer expires (thus generating a
	# timer interrupt). You'll probably want to use this routine to control
	# the retransmission of packets. See startTimer() and stopTimer(), above,
	# for how the timer is started and stopped.

	def a_timer_interrupt(self):

		self.lost_packets_or_acks = self.lost_packets_or_acks + 1

		# Retransmitting window data
		print("Timeout detected: Packet or ack loss)")

		for seq_num, packet in self.send_packets.items():
			print("retransmitting: ", self.send_packets[seq_num].get_payload())
			# increase resent count
			self.resent_messages = self.resent_messages + 1
			# resend the message to layer 3 from A
			self.to_layer3(0, packet)
			if self.base == seq_num:
				self.start_timer(0, self.timer_amount)

	# This routine will be called once, before any of your other A-side
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity A).

	def a_init(self):

		# sequence number for packets being sent out
		self.next_sequence_num = 0

		# number of the base of the sliding window
		self.base = 0

		# size of the sliding window
		self.N = 8

		# dictionary for packets to be stored in case of a drop of the packets
		self.send_packets = {}

		# timer amount until the A resends a message
		self.timer_amount = 10

		# Stats in A
		self.received_messages = 0
		self.sent_packets = 0
		self.successful_acks = 0
		self.corrupt_acks = 0
		self.received_acks = 0
		self.incorrect_acks = 0
		self.resent_messages = 0
		self.resent_message = False
		self.message_discarded = 0
		self.buffer = []
		self.buffer_used = 0

		# Shared
		self.lost_packets_or_acks = 0

		return

	# This routine will be called whenever a packet sent from the B-side
	# (i.e. as a result of a toLayer3() being done by an A-side procedure)
	# arrives at the B-side.  "packet" is the (possibly corrupted) packet
	# sent from the A-side.

	def b_input(self, packet):
		self.received_packets_from_a = self.received_packets_from_a + 1

		# extract the payload from the packet received from layer 3 and turn it into a message
		self.message_to_5 = Message(packet.get_payload())

		# check for corrupt packet
		checksum_check = 0
		for char in self.message_to_5.get_data():
			checksum_check += ord(char)
		checksum_check = checksum_check + packet.get_seqnum() + packet.get_acknum()

		if checksum_check != packet.get_checksum() or packet.get_seqnum() != packet.get_acknum():
			print('Corruption Detected!')
			print('Checksum Field: ', packet.get_checksum())
			print('calculated: ', checksum_check)
			self.corrupt_packets_from_a = self.corrupt_packets_from_a + 1
			self.sent_acks = self.sent_acks + 1
			self.to_layer3(1, self.send_packet_b)
			return

		# if correct alternating bit not rec, send the awk of the of the number you wish to receive
		if packet.get_seqnum() != self.expected_sequence_num:
			print('Received wrong sequence number!')
			print('Expected: ', self.expected_sequence_num)
			print('Received: ', packet.get_seqnum())
			self.incorrect_sequence_nums = self.incorrect_sequence_nums + 1
			self.sent_acks = self.sent_acks + 1
			self.to_layer3(1, self.send_packet_b)
			return

		# correct packet number received
		self.correct_sequence_nums = self.correct_sequence_nums + 1

		# deliver the packet to layer 5
		self.to_layer5(1, self.message_to_5)

		checksum = 0
		for char in packet.get_payload():
			checksum += ord(char)
		checksum = checksum + self.expected_sequence_num + self.expected_sequence_num

		# create an awk packet of the correct packet being seen
		self.send_packet_b = Packet(self.expected_sequence_num, self.expected_sequence_num, checksum, packet.get_payload())

		self.sent_acks = self.sent_acks + 1
		# send the awk packet back to A
		self.to_layer3(1, self.send_packet_b)

		# change the expected sequence number to the next
		self.expected_sequence_num = self.expected_sequence_num + 1
		return

	# This routine will be called once, before any of your other B-side
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity B).
	def b_init(self):

		# Set the expected sequence number for B
		self.expected_sequence_num = 0

		# Set a message object that will be transported to top layer 5 from B
		self.message_to_5 = Message("")

		self.send_packet_b = Packet(-1, -1, 0, "")

		# IN B
		self.corrupt_packets_from_a = 0
		self.sent_acks = 0
		self.correct_sequence_nums = 0
		self.received_packets_from_a = 0
		self.incorrect_sequence_nums = 0
		return

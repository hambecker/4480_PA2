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

	message_in_transit = False
	global_message = ""
	alternating_bit_a = 0
	alternating_bit_b = 0
	send_packet_b = Packet(0, 0, 0, "")
	message_to_5 = ""

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
		if self.resent_message is False:
			# statistic for output
			self.received_messages = self.received_messages + 1
		else:
			self.resent_messages = self.resent_messages + 1
			self.resent_message = False

		# print(self.received_messages)

		# reject any calls from layer 5 if there is a packet already being sent and waiting for an awk
		if not self.message_in_transit:

			# global message to resend if it fails
			self.global_message = message

			# checksum to check for corruption when it gets to b
			checksum = 0
			for char in message.get_data():
				checksum += ord(char)

			checksum = checksum + self.alternating_bit_a + self.alternating_bit_a	

			# create the packet to send to the transport layer
			packet2 = Packet(self.alternating_bit_a, self.alternating_bit_a, checksum, message.get_data())

			# boolean to keep track of whether or not a packet is currently being sent from A
			self.message_in_transit = True

			# start timer to check for a timeout
			self.start_timer(0, 1000)

			# send the packet to the transport layer
			self.to_layer3(0, packet2)

			# statistic for output
			self.sent_packets = self.sent_packets + 1
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
		self.message_in_transit = False
		self.stop_timer(0)

		# extract the payload from the packet received from layer 3 and turn it into a message
		message_from_b = Message(packet.get_payload())


		# corruption calculation
		checksum_check = 0
		for char in message_from_b.get_data():
			checksum_check += ord(char)

		checksum_check = checksum_check + packet.get_seqnum() + packet.get_acknum()

		# check if checksum is correct
		if packet.get_checksum() != checksum_check:
			print("Corruption detected: bad checksum for ack")
			print("retransmitting: ", self.global_message.get_data())
			self.resent_message = True
			self.corrupt_acks = self.corrupt_acks + 1
			self.a_output(self.global_message)
			return

		# check to see if ack number was the one just sent, if not resend the last message
		if packet.get_acknum() != self.alternating_bit_a:
			print("Corruption detected (Bad Ack num): retransmitting: ")
			print("retransmitting: ", self.global_message.get_data())
			self.resent_message = True
			self.incorrect_acks = self.incorrect_acks + 1
			self.a_output(self.global_message)
			return

		# check to see if the awk was corrupted
		if packet.get_acknum() != packet.get_seqnum():
			print("Corruption detected: ack and packet num do not match")
			print("retransmitting: ", self.global_message.get_data())
			self.resent_message = True
			self.corrupt_acks = self.corrupt_acks + 1
			self.a_output(self.global_message)
			return


		# awk received okay, change the alternating_bit for A
		self.successful_acks = self.successful_acks + 1
		if self.alternating_bit_a == 1:
			self.alternating_bit_a = 0
		else:
			self.alternating_bit_a = 1
		return

	# This routine will be called when A's timer expires (thus generating a
	# timer interrupt). You'll probably want to use this routine to control
	# the retransmission of packets. See startTimer() and stopTimer(), above,
	# for how the timer is started and stopped.

	def a_timer_interrupt(self):

		self.lost_packets_or_acks = self.lost_packets_or_acks + 1

		print("Timeout detected: Packet or ack loss)")
		print("retransmitting: ", self.global_message.get_data())
		# Turn the boolean off because there has been a timeout and the packet or the awk clearly isnt in transit anymore
		self.message_in_transit = False

		self.resent_message = True

		# resend the message to layer 3 from A
		self.a_output(self.global_message)
		pass

	# This routine will be called once, before any of your other A-side
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity A).

	def a_init(self):

		# Set the alternating bit of A
		self.alternating_bit_a = 0

		# Set the boolean that a message is not currently in the transport layer
		self.message_in_transit = False

		# Set the message to store in case of a lost packet to blank
		self.global_message = Message("")

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

		if checksum_check != packet.get_checksum():
			print('Corruption Detected!')
			print('Checksum Field: ', packet.get_checksum())
			print('calculated: ', checksum_check)
			self.corrupt_packets_from_a = self.corrupt_packets_from_a + 1
			self.sent_acks = self.sent_acks + 1
			self.to_layer3(1, self.send_packet_b)
			return

		# check to see if correct alternating bits were sent
		if self.alternating_bit_b == 0:

			# if correct alternating bit not rec, send the awk of the of the number you wish to receive
			if packet.get_seqnum() != 0:
				print('Received wrong sequence number!')
				print('Expected: ', 0)
				print('Received: ', packet.get_seqnum())
				self.incorrect_sequence_nums = self.incorrect_sequence_nums + 1
				self.sent_acks = self.sent_acks + 1
				self.to_layer3(1, self.send_packet_b)
				return

			# correct packet number received
			else:
				self.correct_sequence_nums = self.correct_sequence_nums + 1

				# deliver the packet to layer 5
				self.to_layer5(1, self.message_to_5)

				# create an awk packet of the correct packet being seen
				self.send_packet_b = Packet(self.alternating_bit_b, self.alternating_bit_b, checksum_check, packet.get_payload())

				self.sent_acks = self.sent_acks + 1
				# send the awk packet back to A
				self.to_layer3(1, self.send_packet_b)

				# change the alternating bit for next call
				self.alternating_bit_b = 1
				return
		else:

			# if correct alternating bit not rec, send the awk of the of the number you wish to receive
			if packet.get_seqnum() != 1:
				print('Received wrong sequence number!')
				print('Expected: ', 1)
				print('Received: ', packet.get_seqnum())
				self.incorrect_sequence_nums = self.incorrect_sequence_nums + 1
				self.sent_acks = self.sent_acks + 1
				self.to_layer3(1, self.send_packet_b)
				return

			# correct packet number received
			else:

				self.correct_sequence_nums = self.correct_sequence_nums + 1
				# deliver the packet to layer 5
				self.to_layer5(1, self.message_to_5)

				# create an awk packet of the correct packet being seen
				self.send_packet_b = Packet(self.alternating_bit_b, self.alternating_bit_b, checksum_check, packet.get_payload())

				self.sent_acks = self.sent_acks + 1
				# send the awk packet back to A
				self.to_layer3(1, self.send_packet_b)

				# change the alternating bit for next call
				self.alternating_bit_b = 0
				return

	# This routine will be called once, before any of your other B-side
	# routines are called. It can be used to do any required
	# initialization (e.g. of member variables you add to control the state
	# of entity B).
	def b_init(self):

		# Set the alternating bit of B
		self.alternating_bit_b = 0

		# Set the default message back in case there is an a wrong packet sent first, first packet should be seq 0
		self.send_packet_b = Packet(1, 1, 0, "")

		# Set a message object that will be transported to top layer 5 from B
		self.message_to_5 = Message("")

		# IN B
		self.corrupt_packets_from_a = 0
		self.sent_acks = 0
		self.correct_sequence_nums = 0
		self.received_packets_from_a = 0
		self.incorrect_sequence_nums = 0
		return

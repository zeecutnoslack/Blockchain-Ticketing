import streamlit as st
import hashlib
import time
import random

# ---------------------------
# Blockchain Classes
# ---------------------------
class Block:
    def __init__(self, index, previous_hash, transaction, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.strftime("%Y-%m-%d %H:%M:%S")
        self.transaction = transaction
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.transaction}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", {"ticket_id": "GENESIS", "buyer": "System"})

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, transaction):
        index = len(self.chain)
        previous_hash = self.get_last_block().hash
        new_block = Block(index, previous_hash, transaction)
        self.chain.append(new_block)
        return new_block

    def is_ticket_valid(self, ticket_id=None, buyer_name=None):
        results = []
        for block in self.chain:
            tx = block.transaction
            if ticket_id and tx.get("ticket_id") == ticket_id:
                results.append(tx)
            if buyer_name and tx.get("buyer", "").lower() == buyer_name.lower():
                results.append(tx)
        return results


# ---------------------------
# Event Data
# ---------------------------
EVENTS = [
    {
        "name": "Future Beats Concert",
        "artist": "DJ Nova",
        "date": "15th November 2025",
        "venue": "Skyline Arena, Mumbai",
        "cost": 1500,
        "perks": ["Free Glow Sticks", "VIP Lounge Access", "Blockchain-Protected Tickets"],
        "tickets": 200,
    },
    {
        "name": "Rock Revolution",
        "artist": "The StarLights",
        "date": "20th November 2025",
        "venue": "Bandra Stadium, Mumbai",
        "cost": 1800,
        "perks": ["Backstage Pass (limited)", "Free Band Merch", "Meet & Greet"],
        "tickets": 150,
    },
    {
        "name": "Classical Nights",
        "artist": "Symphony of India",
        "date": "1st December 2025",
        "venue": "Delhi Opera Hall",
        "cost": 1200,
        "perks": ["Complimentary Wine", "Front Row Seating Upgrade", "Blockchain Tickets"],
        "tickets": 100,
    },
]

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="Blockchain Ticketing System", layout="centered")

if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "sold_tickets" not in st.session_state:
    st.session_state["sold_tickets"] = {i: 0 for i in range(len(EVENTS))}

st.title("🎟 Blockchain Event Ticketing System")
st.write("Secure, Fun, and Fraud-Proof Tickets for Your Favorite Events")

menu = st.sidebar.radio("Menu", ["Home", "Buy Ticket", "Verify Ticket", "View Blockchain"])

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Upcoming Concerts & Events")
    for idx, event in enumerate(EVENTS):
        st.markdown(f"""
        ### {event['name']}  
        - **Artist:** {event['artist']}  
        - **Date:** {event['date']}  
        - **Venue:** {event['venue']}  
        - **Ticket Price:** ₹{event['cost']}  
        - **Tickets Available:** {event['tickets'] - st.session_state['sold_tickets'][idx]}  
        - **Perks:** {", ".join(event['perks'])}  
        """)

# ---------------------------
# Buy Ticket
# ---------------------------
elif menu == "Buy Ticket":
    st.header("Buy Your Ticket")
    event_choice = st.selectbox("Select Event", [e["name"] for e in EVENTS])
    buyer_name = st.text_input("Enter Your Name")

    if st.button("Buy Ticket"):
        event_index = [e["name"] for e in EVENTS].index(event_choice)
        event = EVENTS[event_index]

        if st.session_state["sold_tickets"][event_index] < event["tickets"]:
            ticket_id = f"TICKET{random.randint(1000, 9999)}"
            transaction = {
                "ticket_id": ticket_id,
                "buyer": buyer_name,
                "event": event["name"],
                "artist": event["artist"],
                "date": event["date"],
                "venue": event["venue"],
                "cost": event["cost"],
            }
            st.session_state["blockchain"].add_block(transaction)
            st.session_state["sold_tickets"][event_index] += 1

            st.success(f"Ticket Purchased Successfully! Your Ticket ID is: {ticket_id}")
            st.info(f"Event: {event['name']} | Artist: {event['artist']} | Date: {event['date']}")
        else:
            st.error("Sorry, tickets for this event are sold out!")

# ---------------------------
# Verify Ticket
# ---------------------------
elif menu == "Verify Ticket":
    st.header("Verify Your Ticket")
    verify_option = st.radio("Choose verification method:", ["By Ticket ID", "By Buyer Name"])

    if verify_option == "By Ticket ID":
        ticket_id_input = st.text_input("Enter your Ticket ID")
        if st.button("Check by Ticket ID"):
            results = st.session_state["blockchain"].is_ticket_valid(ticket_id=ticket_id_input)
            if results:
                tx = results[0]
                st.success("Ticket is VALID ✅")
                st.write(f"- Buyer: {tx['buyer']}")
                st.write(f"- Event: {tx['event']} ({tx['artist']})")
                st.write(f"- Date: {tx['date']} at {tx['venue']}")
                st.write(f"- Ticket ID: {tx['ticket_id']}")
            else:
                st.error("Invalid Ticket ❌")

    elif verify_option == "By Buyer Name":
        buyer_name_input = st.text_input("Enter Buyer Name")
        if st.button("Check by Buyer Name"):
            results = st.session_state["blockchain"].is_ticket_valid(buyer_name=buyer_name_input)
            if results:
                st.success(f"Tickets found for {buyer_name_input}:")
                for tx in results:
                    st.write(f"- {tx['event']} ({tx['artist']}) on {tx['date']} | Ticket ID: {tx['ticket_id']}")
            else:
                st.error("No tickets found for this buyer ❌")

# ---------------------------
# View Blockchain
# ---------------------------
elif menu == "View Blockchain":
    st.header("Blockchain Ledger")
    for block in reversed(st.session_state["blockchain"].chain):
        st.markdown(f"""
        ### Block {block.index}
        - Timestamp: {block.timestamp}
        - Buyer: {block.transaction.get("buyer")}
        - Event: {block.transaction.get("event")}
        - Ticket ID: {block.transaction.get("ticket_id")}
        - Hash: {block.hash[:10]}...
        - Previous Hash: {block.previous_hash[:10]}...
        ---
        """)

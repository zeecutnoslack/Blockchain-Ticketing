import streamlit as st
import time
import qrcode
import io
from PIL import Image

# -------------------------------
# Blockchain Simulation
# -------------------------------
class Block:
    def __init__(self, index, buyer, event, seat, tickets, price, perks, previous_hash="0"):
        self.index = index
        self.timestamp = time.ctime()
        self.buyer = buyer
        self.event = event
        self.seat = seat
        self.tickets = tickets
        self.price = price
        self.perks = perks
        self.previous_hash = previous_hash
        self.hash = hash((index, buyer, event, seat, tickets, price, perks, self.timestamp, previous_hash))

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, "Genesis", "None", "None", 0, 0, "None", "0")

    def add_block(self, buyer, event, seat, tickets, price, perks):
        prev = self.chain[-1]
        block = Block(len(self.chain), buyer, event, seat, tickets, price, perks, prev.hash)
        self.chain.append(block)
        return block

    def verify_ticket(self, buyer):
        for b in self.chain:
            if b.buyer == buyer and b.index != 0:
                return True, b
        return False, None

# -------------------------------
# Initialize Session
# -------------------------------
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Home"
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

# -------------------------------
# Dummy Events
# -------------------------------
events = [
    {"artist": "Imagine Dragons", "location": "Mumbai", "date": "12 Oct 2025", "time": "7:00 PM", "price": 2500, "tickets": 50},
    {"artist": "Arijit Singh", "location": "Delhi", "date": "18 Oct 2025", "time": "8:00 PM", "price": 3000, "tickets": 70},
    {"artist": "Coldplay", "location": "Bangalore", "date": "22 Oct 2025", "time": "6:30 PM", "price": 5000, "tickets": 100},
]

# -------------------------------
# Navigation
# -------------------------------
menu = st.radio("🎤 Navigate", ["Home", "Buy Ticket", "Verify Ticket", "Ledger"],
                horizontal=True, index=["Home","Buy Ticket","Verify Ticket","Ledger"].index(st.session_state["menu"]))
st.session_state["menu"] = menu

# -------------------------------
# HOME
# -------------------------------
if menu == "Home":
    st.title("🎶 Blockchain Concert Ticketing")
    st.subheader("Browse Events")

    cols = st.columns(len(events))
    for i, ev in enumerate(events):
        with cols[i]:
            st.markdown(f"### {ev['artist']}")
            st.write(f"📍 {ev['location']}") 
            st.write(f"📅 {ev['date']} | 🕖 {ev['time']}")
            st.write(f"💰 {ev['price']} INR")
            st.write(f"🎟️ {ev['tickets']} tickets left")

            if st.button("Book Now", key=f"book_{i}"):
                st.session_state["selected_event"] = ev
                st.session_state["menu"] = "Buy Ticket"
                st.experimental_rerun()

# -------------------------------
# BUY TICKET
# -------------------------------
elif menu == "Buy Ticket":
    st.title("🎟️ Buy Tickets")

    if not st.session_state["selected_event"]:
        st.warning("Please select an event from Home.")
    else:
        ev = st.session_state["selected_event"]
        st.subheader(f"{ev['artist']} - {ev['location']}")
        st.write(f"📅 {ev['date']} | 🕖 {ev['time']}")
        st.write(f"💰 Price: {ev['price']} INR per ticket")

        buyer = st.text_input("👤 Enter Your Name")
        num_tickets = st.number_input("🔢 Number of Tickets", 1, ev["tickets"], 1)
        seat_type = st.selectbox("🪑 Choose Seat Type", ["Regular", "VIP", "VVIP"])
        perks = st.multiselect("✨ Select Perks", ["Backstage Access", "Free Drinks", "Merchandise Kit"])
        
        total_price = ev["price"] * num_tickets
        st.info(f"Total: {total_price} INR")

        if st.button("💳 Proceed to Payment"):
            with st.spinner("Processing payment..."):
                time.sleep(2)

            block = st.session_state["blockchain"].add_block(
                buyer, ev["artist"], seat_type, num_tickets, total_price, perks
            )

            ev["tickets"] -= num_tickets  # reduce availability

            # Generate QR Code
            qr_data = f"Ticket for {buyer} | {ev['artist']} | {seat_type} | {num_tickets} seats | {total_price} INR"
            qr = qrcode.make(qr_data)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Your Ticket QR Code")

            st.success(f"✅ Ticket booked for {buyer}! Enjoy {ev['artist']} 🎶")

# -------------------------------
# VERIFY TICKET
# -------------------------------
elif menu == "Verify Ticket":
    st.title("🔍 Verify Your Ticket")
    buyer = st.text_input("Enter buyer name to verify")
    if st.button("Check Ticket"):
        valid, block = st.session_state["blockchain"].verify_ticket(buyer)
        if valid:
            st.success("✅ Ticket is valid!")
            st.write(f"👤 Buyer: {block.buyer}")
            st.write(f"🎶 Event: {block.event}")
            st.write(f"🪑 Seat: {block.seat}")
            st.write(f"🔢 Tickets: {block.tickets}")
            st.write(f"💰 Paid: {block.price} INR")
            st.write(f"✨ Perks: {', '.join(block.perks) if block.perks else 'None'}")
        else:
            st.error("❌ No valid ticket found.")

# -------------------------------
# LEDGER
# -------------------------------
elif menu == "Ledger":
    st.title("📜 Blockchain Ledger")
    for b in st.session_state["blockchain"].chain:
        if b.index == 0: 
            continue
        st.markdown(f"""
        **Block {b.index}**  
        👤 {b.buyer} | 🎶 {b.event} | 🪑 {b.seat} | 🔢 {b.tickets} | 💰 {b.price} INR  
        ✨ Perks: {', '.join(b.perks) if b.perks else 'None'}  
        ⏰ {b.timestamp}  
        ---
        """)

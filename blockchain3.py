import streamlit as st
import hashlib
import time
import random

# QR code support (optional)
try:
    import qrcode, io
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# -----------------------
# Blockchain Classes
# -----------------------
class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        record = str(self.index) + str(self.timestamp) + str(self.data) + str(self.prev_hash)
        return hashlib.sha256(record.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, time.time(), {"genesis": "First Block"}, "0")

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), time.time(), data, prev_block.hash)
        self.chain.append(new_block)
        return new_block

    def is_ticket_valid(self, ticket_id=None, buyer_name=None):
        for block in self.chain:
            data = block.data
            if isinstance(data, dict):
                if ticket_id and data.get("ticket_id") == ticket_id:
                    return True, data
                if buyer_name and data.get("buyer") == buyer_name:
                    return True, data
        return False, None

# -----------------------
# Events Setup
# -----------------------
events = [
    {
        "id": 1,
        "name": "Rocking Beats Night",
        "artist": "Imagine Dragons",
        "date": "2025-10-15",
        "venue": "Wembley Stadium, London",
        "price": 120,
        "tickets": 50,
        "perks": "Free Drinks + Backstage Access"
    },
    {
        "id": 2,
        "name": "Bollywood Magic",
        "artist": "Arijit Singh",
        "date": "2025-11-10",
        "venue": "NSCI Dome, Mumbai",
        "price": 80,
        "tickets": 40,
        "perks": "Meet & Greet + Free Merchandise"
    },
    {
        "id": 3,
        "name": "Hip-Hop Fever",
        "artist": "Travis Scott",
        "date": "2025-12-05",
        "venue": "Madison Square Garden, NY",
        "price": 150,
        "tickets": 60,
        "perks": "VIP Lounge + Signed Poster"
    },
]

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Blockchain Ticketing", layout="centered")

if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()

st.title("🎟️ Blockchain-Based Event Ticketing System")

menu = st.radio("Choose an option", ["Buy Ticket", "Verify Ticket", "View Ledger"])

# -----------------------
# Buy Ticket
# -----------------------
if menu == "Buy Ticket":
    st.header("🛒 Buy a Ticket")

    event_choice = st.selectbox("Select an Event", events, format_func=lambda e: f"{e['name']} ({e['artist']})")

    if event_choice["tickets"] > 0:
        buyer_name = st.text_input("Enter your Name")
        if st.button("Proceed to Payment"):
            if buyer_name.strip() == "":
                st.warning("Please enter your name before buying.")
            else:
                # Mock payment
                with st.spinner("Processing payment..."):
                    time.sleep(2)

                # Generate ticket details
                ticket_id = hashlib.sha256(f"{buyer_name}{time.time()}".encode()).hexdigest()[:10]
                seat = f"Seat-{random.randint(1,100)}"

                ticket_data = {
                    "ticket_id": ticket_id,
                    "buyer": buyer_name,
                    "event": event_choice["name"],
                    "artist": event_choice["artist"],
                    "date": event_choice["date"],
                    "venue": event_choice["venue"],
                    "seat": seat,
                    "price": event_choice["price"]
                }

                # Add to blockchain
                new_block = st.session_state["blockchain"].add_block(ticket_data)

                # Reduce available tickets
                for ev in events:
                    if ev["id"] == event_choice["id"]:
                        ev["tickets"] -= 1

                # Show ticket summary
                st.success("✅ Ticket Purchased Successfully!")

                st.subheader("Your Ticket Details")
                st.write(f"**Ticket ID:** {ticket_id}")
                st.write(f"**Buyer:** {buyer_name}")
                st.write(f"**Event:** {event_choice['name']} ({event_choice['artist']})")
                st.write(f"**Date & Venue:** {event_choice['date']} at {event_choice['venue']}")
                st.write(f"**Seat:** {seat}")
                st.write(f"**Price:** ${event_choice['price']}")
                st.write(f"**Perks:** {event_choice['perks']}")
                st.caption(f"Hash: {new_block.hash[:12]}...")

                # QR Code
                if QR_AVAILABLE:
                    qr = qrcode.make(f"Ticket ID: {ticket_id}\nBuyer: {buyer_name}\nEvent: {event_choice['name']}\nSeat: {seat}")
                    buf = io.BytesIO()
                    qr.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption="📷 Scan QR to Verify", use_container_width=False)
                else:
                    st.warning("⚠️ QR code library not installed. Add `qrcode[pil]` to requirements.txt")

    else:
        st.error("❌ No tickets left for this event!")

# -----------------------
# Verify Ticket
# -----------------------
elif menu == "Verify Ticket":
    st.header("🔍 Verify Ticket")

    option = st.radio("Choose Verification Method", ["By Ticket ID", "By Buyer Name"])

    if option == "By Ticket ID":
        ticket_id_input = st.text_input("Enter Ticket ID")
        if st.button("Verify by ID"):
            valid, data = st.session_state["blockchain"].is_ticket_valid(ticket_id=ticket_id_input)
            if valid:
                st.success("✅ Ticket Found & Verified!")
                st.write(data)
            else:
                st.error("❌ Ticket not found!")

    else:
        buyer_name_input = st.text_input("Enter Buyer Name")
        if st.button("Verify by Name"):
            valid, data = st.session_state["blockchain"].is_ticket_valid(buyer_name=buyer_name_input)
            if valid:
                st.success("✅ Ticket Found & Verified!")
                st.write(data)
            else:
                st.error("❌ Ticket not found!")

# -----------------------
# Ledger
# -----------------------
elif menu == "View Ledger":
    st.header("📒 Blockchain Ledger")

    for block in st.session_state["blockchain"].chain:
        with st.container():
            st.markdown(f"### 🔗 Block {block.index}")
            st.write(f"⏰ Timestamp: {time.ctime(block.timestamp)}")
            st.write(f"📦 Data: {block.data}")
            st.write(f"🔑 Prev Hash: {block.prev_hash[:12]}...")
            st.write(f"🔒 Hash: {block.hash[:12]}...")
            st.divider()

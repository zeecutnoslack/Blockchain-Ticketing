import streamlit as st
import hashlib
import time
import random
import string

# Try importing QR library
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ---------------- Blockchain Setup ---------------- #
class Block:
    def __init__(self, index, previous_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.nonce}".encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), latest_block.hash, time.time(), data)
        self.chain.append(new_block)
        return new_block

    def is_ticket_valid(self, ticket_id):
        for block in self.chain[1:]:
            if isinstance(block.data, dict) and block.data.get("ticket_id") == ticket_id:
                return True, block.data
        return False, None

# ---------------- Event Data ---------------- #
events = {
    "Rocking Beats Night (Imagine Dragons)": {
        "artist": "Imagine Dragons",
        "date": "2025-10-15",
        "venue": "Wembley Stadium, London",
        "price": 120,
        "tickets": 50,
        "perks": "🎉 Free Drinks + Backstage Access",
    },
    "Bollywood Magic (Arijit Singh)": {
        "artist": "Arijit Singh",
        "date": "2025-11-10",
        "venue": "NSCI Dome, Mumbai",
        "price": 80,
        "tickets": 40,
        "perks": "🎁 Meet & Greet + Free Merchandise",
    },
    "Hip-Hop Fever (Travis Scott)": {
        "artist": "Travis Scott",
        "date": "2025-12-05",
        "venue": "Madison Square Garden, NY",
        "price": 150,
        "tickets": 60,
        "perks": "🔥 VIP Lounge + Signed Poster",
    },
}

# ---------------- Helpers ---------------- #
def generate_ticket_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def generate_qr_code(ticket_id):
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(ticket_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="Blockchain Ticketing", page_icon="🎟️", layout="wide")

if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "menu" not in st.session_state:
    st.session_state["menu"] = "🏠 Home"
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

st.sidebar.title("🎶 Navigation")
menu = st.sidebar.radio("Go to", ["🏠 Home", "🎫 Buy Ticket", "✅ Verify Ticket", "📜 Ledger"], index=["🏠 Home","🎫 Buy Ticket","✅ Verify Ticket","📜 Ledger"].index(st.session_state["menu"]))
st.session_state["menu"] = menu

# ---------------- Home ---------------- #
if menu == "🏠 Home":
    st.title("🎟️ Welcome to Blockchain Event Ticketing")
    st.write("Experience the future of ticketing — secure, fun, and verifiable on the blockchain.")
    st.subheader("✨ Featured Events")

    cols = st.columns(len(events))
    for i, (event_name, details) in enumerate(events.items()):
        with cols[i]:
            st.markdown(f"### {event_name.split('(')[0]}")
            st.write(f"**Artist:** {details['artist']}")
            st.write(f"**Date:** {details['date']}")
            st.write(f"**Venue:** {details['venue']}")
            st.write(f"**Price:** ${details['price']}")
            st.write(f"**Tickets Left:** {details['tickets']}")
            st.write(f"**Perks:** {details['perks']}")
            if st.button(f"🎟️ Book {details['artist']} Now", key=event_name):
                st.session_state["selected_event"] = event_name
                st.session_state["menu"] = "🎫 Buy Ticket"
                st.experimental_rerun()

# ---------------- Buy Ticket ---------------- #
elif menu == "🎫 Buy Ticket":
    st.header("🛒 Buy a Ticket")
    event_list = list(events.keys())
    default_index = event_list.index(st.session_state["selected_event"]) if st.session_state["selected_event"] in event_list else 0
    selected_event = st.selectbox("🎤 Select an Event", event_list, index=default_index)

    st.subheader("📝 Buyer Information")
    buyer_name = st.text_input("👤 Full Name")
    buyer_email = st.text_input("📧 Email Address")
    buyer_phone = st.text_input("📱 Phone Number")
    ticket_qty = st.number_input("🎟️ Number of Tickets", min_value=1, max_value=events[selected_event]["tickets"], value=1)
    seat_type = st.radio("💺 Seat Preference", ["VIP", "Premium", "Balcony", "Regular", "Standing"])
    st.info(f"✨ Perks with this ticket: {events[selected_event]['perks']}")

    if st.button("💳 Proceed to Payment"):
        ticket_id = generate_ticket_id()
        purchase = {
            "ticket_id": ticket_id,
            "event": selected_event,
            "buyer_name": buyer_name,
            "buyer_email": buyer_email,
            "buyer_phone": buyer_phone,
            "seat_type": seat_type,
            "quantity": ticket_qty,
            "price": events[selected_event]["price"] * ticket_qty,
        }
        st.session_state["blockchain"].add_block(purchase)
        events[selected_event]["tickets"] -= ticket_qty
        st.success("🎉 Ticket Purchased Successfully!")

        st.subheader("🎟️ Your Ticket Details")
        st.write(f"**Ticket ID:** `{ticket_id}`")
        st.write(f"**Event:** {selected_event}")
        st.write(f"**Name:** {buyer_name}")
        st.write(f"**Email:** {buyer_email}")
        st.write(f"**Phone:** {buyer_phone}")
        st.write(f"**Seat Type:** {seat_type}")
        st.write(f"**Quantity:** {ticket_qty}")
        st.write(f"**Total Price:** ${purchase['price']}")

        if QR_AVAILABLE:
            img = generate_qr_code(ticket_id)
            st.image(img, caption="📷 Your Ticket QR Code")

# ---------------- Verify Ticket ---------------- #
elif menu == "✅ Verify Ticket":
    st.header("🔍 Verify Your Ticket")
    ticket_id_input = st.text_input("Enter Ticket ID to Verify")
    if st.button("✅ Verify"):
        valid, data = st.session_state["blockchain"].is_ticket_valid(ticket_id_input)
        if valid:
            st.success("🎉 Ticket is VALID!")
            st.json(data)
        else:
            st.error("❌ Ticket not found or invalid!")

# ---------------- Ledger ---------------- #
elif menu == "📜 Ledger":
    st.header("📜 Blockchain Ledger")
    for block in st.session_state["blockchain"].chain:
        with st.expander(f"Block {block.index} | Hash: {block.hash[:10]}..."):
            st.write(f"⏰ {time.ctime(block.timestamp)}")
            st.write(f"🔗 Prev Hash: {block.previous_hash[:10]}...")
            st.write(f"📦 Data: {block.data}")

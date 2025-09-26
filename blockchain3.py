import streamlit as st
import hashlib
import time
import random
from datetime import datetime
from PIL import Image
import io

# Optional: QRCode library
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ---------------- Blockchain ---------------- #
class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.timestamp}{self.data}{self.prev_hash}".encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, {"msg": "Genesis Block"}, "0")

    def add_block(self, data):
        prev = self.chain[-1]
        new = Block(len(self.chain), data, prev.hash)
        self.chain.append(new)
        return new

    def is_ticket_valid(self, ticket_id):
        for block in self.chain[1:]:
            if block.data.get("ticket_id") == ticket_id:
                return True, block.data
        return False, None

# ---------------- Helpers ---------------- #
def generate_ticket_id():
    return hashlib.sha1(str(time.time()).encode()).hexdigest()[:10]

def generate_qr(text):
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(box_size=5, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def rerun():
    try:
        st.rerun()
    except:
        pass

# ---------------- Events ---------------- #
events = [
    {"name": "Imagine Dragons Live", "artist": "Imagine Dragons", "location": "Mumbai", "date": "2025-10-15", "price": 8000, "tickets_left": 50},
    {"name": "Ed Sheeran World Tour", "artist": "Ed Sheeran", "location": "Delhi", "date": "2025-11-02", "price": 9500, "tickets_left": 70},
    {"name": "Taylor Swift Eras Tour", "artist": "Taylor Swift", "location": "Bengaluru", "date": "2025-12-01", "price": 12000, "tickets_left": 100},
    {"name": "Coldplay Night", "artist": "Coldplay", "location": "Hyderabad", "date": "2025-10-20", "price": 10000, "tickets_left": 40},
    {"name": "Drake Live", "artist": "Drake", "location": "Kolkata", "date": "2025-11-15", "price": 9000, "tickets_left": 60},
]

# ---------------- Session ---------------- #
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

# ---------------- UI Layout ---------------- #
st.set_page_config(page_title="🎟️ Blockchain Ticketing", layout="wide")
menu = st.radio("Navigate", ["Home", "Buy Ticket", "Verify Ticket", "Ledger"], horizontal=True)

# ---------------- Home ---------------- #
if menu == "Home":
    st.header("🎶 Upcoming Events")
    cols = st.columns(3)
    for i, ev in enumerate(events):
        with cols[i % 3]:
            st.subheader(ev["name"])
            st.write(f"🎤 {ev['artist']}")
            st.write(f"📍 {ev['location']} | 📅 {ev['date']}")
            st.write(f"💰 ₹{ev['price']} | 🎟️ Left: {ev['tickets_left']}")
            if st.button("Book Now", key=f"book{i}"):
                st.session_state["selected_event"] = ev
                st.session_state["force_buy"] = True
                rerun()

# ---------------- Buy Ticket ---------------- #
elif menu == "Buy Ticket":
    st.header("🎫 Buy Ticket")
    ev = st.session_state.get("selected_event")
    if ev:
        st.subheader(ev["name"])
        st.write(f"🎤 {ev['artist']} | 📍 {ev['location']} | 📅 {ev['date']}")
        st.write(f"💰 Base Price: ₹{ev['price']} | 🎟️ Tickets Left: {ev['tickets_left']}")

        buyer = st.text_input("👤 Your Name")

        seat_type = st.selectbox("Choose Seat Type", ["Standard", "VIP", "Premium"])
        base_price = ev["price"] + (0 if seat_type == "Standard" else 3000 if seat_type == "VIP" else 5000)

        num_tickets = st.number_input("Number of Tickets", min_value=1, max_value=5, value=1)

        row = st.selectbox("Row", list("ABCDEFGH"))
        seats = [f"{row}{random.randint(1, 30)}" for _ in range(num_tickets)]

        perks = st.multiselect("Choose Perks", ["Free Drink", "Backstage Pass", "Merchandise", "Meet & Greet"])
        total_price = (base_price + len(perks) * 500) * num_tickets
        st.info(f"💵 Total Price: ₹{total_price}")

        with st.form("payment_form"):
            card_name = st.text_input("Name on Card")
            card_number = st.text_input("Card Number", type="password", max_chars=16)
            expiry = st.text_input("Expiry (MM/YY)")
            cvv = st.text_input("CVV", type="password", max_chars=3)
            confirm = st.form_submit_button("✅ Confirm & Pay")

        if confirm:
            if not buyer or not card_name or not card_number or not expiry or not cvv:
                st.error("⚠️ Fill all fields")
            elif ev["tickets_left"] < num_tickets:
                st.error("❌ Not enough tickets available")
            else:
                tickets = []
                for seat in seats:
                    ticket_id = generate_ticket_id()
                    ev["tickets_left"] -= 1
                    tx = {
                        "buyer": buyer, "event": ev["name"], "artist": ev["artist"],
                        "location": ev["location"], "date": ev["date"],
                        "seat": seat, "seat_type": seat_type, "perks": perks,
                        "price": total_price, "ticket_id": ticket_id
                    }
                    st.session_state["blockchain"].add_block(tx)
                    tickets.append((ticket_id, seat))

                st.success("🎉 Ticket(s) Booked!")
                for tid, seat in tickets:
                    st.subheader("Your Ticket")
                    st.write(f"👤 {buyer}")
                    st.write(f"🎤 {ev['artist']}")
                    st.write(f"📍 {ev['location']} | {ev['date']}")
                    st.write(f"🎟️ Seat: {seat} ({seat_type})")
                    st.write(f"⭐ Perks: {', '.join(perks) if perks else 'None'}")
                    st.write(f"💵 Price: ₹{total_price//num_tickets}")
                    st.code(tid, language="bash")
                    if QR_AVAILABLE:
                        qr_buf = generate_qr(f"Ticket:{tid}|Buyer:{buyer}|Event:{ev['name']}")
                        st.image(Image.open(qr_buf), caption="📲 Scan to Verify Ticket")
    else:
        st.info("Select an event from Home to book tickets.")

# ---------------- Verify Ticket ---------------- #
elif menu == "Verify Ticket":
    st.header("🔍 Verify Ticket")
    tid = st.text_input("Enter Ticket ID")
    if st.button("Verify"):
        valid, data = st.session_state["blockchain"].is_ticket_valid(tid)
        if valid:
            st.success("✅ Valid Ticket")
            st.json(data)
        else:
            st.error("❌ Invalid Ticket")

# ---------------- Ledger ---------------- #
elif menu == "Ledger":
    st.header("📒 Blockchain Ledger")
    if "blockchain" in st.session_state:
        for block in st.session_state["blockchain"].chain:
            with st.expander(f"Block {block.index} | Hash: {block.hash[:10]}..."):
                st.write(f"⏰ {datetime.fromtimestamp(block.timestamp)}")
                st.json(block.data)
    else:
        st.error("⚠️ Blockchain not initialized")

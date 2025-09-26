import streamlit as st
import time
import hashlib
import random
import string
from io import BytesIO
from PIL import Image
import qrcode


# ---------------- Blockchain ---------------- #
class Block:
    def __init__(self, index, prev_hash, timestamp, data, nonce=0):
        self.index = index
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.calc_hash()

    def calc_hash(self):
        block_string = f"{self.index}{self.prev_hash}{self.timestamp}{self.data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, "0", time.time(), "Genesis Block")

    def add_block(self, data):
        prev = self.chain[-1]
        new_block = Block(len(self.chain), prev.hash, time.time(), data)
        self.chain.append(new_block)
        return new_block


# ---------------- Helper Functions ---------------- #
def generate_ticket_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_seat():
    row = random.choice("ABCDEFGH")
    number = random.randint(1, 30)
    return f"{row}{number}"


def generate_qr(data: str):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    return buf


def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except Exception:
            st.session_state["_rerun_requested"] = True
            st.stop()


# ---------------- Event Data ---------------- #
events = [
    {"name": "Imagine Dragons Live", "artist": "Imagine Dragons", "location": "New York", "date": "2025-10-05", "price": 120, "tickets_left": 50},
    {"name": "Coldplay World Tour", "artist": "Coldplay", "location": "Los Angeles", "date": "2025-11-12", "price": 150, "tickets_left": 70},
    {"name": "Ed Sheeran Night", "artist": "Ed Sheeran", "location": "London", "date": "2025-09-30", "price": 100, "tickets_left": 30},
    {"name": "Adele Special", "artist": "Adele", "location": "Paris", "date": "2025-12-01", "price": 200, "tickets_left": 20},
    {"name": "The Weeknd Concert", "artist": "The Weeknd", "location": "Toronto", "date": "2025-10-20", "price": 180, "tickets_left": 40},
]


# ---------------- Streamlit App ---------------- #
st.set_page_config(page_title="Blockchain Ticketing", layout="wide")
st.title("🎟️ Blockchain-based Event Ticketing System")

# Session state
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

# Navigation bar
if "force_tab" in st.session_state:
    default_tab = st.session_state.pop("force_tab")
else:
    default_tab = "Home"

menu = st.radio(
    "Navigate",
    ["Home", "Buy Ticket", "Verify Ticket", "Ledger"],
    horizontal=True,
    index=["Home", "Buy Ticket", "Verify Ticket", "Ledger"].index(default_tab),
)


# ---------------- Home ---------------- #
if menu == "Home":
    st.header("Upcoming Events")
    for i, ev in enumerate(events):
        with st.container():
            st.subheader(ev["name"])
            st.write(f"🎤 Artist: {ev['artist']}")
            st.write(f"📍 Location: {ev['location']}")
            st.write(f"📅 Date: {ev['date']}")
            st.write(f"💵 Price: ${ev['price']}")
            st.write(f"🎟️ Tickets Left: {ev['tickets_left']}")
            if st.button("Book Now", key=f"book{i}"):
                st.session_state["selected_event"] = ev
                st.session_state["force_tab"] = "Buy Ticket"
                safe_rerun()


# ---------------- Buy Ticket ---------------- #
elif menu == "Buy Ticket":
    st.header("🎫 Buy Ticket")

    if st.session_state["selected_event"]:
        ev = st.session_state["selected_event"]
        st.subheader(ev["name"])
        st.write(f"Artist: {ev['artist']}")
        st.write(f"Location: {ev['location']} | Date: {ev['date']}")
        st.write(f"Price: ${ev['price']} | Tickets Left: {ev['tickets_left']}")

        buyer = st.text_input("Enter Your Name")
        with st.form("payment_form"):
            card_name = st.text_input("Name on Card")
            card_number = st.text_input("Card Number", max_chars=16, type="password")
            expiry = st.text_input("Expiry Date (MM/YY)")
            cvv = st.text_input("CVV", max_chars=3, type="password")
            confirm = st.form_submit_button("✅ Confirm & Pay")

        if confirm:
            if not buyer or not card_name or not card_number or not expiry or not cvv:
                st.error("⚠️ Please fill all fields")
            elif ev["tickets_left"] <= 0:
                st.error("❌ No tickets left for this event.")
            else:
                ticket_id = generate_ticket_id()
                seat = generate_seat()
                ev["tickets_left"] -= 1

                tx_data = {
                    "buyer": buyer,
                    "event": ev["name"],
                    "artist": ev["artist"],
                    "location": ev["location"],
                    "date": ev["date"],
                    "seat": seat,
                    "price": ev["price"],
                    "ticket_id": ticket_id,
                }
                st.session_state["blockchain"].add_block(tx_data)

                st.success("🎉 Payment Successful! Ticket Booked.")
                st.subheader("Your Ticket")
                st.write(f"👤 {buyer}")
                st.write(f"🎤 {ev['artist']}")
                st.write(f"📍 {ev['location']} | {ev['date']}")
                st.write(f"🎟️ Seat: {seat}")
                st.write(f"💵 Price: ${ev['price']}")
                st.code(ticket_id, language="bash")

                qr_buf = generate_qr(f"TicketID:{ticket_id}|Buyer:{buyer}|Event:{ev['name']}")
                st.image(Image.open(qr_buf), caption="Scan to Verify Ticket")
    else:
        st.info("Select an event from Home to book tickets.")


# ---------------- Verify Ticket ---------------- #
elif menu == "Verify Ticket":
    st.header("🔎 Verify Ticket")
    option = st.radio("Search By:", ["Buyer Name", "Ticket ID"], horizontal=True)
    query = st.text_input("Enter your details")

    if st.button("Verify"):
        found = False
        for block in st.session_state["blockchain"].chain:
            if isinstance(block.data, dict):
                if (option == "Buyer Name" and block.data["buyer"].lower() == query.lower()) or \
                   (option == "Ticket ID" and block.data["ticket_id"] == query):
                    st.success("✅ Ticket Found!")
                    st.subheader(block.data["event"])
                    st.write(f"👤 {block.data['buyer']}")
                    st.write(f"🎤 {block.data['artist']}")
                    st.write(f"📍 {block.data['location']}")
                    st.write(f"📅 {block.data['date']}")
                    st.write(f"🎟️ Seat: {block.data['seat']}")
                    st.write(f"💵 Price: ${block.data['price']}")
                    st.write(f"🆔 Ticket ID: `{block.data['ticket_id']}`")
                    found = True
        if not found:
            st.error("❌ Ticket not found or invalid")


# ---------------- Ledger ---------------- #
elif menu == "Ledger":
    st.header("📜 Blockchain Ledger")
    for i, block in enumerate(st.session_state["blockchain"].chain):
        with st.expander(f"Block {i} | Hash {block.hash[:12]}..."):
            st.write(f"⏰ {time.ctime(block.timestamp)}")
            st.write(f"🔗 Prev Hash: {block.prev_hash[:12]}...")
            st.write(f"🔑 Hash: {block.hash[:12]}...")
            if isinstance(block.data, dict):
                st.markdown("**Ticket Data:**")
                for k, v in block.data.items():
                    st.write(f"- {k}: {v}")

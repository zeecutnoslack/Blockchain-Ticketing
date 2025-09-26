import streamlit as st
import random
import time
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Blockchain Class
# -----------------------------
class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.ctime()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = hash((self.index, self.timestamp, str(self.data), self.prev_hash))


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), data, prev_block.hash)
        self.chain.append(new_block)

    def get_chain(self):
        return self.chain


# -----------------------------
# Initialize Session State
# -----------------------------
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "events" not in st.session_state:
    st.session_state["events"] = [
        {
            "artist": "Imagine Dragons",
            "event": "Night Visions Tour",
            "date": "2025-10-12",
            "time": "7:30 PM",
            "venue": "Mumbai Stadium",
            "location": "Mumbai, India",
            "price": 2500,
            "total_seats": 30,
            "available_seats": [f"A{i}" for i in range(1, 31)],
            "perks": ["Free Drinks", "Backstage Access"],
            "banner": "https://upload.wikimedia.org/wikipedia/en/3/3f/Imagine_Dragons_Night_Visions.jpg"
        },
        {
            "artist": "Arijit Singh",
            "event": "Romantic Melodies",
            "date": "2025-11-05",
            "time": "8:00 PM",
            "venue": "Delhi Concert Arena",
            "location": "Delhi, India",
            "price": 1800,
            "total_seats": 25,
            "available_seats": [f"B{i}" for i in range(1, 26)],
            "perks": ["Meet & Greet", "VIP Lounge"],
            "banner": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Arijit_Singh.jpg"
        },
        {
            "artist": "Taylor Swift",
            "event": "Eras Tour",
            "date": "2025-12-20",
            "time": "6:30 PM",
            "venue": "Bengaluru Open Grounds",
            "location": "Bengaluru, India",
            "price": 4500,
            "total_seats": 40,
            "available_seats": [f"C{i}" for i in range(1, 41)],
            "perks": ["Signed Poster", "Premium Goodies"],
            "banner": "https://upload.wikimedia.org/wikipedia/en/f/f2/Taylor_Swift_-_1989.png"
        },
        {
            "artist": "Coldplay",
            "event": "Music of the Spheres",
            "date": "2026-01-15",
            "time": "7:00 PM",
            "venue": "Hyderabad Rock Arena",
            "location": "Hyderabad, India",
            "price": 3200,
            "total_seats": 35,
            "available_seats": [f"D{i}" for i in range(1, 36)],
            "perks": ["Glow Bands", "Exclusive Merch"],
            "banner": "https://upload.wikimedia.org/wikipedia/en/0/0a/Coldplay_-_Music_of_the_Spheres.png"
        },
    ]
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None
if "ticket" not in st.session_state:
    st.session_state["ticket"] = None


# -----------------------------
# Generate QR Code
# -----------------------------
def generate_qr(data: str):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf


# -----------------------------
# Main App
# -----------------------------
st.set_page_config(page_title="🎟️ Blockchain Ticketing", layout="wide")
st.title("🎶 Blockchain-Powered Concert Ticketing System")

menu = st.tabs(["🏠 Home", "🎫 Buy Ticket", "✅ Verify Ticket", "📜 Ledger"])

# -----------------------------
# HOME TAB
# -----------------------------
with menu[0]:
    st.subheader("🔥 Upcoming Events")
    cols = st.columns(len(st.session_state["events"]))

    for i, ev in enumerate(st.session_state["events"]):
        with cols[i]:
            st.image(ev["banner"], use_container_width=True)
            st.markdown(f"### {ev['artist']}")
            st.markdown(f"**Event:** {ev['event']}")
            st.markdown(f"📍 {ev['venue']} - {ev['location']}")
            st.markdown(f"📅 {ev['date']} | 🕒 {ev['time']}")
            st.markdown(f"💰 Price: ₹{ev['price']}")
            st.markdown(f"🎟️ Seats Left: {len(ev['available_seats'])}/{ev['total_seats']}")
            if st.button(f"Book Now - {ev['artist']}", key=f"book_{i}"):
                st.session_state["selected_event"] = ev
                st.session_state["ticket"] = None


# -----------------------------
# BUY TICKET TAB
# -----------------------------
with menu[1]:
    if not st.session_state["selected_event"]:
        st.warning("👉 Select an event from Home to continue.")
    else:
        ev = st.session_state["selected_event"]
        st.header(f"🎫 Booking: {ev['event']} - {ev['artist']}")
        st.image(ev["banner"], use_container_width=True)
        st.markdown(f"📍 Venue: **{ev['venue']} - {ev['location']}**")
        st.markdown(f"📅 {ev['date']} | 🕒 {ev['time']}")
        st.markdown(f"💰 Price per Ticket: **₹{ev['price']}**")
        st.markdown(f"🎟️ Seats Left: **{len(ev['available_seats'])}**")

        buyer = st.text_input("👤 Enter Your Name")
        num_tickets = st.number_input("🎟️ Number of Tickets", min_value=1, max_value=5, value=1)
        seats = st.multiselect("🪑 Select Your Seats", ev["available_seats"], max_selections=num_tickets)
        perk = st.selectbox("✨ Choose a Perk", ev["perks"])

        if st.button("Proceed to Payment"):
            if not buyer or len(seats) != num_tickets:
                st.error("⚠️ Please enter name and select required number of seats.")
            else:
                total_cost = ev["price"] * num_tickets
                st.success(f"✅ Payment Successful! Amount Paid: ₹{total_cost}")
                for s in seats:
                    ev["available_seats"].remove(s)

                ticket_id = f"TKT{random.randint(1000,9999)}"
                ticket_data = {
                    "ticket_id": ticket_id,
                    "buyer": buyer,
                    "artist": ev["artist"],
                    "event": ev["event"],
                    "date": ev["date"],
                    "time": ev["time"],
                    "venue": ev["venue"],
                    "location": ev["location"],
                    "seats": seats,
                    "perk": perk,
                    "price": total_cost,
                }
                st.session_state["blockchain"].add_block(ticket_data)
                st.session_state["ticket"] = ticket_data

        if st.session_state["ticket"]:
            t = st.session_state["ticket"]
            st.subheader("🎟️ Your Digital Ticket")
            st.markdown(f"**Ticket ID:** {t['ticket_id']}")
            st.markdown(f"👤 Name: {t['buyer']}")
            st.markdown(f"🎶 Artist: {t['artist']}")
            st.markdown(f"📍 Venue: {t['venue']} - {t['location']}")
            st.markdown(f"📅 {t['date']} | 🕒 {t['time']}")
            st.markdown(f"🪑 Seats: {', '.join(t['seats'])}")
            st.markdown(f"✨ Perk: {t['perk']}")
            st.markdown(f"💰 Paid: ₹{t['price']}")

            qr_buf = generate_qr(f"TicketID: {t['ticket_id']} | Buyer: {t['buyer']} | Seats: {t['seats']}")
            st.image(qr_buf, caption="Scan for Ticket Verification", use_container_width=False)


# -----------------------------
# VERIFY TICKET TAB
# -----------------------------
with menu[2]:
    st.subheader("🔍 Verify Ticket")
    tid = st.text_input("Enter Ticket ID to verify")
    if st.button("Verify"):
        valid = False
        for blk in st.session_state["blockchain"].chain:
            if isinstance(blk.data, dict) and blk.data.get("ticket_id") == tid:
                st.success(f"✅ Ticket is valid for {blk.data['event']} - {blk.data['artist']}")
                st.json(blk.data)
                valid = True
                break
        if not valid:
            st.error("❌ Ticket not found!")


# -----------------------------
# LEDGER TAB
# -----------------------------
with menu[3]:
    st.subheader("📜 Blockchain Ledger")
    for blk in st.session_state["blockchain"].chain:
        with st.expander(f"Block {blk.index} | {blk.timestamp}"):
            st.write(f"🔗 Previous Hash: {blk.prev_hash}")
            st.write(f"🔒 Hash: {blk.hash}")
            st.json(blk.data)

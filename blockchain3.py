import streamlit as st
import time, hashlib, random, qrcode
from io import BytesIO
from PIL import Image

# ---------------- Blockchain ----------------
class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        return hashlib.sha256(
            f"{self.index}{self.timestamp}{self.data}{self.prev_hash}".encode()
        ).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.genesis_block()]

    def genesis_block(self):
        return Block(0, time.time(), {"genesis": True}, "0")

    def add_block(self, data):
        prev = self.chain[-1]
        block = Block(len(self.chain), time.time(), data, prev.hash)
        self.chain.append(block)
        return block

    def is_ticket_valid(self, ticket_id):
        for block in self.chain:
            if block.data.get("ticket_id") == ticket_id:
                return True, block.data
        return False, None


# ---------------- Events ----------------
events = [
    {
        "artist": "Imagine Dragons",
        "image": "https://upload.wikimedia.org/wikipedia/en/0/05/Imagine_Dragons.png",
        "dates": [
            {"city": "Mumbai", "date": "2025-11-10", "price": 3000},
            {"city": "Delhi", "date": "2025-11-12", "price": 2800},
        ],
    },
    {
        "artist": "Arijit Singh",
        "image": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Arijit_Singh.png",
        "dates": [
            {"city": "Kolkata", "date": "2025-11-15", "price": 2000},
            {"city": "Bangalore", "date": "2025-11-18", "price": 2200},
        ],
    },
    {
        "artist": "BTS",
        "image": "https://upload.wikimedia.org/wikipedia/commons/9/97/BTS_logo.png",
        "dates": [
            {"city": "Seoul", "date": "2025-12-01", "price": 10000},
            {"city": "Tokyo", "date": "2025-12-05", "price": 9500},
        ],
    },
    {
        "artist": "Taylor Swift",
        "image": "https://upload.wikimedia.org/wikipedia/en/f/f6/Taylor_Swift.png",
        "dates": [
            {"city": "London", "date": "2025-12-10", "price": 12000},
            {"city": "New York", "date": "2025-12-15", "price": 12500},
        ],
    },
]

# ---------------- Session ----------------
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "menu" not in st.session_state:
    st.session_state["menu"] = "Home"
if "selected_event" not in st.session_state:
    st.session_state["selected_event"] = None

# ---------------- Menu ----------------
menu = st.radio(
    "Navigate",
    ["Home", "Buy Ticket", "Verify Ticket", "Ledger"],
    horizontal=True,
    index=["Home", "Buy Ticket", "Verify Ticket", "Ledger"].index(st.session_state["menu"]),
)
st.session_state["menu"] = menu

# ---------------- Home ----------------
if menu == "Home":
    st.title("🎟️ Blockchain Event Ticketing")
    st.subheader("Choose your concert experience")

    cols = st.columns(2)
    for i, ev in enumerate(events):
        with cols[i % 2]:
            st.image(ev["image"], width=250)
            st.markdown(f"### {ev['artist']}")
            for d in ev["dates"]:
                st.write(f"📍 {d['city']} — {d['date']} — ₹{d['price']}")
            if st.button("Book Now", key=f"book_{i}"):
                st.session_state["selected_event"] = ev
                st.session_state["menu"] = "Buy Ticket"
                st.rerun()

# ---------------- Buy Ticket ----------------
elif menu == "Buy Ticket":
    if st.session_state["selected_event"] is None:
        st.warning("Pick an event from Home first.")
    else:
        ev = st.session_state["selected_event"]
        st.header(f"🎤 Book Tickets for {ev['artist']}")
        st.image(ev["image"], width=300)

        buyer_name = st.text_input("👤 Your Name")
        city_date = st.selectbox(
            "📅 Choose Date & Location",
            [f"{d['city']} — {d['date']} — ₹{d['price']}" for d in ev["dates"]],
        )
        tickets = st.number_input("🎟 Number of Tickets", 1, 6, 1)

        # Seat selection
        row = st.selectbox("Row", ["A", "B", "C", "D"])
        seat_num = st.selectbox("Seat Number", list(range(1, 11)))
        seat = f"{row}{seat_num}"

        # Perks
        perks = st.multiselect("✨ Choose Perks", ["Free Merch", "Backstage Pass", "Food & Drinks"])

        # Seat type pricing
        seat_type = st.radio("Seat Type", ["Regular", "VIP (+₹2000)", "VVIP (+₹5000)"])

        # Mock payment
        st.subheader("💳 Payment Details")
        card = st.text_input("Card Number")
        cvv = st.text_input("CVV", type="password")

        if st.button("Confirm & Pay"):
            base_price = next(d["price"] for d in ev["dates"] if d["city"] in city_date)
            extra = 0
            if "VIP" in seat_type:
                extra = 2000
            if "VVIP" in seat_type:
                extra = 5000
            total = (base_price + extra) * tickets

            st.success(f"✅ Payment successful! You paid ₹{total}")
            ticket_id = str(random.randint(1000000000, 9999999999))

            st.session_state["blockchain"].add_block(
                {
                    "ticket_id": ticket_id,
                    "buyer": buyer_name,
                    "event": ev["artist"],
                    "city_date": city_date,
                    "seat": seat,
                    "seat_type": seat_type,
                    "perks": perks,
                    "tickets": tickets,
                    "amount": total,
                }
            )

            # QR code
            qr = qrcode.make(f"Ticket ID: {ticket_id}\nEvent: {ev['artist']}\nSeat: {seat}")
            buf = BytesIO()
            qr.save(buf)
            st.image(Image.open(BytesIO(buf.getvalue())), caption="Your Ticket QR Code")

            st.info(f"🎟️ Your Ticket ID: {ticket_id}")

# ---------------- Verify Ticket ----------------
elif menu == "Verify Ticket":
    st.header("🔍 Verify Ticket")
    ticket_id = st.text_input("Enter Ticket ID")
    if st.button("Verify"):
        valid, data = st.session_state["blockchain"].is_ticket_valid(ticket_id)
        if valid:
            st.success("✔ Ticket is VALID")
            st.markdown(f"""
            **Buyer:** {data['buyer']}  
            **Event:** {data['event']}  
            **Location & Date:** {data['city_date']}  
            **Seat:** {data['seat']} ({data['seat_type']})  
            **Tickets:** {data['tickets']}  
            **Amount Paid:** ₹{data['amount']}  
            **Perks:** {', '.join(data['perks']) if data['perks'] else 'None'}  
            """)
        else:
            st.error("❌ Ticket not found")

# ---------------- Ledger ----------------
elif menu == "Ledger":
    st.header("📜 Blockchain Ledger")
    for block in st.session_state["blockchain"].chain:
        st.markdown(f"**Block {block.index}** — {time.ctime(block.timestamp)}")
        st.write(block.data)
        st.caption(f"Hash: {block.hash[:12]}...")
        st.markdown("---")

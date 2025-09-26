import streamlit as st
import hashlib
import time
import random
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


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

    def search_tickets(self, ticket_id=None, buyer_name=None):
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
        "date": "15th Nov 2025",
        "venue": "Skyline Arena, Mumbai",
        "cost": 1500,
        "image": "https://images.unsplash.com/photo-1507874457470-272b3c8d8ee2",
        "perks": ["Glow sticks", "VIP lounge", "Blockchain-protected ticket"],
        "tickets": 200,
        "rows": 20,  # seat rows
        "cols": 10,  # seats per row
    },
    {
        "name": "Rock Revolution",
        "artist": "The StarLights",
        "date": "20th Nov 2025",
        "venue": "Bandra Stadium, Mumbai",
        "cost": 1800,
        "image": "https://images.unsplash.com/photo-1507878866276-a947ef722fee",
        "perks": ["Backstage pass", "Free merch", "Meet & greet"],
        "tickets": 150,
        "rows": 15,
        "cols": 10,
    },
    {
        "name": "Classical Nights",
        "artist": "Symphony of India",
        "date": "1st Dec 2025",
        "venue": "Delhi Opera Hall",
        "cost": 1200,
        "image": "https://images.unsplash.com/photo-1521335629791-ce4aec67dd53",
        "perks": ["Complimentary wine", "Front row upgrade", "Blockchain ticket"],
        "tickets": 100,
        "rows": 10,
        "cols": 10,
    },
]

# ---------------------------
# Helper: QR Code Generator
# ---------------------------
def generate_qr_code(data: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


# ---------------------------
# Streamlit Config
# ---------------------------
st.set_page_config(page_title="🎟 Blockchain Ticketing", layout="wide")

if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "sold_tickets" not in st.session_state:
    st.session_state["sold_tickets"] = {i: 0 for i in range(len(EVENTS))}
if "used_seats" not in st.session_state:
    st.session_state["used_seats"] = {i: [] for i in range(len(EVENTS))}

st.markdown(
    "<h1 style='text-align: center; color: #ff4b4b;'>🎶 Blockchain Ticketing System 🎶</h1>",
    unsafe_allow_html=True,
)
st.write("Secure • Transparent • Fraud-Proof")

# ---------------------------
# Tabs for Navigation
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "🛒 Buy Ticket", "✅ Verify Ticket", "📒 Blockchain Ledger"])

# ---------------------------
# Home
# ---------------------------
with tab1:
    st.subheader("Upcoming Events")
    cols = st.columns(3)
    for idx, event in enumerate(EVENTS):
        with cols[idx % 3]:
            st.image(event["image"], use_column_width=True)
            st.markdown(f"### {event['name']}")
            st.write(f"**Artist:** {event['artist']}")
            st.write(f"📅 {event['date']} | 📍 {event['venue']}")
            st.write(f"💰 ₹{event['cost']} per ticket")
            st.progress(st.session_state["sold_tickets"][idx] / event["tickets"])
            st.caption(f"{event['tickets'] - st.session_state['sold_tickets'][idx]} tickets left")
            with st.expander("Perks Included"):
                st.write(", ".join(event["perks"]))

# ---------------------------
# Buy Ticket
# ---------------------------
with tab2:
    st.subheader("Buy Your Ticket")
    event_choice = st.selectbox("Choose Event", [e["name"] for e in EVENTS])
    buyer_name = st.text_input("Your Full Name")

    if st.button("🎟 Confirm Purchase"):
        event_index = [e["name"] for e in EVENTS].index(event_choice)
        event = EVENTS[event_index]

        if st.session_state["sold_tickets"][event_index] < event["tickets"]:
            # Assign unique ticket ID
            ticket_id = f"TKT{random.randint(10000, 99999)}"

            # Assign seat (random unused)
            all_seats = [f"{chr(65+r)}{c+1}" for r in range(event["rows"]) for c in range(event["cols"])]
            available_seats = list(set(all_seats) - set(st.session_state["used_seats"][event_index]))
            if not available_seats:
                st.error("No seats left!")
            else:
                seat = random.choice(available_seats)
                st.session_state["used_seats"][event_index].append(seat)

                # Save transaction
                transaction = {
                    "ticket_id": ticket_id,
                    "buyer": buyer_name,
                    "event": event["name"],
                    "artist": event["artist"],
                    "date": event["date"],
                    "venue": event["venue"],
                    "cost": event["cost"],
                    "seat": seat,
                }
                st.session_state["blockchain"].add_block(transaction)
                st.session_state["sold_tickets"][event_index] += 1

                # Generate QR Code
                if QR_AVAILABLE:
                qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=6,
                border=4,
                )
                qr.add_data(ticket_details)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                st.image(img, caption="Your Ticket QR Code")
                else:
                st.warning("⚠ QR code feature is unavailable (missing `qrcode` library). Please check requirements.txt")


                # Show ticket card
                st.success("✅ Purchase Successful!")
                st.markdown(
                    f"""
                    <div style="border:2px solid #ff4b4b; border-radius:10px; padding:15px; background:#fff3f3;">
                    <h3 style="color:#ff4b4b;">🎟 Your Ticket</h3>
                    <b>Ticket ID:</b> {ticket_id} <br>
                    <b>Buyer:</b> {buyer_name} <br>
                    <b>Event:</b> {event['name']} ({event['artist']}) <br>
                    <b>Date:</b> {event['date']} <br>
                    <b>Venue:</b> {event['venue']} <br>
                    <b>Seat:</b> {seat} <br>
                    <b>Cost:</b> ₹{event['cost']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.error("❌ Tickets Sold Out!")

# ---------------------------
# Verify Ticket
# ---------------------------
with tab3:
    st.subheader("Verify Your Ticket")
    method = st.radio("Verify by:", ["Ticket ID", "Buyer Name"])

    if method == "Ticket ID":
        tid = st.text_input("Enter Ticket ID")
        if st.button("Check Ticket"):
            results = st.session_state["blockchain"].search_tickets(ticket_id=tid)
            if results:
                tx = results[0]
                st.success("Ticket Found ✅")
                st.write(tx)
            else:
                st.error("Invalid Ticket ❌")

    elif method == "Buyer Name":
        name = st.text_input("Enter Buyer Name")
        if st.button("Check Buyer"):
            results = st.session_state["blockchain"].search_tickets(buyer_name=name)
            if results:
                st.success(f"Tickets found for {name}:")
                for tx in results:
                    st.write(f"- {tx['event']} | ID: {tx['ticket_id']} | Seat: {tx['seat']}")
            else:
                st.error("No Tickets Found ❌")

# ---------------------------
# Blockchain Ledger
# ---------------------------
with tab4:
    st.subheader("Blockchain Ledger")
    for block in reversed(st.session_state["blockchain"].chain):
        st.markdown(
            f"""
            <div style="border:1px solid #ccc; border-radius:10px; padding:10px; margin:10px; background:#f9f9f9;">
            <b>Block:</b> {block.index} <br>
            <b>Timestamp:</b> {block.timestamp} <br>
            <b>Buyer:</b> {block.transaction.get("buyer")} <br>
            <b>Event:</b> {block.transaction.get("event")} <br>
            <b>Seat:</b> {block.transaction.get("seat")} <br>
            <b>Ticket ID:</b> {block.transaction.get("ticket_id")} <br>
            <b>Hash:</b> {block.hash[:12]}... <br>
            <b>Prev Hash:</b> {block.previous_hash[:12]}...
            </div>
            """,
            unsafe_allow_html=True,
        )

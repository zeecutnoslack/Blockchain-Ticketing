import streamlit as st
import hashlib, json, time, uuid, io
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ------------------------
# Blockchain Implementation
# ------------------------
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        return hashlib.sha256(
            (str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode()
        ).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, time.time(), {"message": "Genesis Block"}, "0")
        self.chain.append(genesis)

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), time.time(), data, prev_block.hash)
        self.chain.append(new_block)
        return new_block

    def verify_ticket(self, ticket_id):
        for block in self.chain:
            if "ticket_id" in block.data and block.data["ticket_id"] == ticket_id:
                return True, block.data
        return False, None

# ------------------------
# Session State
# ------------------------
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

# ------------------------
# Events List
# ------------------------
events = [
    {"name": "Rocking Beats Night", "artist": "Imagine Dragons", "date": "2025-10-15", "venue": "Wembley Stadium, London", "price": 120},
    {"name": "Bollywood Magic", "artist": "Arijit Singh", "date": "2025-11-10", "venue": "NSCI Dome, Mumbai", "price": 80},
    {"name": "Hip-Hop Fever", "artist": "Travis Scott", "date": "2025-12-05", "venue": "Madison Square Garden, NY", "price": 150},
]

# ------------------------
# Navigation Tabs
# ------------------------
tabs = st.tabs(["🏠 Home", "🎟 Buy Ticket", "✅ Verify Ticket", "📜 Ledger"])

# ------------------------
# Home Page
# ------------------------
with tabs[0]:
    st.title("🎫 Welcome to Blockchain Event Ticketing")
    st.write("Experience the future of ticketing — secure, fun, and verifiable on the blockchain.")
    st.subheader("✨ Featured Events")

    cols = st.columns(len(events))
    for i, ev in enumerate(events):
        with cols[i]:
            st.markdown(f"**{ev['name']}**")
            st.write(f"**Artist:** {ev['artist']}")
            st.write(f"**Date:** {ev['date']}")
            st.write(f"**Venue:** {ev['venue']}")
            st.write(f"**Price:** ${ev['price']}")
            if st.button(f"Book {ev['artist']} Now", key=f"book_{i}"):
                st.session_state.selected_event = ev
                st.experimental_rerun()

# ------------------------
# Buy Ticket Page
# ------------------------
with tabs[1]:
    st.header("🛒 Buy a Ticket")

    event_names = [e["name"] for e in events]
    default_index = event_names.index(st.session_state.selected_event["name"]) if st.session_state.selected_event else 0
    event_choice = st.selectbox("Select Event", event_names, index=default_index)

    buyer_name = st.text_input("Enter Your Full Name")
    buyer_email = st.text_input("Enter Your Email")
    buyer_phone = st.text_input("Enter Your Phone Number")
    payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "UPI", "PayPal"])

    if st.button("💳 Proceed to Payment"):
        if buyer_name and buyer_email and buyer_phone:
            ticket_id = str(uuid.uuid4())[:8]
            data = {
                "ticket_id": ticket_id,
                "event": event_choice,
                "buyer_name": buyer_name,
                "buyer_email": buyer_email,
                "buyer_phone": buyer_phone,
                "payment_method": payment_method,
            }
            block = st.session_state.blockchain.add_block(data)

            st.success("✅ Ticket Purchased Successfully!")
            st.subheader("Your Ticket Details")
            st.write(f"**Ticket ID:** {ticket_id}")
            st.write(f"**Event:** {event_choice}")
            st.write(f"**Name:** {buyer_name}")
            st.write(f"**Email:** {buyer_email}")
            st.write(f"**Phone:** {buyer_phone}")
            st.write(f"**Payment Method:** {payment_method}")

            # QR Code
            qr = qrcode.make(f"TicketID: {ticket_id}\nEvent: {event_choice}\nName: {buyer_name}")
            st.image(qr, caption="🎟 Your QR Ticket", use_container_width=True)

            # Download PDF Ticket
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            c.drawString(100, 750, "Blockchain Event Ticket")
            c.drawString(100, 720, f"Ticket ID: {ticket_id}")
            c.drawString(100, 700, f"Event: {event_choice}")
            c.drawString(100, 680, f"Name: {buyer_name}")
            c.drawString(100, 660, f"Email: {buyer_email}")
            c.drawString(100, 640, f"Phone: {buyer_phone}")
            c.drawString(100, 620, f"Payment: {payment_method}")
            c.save()
            pdf_buffer.seek(0)
            st.download_button("⬇️ Download Ticket PDF", data=pdf_buffer, file_name=f"ticket_{ticket_id}.pdf", mime="application/pdf")
        else:
            st.error("⚠️ Please fill all fields before proceeding.")

# ------------------------
# Verify Ticket
# ------------------------
with tabs[2]:
    st.header("🔍 Verify a Ticket")
    ticket_id_input = st.text_input("Enter Ticket ID")
    if st.button("Verify Ticket"):
        valid, data = st.session_state.blockchain.verify_ticket(ticket_id_input)
        if valid:
            st.success("✅ Ticket is VALID")
            st.write(data)
        else:
            st.error("❌ Invalid Ticket ID")

# ------------------------
# Ledger
# ------------------------
with tabs[3]:
    st.header("📜 Blockchain Ledger")
    for block in st.session_state.blockchain.chain:
        st.write(f"**Block {block.index}**")
        st.write(f"⏰ {time.ctime(block.timestamp)}")
        st.write(f"🔗 Hash: {block.hash[:15]}...")
        st.write(f"📦 Data: {block.data}")
        st.markdown("---")

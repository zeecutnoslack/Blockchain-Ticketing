import streamlit as st
import hashlib, datetime, random, json
from io import BytesIO

# Safe optional imports
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False


# ------------------ Blockchain ------------------
class Block:
    def __init__(self, index, timestamp, transaction, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) + str(self.timestamp) + json.dumps(self.transaction, sort_keys=True) + str(self.previous_hash)).encode("utf-8"))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, str(datetime.datetime.now()), {"genesis": True}, "0")

    def add_block(self, transaction: dict):
        prev = self.chain[-1]
        new_block = Block(prev.index + 1, str(datetime.datetime.now()), transaction, prev.hash)
        self.chain.append(new_block)
        return new_block

    def find_transactions(self, ticket_id=None, buyer_name=None):
        matches = []
        for block in self.chain:
            tx = block.transaction
            if ticket_id and tx.get("ticket_id") == ticket_id:
                matches.append((block, tx))
            if buyer_name and str(tx.get("buyer", "")).strip().lower() == str(buyer_name).strip().lower():
                matches.append((block, tx))
        return matches


# ------------------ Events ------------------
EVENTS = {
    "Future Beats 2025": {
        "artist": "DJ Nova",
        "date": "15 Nov 2025",
        "venue": "Skyline Arena, Mumbai",
        "price": 1500,
        "perks": ["Glow Sticks", "VIP Lounge (first 50)", "Blockchain-secured"],
        "total_tickets": 50,
    },
    "Rock Revolution": {
        "artist": "The StarLights",
        "date": "20 Dec 2025",
        "venue": "Echo Stadium, Delhi",
        "price": 1800,
        "perks": ["Free T-Shirt", "Backstage (limited)"],
        "total_tickets": 40,
    },
    "Classical Nights": {
        "artist": "Symphony X",
        "date": "10 Jan 2026",
        "venue": "Royal Opera House, Mumbai",
        "price": 1200,
        "perks": ["Program Booklet", "Front Row Upgrade"],
        "total_tickets": 30,
    },
}


# ------------------ PDF Generator ------------------
def generate_ticket_pdf_bytes(ticket: dict):
    if not PDF_AVAILABLE:
        return None

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(60, height - 80, f"{ticket['event']}")

    c.setFont("Helvetica", 12)
    c.drawString(60, height - 110, f"Artist: {ticket['artist']}")
    c.drawString(60, height - 130, f"Date: {ticket['date']}")
    c.drawString(60, height - 150, f"Venue: {ticket['venue']}")
    c.drawString(60, height - 170, f"Buyer: {ticket['buyer']}")
    c.drawString(60, height - 190, f"Ticket ID: {ticket['ticket_id']}")
    c.drawString(60, height - 210, f"Seat: {ticket.get('seat','N/A')}")
    c.drawString(60, height - 230, f"Price: ₹{ticket['price']}")

    if QR_AVAILABLE:
        qr_data = f"TICKET|{ticket['ticket_id']}|{ticket['buyer']}|{ticket['event']}|{ticket.get('seat','')}"
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_buf = BytesIO()
        img.save(qr_buf, format="PNG")
        qr_buf.seek(0)
        c.drawInlineImage(qr_buf, width - 200, height - 300, 140, 140)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ------------------ Streamlit App ------------------
st.set_page_config(page_title="Blockchain Ticketing", layout="wide")
st.title("🎟 Blockchain Ticketing with Mock Payment")

if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()

if "pending_purchase" not in st.session_state:
    st.session_state["pending_purchase"] = None


tab_home, tab_buy, tab_verify, tab_ledger = st.tabs(["Home", "Buy Ticket", "Verify Ticket", "Ledger"])


# ---- Home ----
with tab_home:
    st.header("Available Events")
    for name, e in EVENTS.items():
        sold = sum(1 for b in st.session_state["blockchain"].chain if b.transaction.get("event") == name)
        remaining = e["total_tickets"] - sold
        st.subheader(f"{name} — {e['artist']}")
        st.write(f"📅 {e['date']}  •  📍 {e['venue']}")
        st.write(f"💰 Price: ₹{e['price']}")
        st.write(f"🎁 Perks: {', '.join(e['perks'])}")
        st.progress(remaining / e["total_tickets"])
        st.caption(f"{remaining} tickets remaining")


# ---- Buy Ticket ----
with tab_buy:
    st.header("Buy Ticket")

    if not st.session_state["pending_purchase"]:
        event_choice = st.selectbox("Choose Event", list(EVENTS.keys()))
        buyer_name = st.text_input("Your full name")
        if st.button("Proceed to Payment"):
            if not buyer_name.strip():
                st.error("Enter your name first.")
            else:
                st.session_state["pending_purchase"] = {
                    "event": event_choice,
                    "buyer": buyer_name.strip(),
                }
                st.experimental_rerun()

    else:
        purchase = st.session_state["pending_purchase"]
        event = EVENTS[purchase["event"]]
        st.subheader(f"Checkout — {purchase['event']}")
        st.write(f"Buyer: **{purchase['buyer']}**")
        st.write(f"Price: ₹{event['price']}")
        card = st.text_input("Enter mock card number (e.g., 1234 5678 9012 3456)")
        if st.button("Pay Now"):
            if not card.strip():
                st.error("Enter a fake card number.")
            else:
                # Payment simulated -> Issue ticket
                ticket_id = f"TKT{random.randint(10000,99999)}"
                seat = f"{random.choice('ABCDEF')}{random.randint(1,30)}"
                tx = {
                    "ticket_id": ticket_id,
                    "buyer": purchase["buyer"],
                    "event": purchase["event"],
                    "artist": event["artist"],
                    "date": event["date"],
                    "venue": event["venue"],
                    "price": event["price"],
                    "seat": seat
                }
                block = st.session_state["blockchain"].add_block(tx)

                st.success("✅ Payment Successful! Ticket issued.")
                st.write(f"**Ticket ID:** `{ticket_id}`")
                st.write(f"Seat: {seat} • Event: {event['artist']} on {event['date']} at {event['venue']}")

                if QR_AVAILABLE:
                    qr_data = f"TICKET|{ticket_id}|{purchase['buyer']}|{purchase['event']}|{seat}"
                    qr = qrcode.QRCode(version=1, box_size=6, border=2)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    st.image(img, caption="Scan QR at the venue", width=200)

                pdf_buf = generate_ticket_pdf_bytes({**tx, "block_index": block.index, "block_hash": block.hash})
                if pdf_buf:
                    st.download_button("Download Ticket (PDF)", data=pdf_buf, file_name=f"{ticket_id}.pdf", mime="application/pdf")

                st.session_state["pending_purchase"] = None


# ---- Verify ----
with tab_verify:
    st.header("Verify Ticket")
    method = st.radio("Verify by", ["Ticket ID", "Buyer Name"])
    if method == "Ticket ID":
        tid = st.text_input("Enter Ticket ID")
        if st.button("Check ID"):
            matches = st.session_state["blockchain"].find_transactions(ticket_id=tid.strip())
            if matches:
                st.success("Ticket VALID ✅")
                st.json(matches[0][1])
            else:
                st.error("Ticket not found.")
    else:
        name = st.text_input("Enter Buyer Name")
        if st.button("Check Buyer"):
            matches = st.session_state["blockchain"].find_transactions(buyer_name=name.strip())
            if matches:
                st.success(f"Found {len(matches)} tickets.")
                for _, tx in matches:
                    st.json(tx)
            else:
                st.error("No tickets found.")


# ---- Ledger ----
with tab_ledger:
    st.header("Blockchain Ledger")
    for block in reversed(st.session_state["blockchain"].chain):
        st.write(f"Block {block.index} | {block.timestamp}")
        st.json(block.transaction)
        st.caption(f"Hash: {block.hash[:12]}... | Prev: {block.previous_hash[:12]}...")

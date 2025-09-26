import streamlit as st
import hashlib
import time
import random
import string
import json
import datetime
import io

# -------- Optional Libraries (safe imports) --------
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


# -------- Safe rerun --------
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except Exception:
            st.session_state["_rerun_requested"] = True
            st.stop()


# -------- Blockchain --------
class Block:
    def __init__(self, index, prev_hash, timestamp, data):
        self.index = index
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calc_hash()

    def calc_hash(self):
        s = json.dumps(self.data, sort_keys=True, ensure_ascii=False)
        payload = f"{self.index}{self.prev_hash}{self.timestamp}{s}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Blockchain:
    def __init__(self):
        if "chain_data" not in st.session_state:
            genesis = Block(0, "0", time.time(), {"genesis": True})
            st.session_state["chain_data"] = [genesis]

    def add_block(self, data):
        chain = st.session_state["chain_data"]
        last = chain[-1]
        new_block = Block(len(chain), last.hash, time.time(), data)
        chain.append(new_block)
        st.session_state["chain_data"] = chain
        return new_block

    def find_ticket(self, ticket_id=None, buyer_email=None, buyer_name=None):
        results = []
        for blk in st.session_state["chain_data"][1:]:
            d = blk.data
            if ticket_id and d.get("ticket_id") == ticket_id:
                results.append((blk, d))
            elif buyer_email and d.get("buyer_email","").lower() == buyer_email.lower():
                results.append((blk, d))
            elif buyer_name and d.get("buyer_name","").lower() == buyer_name.lower():
                results.append((blk, d))
        return results


# -------- Helpers --------
def gen_ticket_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_qr_bytes(payload):
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def generate_pdf(tickets, event):
    if not PDF_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    for t in tickets:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 80, event["name"])
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 110, f"Artist: {event['artist']}")
        c.drawString(50, height - 130, f"Date: {event['date']}")
        c.drawString(50, height - 150, f"Venue: {event['venue']}")
        c.drawString(50, height - 170, f"Buyer: {t['buyer_name']}")
        c.drawString(50, height - 190, f"Ticket ID: {t['ticket_id']}")
        c.drawString(50, height - 210, f"Seat: {t['seat']}  Price: ₹{t['price']}")
        if QR_AVAILABLE:
            qr = qrcode.make(f"TICKET|{t['ticket_id']}|{t['buyer_name']}|{event['name']}|{t['seat']}")
            qr_buf = io.BytesIO()
            qr.save(qr_buf, format="PNG")
            qr_buf.seek(0)
            c.drawInlineImage(qr_buf, width - 200, height - 250, 150, 150)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


# -------- Events --------
EVENTS = [
    {"name": "Rocking Beats Night", "artist": "Imagine Dragons", "date": "2025-10-15",
     "venue": "Wembley Stadium, London", "price": 1200, "perks": "Free Drinks + Backstage Access"},
    {"name": "Bollywood Magic", "artist": "Arijit Singh", "date": "2025-11-10",
     "venue": "NSCI Dome, Mumbai", "price": 800, "perks": "Meet & Greet + Free Merchandise"},
    {"name": "Hip-Hop Fever", "artist": "Travis Scott", "date": "2025-12-05",
     "venue": "Madison Square Garden, NY", "price": 1500, "perks": "VIP Lounge + Signed Poster"},
]


# -------- Session Init --------
st.set_page_config(page_title="Boss Ticketing", layout="wide")
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "seats" not in st.session_state:
    st.session_state["seats"] = {e["name"]: [f"{r}{c}" for r in "ABCDEF" for c in range(1, 11)] for e in EVENTS}


# -------- Navigation --------
menu = st.radio("Navigate", ["Home", "Buy Ticket", "Verify Ticket", "Ledger"], horizontal=True)
st.markdown("<hr/>", unsafe_allow_html=True)


# -------- HOME --------
if menu == "Home":
    st.title("🎶 Featured Concerts")
    cols = st.columns(len(EVENTS))
    for i, ev in enumerate(EVENTS):
        with cols[i]:
            st.subheader(ev["name"])
            st.write(f"**Artist:** {ev['artist']}")
            st.write(f"📅 {ev['date']}  •  📍 {ev['venue']}")
            st.write(f"💰 Price: ₹{ev['price']}")
            st.write(f"✨ Perks: {ev['perks']}")
            remaining = len(st.session_state["seats"][ev["name"]])
            st.metric("Tickets left", remaining)
            if st.button("Book Now", key=f"book{i}"):
                st.session_state["selected_event"] = ev
                safe_rerun()


# -------- BUY TICKET --------
elif menu == "Buy Ticket" or st.session_state.get("selected_event"):
    ev = st.session_state.get("selected_event", EVENTS[0])
    st.title("🛒 Buy Ticket")
    st.subheader(f"{ev['name']} — {ev['artist']}")
    st.write(f"📅 {ev['date']} • 📍 {ev['venue']}")
    st.write(f"✨ {ev['perks']}")
    remaining = len(st.session_state["seats"][ev["name"]])
    st.info(f"Tickets remaining: {remaining}")

    st.markdown("### Buyer Info")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    qty = st.number_input("Number of Tickets", min_value=1, max_value=min(5, remaining), value=1)

    st.markdown("### Mock Payment")
    with st.form("pay_form"):
        card_name = st.text_input("Cardholder Name")
        card_num = st.text_input("Card Number (mock)")
        exp = st.text_input("Expiry (MM/YY)")
        cvv = st.text_input("CVV", type="password")
        pay = st.form_submit_button("Pay Now")

    if pay:
        if not name.strip() or not email.strip():
            st.error("Enter name and email.")
        else:
            seats = []
            for _ in range(qty):
                if st.session_state["seats"][ev["name"]]:
                    seats.append(st.session_state["seats"][ev["name"]].pop(0))

            tickets = []
            for s in seats:
                tid = gen_ticket_id()
                tx = {"ticket_id": tid, "buyer_name": name, "buyer_email": email,
                      "event": ev["name"], "artist": ev["artist"], "date": ev["date"],
                      "venue": ev["venue"], "seat": s, "price": ev["price"],
                      "purchased_at": datetime.datetime.now().isoformat(sep=" ", timespec="seconds")}
                st.session_state["blockchain"].add_block(tx)
                tickets.append(tx)

            st.success("🎉 Payment Successful!")
            for t in tickets:
                st.markdown("---")
                st.subheader(f"Ticket {t['ticket_id']}")
                st.write(f"{t['event']} — {t['artist']}")
                st.write(f"Seat: {t['seat']} | Price: ₹{t['price']}")
                qr = generate_qr_bytes(f"TICKET|{t['ticket_id']}|{t['buyer_name']}")
                if qr: st.image(qr, width=180)

            pdf = generate_pdf(tickets, ev)
            if pdf:
                st.download_button("Download Tickets (PDF)", pdf, file_name="tickets.pdf")


# -------- VERIFY --------
elif menu == "Verify Ticket":
    st.title("✅ Verify Ticket")
    method = st.radio("Search By", ["Ticket ID", "Buyer Email", "Buyer Name"], horizontal=True)
    query = st.text_input("Enter value")
    if st.button("Verify"):
        results = []
        if method == "Ticket ID":
            results = st.session_state["blockchain"].find_ticket(ticket_id=query)
        elif method == "Buyer Email":
            results = st.session_state["blockchain"].find_ticket(buyer_email=query)
        else:
            results = st.session_state["blockchain"].find_ticket(buyer_name=query)

        if results:
            for blk, t in results:
                st.success(f"Valid Ticket {t['ticket_id']} for {t['event']}")
                st.write(f"Seat {t['seat']} | Buyer {t['buyer_name']} | Block {blk.index}")
        else:
            st.error("No match found.")


# -------- LEDGER --------
elif menu == "Ledger":
    st.title("📒 Blockchain Ledger")
    for blk in reversed(st.session_state["chain_data"]):
        if blk.index == 0: continue
        with st.expander(f"Block {blk.index} — Ticket {blk.data['ticket_id']}"):
            st.write(f"Buyer: {blk.data['buyer_name']} ({blk.data['buyer_email']})")
            st.write(f"Event: {blk.data['event']} • Seat: {blk.data['seat']}")
            st.caption(f"Hash: {blk.hash[:12]}... | Prev: {blk.prev_hash[:12]}...")

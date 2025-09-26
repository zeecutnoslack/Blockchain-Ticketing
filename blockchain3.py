# app.py
import streamlit as st
import hashlib
import time
import random
import json
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime

# ---------------------------
# Blockchain core
# ---------------------------
class Block:
    def __init__(self, index, previous_hash, transaction, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        self.transaction = transaction  # transaction is a dict
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        tx_str = json.dumps(self.transaction, sort_keys=True, ensure_ascii=False)
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{tx_str}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        if not hasattr(self, "chain"):
            self.chain = [self._create_genesis()]

    def _create_genesis(self):
        return Block(0, "0", {"ticket_id": "GENESIS", "buyer": "SYSTEM", "note": "genesis"})

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, transaction: dict):
        index = len(self.chain)
        previous_hash = self.get_last_block().hash
        new_block = Block(index, previous_hash, transaction)
        self.chain.append(new_block)
        return new_block

    def find_transactions(self, ticket_id: str = None, buyer_name: str = None):
        """
        Return list of matches. Each match is dict:
        {
            'index': block.index,
            'timestamp': block.timestamp,
            'transaction': block.transaction,
            'hash': block.hash,
            'previous_hash': block.previous_hash
        }
        """
        matches = []
        for block in self.chain:
            tx = block.transaction
            if ticket_id and tx.get("ticket_id") == ticket_id:
                matches.append({
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "transaction": tx,
                    "hash": block.hash,
                    "previous_hash": block.previous_hash
                })
            elif buyer_name and str(tx.get("buyer", "")).strip().lower() == buyer_name.strip().lower():
                matches.append({
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "transaction": tx,
                    "hash": block.hash,
                    "previous_hash": block.previous_hash
                })
        return matches


# ---------------------------
# Sample events / multi-artist, multi-date
# ---------------------------
EVENTS = [
    {
        "artist": "DJ NOVA",
        "show_name": "Future Beats Live",
        "tour": [
            {"city": "Mumbai", "date": "2025-11-15", "capacity": 200},
            {"city": "Delhi", "date": "2025-11-18", "capacity": 150},
            {"city": "Bengaluru", "date": "2025-11-20", "capacity": 180},
            {"city": "Hyderabad", "date": "2025-11-23", "capacity": 160},
            {"city": "Kolkata", "date": "2025-11-25", "capacity": 140},
            {"city": "Pune", "date": "2025-11-28", "capacity": 120},
        ],
        "price": 1500,
        "perks": ["Glow Sticks", "VIP Lounge (first buyers)", "Blockchain Ticket"]
    },
    {
        "artist": "THE STARLIGHTS",
        "show_name": "Rock Revolution",
        "tour": [
            {"city": "Goa", "date": "2025-12-01", "capacity": 200},
            {"city": "Pune", "date": "2025-12-03", "capacity": 180},
            {"city": "Chennai", "date": "2025-12-06", "capacity": 160},
            {"city": "Jaipur", "date": "2025-12-09", "capacity": 120},
            {"city": "Surat", "date": "2025-12-12", "capacity": 100},
        ],
        "price": 1800,
        "perks": ["Backstage Pass (limited)", "Free Merch", "Meet & Greet"]
    },
    {
        "artist": "SYMPHONY X",
        "show_name": "Classical Nights",
        "tour": [
            {"city": "Delhi", "date": "2025-12-20", "capacity": 120},
            {"city": "Mumbai", "date": "2025-12-22", "capacity": 120},
            {"city": "Bengaluru", "date": "2025-12-24", "capacity": 100},
        ],
        "price": 2500,
        "perks": ["Complimentary Drink", "Front Row Upgrade", "Blockchain Ticket"]
    },
    {
        "artist": "ELECTRO VIBE",
        "show_name": "Electro Nights",
        "tour": [
            {"city": "Dubai", "date": "2025-12-28", "capacity": 200},
            {"city": "Abu Dhabi", "date": "2025-12-30", "capacity": 180},
            {"city": "Doha", "date": "2026-01-02", "capacity": 160},
        ],
        "price": 2200,
        "perks": ["Light Stick", "DJ Meet", "Blockchain Ticket"]
    },
    {
        "artist": "ROCKNATION",
        "show_name": "Nation Tour",
        "tour": [
            {"city": "London", "date": "2026-01-10", "capacity": 300},
            {"city": "Berlin", "date": "2026-01-13", "capacity": 250},
            {"city": "Amsterdam", "date": "2026-01-16", "capacity": 220},
            {"city": "Paris", "date": "2026-01-19", "capacity": 240},
        ],
        "price": 3000,
        "perks": ["VIP Access", "Signed Poster", "Blockchain Ticket"]
    },
]


# ---------------------------
# Helpers: PDF + QR
# ---------------------------
def generate_ticket_pdf(ticket: dict):
    """
    ticket is a dict containing:
    ticket_id, buyer, artist, show_name, city, date, price, block_index, block_hash
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60, height - 80, ticket["show_name"])
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 100, f"Artist: {ticket['artist']}")
    c.drawString(60, height - 120, f"Date: {ticket['date']}    Venue: {ticket['city']}")
    c.drawString(60, height - 140, f"Buyer: {ticket['buyer']}")
    c.drawString(60, height - 160, f"Ticket ID: {ticket['ticket_id']}")
    c.drawString(60, height - 180, f"Price: ₹{ticket['price']}")
    c.drawString(60, height - 200, f"Block: {ticket.get('block_index', '-')}")
    c.drawString(60, height - 220, "This ticket is secured by blockchain technology. Verify at the event.")

    # Generate QR (ticket_id encoded)
    qr_img = qrcode.make(ticket["ticket_id"])
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    # place QR on right
    c.drawInlineImage(qr_buffer, width - 200, height - 280, 140, 140)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ---------------------------
# Initialization (session state)
# ---------------------------
st.set_page_config(page_title="Boss Ticketing Platform", layout="centered")
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "inventory" not in st.session_state:
    # inventory[ event_index ] = [remaining for each tour index]
    inv = {}
    for i, e in enumerate(EVENTS):
        inv[i] = [show["capacity"] for show in e["tour"]]
    st.session_state["inventory"] = inv
if "last_ticket" not in st.session_state:
    st.session_state["last_ticket"] = None

# ---------------------------
# UI - Header / Event showcase
# ---------------------------
st.title("Boss-Level Multi-Event Ticketing Platform")
st.write("Pick an artist, choose a date & city, buy a ticket and get a blockchain-backed PDF ticket.")

menu = st.radio("Select action:", ["Events", "Buy Ticket", "Verify Ticket", "View Ledger", "My Last Ticket"])

# ---------------------------
# Events page: show available shows cleanly
# ---------------------------
if menu == "Events":
    st.header("Upcoming Shows")
    for idx, ev in enumerate(EVENTS):
        st.subheader(f"{ev['show_name']} — {ev['artist']}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Price: ₹{ev['price']}")
            st.write("Perks: " + ", ".join(ev["perks"]))
            st.write("Upcoming stops:")
            for tidx, show in enumerate(ev["tour"]):
                remaining = st.session_state["inventory"][idx][tidx]
                st.write(f"- {show['city']} on {show['date']}  |  Remaining: {remaining}")
        with col2:
            # small summary card
            st.markdown(f"**Total stops:** {len(ev['tour'])}")
            st.markdown(f"**Capacity per stop:** varies")
            st.markdown(f"**Event index:** {idx}")

# ---------------------------
# Buy Ticket page
# ---------------------------
elif menu == "Buy Ticket":
    st.header("Buy Ticket")
    artist_names = [f"{ev['artist']} — {ev['show_name']}" for ev in EVENTS]
    selection = st.selectbox("Choose an event (artist & show):", artist_names)
    event_index = artist_names.index(selection)
    event = EVENTS[event_index]

    # choose date/location
    tour_options = [f"{show['city']} — {show['date']}" for show in event["tour"]]
    chosen = st.selectbox("Choose date & city:", tour_options)
    tour_index = tour_options.index(chosen)
    remaining = st.session_state["inventory"][event_index][tour_index]

    st.write(f"Tickets remaining for this show: {remaining}")
    st.write(f"Price: ₹{event['price']}")
    st.write("Perks: " + ", ".join(event["perks"]))

    buyer = st.text_input("Buyer name (as it will appear on ticket):")

    # seat class option (fun)
    seat_class = st.selectbox("Seat type:", ["General", "Silver (front)", "Gold (VIP)"])
    if seat_class == "Gold (VIP)":
        extra = 500
    elif seat_class == "Silver (front)":
        extra = 200
    else:
        extra = 0
    total_price = event["price"] + extra
    st.write(f"Total price: ₹{total_price}")

    if st.button("Purchase"):
        if not buyer.strip():
            st.error("Please enter your name to purchase.")
        elif remaining <= 0:
            st.error("Sold out for this show.")
        else:
            # generate a unique id
            # try a few times if colliding (very unlikely)
            attempt = 0
            while True:
                candidate = f"{event['artist'].split()[0][:3].upper()}-{random.randint(10000,99999)}"
                if not st.session_state["blockchain"].find_transactions(ticket_id=candidate):
                    ticket_id = candidate
                    break
                attempt += 1
                if attempt > 10:
                    ticket_id = f"{event['artist'][:3].upper()}-{int(time.time())}"
                    break

            transaction = {
                "ticket_id": ticket_id,
                "buyer": buyer.strip(),
                "artist": event["artist"],
                "show_name": event["show_name"],
                "city": event["tour"][tour_index]["city"],
                "date": event["tour"][tour_index]["date"],
                "seat_class": seat_class,
                "price": total_price,
                "purchased_at": datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            }

            block = st.session_state["blockchain"].add_block(transaction)
            # decrement inventory
            st.session_state["inventory"][event_index][tour_index] -= 1
            # store last ticket for convenience
            st.session_state["last_ticket"] = {
                **transaction,
                "block_index": block.index,
                "block_hash": block.hash
            }

            st.success(f"Purchase complete. Ticket ID: {ticket_id}")
            st.info("Download your PDF ticket below for entry and scanning at the venue.")

            # generate and offer PDF
            pdf_bytes = generate_ticket_pdf(st.session_state["last_ticket"])
            st.download_button(
                "Download Ticket (PDF)",
                data=pdf_bytes,
                file_name=f"{ticket_id}.pdf",
                mime="application/pdf"
            )

# ---------------------------
# Verify Ticket page (multiple options)
# ---------------------------
elif menu == "Verify Ticket":
    st.header("Verify Ticket")
    verify_method = st.radio("Verification method:", ["By Ticket ID", "By Buyer Name"])

    if verify_method == "By Ticket ID":
        q = st.text_input("Enter Ticket ID:")
        if st.button("Verify Ticket ID"):
            if not q.strip():
                st.error("Type a ticket ID to verify.")
            else:
                matches = st.session_state["blockchain"].find_transactions(ticket_id=q.strip())
                if matches:
                    m = matches[0]
                    tx = m["transaction"]
                    st.success("Ticket is VALID")
                    st.write(f"Ticket ID: {tx['ticket_id']}")
                    st.write(f"Buyer: {tx['buyer']}")
                    st.write(f"Artist: {tx['artist']} — {tx.get('show_name', '')}")
                    st.write(f"Date / City: {tx.get('date')} / {tx.get('city')}")
                    st.write(f"Seat: {tx.get('seat_class')} | Price: ₹{tx.get('price')}")
                    st.write(f"Block index: {m['index']} | Hash preview: {m['hash'][:10]}...")
                else:
                    st.error("No record found. Ticket is INVALID or not registered.")

    else:  # By Buyer Name
        name_q = st.text_input("Enter Buyer Name:")
        if st.button("Find by Buyer"):
            if not name_q.strip():
                st.error("Type a buyer name to search.")
            else:
                matches = st.session_state["blockchain"].find_transactions(buyer_name=name_q.strip())
                if matches:
                    st.success(f"Found {len(matches)} ticket(s) for {name_q.strip()}:")
                    for m in matches:
                        tx = m["transaction"]
                        st.write(f"- {tx['artist']} ({tx.get('show_name','')}) on {tx.get('date')} in {tx.get('city')} — Ticket ID: {tx['ticket_id']}")
                else:
                    st.error("No tickets found for this buyer.")

# ---------------------------
# Ledger view
# ---------------------------
elif menu == "View Ledger":
    st.header("Blockchain Ledger (newest first)")
    for block in reversed(st.session_state["blockchain"].chain):
        idx = block.index
        if idx == 0:
            # show only as tiny header
            st.markdown("**Genesis block**")
            continue
        tx = block.transaction
        st.markdown(f"### Block {idx}")
        st.write(f"Timestamp: {block.timestamp}")
        st.write(f"Ticket ID: {tx.get('ticket_id')}")
        st.write(f"Buyer: {tx.get('buyer')}")
        st.write(f"Artist / Show: {tx.get('artist')} — {tx.get('show_name')}")
        st.write(f"Date / City: {tx.get('date')} / {tx.get('city')}")
        st.write(f"Seat: {tx.get('seat_class')} | Price: ₹{tx.get('price')}")
        st.write(f"Hash: {block.hash[:10]}...   Prev: {block.previous_hash[:10]}...")
        st.write("---")

# ---------------------------
# My last ticket (convenience)
# ---------------------------
elif menu == "My Last Ticket":
    st.header("Your Most Recent Ticket (if any)")
    t = st.session_state.get("last_ticket")
    if not t:
        st.info("No recent ticket found. Buy one to see it here.")
    else:
        st.write(f"Ticket ID: {t['ticket_id']}")
        st.write(f"Buyer: {t['buyer']}")
        st.write(f"Artist: {t['artist']}")
        st.write(f"Date / City: {t['date']} / {t['city']}")
        st.write(f"Seat: {t['seat_class']} | Price: ₹{t['price']}")
        st.write(f"Block index: {t['block_index']}   Hash preview: {t['block_hash'][:10]}...")
        pdf_bytes = generate_ticket_pdf(t)
        st.download_button("Download this ticket (PDF)", data=pdf_bytes, file_name=f"{t['ticket_id']}.pdf", mime="application/pdf")

# Footer
st.caption("Built with Streamlit — Blockchain simulation for education & demo purposes.")

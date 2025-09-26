# app.py
import streamlit as st
import time
import hashlib
import random
import string
import json
from io import BytesIO

# Optional QR imports (safe)
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

# --------------------------
# Utility / Safe functions
# --------------------------
def safe_rerun():
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            # best-effort: mark and stop
            st.session_state["_rerun_requested"] = True
            st.stop()


def gen_ticket_id(length: int = 10):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def make_qr_bytes(text: str):
    """Return PNG bytes for QR or None if qrcode missing."""
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

# --------------------------
# Blockchain implementation
# --------------------------
class Block:
    def __init__(self, index: int, timestamp: float, data: dict, prev_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = sha256_of({
            "index": index,
            "timestamp": timestamp,
            "data": data,
            "prev_hash": prev_hash
        })

class Blockchain:
    def __init__(self):
        # ensure chain exists in session to persist across reruns
        if "chain" not in st.session_state:
            genesis = Block(0, time.time(), {"genesis": True}, "0")
            st.session_state["chain"] = [genesis]

    def chain(self):
        return st.session_state["chain"]

    def add_block(self, data: dict) -> Block:
        chain = st.session_state["chain"]
        prev = chain[-1]
        new_block = Block(len(chain), time.time(), data, prev.hash)
        chain.append(new_block)
        st.session_state["chain"] = chain
        return new_block

    def find_by_ticket(self, ticket_id: str):
        results = []
        for blk in st.session_state["chain"][1:]:
            d = blk.data
            if isinstance(d, dict) and d.get("ticket_id") == ticket_id:
                results.append((blk, d))
        return results

    def find_by_buyer_email(self, email: str):
        results = []
        for blk in st.session_state["chain"][1:]:
            d = blk.data
            if isinstance(d, dict) and str(d.get("buyer_email","")).strip().lower() == email.strip().lower():
                results.append((blk, d))
        return results

# --------------------------
# Initial events data (persist in session)
# --------------------------
INITIAL_EVENTS = [
    {
        "id": "ev1",
        "artist": "Imagine Dragons",
        "title": "Night Visions Tour",
        "banner": "https://upload.wikimedia.org/wikipedia/en/3/3f/Imagine_Dragons_Night_Visions.jpg",
        "venue": "Mumbai Stadium",
        "location": "Mumbai, India",
        "date": "2025-10-12",
        "time": "19:30",
        "price_inr": 2500,
        "total_seats": 30,
        # seats: rows A-D, 1-8 => 32 seats; we'll use exactly total_seats
        "available_seats": [],   # populated below
        "perks": ["Free Drinks", "Backstage Access"]
    },
    {
        "id": "ev2",
        "artist": "Arijit Singh",
        "title": "Romantic Melodies",
        "banner": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Arijit_Singh.jpg",
        "venue": "Delhi Concert Arena",
        "location": "Delhi, India",
        "date": "2025-11-05",
        "time": "20:00",
        "price_inr": 1800,
        "total_seats": 25,
        "available_seats": [],
        "perks": ["Meet & Greet", "VIP Lounge"]
    },
    {
        "id": "ev3",
        "artist": "Taylor Swift",
        "title": "Eras Tour",
        "banner": "https://upload.wikimedia.org/wikipedia/en/f/f2/Taylor_Swift_-_1989.png",
        "venue": "Bengaluru Open Grounds",
        "location": "Bengaluru, India",
        "date": "2025-12-20",
        "time": "18:30",
        "price_inr": 4500,
        "total_seats": 40,
        "available_seats": [],
        "perks": ["Signed Poster", "Premium Goodies"]
    },
    {
        "id": "ev4",
        "artist": "Coldplay",
        "title": "Music of the Spheres",
        "banner": "https://upload.wikimedia.org/wikipedia/en/0/0a/Coldplay_-_Music_of_the_Spheres.png",
        "venue": "Hyderabad Rock Arena",
        "location": "Hyderabad, India",
        "date": "2026-01-15",
        "time": "19:00",
        "price_inr": 3200,
        "total_seats": 35,
        "available_seats": [],
        "perks": ["Glow Bands", "Exclusive Merch"]
    },
]

# create seat labels for each event and persist
def ensure_events_in_session():
    if "events" not in st.session_state:
        events = []
        for ev in INITIAL_EVENTS:
            seats = []
            # build seat labels row-wise A..F and numbers 1..n until total seats filled
            rows = [chr(ord('A') + i) for i in range(6)]  # A-F
            seat_num = 1
            for r in rows:
                for _ in range(10):
                    seats.append(f"{r}{seat_num}")
                    seat_num += 1
                    if len(seats) >= ev["total_seats"]:
                        break
                if len(seats) >= ev["total_seats"]:
                    break
            copy_ev = ev.copy()
            copy_ev["available_seats"] = seats.copy()
            events.append(copy_ev)
        st.session_state["events"] = events

ensure_events_in_session()

# Blockchain in session
if "blockchain" not in st.session_state or not hasattr(st.session_state["blockchain"], "add_block"):
    st.session_state["blockchain"] = Blockchain()

# selection and last purchase state
if "selected_event_id" not in st.session_state:
    st.session_state["selected_event_id"] = None
if "last_purchase" not in st.session_state:
    st.session_state["last_purchase"] = None

# --------------------------
# UI: top navigation (front)
# --------------------------
st.set_page_config(page_title="Boss Ticketing — Blockchain Tickets", layout="wide")
st.title("🎟️ Boss — Blockchain Ticketing (Interactive Demo)")

menu_list = ["Home", "Buy Ticket", "Verify Ticket", "Ledger"]
# determine default index using session
default_index = 0
if "menu" in st.session_state:
    try:
        default_index = menu_list.index(st.session_state.get("menu", "Home"))
    except Exception:
        default_index = 0

menu = st.radio("Navigate", menu_list, index=default_index, horizontal=True)
st.session_state["menu"] = menu
st.markdown("---")

# helper to find event by id
def get_event_by_id(eid):
    for e in st.session_state["events"]:
        if e["id"] == eid:
            return e
    return None

# --------------------------
# HOME (horizontal, rich cards)
# --------------------------
if menu == "Home":
    st.header("🔥 Featured Concerts")
    evs = st.session_state["events"]
    # show 3 cards per row
    per_row = 3
    rows = [evs[i:i+per_row] for i in range(0, len(evs), per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for col, ev in zip(cols, row):
            with col:
                st.image(ev["banner"], use_container_width=True)
                st.markdown(f"### {ev['artist']} — {ev['title']}")
                st.write(f"📍 {ev['venue']} — {ev['location']}")
                st.write(f"📅 {ev['date']}  •  🕒 {ev['time']}")
                st.write(f"💰 Price: ₹{ev['price_inr']}  •  🎟 Seats left: **{len(ev['available_seats'])}**")
                st.write("**Perks:** " + ", ".join(ev.get("perks", [])))
                # small stats
                st.write(f"🔒 Blockchain-secured ticketing • Unique Ticket IDs")
                if st.button("Book Now", key=f"book_{ev['id']}"):
                    st.session_state["selected_event_id"] = ev["id"]
                    st.session_state["menu"] = "Buy Ticket"
                    safe_rerun()

# --------------------------
# BUY TICKET (interactive seats + mock payment)
# --------------------------
elif menu == "Buy Ticket":
    if not st.session_state.get("selected_event_id"):
        st.info("Select an event from Home (click Book Now) to prefill booking info, or choose below.")
        # allow choosing if not selected
        event_options = {e["id"]: f"{e['artist']} — {e['title']} ({e['date']}, {e['location']})" for e in st.session_state["events"]}
        chosen_id = st.selectbox("Choose Event", list(event_options.keys()), format_func=lambda k: event_options[k])
        st.session_state["selected_event_id"] = chosen_id
        safe_rerun()
    else:
        ev = get_event_by_id(st.session_state["selected_event_id"])
        if not ev:
            st.error("Selected event not found. Go to Home and pick an event.")
        else:
            st.header(f"{ev['artist']} — {ev['title']}")
            st.image(ev["banner"], use_container_width=True)
            st.write(f"📍 {ev['venue']} — {ev['location']}")
            st.write(f"📅 {ev['date']}  •  🕒 {ev['time']}")
            st.write(f"💰 Price per ticket: ₹{ev['price_inr']}")
            st.write(f"🎟 Seats remaining: **{len(ev['available_seats'])}**")
            st.write("**Perks available:** " + ", ".join(ev.get("perks", [])))
            st.markdown("---")

            # Buyer inputs
            buyer_name = st.text_input("Full name", key="buyer_name_input")
            buyer_email = st.text_input("Email (for verification & receipt)", key="buyer_email_input")

            # number of tickets
            max_allowed = min(6, len(ev["available_seats"]))
            qty = st.number_input("Number of tickets", min_value=1, max_value=max_allowed, value=1)

            # seat type (affects price)
            seat_type = st.selectbox("Seat type (affects price)", ["Regular", "Premium (+₹500)", "VIP (+₹1500)"])
            add_cost = 0
            if "Premium" in seat_type:
                add_cost = 500
            if "VIP" in seat_type:
                add_cost = 1500

            # seat selection (show available seats)
            st.markdown("#### Pick exact seats")
            st.write("Select the seats you want (click up to number of tickets).")
            selected_seats = st.multiselect("Available seats", ev["available_seats"], default=None)

            # perks
            chosen_perks = st.multiselect("Choose perks (optional)", ev.get("perks", []))

            # price calculation preview
            unit_price = ev["price_inr"] + add_cost
            total_price = unit_price * qty + (len(chosen_perks) * 200 * qty)
            st.info(f"Unit price: ₹{unit_price}  •  Perks cost: ₹{200 * len(chosen_perks)} per ticket  •  **Total = ₹{total_price}**")

            # Validate seats selection length
            if selected_seats and len(selected_seats) > qty:
                st.warning(f"You selected {len(selected_seats)} seats but qty is {qty}. Please select exactly {qty} seats.")
            if selected_seats and len(selected_seats) < qty:
                st.info(f"Select {qty - len(selected_seats)} more seat(s).")

            # Payment form
            st.markdown("---")
            st.subheader("Mock Payment")
            with st.form("payment_form"):
                card_holder = st.text_input("Name on card")
                card_number = st.text_input("Card number (mock)", max_chars=19)
                expiry = st.text_input("Expiry (MM/YY)")
                cvv = st.text_input("CVV (mock)", max_chars=4, type="password")
                pay_btn = st.form_submit_button("Pay Now (Mock)")

            if pay_btn:
                # validations
                if not buyer_name.strip() or not buyer_email.strip():
                    st.error("Please enter your name and email.")
                elif len(selected_seats) != qty:
                    st.error(f"Please select exactly {qty} seat(s).")
                elif not card_holder.strip() or not card_number.strip() or not expiry.strip() or not cvv.strip():
                    st.error("Fill mock payment details.")
                else:
                    # simulate processing
                    with st.spinner("Processing payment securely..."):
                        time.sleep(1.2)

                    # create tickets — persist seats removal & create blockchain entries
                    created_tickets = []
                    for seat in selected_seats:
                        ticket_id = gen_ticket_id()
                        ticket_tx = {
                            "ticket_id": ticket_id,
                            "buyer_name": buyer_name.strip(),
                            "buyer_email": buyer_email.strip(),
                            "event_id": ev["id"],
                            "event_name": ev["title"],
                            "artist": ev["artist"],
                            "venue": ev["venue"],
                            "location": ev["location"],
                            "date": ev["date"],
                            "time": ev["time"],
                            "seat": seat,
                            "seat_type": seat_type,
                            "perks": chosen_perks,
                            "unit_price": unit_price,
                            "total_price": total_price,
                            "purchased_at": time.ctime()
                        }
                        # remove seat from availability
                        try:
                            ev["available_seats"].remove(seat)
                        except ValueError:
                            # seat already taken concurrently — skip
                            st.error(f"Seat {seat} is no longer available. Please try again.")
                            continue

                        # add to blockchain
                        st.session_state["blockchain"].add_block(ticket_tx)
                        created_tickets.append(ticket_tx)

                    # store last purchase for download/receipt
                    st.session_state["last_purchase"] = {
                        "buyer": buyer_name.strip(),
                        "email": buyer_email.strip(),
                        "tickets": created_tickets,
                        "event": ev
                    }

                    st.success(f"🎉 Payment complete — {len(created_tickets)} ticket(s) booked. Check your ticket(s) below.")

                    # show digital ticket cards
                    for t in created_tickets:
                        st.markdown("---")
                        c1, c2 = st.columns([3,1])
                        with c1:
                            st.markdown(f"### {t['event_name']} — {t['artist']}")
                            st.write(f"👤 **{t['buyer_name']}**  •  ✉️ {t['buyer_email']}")
                            st.write(f"📍 {t['venue']}, {t['location']}")
                            st.write(f"📅 {t['date']}  •  🕒 {t['time']}")
                            st.write(f"🪑 Seat: **{t['seat']}**  •  Type: {t['seat_type']}")
                            st.write(f"⭐ Perks: {', '.join(t['perks']) if t['perks'] else 'None'}")
                            st.write(f"💰 Paid: ₹{t['unit_price']}")
                            st.write(f"🆔 Ticket ID: `{t['ticket_id']}`")
                        with c2:
                            qr_b = make_qr_bytes(f"TICKET|{t['ticket_id']}|{t['buyer_name']}")
                            if qr_b:
                                st.image(qr_b, use_column_width=True)
                            else:
                                st.info("QR unavailable (install qrcode[pil] and Pillow).")

# --------------------------
# VERIFY TICKET
# --------------------------
elif menu == "Verify Ticket":
    st.header("🔎 Verify Ticket")
    method = st.radio("Verify by", ["Ticket ID", "Buyer Email"], horizontal=True)
    query = st.text_input("Enter value to verify")
    if st.button("Check"):
        results = []
        if method == "Ticket ID":
            if query.strip():
                results = st.session_state["blockchain"].find_by_ticket(query.strip())
        else:
            if query.strip():
                results = st.session_state["blockchain"].find_by_buyer_email(query.strip())

        if results:
            for blk, data in results:
                st.success(f"Valid — Ticket {data['ticket_id']} for {data['event_name']}")
                st.write(f"Buyer: {data['buyer_name']}  •  Email: {data['buyer_email']}")
                st.write(f"Event: {data['event_name']} ({data['artist']})")
                st.write(f"Seat: {data['seat']}  •  Type: {data['seat_type']}")
                st.write(f"Paid: ₹{data['unit_price']}")
                qr_b = make_qr_bytes(f"TICKET|{data['ticket_id']}|{data['buyer_name']}")
                if qr_b:
                    st.image(qr_b, width=180)
        else:
            st.error("No matching ticket found.")

# --------------------------
# LEDGER
# --------------------------
elif menu == "Ledger":
    st.header("📒 Blockchain Ledger")
    chain = st.session_state.get("chain", [])
    if not chain:
        st.info("Blockchain is empty.")
    else:
        # show newest first
        for blk in reversed(chain):
            if blk.index == 0:
                with st.expander("Genesis Block"):
                    st.write(blk.data)
                continue
            with st.expander(f"Block {blk.index} — {blk.data.get('ticket_id', blk.data.get('event_name',''))}"):
                st.write(f"Timestamp: {blk.timestamp}")
                st.write(f"Event: {blk.data.get('event_name')}")
                st.write(f"Buyer: {blk.data.get('buyer_name')}  •  Email: {blk.data.get('buyer_email')}")
                st.write(f"Seat: {blk.data.get('seat')}  •  Price: ₹{blk.data.get('unit_price')}")
                st.caption(f"Hash: {blk.hash[:12]}  •  Prev: {blk.prev_hash[:12]}")
                # small JSON preview
                st.json(blk.data)

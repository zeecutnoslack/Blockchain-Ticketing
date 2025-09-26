import streamlit as st
import hashlib
import datetime

# -----------------------------
# Blockchain Classes
# -----------------------------
class Block:
    def __init__(self, index, timestamp, transaction, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        block_string = f"{self.index}{self.timestamp}{self.transaction}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, str(datetime.datetime.now()), {"ticket_id": "GENESIS"}, "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, transaction):
        last_block = self.get_last_block()
        new_block = Block(len(self.chain), str(datetime.datetime.now()), transaction, last_block.hash)
        self.chain.append(new_block)
        return new_block

    def is_ticket_valid(self, ticket_id):
        return any(block.transaction["ticket_id"] == ticket_id for block in self.chain)

# -----------------------------
# Streamlit Setup
# -----------------------------
st.set_page_config(page_title="Blockchain Ticketing", layout="wide")

# Ensure blockchain & counter exist in session_state
if "blockchain" not in st.session_state:
    st.session_state["blockchain"] = Blockchain()
if "ticket_counter" not in st.session_state:
    st.session_state["ticket_counter"] = 1

st.title("🎟 Blockchain-based Event Ticketing System")

# In-page menu instead of sidebar
menu = st.radio("Select an Option:", ["Buy Ticket", "Verify Ticket", "View Blockchain"])

# -----------------------------
# Buy Ticket
# -----------------------------
if menu == "Buy Ticket":
    st.subheader("🛒 Buy a Ticket")

    # Auto-generate ticket ID
    ticket_id = f"TICKET{st.session_state['ticket_counter']}"

    if st.button("Generate Ticket"):
        new_block = st.session_state["blockchain"].add_block({"ticket_id": ticket_id})
        st.session_state["ticket_counter"] += 1
        st.success(f"🎉 Your ticket has been issued!\n\n**Ticket ID: {ticket_id}**")

# -----------------------------
# Verify Ticket
# -----------------------------
elif menu == "Verify Ticket":
    st.subheader("🔍 Verify Ticket")
    ticket_id_input = st.text_input("Enter Ticket ID to Verify")
    if st.button("Verify"):
        if st.session_state["blockchain"].is_ticket_valid(ticket_id_input):
            st.success(f"✅ Ticket ID {ticket_id_input} is valid and exists on blockchain.")
        else:
            st.error(f"❌ Ticket ID {ticket_id_input} is invalid or not found.")

# -----------------------------
# View Blockchain
# -----------------------------
elif menu == "View Blockchain":
    st.subheader("⛓ Blockchain Ledger")
    for block in st.session_state["blockchain"].chain:
        st.json({
            "Index": block.index,
            "Timestamp": block.timestamp,
            "Ticket": block.transaction,
            "Hash": block.hash,
            "Previous Hash": block.previous_hash
        })

st.caption("🚀 Powered by Blockchain Simulation in Python & Streamlit")

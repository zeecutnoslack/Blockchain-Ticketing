import hashlib
import json
import time
import streamlit as st

# ---------------- Blockchain ----------------
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash="0", data="Genesis Block")

    def create_block(self, previous_hash, data):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(time.time()),
            "data": data,
            "previous_hash": previous_hash,
            "hash": self.hash_block(len(self.chain) + 1, time.time(), data, previous_hash),
        }
        self.chain.append(block)
        return block

    def hash_block(self, index, timestamp, data, previous_hash):
        block_string = f"{index}{timestamp}{data}{previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def get_previous_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current["previous_hash"] != prev["hash"]:
                return False
        return True

    def verify_ticket(self, ticket_id):
        for block in self.chain:
            if block["data"] == ticket_id:
                return True
        return False


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Blockchain Ticketing", page_icon="🎟️", layout="centered")
st.title("🎟️ Blockchain-based Event Ticketing System")

# Initialize blockchain (session state)
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

blockchain = st.session_state.blockchain

menu = ["Buy Ticket", "Verify Ticket", "View Blockchain"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Buy Ticket":
    st.subheader("🛒 Buy a Ticket")
    ticket_id = st.text_input("Enter Ticket ID")
    if st.button("Buy Ticket"):
        if blockchain.verify_ticket(ticket_id):
            st.error("❌ Ticket already exists (duplicate not allowed)!")
        else:
            prev_block = blockchain.get_previous_block()
            new_block = blockchain.create_block(prev_block["hash"], ticket_id)
            st.success(f"✅ Ticket Purchased Successfully! Block #{new_block['index']} created.")

elif choice == "Verify Ticket":
    st.subheader("🔍 Verify Ticket")
    ticket_id = st.text_input("Enter Ticket ID to Verify")
    if st.button("Verify"):
        if blockchain.verify_ticket(ticket_id):
            st.success("✅ Ticket is VALID (exists in blockchain).")
        else:
            st.error("❌ Ticket is INVALID (not found in blockchain).")

elif choice == "View Blockchain":
    st.subheader("⛓️ Blockchain Ledger")
    for block in blockchain.chain:
        st.json(block)

# Footer
st.caption("🚀 Powered by Blockchain Simulation in Python & Streamlit")

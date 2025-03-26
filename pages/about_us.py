import streamlit as st

# Set page configuration for About Us
st.set_page_config(page_title="About Us - MindEase", layout="wide")

st.title("📌 About MindEase")
st.write("""
MindEase is our capstone project developed under the **Microsoft Hackathon** initiative. 
It is an AI-powered wellness assistant designed to help users track their mood and provide a responsive medical chatbot for mental well-being.
""")

st.subheader("👨‍💻 Meet the Team")

# List of team members (replace placeholder URLs with your actual images)
team_members = [
    {"name": "Alice Johnson", "role": "Developer", "image": "https://via.placeholder.com/150"},
    {"name": "Bob Smith", "role": "Designer", "image": "https://via.placeholder.com/150"},
    {"name": "Charlie Lee", "role": "AI Researcher", "image": "https://via.placeholder.com/150"},
    {"name": "David Kim", "role": "Product Manager", "image": "https://via.placeholder.com/150"},
    {"name": "Eve Williams", "role": "QA Engineer", "image": "https://via.placeholder.com/150"},
]

st.markdown('<div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">', unsafe_allow_html=True)
for member in team_members:
    st.markdown(f"""
        <div style="text-align: center; width: 180px;">
            <img src="{member['image']}" alt="{member['name']}" style="width: 150px; height: 150px; border-radius: 50%; border: 3px solid #2D5F5D;">
            <p style="font-weight: bold; color: #2D5F5D;">{member['name']}</p>
            <p style="font-style: italic; color: #555;">{member['role']}</p>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

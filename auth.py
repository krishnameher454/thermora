import streamlit as st

def login(username: str, password: str) -> bool:
    """Simple placeholder login.
    In a real deployment replace with secure authentication.
    For now any non‑empty username/password logs in.
    """
    if username and password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        return True
    return False

def logout() -> None:
    """Clear session state for logout."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def role_switcher() -> None:
    """Sidebar widget to select user role.
    Available roles: "citizen" and "officer".
    """
    if 'role' not in st.session_state:
        st.session_state['role'] = 'citizen'
    role = st.sidebar.selectbox('Select Role', ['citizen', 'officer'], index=0 if st.session_state['role'] == 'citizen' else 1)
    st.session_state['role'] = role

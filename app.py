import streamlit as st, pandas as pd, json, os, time
st.set_page_config(page_title="CIO Sniper Terminal", layout="wide")

if os.path.exists('status.json'):
    with open('status.json', 'r') as f: stat = json.load(f)
    st.markdown(f"## 🛰️ CURRENT TARGET: `{stat['asset']}`")
    st.info(f"**STATUS:** {stat['msg']} | **TIME:** {stat['time']}")

if os.path.exists('live_consensus.json'):
    with open('live_consensus.json', 'r') as f: live = json.load(f)
    st.subheader(f"🗳️ Live Voting Board: {live['asset']} ({live['progress']})")
    st.dataframe(pd.DataFrame([live['votes']]), width='stretch', hide_index=True)

st.divider()

if os.path.exists('state.json'):
    with open('state.json', 'r') as f: s = json.load(f)
    df = pd.DataFrame.from_dict(s["model_stats"], orient='index')
    if not df.empty and 'Signals' in df.columns:
        df['Accuracy'] = (df['Wins'] / df['Signals']).fillna(0.0).round(4)
        df.index.name = 'AI Model'
        display_df = df.reset_index().sort_values(by=["Accuracy", "Signals", "PL"], ascending=False)
        leader = display_df.iloc[0]['AI Model'] if display_df.iloc[0]['Signals'] > 0 else "Pending..."
        
        c1, c2 = st.columns([3, 2])
        c1.subheader(f"🏆 Leaderboard (Top Sniper: {leader})")
        c1.dataframe(display_df[['AI Model', 'Accuracy', 'PL', 'Signals']], hide_index=True, width='stretch')
        
        c2.subheader("⏱️ Pending Forecasts (5-Min Maturity)")
        if s.get("active_signals"):
            st.dataframe(pd.DataFrame(s["active_signals"])[['asset', 'model', 'score', 'expiry']], hide_index=True, width='stretch')
        else:
            st.info("No active signals maturing.")

time.sleep(10)
st.rerun()

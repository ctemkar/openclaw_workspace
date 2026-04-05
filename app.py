import streamlit as st, pandas as pd, json, os, time
from datetime import datetime
st.set_page_config(page_title="CIO Sniper Terminal", layout="wide")

if os.path.exists('status.json'):
    try:
        with open('status.json', 'r') as f: stat = json.load(f)
        st.markdown(f"## 🛰️ CURRENT TARGET: `{stat.get('asset', '-')}`")
        st.info(f"**STATUS:** {stat.get('msg', 'Initializing...')} | **TIME:** {stat.get('time', '-')}")
    except: pass

if os.path.exists('live_consensus.json'):
    try:
        with open('live_consensus.json', 'r') as f: live = json.load(f)
        st.subheader(f"🗳️ Voting Board: {live.get('asset', '-')} ({live.get('progress', '...')})")
        if 'votes' in live:
            st.dataframe(pd.DataFrame([live['votes']]), width='stretch', hide_index=True)
    except: pass

st.divider()

if os.path.exists('state.json'):
    try:
        with open('state.json', 'r') as f: s = json.load(f)
        df = pd.DataFrame.from_dict(s["model_stats"], orient='index')
        if not df.empty and 'Signals' in df.columns:
            df['Accuracy'] = (df['Wins'] / df['Signals']).fillna(0.0).round(4)
            df.index.name = 'AI Model'
            display_df = df.reset_index().sort_values(by=["Accuracy", "Signals", "PL"], ascending=False)
            leader = display_df.iloc[0]['AI Model'] if display_df.iloc[0]['Signals'] > 0 else "Analyzing..."
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.subheader(f"🏆 Leaderboard (Winner: {leader})")
                st.dataframe(display_df[['AI Model', 'Accuracy', 'PL', 'Signals']], hide_index=True, width='stretch', column_config={"AI Model": st.column_config.TextColumn("Model", width="medium"), "Accuracy": st.column_config.NumberColumn("Acc", format="%.4f"), "PL": st.column_config.NumberColumn("P/L", format="$%.4f")})
            with col2:
                st.subheader("⏱️ Pending Forecasts")
                if s.get("active_signals"):
                    adf = pd.DataFrame(s["active_signals"])
                    adf['expiry'] = adf['expiry'].apply(lambda x: datetime.fromisoformat(x).strftime("%H:%M:%S"))
                    st.dataframe(adf[['asset', 'model', 'score', 'expiry']], hide_index=True, width='stretch', column_config={"asset": st.column_config.TextColumn("Asset", width="small"), "model": st.column_config.TextColumn("Model", width="small"), "score": st.column_config.NumberColumn("Score", format="%.1f"), "expiry": st.column_config.TextColumn("Time", width="small")})
                else: st.info("No active signals.")
    except: pass

time.sleep(10)
st.rerun()

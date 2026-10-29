"""
streamlit_app.py — Perudo, il gioco di dadi e bluff, versione web.
Avvio locale: streamlit run streamlit_app.py
"""

import html

import streamlit as st

import perudo_engine as E

st.set_page_config(page_title="Perudo", page_icon="🎲", layout="wide")

# ── Stile ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --felt-1: #1f6b45; --felt-2: #0f3d27; --felt-3: #0a2a1b;
  --wood: #5a3b1c; --gold: #E9B949; --ivory: #FBF7EE; --ink: #F3EFE0;
}
.block-container { padding-top: 3.4rem; max-width: 1200px; }
.felt {
  background: radial-gradient(ellipse at center, var(--felt-1) 0%, var(--felt-2) 70%, var(--felt-3) 100%);
  border: 8px solid var(--wood); border-radius: 28px; padding: 18px 18px 8px;
  box-shadow: inset 0 0 50px rgba(0,0,0,.55), 0 8px 24px rgba(0,0,0,.35);
  color: var(--ink); margin-bottom: 14px;
}
.felt .ptitle { font-size: 2.4rem; font-weight: 800; letter-spacing: .04em; line-height: 1.1; }
.felt .psub { opacity: .75; margin: 0 0 .7rem; }
.pgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
.pcard {
  background: rgba(0,0,0,.28); border: 2px solid rgba(255,255,255,.06); border-radius: 18px;
  padding: 10px 8px 8px; text-align: center; transition: all .2s;
}
.pcard.turn { border-color: var(--gold); box-shadow: 0 0 20px rgba(233,185,73,.55); }
.pcard.out { opacity: .38; }
.pname { font-weight: 700; font-size: 1.05rem; }
.pmeta { font-size: .8rem; opacity: .75; min-height: 1.1em; margin-bottom: 6px; }
.avatar { font-size: 1.8rem; line-height: 1.2; }
.bidbox { text-align: center; padding: 12px 6px 4px; }
.bidlabel { text-transform: uppercase; font-size: .78rem; letter-spacing: .12em; opacity: .7; }
.bidval { font-size: 2.2rem; font-weight: 800; display: inline-flex; align-items: center; gap: 10px; }
.bidby { opacity: .8; font-size: .95rem; }
.die {
  --s: 40px; display: inline-grid; grid-template: repeat(3, 1fr) / repeat(3, 1fr);
  width: var(--s); height: var(--s); padding: calc(var(--s) * .12); margin: 3px; box-sizing: border-box;
  background: var(--ivory); border-radius: 22%; vertical-align: middle;
  box-shadow: 0 3px 0 #c9bfa8, 0 5px 9px rgba(0,0,0,.35); transition: transform .2s;
}
.die span { border-radius: 50%; margin: 14%; }
.die span.on { background: #1d1d1f; }
.die.lama { background: #F4D03F; box-shadow: 0 3px 0 #b8961f, 0 5px 9px rgba(0,0,0,.35); }
.die.lama span.on { background: #5a3b1c; }
.die.hidden { background: #3b2414; box-shadow: 0 3px 0 #22140a, 0 5px 9px rgba(0,0,0,.35); }
.die.match { outline: 3px solid var(--gold); outline-offset: 2px; transform: translateY(-4px); }
.die.dim { opacity: .3; }
.die.big { --s: 58px; }
.die.small { --s: 26px; margin: 1px; }
.log { background: rgba(0,0,0,.22); border-radius: 14px; padding: 8px 12px; max-height: 260px; overflow-y: auto; }
.logrow { padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,.06); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.logrow:last-child { border-bottom: none; }
.logrow.round { opacity: .65; font-style: italic; }
.logrow.bugiardo, .logrow.calza { color: var(--gold); font-weight: 600; }
.logrow.win { color: var(--gold); font-weight: 800; font-size: 1.1rem; }
.outcome { background: rgba(233,185,73,.15); border: 1px solid var(--gold); border-radius: 14px; padding: 10px 14px; margin: 8px 0; }
.you { text-align: center; }
@media (max-width: 640px) {
  .felt { padding: 12px 10px 6px; border-width: 6px; }
  .felt .ptitle { font-size: 1.8rem; } .bidval { font-size: 1.7rem; }
  .pgrid { grid-template-columns: repeat(auto-fit, minmax(96px, 1fr)); gap: 6px; }
  .pcard { padding: 6px 4px; border-radius: 14px; }
  .avatar { font-size: 1.3rem; } .pname { font-size: .9rem; } .pmeta { font-size: .7rem; }
  .die { --s: 32px; } .die.big { --s: 46px; } .die.small { --s: 15px; margin: 1px; }
}
</style>
""", unsafe_allow_html=True)

_PIPS = {1: [4], 2: [0, 8], 3: [0, 4, 8], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8]}
_FACE_LABEL = {1: "🦙 Lame (1)", 2: "⚁ 2", 3: "⚂ 3", 4: "⚃ 4", 5: "⚄ 5", 6: "⚅ 6"}


def die_html(v: int, size: str = "", hidden: bool = False, match: bool = False, dim: bool = False) -> str:
    cls = ["die", size]
    if hidden:
        return f'<span class="die hidden {size}"></span>'
    if v == E.LAMA:
        cls.append("lama")
    if match:
        cls.append("match")
    if dim:
        cls.append("dim")
    pips = "".join(f'<span class="{"on" if k in _PIPS[v] else ""}"></span>' for k in range(9))
    return f'<span class="{" ".join(c for c in cls if c)}" title="{v}">{pips}</span>'


def bid_html(bid, size: str = "") -> str:
    q, f = bid
    return f"{q} × {die_html(f, size)}"


def counts_for(face: int, d: int) -> bool:
    return d == face or (face != E.LAMA and d == E.LAMA)


# ── Stato ─────────────────────────────────────────────────────────────────────
ss = st.session_state


def start_new_game():
    ss.game = E.new_game(ss.get("cfg_name", "Tu").strip() or "Tu",
                         int(ss.get("cfg_opp", 3)), ss.get("cfg_diff") or "Normale")
    ss.pop("bid_face", None)


if "game" not in ss:
    start_new_game()
g: E.Game = ss.game
me = g.players[g.human]

# ── Barra laterale: impostazioni e regole ────────────────────────────────────
with st.sidebar:
    st.header("🎲 Nuova partita")
    st.text_input("Il tuo nome", value="Tu", key="cfg_name", max_chars=16)
    st.slider("Avversari", 1, 6, 3, key="cfg_opp")
    st.segmented_control("Difficoltà", E.DIFFICULTIES, default="Normale", key="cfg_diff")
    st.button("Inizia una nuova partita", on_click=start_new_game, type="primary",
              use_container_width=True)
    st.divider()
    st.toggle("Mostra le probabilità", value=True, key="show_prob",
              help="Calcolate solo sui tuoi dadi: gli altri sono un segreto anche per l'app.")
    with st.expander("📜 Regole"):
        st.markdown(
            "- Ognuno ha **5 dadi** nascosti sotto il bicchiere.\n"
            "- A turno si dichiara quanti dadi di un valore ci sono **in tutto sul tavolo**, "
            "es. *«sette 4»*.\n"
            "- Le **lame** (gli 1, in oro) sono **jolly**: contano per qualunque valore, "
            "ma non quando si punta proprio sulle lame.\n"
            "- Per rilanciare: più dadi, oppure stessi dadi con un valore più alto. "
            "Passare alle lame: almeno **metà** (per eccesso). Tornare dalle lame: almeno "
            "il **doppio + 1**.\n"
            "- **Bugiardo!** se pensi che la puntata sia troppo alta: si scoprono i dadi e "
            "perde un dado chi ha torto.\n"
            "- **Calza!** se pensi che sia esatta: se hai ragione guadagni un dado (max 5), "
            "altrimenti ne perdi uno. Senza dadi puoi ancora calzare **una volta** per rientrare.\n"
            "- Chi perde un dado apre il giro successivo. Vince l'ultimo con dei dadi."
        )

# ── Intestazione e avversari ──────────────────────────────────────────────────
cards = []
for i, p in enumerate(g.players):
    if p.is_human:
        continue
    state = "turn" if (i == g.turn and g.phase == "bidding") else ("out" if not p.in_game else "")
    if g.phase == "reveal" and g.reveal:
        face = g.reveal["bid"][1]
        dice = "".join(die_html(d, "small", match=counts_for(face, d), dim=not counts_for(face, d))
                       for d in g.reveal["dice"][i])
    elif g.phase == "over":
        dice = "".join(die_html(d, "small") for d in p.dice)
    else:
        dice = "".join(die_html(0, "small", hidden=True) for _ in range(p.n_dice))
    if p.n_dice == 0:
        meta = "può ancora calzare" if p.can_reenter else "fuori dal gioco"
    else:
        meta = f"{p.n_dice} dad{'o' if p.n_dice == 1 else 'i'}"
    if i == g.turn and g.phase == "bidding":
        meta = "🎯 sta pensando…"
    cards.append(f'<div class="pcard {state}"><div class="avatar">{p.avatar}</div>'
                 f'<div class="pname">{html.escape(p.name)}</div>'
                 f'<div class="pmeta">{meta}</div><div>{dice or "&nbsp;"}</div></div>')

if g.bid is not None:
    by = g.players[g.last_bidder]
    bid_block = (f'<div class="bidbox"><div class="bidlabel">Puntata sul tavolo</div>'
                 f'<div class="bidval">{bid_html((g.bid.qty, g.bid.face), "big")}</div>'
                 f'<div class="bidby">di {by.avatar} {html.escape(by.name)} · '
                 f'{g.total_dice} dadi in gioco</div></div>')
else:
    bid_block = (f'<div class="bidbox"><div class="bidlabel">Nessuna puntata</div>'
                 f'<div class="bidby">Giro {g.round_no} · {g.total_dice} dadi in gioco · apre '
                 f'{g.current.avatar} {html.escape(g.current.name)}</div></div>')

st.markdown(
    '<div class="felt"><div class="ptitle">🎲 Perudo</div>'
    '<div class="psub">Il gioco di dadi e bluff delle Ande</div>'
    f'<div class="pgrid">{"".join(cards)}</div>{bid_block}</div>',
    unsafe_allow_html=True)


# ── Azioni del giocatore ──────────────────────────────────────────────────────
def act(fn, *args):
    try:
        fn(*args)
    except ValueError as e:
        ss.flash = str(e)
        return
    g.run_ai()


def do_next_round():
    g.next_round()
    g.run_ai()


def play_to_end():
    for _ in range(500):
        if g.phase == "over":
            break
        if g.phase == "reveal":
            g.next_round()
        g.run_ai()


left, right = st.columns([3, 2], gap="large")

with left:
    if g.phase == "over":
        if g.winner == g.human:
            st.success(f"🏆 Hai vinto, {me.name}! Nessuno ti ha smascherato.")
            if not ss.get("celebrated"):
                st.balloons()
                ss.celebrated = True
        else:
            w = g.players[g.winner]
            st.info(f"{w.avatar} **{w.name}** vince la partita.")
        st.button("🎲 Gioca ancora", on_click=start_new_game, type="primary", use_container_width=True)
    else:
        ss.celebrated = False

    if g.phase == "reveal" and g.reveal:
        r = g.reveal
        face = r["bid"][1]
        st.markdown(f'<div class="outcome">{html.escape(g.log[-1]["text"])}</div>',
                    unsafe_allow_html=True)
        mine = "".join(die_html(d, "big", match=counts_for(face, d), dim=not counts_for(face, d))
                       for d in r["dice"][g.human])
        st.markdown(f'<div class="you">I tuoi dadi: {mine or "nessuno"}<br>'
                    f'Puntata {bid_html(r["bid"])} — validi sul tavolo: <b>{r["actual"]}</b></div>',
                    unsafe_allow_html=True)
        st.button("🎲 Prossimo giro", on_click=do_next_round, type="primary", use_container_width=True)

    elif g.phase == "bidding":
        your_dice = "".join(die_html(d, "big") for d in me.dice)
        st.markdown(f'<div class="you"><b>{me.avatar} {html.escape(me.name)}</b> — '
                    f'i tuoi dadi<br>{your_dice or "<i>nessun dado</i>"}</div>',
                    unsafe_allow_html=True)

        if g.current.is_human:
            acts = g.legal_actions()
            unknown = g.total_dice - me.n_dice
            if "punta" in acts:
                faces = [f for f in range(1, 7) if not (g.bid is None and f == E.LAMA)]
                if ss.get("bid_face") not in faces:
                    ss.bid_face = faces[-1] if g.bid is None else g.bid.face
                face = st.segmented_control("Valore", faces, format_func=_FACE_LABEL.get,
                                            key="bid_face") or faces[0]
                q_min = E.min_qty_for(face, g.bid)
                qty = st.number_input("Quantità", min_value=q_min, max_value=max(q_min, g.total_dice),
                                      value=q_min, step=1,
                                      key=f"bid_qty_{g.round_no}_{len(g.log)}_{face}")
                if ss.show_prob:
                    pr = E.bid_probability(me.dice, unknown, E.Bid(int(qty), face))
                    st.caption(f"Con i tuoi dadi, «{qty} × {face}» è vera nel **{pr:.0%}** dei casi.")
            b1, b2, b3 = st.columns(3)
            with b1:
                if "punta" in acts:
                    st.button("📣 Dichiara", type="primary", use_container_width=True,
                              on_click=act, args=(g.make_bid, int(qty), face))
                elif "passa" in acts:
                    st.button("⏭️ Passa", use_container_width=True, on_click=act, args=(g.pass_turn,))
            with b2:
                st.button("🤥 Bugiardo!", use_container_width=True, disabled="bugiardo" not in acts,
                          on_click=act, args=(g.call_liar,))
            with b3:
                st.button("🎯 Calza!", use_container_width=True, disabled="calza" not in acts,
                          on_click=act, args=(g.call_exact,))
            if ss.show_prob and g.bid is not None:
                p_true = E.bid_probability(me.dice, unknown, g.bid)
                p_ex = E.exact_probability(me.dice, unknown, g.bid)
                st.caption(f"La puntata sul tavolo è vera nel **{p_true:.0%}** dei casi, "
                           f"esatta nel **{p_ex:.0%}**.")
        elif not me.in_game:
            st.info("Sei fuori dal gioco: guarda come va a finire.")
            st.button("⏩ Vai alla fine della partita", on_click=play_to_end, use_container_width=True)

    if ss.get("flash"):
        st.warning(ss.pop("flash"))

with right:
    st.markdown("#### 📜 Cronaca del giro")
    rows = []
    for ev in reversed([e for e in g.log if e["round"] == g.round_no] or g.log[-1:]):
        who = g.players[ev["who"]] if ev["who"] is not None else None
        if ev["kind"] == "bid":
            text = f'{who.avatar} <b>{html.escape(who.name)}</b> punta {bid_html(ev["bid"], "small")}'
        else:
            text = (f"{who.avatar} " if who else "") + html.escape(ev["text"])
        rows.append(f'<div class="logrow {ev["kind"]}">{text}</div>')
    st.markdown(f'<div class="log">{"".join(rows)}</div>', unsafe_allow_html=True)
    st.caption(f"Difficoltà: {g.difficulty} · giro {g.round_no}")

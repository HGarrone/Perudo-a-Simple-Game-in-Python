"""
perudo_engine.py
Regole e avversari di Perudo, senza interfaccia (usato da streamlit_app.py).

Regole (come in Perudo.py, senza la regola "palifico"):
- ogni giocatore parte con 5 dadi; le "lame" (gli 1) sono jolly e contano per
  qualunque valore, tranne quando si punta proprio sulle lame;
- una puntata è (quantità, valore): si rilancia aumentando la quantità, oppure
  a parità di quantità con un valore più alto; si passa alle lame con almeno
  metà della quantità (arrotondata per eccesso) e si torna dalle lame con
  almeno il doppio + 1;
- "Bugiardo!": se i dadi sul tavolo sono meno della puntata perde un dado chi
  l'ha fatta, altrimenti chi ha accusato;
- "Calza!": se i dadi sono esattamente quelli della puntata chi ha calzato
  guadagna un dado (massimo 5), altrimenti ne perde uno. Chi è rimasto senza
  dadi può ancora calzare una volta per rientrare con un dado;
- vince l'ultimo giocatore con dei dadi.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

MAX_DICE = 5
LAMA = 1

DIFFICULTIES = ("Facile", "Normale", "Difficile")

# Per difficoltà: soglia di probabilità sotto cui si dà del bugiardo,
# rumore sulle stime (più rumore = errori più frequenti) e propensione al bluff.
# Tarati con partite simulate: contro "Normale", "Difficile" vince ~2 volte su 3
# e "Facile" ~1 su 4 (accusa troppo presto e stima male).
_AI_PARAMS = {
    "Facile":    {"liar": 0.48, "noise": 0.25, "bluff": 0.30},
    "Normale":   {"liar": 0.33, "noise": 0.12, "bluff": 0.18},
    "Difficile": {"liar": 0.25, "noise": 0.00, "bluff": 0.12},
}

AI_NAMES = ["Luna", "Pablo", "Inés", "Marco", "Sofía", "Diego", "Carmen", "Mateo", "Valeria"]
AI_AVATARS = ["🦜", "🦙", "🐆", "🦉", "🐍", "🦊", "🐢", "🦅", "🐒"]


@dataclass
class Bid:
    qty: int
    face: int


@dataclass
class Player:
    name: str
    is_human: bool = False
    avatar: str = "🙂"
    dice: list[int] = field(default_factory=lambda: [0] * MAX_DICE)
    can_reenter: bool = True
    # carattere dell'avversario: >0 più spavaldo, <0 più prudente
    temper: float = 0.0

    @property
    def n_dice(self) -> int:
        return len(self.dice)

    @property
    def in_game(self) -> bool:
        """Ancora al tavolo: ha dadi, oppure può ancora rientrare calzando."""
        return self.n_dice > 0 or self.can_reenter


def count_matching(dice: list[int], face: int) -> int:
    """Dadi che valgono per `face` (le lame sono jolly, tranne puntando sulle lame)."""
    if face == LAMA:
        return sum(1 for d in dice if d == LAMA)
    return sum(1 for d in dice if d == face or d == LAMA)


def is_valid_raise(new: Bid, cur: Bid | None) -> bool:
    if not (1 <= new.face <= 6) or new.qty < 1:
        return False
    if cur is None:
        return new.face != LAMA  # non si apre sulle lame
    if cur.face == LAMA:
        if new.face == LAMA:
            return new.qty > cur.qty
        return new.qty >= 2 * cur.qty + 1
    if new.face == LAMA:
        return new.qty >= math.ceil(cur.qty / 2)
    return new.qty > cur.qty or (new.qty == cur.qty and new.face > cur.face)


def min_qty_for(face: int, cur: Bid | None) -> int:
    """Quantità minima valida per puntare su `face` dopo la puntata `cur`."""
    if cur is None:
        return 1
    if cur.face == LAMA:
        return cur.qty + 1 if face == LAMA else 2 * cur.qty + 1
    if face == LAMA:
        return math.ceil(cur.qty / 2)
    return cur.qty if face > cur.face else cur.qty + 1


def _binom_tail(n: int, k: int, p: float) -> float:
    """P(X >= k) con X ~ Binomiale(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _binom_exact(n: int, k: int, p: float) -> float:
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def bid_probability(own_dice: list[int], unknown: int, bid: Bid) -> float:
    """Probabilità che la puntata sia vera, sapendo solo i propri dadi."""
    p = 1 / 6 if bid.face == LAMA else 1 / 3
    return _binom_tail(unknown, bid.qty - count_matching(own_dice, bid.face), p)


def exact_probability(own_dice: list[int], unknown: int, bid: Bid) -> float:
    p = 1 / 6 if bid.face == LAMA else 1 / 3
    return _binom_exact(unknown, bid.qty - count_matching(own_dice, bid.face), p)


@dataclass
class Game:
    players: list[Player]
    difficulty: str = "Normale"
    seed: int | None = None
    turn: int = 0
    bid: Bid | None = None
    last_bidder: int | None = None
    phase: str = "bidding"          # bidding | reveal | over
    round_no: int = 0
    log: list[dict] = field(default_factory=list)
    reveal: dict | None = None
    winner: int | None = None
    next_starter: int = 0           # chi apre il prossimo giro (chi ha perso/calzato)

    def __post_init__(self):
        self.rng = random.Random(self.seed)

    # ── stato ────────────────────────────────────────────────────────────
    @property
    def total_dice(self) -> int:
        return sum(p.n_dice for p in self.players)

    @property
    def human(self) -> int:
        return next(i for i, p in enumerate(self.players) if p.is_human)

    @property
    def current(self) -> Player:
        return self.players[self.turn]

    def _next_in_game(self, i: int) -> int:
        n = len(self.players)
        for step in range(1, n + 1):
            j = (i + step) % n
            if self.players[j].in_game:
                return j
        return i

    def _with_dice_from(self, i: int) -> int:
        """`i` se ha dadi, altrimenti il primo giocatore con dadi dopo di lui."""
        n = len(self.players)
        for step in range(n):
            j = (i + step) % n
            if self.players[j].n_dice > 0:
                return j
        return i

    def _say(self, kind: str, text: str, who: int | None = None, bid: Bid | None = None):
        self.log.append({"kind": kind, "text": text, "who": who, "round": self.round_no,
                         "bid": (bid.qty, bid.face) if bid else None})

    # ── giri ─────────────────────────────────────────────────────────────
    def start_round(self, starter: int):
        self.round_no += 1
        for p in self.players:
            p.dice = [self.rng.randint(1, 6) for _ in range(p.n_dice)]
        self.bid = None
        self.last_bidder = None
        self.reveal = None
        self.phase = "bidding"
        self.turn = self._with_dice_from(starter)
        self._say("round", f"Giro {self.round_no}: si tirano i dadi ({self.total_dice} in gioco).")

    def _check_over(self) -> bool:
        alive = [i for i, p in enumerate(self.players) if p.n_dice > 0]
        if len(alive) == 1:
            self.winner = alive[0]
            self.phase = "over"
            self._say("win", f"Vince la partita: {self.players[alive[0]].name}!", who=alive[0])
            return True
        return False

    def _advance(self):
        self.turn = self._next_in_game(self.turn)
        # chi non ha dadi non può aprire il giro: passa da solo
        while self.bid is None and self.current.n_dice == 0:
            self.turn = self._next_in_game(self.turn)

    # ── azioni ───────────────────────────────────────────────────────────
    def legal_actions(self) -> set[str]:
        if self.phase != "bidding":
            return set()
        p = self.current
        if p.n_dice == 0:
            return {"calza", "passa"} if self.bid is not None else {"passa"}
        acts = {"punta"}
        if self.bid is not None and self.last_bidder != self.turn:
            acts |= {"bugiardo", "calza"}
        return acts

    def make_bid(self, qty: int, face: int):
        new = Bid(qty, face)
        if "punta" not in self.legal_actions() or not is_valid_raise(new, self.bid):
            raise ValueError("Puntata non valida.")
        self.bid = new
        self.last_bidder = self.turn
        self._say("bid", f"{self.current.name} punta", who=self.turn, bid=new)
        self._advance()

    def pass_turn(self):
        if "passa" not in self.legal_actions():
            raise ValueError("Non puoi passare.")
        self._say("pass", f"{self.current.name}: senza dadi, passa.", who=self.turn)
        self._advance()

    def _resolve(self, kind: str):
        caller = self.turn
        bidder = self.last_bidder
        bid = self.bid
        before = {i: list(p.dice) for i, p in enumerate(self.players)}
        all_dice = [d for p in self.players for d in p.dice]
        actual = count_matching(all_dice, bid.face)
        caller_p = self.players[caller]
        if kind == "bugiardo":
            liar = actual < bid.qty
            loser = bidder if liar else caller
            self.players[loser].dice.pop()
            outcome = (f"«Bugiardo!» di {caller_p.name} a {self.players[bidder].name}: "
                       f"ci sono {actual} dadi validi su {bid.qty} dichiarati. "
                       f"Perde un dado: {self.players[loser].name}.")
            starter, gained, lost = loser, None, loser
        else:
            exact = actual == bid.qty
            gained = lost = None
            if exact:
                if caller_p.n_dice == 0:
                    caller_p.dice.append(0)
                    caller_p.can_reenter = False
                    tail = f"{caller_p.name} rientra in partita con un dado!"
                elif caller_p.n_dice < MAX_DICE:
                    caller_p.dice.append(0)
                    tail = f"Un dado in più per {caller_p.name}!"
                else:
                    tail = f"Solo gloria per {caller_p.name}: ha già 5 dadi."
                gained = caller
                outcome = f"«Calza!» di {caller_p.name}: ci sono esattamente {actual} dadi validi. {tail}"
            else:
                if caller_p.n_dice == 0:
                    caller_p.can_reenter = False
                    tail = f"{caller_p.name} è fuori dal gioco."
                else:
                    caller_p.dice.pop()
                    tail = f"Perde un dado: {caller_p.name}."
                    lost = caller
                outcome = f"«Calza!» di {caller_p.name}: i dadi validi sono {actual}, non {bid.qty}. {tail}"
            starter = caller
        self.reveal = {"kind": kind, "bid": (bid.qty, bid.face), "actual": actual,
                       "caller": caller, "bidder": bidder, "gained": gained, "lost": lost,
                       "dice": before}
        self._say(kind, outcome, who=caller, bid=bid)
        self.phase = "reveal"
        self.next_starter = starter
        self._check_over()

    def call_liar(self):
        if "bugiardo" not in self.legal_actions():
            raise ValueError("Non puoi dare del bugiardo adesso.")
        self._resolve("bugiardo")

    def call_exact(self):
        if "calza" not in self.legal_actions():
            raise ValueError("Non puoi calzare adesso.")
        self._resolve("calza")

    def next_round(self):
        if self.phase != "reveal":
            return
        self.start_round(self.next_starter)

    # ── avversari ────────────────────────────────────────────────────────
    def ai_move(self):
        """Fa giocare l'avversario di turno (una sola azione)."""
        i = self.turn
        me = self.players[i]
        prm = _AI_PARAMS.get(self.difficulty, _AI_PARAMS["Normale"])
        rng = self.rng
        unknown = self.total_dice - me.n_dice
        noise = lambda: rng.uniform(-prm["noise"], prm["noise"])
        acts = self.legal_actions()

        if me.n_dice == 0:
            if "calza" in acts and exact_probability([], unknown, self.bid) + noise() > 0.24:
                return self.call_exact()
            return self.pass_turn()

        if self.bid is None:
            faces = [f for f in range(2, 7)]
            best = max(faces, key=lambda f: (count_matching(me.dice, f), rng.random()))
            if rng.random() < prm["bluff"]:
                best = rng.choice(faces)
            expected = count_matching(me.dice, best) + unknown / 3
            qty = max(1, int(expected * rng.uniform(0.55, 0.85)))
            return self.make_bid(qty, best)

        p_true = bid_probability(me.dice, unknown, self.bid)
        liar_thr = prm["liar"] - 0.06 * me.temper
        if p_true + noise() < liar_thr:
            return self.call_liar()

        p_exact = exact_probability(me.dice, unknown, self.bid)
        if me.n_dice < MAX_DICE and p_exact + noise() > 0.30 and rng.random() < 0.65:
            return self.call_exact()

        # rilancio: tra le puntate valide più vicine sceglie la più credibile,
        # con un pizzico di bluff e di carattere
        cands = []
        for face in range(1, 7):
            q0 = min_qty_for(face, self.bid)
            for q in range(q0, q0 + 2):
                b = Bid(q, face)
                if not is_valid_raise(b, self.bid):
                    continue
                score = bid_probability(me.dice, unknown, b)
                score += rng.uniform(0, prm["bluff"]) * (1 + me.temper)
                score -= 0.04 * (q - q0)
                cands.append((score, b))
        if not cands:
            return self.call_liar()
        score, best = max(cands, key=lambda t: t[0])
        if score < liar_thr and p_true < 0.5:
            return self.call_liar()
        return self.make_bid(best.qty, best.face)

    def run_ai(self, max_steps: int = 200):
        """Fa giocare gli avversari finché tocca all'umano o il giro si chiude."""
        steps = 0
        while self.phase == "bidding" and not self.current.is_human and steps < max_steps:
            self.ai_move()
            steps += 1


def new_game(human_name: str, n_opponents: int, difficulty: str, seed: int | None = None) -> Game:
    rng = random.Random(seed)
    names = rng.sample(range(len(AI_NAMES)), n_opponents)
    players = [Player(name=human_name or "Tu", is_human=True, avatar="🙂")]
    for k in names:
        players.append(Player(name=AI_NAMES[k], avatar=AI_AVATARS[k], temper=rng.uniform(-1, 1)))
    g = Game(players=players, difficulty=difficulty, seed=seed)
    g.start_round(rng.randrange(len(players)))
    g.run_ai()
    return g
